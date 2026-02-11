"""Optional PyTorch Geometric GNN ranking — gracefully degrades if torch missing.

Ported from the original ``src/gnn/pyg_rag.py`` with key improvements:
- Stateless class (no module-level globals)
- Guard-imported so the backend works without torch installed
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

LOGGER = logging.getLogger(__name__)

# Guard-import PyTorch Geometric
try:
    import torch
    import torch.nn.functional as F
    from torch import Tensor
    from torch_geometric.data import Data
    from torch_geometric.nn import Node2Vec, SAGEConv
    from torch_geometric.utils import to_undirected

    GNN_AVAILABLE = True
except ImportError:
    GNN_AVAILABLE = False

from backend.config import AppConfig

# Node-type → integer namespace
_NAMESPACE = {"Gene": 0, "Disease": 1, "Drug": 2, "Publication": 3}


class GNNRanker:
    """Per-request GNN-based fact ranker (stateless — no globals)."""

    def __init__(self, config: AppConfig) -> None:
        self.dim = int(config.get("gnn.dim", 32))
        self.epochs = max(1, int(config.get("gnn.epochs", 1)))
        self.walk_length = int(config.get("gnn.walk_length", 10))
        self.context_size = int(config.get("gnn.context_size", 5))
        self.walks_per_node = int(config.get("gnn.walks_per_node", 3))
        self.model_choice = (config.get("gnn.model", "node2vec") or "node2vec").lower()
        self.top_facts = int(config.get("gnn.top_facts", 20))

    @staticmethod
    def available() -> bool:
        return GNN_AVAILABLE

    # ------------------------------------------------------------------
    # Build PyG Data from nodes/edges
    # ------------------------------------------------------------------

    def build_pyg_data(
        self, nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]]
    ) -> Tuple[Any, Dict[str, int]]:
        """Create a homogeneous PyG ``Data`` object."""
        if not GNN_AVAILABLE:
            return None, {}

        if not nodes:
            empty = Data()
            empty.x = torch.empty((0, 3), dtype=torch.float)
            empty.edge_index = torch.empty((2, 0), dtype=torch.long)
            return empty, {}

        node_index: Dict[str, int] = {}
        sorted_nodes = sorted(nodes, key=lambda n: n.get("id", ""))
        for idx, node in enumerate(sorted_nodes):
            nid = node.get("id")
            if nid is not None:
                node_index[nid] = idx

        in_deg = [0] * len(node_index)
        out_deg = [0] * len(node_index)
        src_list: List[int] = []
        tgt_list: List[int] = []

        for edge in edges:
            si = node_index.get(edge.get("source"))
            ti = node_index.get(edge.get("target"))
            if si is None or ti is None or si == ti:
                continue
            out_deg[si] += 1
            in_deg[ti] += 1
            src_list.extend([si, ti])
            tgt_list.extend([ti, si])

        features: List[List[float]] = []
        for node in sorted_nodes:
            nid = node.get("id")
            if nid is None:
                continue
            idx = node_index[nid]
            ns = _NAMESPACE.get(node.get("type", ""), 4)
            features.append([float(in_deg[idx]), float(out_deg[idx]), float(ns)])

        data = Data()
        data.x = torch.tensor(features, dtype=torch.float)
        if src_list:
            raw = torch.tensor([src_list, tgt_list], dtype=torch.long)
            data.edge_index = to_undirected(raw)
        else:
            data.edge_index = torch.empty((2, 0), dtype=torch.long)
        return data, node_index

    # ------------------------------------------------------------------
    # Structural embeddings
    # ------------------------------------------------------------------

    def compute_structural_embeddings(self, data: Any) -> Optional[np.ndarray]:
        """Return (num_nodes, dim) structural embeddings via Node2Vec or GraphSAGE."""
        if not GNN_AVAILABLE or data is None:
            return None
        if data.num_nodes == 0:
            return np.zeros((0, self.dim), dtype=np.float32)

        device = torch.device("cpu")

        if self.model_choice == "graphsage":
            emb = self._graphsage(data, device)
        else:
            emb = self._node2vec(data, device)

        return emb

    def _node2vec(self, data: Any, device: Any) -> np.ndarray:
        if data.num_edges == 0 or data.edge_index.numel() == 0:
            return np.zeros((data.num_nodes, self.dim), dtype=np.float32)

        model = Node2Vec(
            edge_index=data.edge_index,
            embedding_dim=self.dim,
            walk_length=self.walk_length,
            context_size=self.context_size,
            walks_per_node=self.walks_per_node,
            sparse=True,
        ).to(device)

        batch_size = min(256, max(1, data.num_nodes))
        loader = model.loader(batch_size=batch_size, shuffle=True)
        optimizer = torch.optim.SparseAdam(model.parameters(), lr=0.01)

        model.train()
        for _ in range(self.epochs):
            for pos_rw, neg_rw in loader:
                optimizer.zero_grad()
                loss = model.loss(pos_rw.to(device), neg_rw.to(device))
                loss.backward()
                optimizer.step()

        with torch.no_grad():
            embeddings = model.embedding.weight.detach().cpu().numpy()
        return embeddings.astype(np.float32)

    def _graphsage(self, data: Any, device: Any) -> np.ndarray:
        x = data.x.to(device)
        edge_index = data.edge_index.to(device)

        if edge_index.numel() == 0:
            return np.zeros((data.num_nodes, self.dim), dtype=np.float32)

        model = _GraphSAGEEncoder(x.size(1), self.dim).to(device)
        optimizer = torch.optim.Adam(model.parameters(), lr=0.01)

        for _ in range(self.epochs):
            model.train()
            optimizer.zero_grad()
            out = model(x, edge_index)
            loss = F.mse_loss(out, x)
            loss.backward()
            optimizer.step()

        with torch.no_grad():
            embeddings = model(x, edge_index).detach().cpu().numpy()
        return embeddings.astype(np.float32)

    # ------------------------------------------------------------------
    # Textify + rank facts
    # ------------------------------------------------------------------

    def textify(
        self, nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]]
    ) -> Tuple[List[str], List[Tuple[str, int]]]:
        """Convert nodes/edges into human-readable fact strings.

        Returns ``(texts, lookup)`` where lookup maps each text index to
        ``("node", node_index)`` or ``("edge", edge_index)``.
        """
        texts: List[str] = []
        lookup: List[Tuple[str, int]] = []

        for idx, node in enumerate(nodes):
            ntype = node.get("type", "Entity")
            name = node.get("name") or node.get("id", "?")
            desc = node.get("description", "")
            text = f"{ntype}({name})"
            if desc:
                text += f" {desc[:200]}"
            texts.append(text)
            lookup.append(("node", idx))

        for idx, edge in enumerate(edges):
            src = edge.get("source", "?")
            tgt = edge.get("target", "?")
            rel = edge.get("relation", "REL")
            text = f"{rel}({src}->{tgt})"
            desc = edge.get("description", "")
            if desc:
                text += f" {desc}"
            texts.append(text)
            lookup.append(("edge", idx))

        return texts, lookup

    def structural_fact_vectors(
        self,
        nodes: List[Dict[str, Any]],
        edges: List[Dict[str, Any]],
        node_embeddings: np.ndarray,
        node_index: Dict[str, int],
        lookup: List[Tuple[str, int]],
    ) -> np.ndarray:
        """Align structural embeddings to the fact-text ordering."""
        dim = node_embeddings.shape[1] if node_embeddings.ndim == 2 else self.dim
        vecs = np.zeros((len(lookup), dim), dtype=np.float32)

        for row, (kind, ref) in enumerate(lookup):
            if kind == "node" and 0 <= ref < len(nodes):
                nid = nodes[ref].get("id")
                emb_idx = node_index.get(nid)
                if emb_idx is not None and emb_idx < node_embeddings.shape[0]:
                    vecs[row] = node_embeddings[emb_idx]
            elif kind == "edge" and 0 <= ref < len(edges):
                si = node_index.get(edges[ref].get("source"))
                ti = node_index.get(edges[ref].get("target"))
                parts = []
                if si is not None and si < node_embeddings.shape[0]:
                    parts.append(node_embeddings[si])
                if ti is not None and ti < node_embeddings.shape[0]:
                    parts.append(node_embeddings[ti])
                if parts:
                    vecs[row] = np.mean(parts, axis=0)
        return vecs

    def rank_and_reorder(
        self,
        query_vec: np.ndarray,
        text_matrix: np.ndarray,
        structural_vecs: np.ndarray,
        nodes: List[Dict[str, Any]],
        edges: List[Dict[str, Any]],
        lookup: List[Tuple[str, int]],
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Fuse text + structural vectors, rank by cosine sim, keep top facts."""
        from backend.embeddings import _normalize_rows, _safe_normalize

        # Fuse: [text_vec | struct_vec]
        text_normed = _normalize_rows(text_matrix)
        struct_normed = _normalize_rows(structural_vecs)
        fact_fused = np.concatenate([text_normed, struct_normed], axis=1)

        query_normed = _safe_normalize(query_vec)
        # Pad query to match fused dimension
        pad = np.zeros(structural_vecs.shape[1], dtype=np.float32)
        query_fused = np.concatenate([query_normed, pad])
        query_fused = _safe_normalize(query_fused)

        scores = fact_fused @ query_fused
        ranked = np.argsort(scores)[::-1].tolist()

        keep_nodes: set[int] = set()
        keep_edges: set[int] = set()
        for idx in ranked[: self.top_facts]:
            kind, ref = lookup[idx]
            if kind == "node":
                keep_nodes.add(ref)
            else:
                keep_edges.add(ref)
                # Also keep the connected nodes
                edge = edges[ref]
                for n_idx, n in enumerate(nodes):
                    if n["id"] in (edge.get("source"), edge.get("target")):
                        keep_nodes.add(n_idx)

        new_nodes = [nodes[i] for i in sorted(keep_nodes) if i < len(nodes)]
        new_edges = [edges[i] for i in sorted(keep_edges) if i < len(edges)]
        return new_nodes, new_edges


# Guarded inner class
if GNN_AVAILABLE:

    class _GraphSAGEEncoder(torch.nn.Module):
        def __init__(self, in_channels: int, hidden_channels: int) -> None:
            super().__init__()
            mid = max(hidden_channels, in_channels)
            self.conv1 = SAGEConv(in_channels, mid)
            self.conv2 = SAGEConv(mid, hidden_channels)

        def forward(self, x: Tensor, edge_index: Tensor) -> Tensor:
            x = torch.relu(self.conv1(x, edge_index))
            return self.conv2(x, edge_index)
