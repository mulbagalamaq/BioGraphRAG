"""Pipeline orchestrator — the heart of BioGraphRAG.

Question → Embed → Fetch KG → Prune → (optional GNN rank) → Prompt → LLM → Response
"""

from __future__ import annotations

import asyncio
import logging
import time
from typing import Any, Dict, List

from backend.config import AppConfig, load_config
from backend.embeddings import EmbeddingModel
from backend.gnn import GNN_AVAILABLE, GNNRanker
from backend.graph import prune_subgraph
from backend.llm import call_llm
from backend.prompt import build_prompt
from backend.pubmed import BiomedicalDataFetcher

LOGGER = logging.getLogger(__name__)


async def answer_question(question: str, config: AppConfig | None = None) -> Dict[str, Any]:
    """Run the full BioGraphRAG pipeline and return a structured result."""
    t0 = time.monotonic()
    if config is None:
        config = load_config()

    # 1. Embed the question (CPU-bound → run in thread)
    embedder = EmbeddingModel(config.get("embedding.model", "sentence-transformers/all-MiniLM-L6-v2"))
    query_vec = await asyncio.to_thread(embedder.embed_query, question)

    # 2. Fetch biomedical data from live APIs
    fetcher = BiomedicalDataFetcher(config)
    kg = await fetcher.build_knowledge_graph(question)
    nodes: List[Dict[str, Any]] = kg["nodes"]
    edges: List[Dict[str, Any]] = kg["edges"]

    # 3. Prune the subgraph
    nodes, edges = prune_subgraph(nodes, edges, config)

    # 4. Optional GNN ranking
    gnn_used = False
    if GNN_AVAILABLE and config.get("gnn.enabled", True):
        try:
            gnn_used = await _gnn_rank(config, embedder, query_vec, nodes, edges)
        except Exception as exc:
            LOGGER.warning("GNN ranking failed, skipping: %s", exc)

    # 5. Build prompt with graph context
    prompt = build_prompt(question, nodes, edges)

    # 6. Call LLM
    answer = await call_llm(prompt, config)

    # 7. Build evidence list from publication nodes
    evidence = _build_evidence(nodes)

    elapsed_ms = int((time.monotonic() - t0) * 1000)
    LOGGER.info("Pipeline completed in %d ms (GNN=%s)", elapsed_ms, gnn_used)

    return {
        "question": question,
        "answer": answer,
        "nodes": nodes,
        "edges": edges,
        "evidence": evidence,
        "metadata": {
            "pipeline_ms": elapsed_ms,
            "gnn_enabled": gnn_used,
            "node_count": len(nodes),
            "edge_count": len(edges),
        },
    }


async def _gnn_rank(
    config: AppConfig,
    embedder: EmbeddingModel,
    query_vec: Any,
    nodes: List[Dict[str, Any]],
    edges: List[Dict[str, Any]],
) -> bool:
    """Apply GNN-based fact ranking.  Mutates *nodes* and *edges* in-place."""
    ranker = GNNRanker(config)
    if not ranker.available():
        return False

    def _do_gnn():
        # Build PyG graph
        data, node_index = ranker.build_pyg_data(nodes, edges)
        if data is None or data.num_nodes == 0:
            return None

        # Structural embeddings
        struct_emb = ranker.compute_structural_embeddings(data)
        if struct_emb is None:
            return None

        # Textify facts + embed them
        fact_texts, lookup = ranker.textify(nodes, edges)
        text_matrix = embedder.embed_texts(fact_texts)
        if text_matrix.size == 0:
            return None

        # Align structural vecs to fact ordering
        struct_vecs = ranker.structural_fact_vectors(nodes, edges, struct_emb, node_index, lookup)

        # Rank and filter
        return ranker.rank_and_reorder(query_vec, text_matrix, struct_vecs, nodes, edges, lookup)

    result = await asyncio.to_thread(_do_gnn)
    if result is not None:
        new_nodes, new_edges = result
        nodes.clear()
        nodes.extend(new_nodes)
        edges.clear()
        edges.extend(new_edges)
        return True
    return False


def _build_evidence(nodes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Extract publication nodes into an evidence list."""
    evidence: List[Dict[str, Any]] = []
    for node in nodes:
        if node.get("type") != "Publication":
            continue
        props = node.get("properties") or {}
        evidence.append(
            {
                "pmid": node.get("pmid", ""),
                "title": node.get("title") or node.get("name", ""),
                "url": props.get("url", ""),
                "score": None,
            }
        )
    return evidence
