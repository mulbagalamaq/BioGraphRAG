"""Knowledge-graph construction, expansion, and PCST-like pruning."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Tuple

import networkx as nx

from backend.config import AppConfig

LOGGER = logging.getLogger(__name__)


def build_nx_graph(
    nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]]
) -> nx.Graph:
    """Build a NetworkX graph from node/edge dicts."""
    G = nx.Graph()
    for node in nodes:
        G.add_node(node["id"], data=node)
    for edge in edges:
        src, tgt = edge["source"], edge["target"]
        if G.has_node(src) and G.has_node(tgt):
            G.add_edge(src, tgt, data=edge, weight=_edge_weight(edge))
    return G


def prune_subgraph(
    nodes: List[Dict[str, Any]],
    edges: List[Dict[str, Any]],
    config: AppConfig,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Prize-collecting greedy pruner — keeps the most valuable nodes.

    Node prizes are read from ``config.yaml`` under ``pruning.prizes``.
    """
    max_nodes = int(config.get("pruning.max_nodes", 25))
    if len(nodes) <= max_nodes:
        return nodes, edges

    prize_map: Dict[str, float] = config.get("pruning.prizes", {}) or {}
    default_prize = float(prize_map.get("default", 1.0))

    G = build_nx_graph(nodes, edges)

    # Score each node: configured prize + degree bonus
    scores: Dict[str, float] = {}
    for nid in G.nodes:
        ndata = G.nodes[nid]["data"]
        ntype = ndata.get("type", "")
        prize = float(prize_map.get(ntype, default_prize))
        degree = G.degree(nid)
        scores[nid] = prize + 0.1 * degree

    ranked = sorted(scores, key=scores.get, reverse=True)  # type: ignore[arg-type]
    keep = set(ranked[:max_nodes])

    sub = G.subgraph(keep).copy()
    pruned_nodes = [G.nodes[n]["data"] for n in sub.nodes]
    pruned_edges = [G.edges[u, v]["data"] for u, v in sub.edges]

    LOGGER.info("Pruned %d→%d nodes, %d→%d edges",
                len(nodes), len(pruned_nodes), len(edges), len(pruned_edges))
    return pruned_nodes, pruned_edges


# ------------------------------------------------------------------
# Internal helpers
# ------------------------------------------------------------------

def _edge_weight(edge: Dict[str, Any]) -> float:
    rel = edge.get("relation", "")
    if rel in {"MEASURES", "DERIVED_FROM"}:
        return 0.5
    if rel in {"ASSOCIATED_WITH", "MENTIONS"}:
        return 0.8
    return 1.0
