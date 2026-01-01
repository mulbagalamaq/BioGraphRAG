"""Real-time graph expansion using live biomedical APIs.

This module fetches real-time data from PubMed, NCBI Gene, and other sources
instead of using pre-loaded graph data.
"""

from __future__ import annotations

import logging
from typing import Dict, List

from src.retrieval.realtime_apis import BiomedicalDataFetcher
from src.utils.config import load_config

LOGGER = logging.getLogger(__name__)


def expand_subgraph_realtime(
    config_path: str,
    seed_ids: List[str],
    hops: int = 2,
    max_degree: int = 10,
) -> List[Dict]:
    """Expand subgraph using real-time API data.

    Parameters
    ----------
    config_path : str
        Path to configuration file
    seed_ids : List[str]
        For realtime mode, seed_ids[0] contains the user's question
    hops : int
        Ignored for realtime mode (kept for interface compatibility)
    max_degree : int
        Ignored for realtime mode (kept for interface compatibility)

    Returns
    -------
    List[Dict]
        List containing single dict with "nodes" and "rels" keys (compatible with expand_graph interface)
    """
    question = seed_ids[0] if seed_ids else ""
    LOGGER.info("Fetching real-time biomedical data for question: %s", question)

    cfg = load_config(config_path)
    email = cfg.get("realtime_apis.ncbi_email")
    api_key = cfg.get("realtime_apis.ncbi_api_key")
    max_nodes = cfg.get("retrieval.prune_max_nodes", 40)

    fetcher = BiomedicalDataFetcher(email=email, api_key=api_key)
    graph = fetcher.build_realtime_graph(question, max_nodes=max_nodes)

    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])

    # Convert to GraphRAG format
    formatted_nodes = []
    for node in nodes:
        formatted_nodes.append({
            "~id": node["id"],
            "~label": node["type"],
            "name": node.get("name", node.get("title", node.get("symbol", ""))),
            "description": node.get("description", node.get("abstract", "")),
            **node.get("properties", {}),
        })

    formatted_edges = []
    for edge in edges:
        formatted_edges.append({
            "~id": f"{edge['source']}__{edge['relation']}__{edge['target']}",
            "~from": edge["source"],
            "~to": edge["target"],
            "~label": edge["relation"],
            "description": edge.get("description", ""),
            **edge.get("properties", {}),
        })

    LOGGER.info("Retrieved %d nodes and %d edges from real-time APIs", len(formatted_nodes), len(formatted_edges))

    # Return in the format expected by expand_graph (list of dicts with "nodes" and "rels")
    return [{"nodes": formatted_nodes, "rels": formatted_edges}]


def query_realtime_vectors(
    config_path: str,
    question: str,
    top_k: int = 10,
) -> List[Dict]:
    """Query real-time biomedical data and return seed nodes.

    Parameters
    ----------
    config_path : str
        Path to configuration file
    question : str
        User's question
    top_k : int
        Number of seed nodes to return

    Returns
    -------
    List[Dict]
        Seed nodes with relevance scores
    """
    LOGGER.info("Fetching real-time seed nodes for: %s", question)

    cfg = load_config(config_path)
    email = cfg.get("realtime_apis.ncbi_email")
    api_key = cfg.get("realtime_apis.ncbi_api_key")

    fetcher = BiomedicalDataFetcher(email=email, api_key=api_key)

    # Search for genes and publications
    genes = fetcher.search_genes(question, max_results=min(5, top_k))
    publications = fetcher.search_publications(question, max_results=min(top_k - len(genes), 10))

    seeds = []
    for i, gene in enumerate(genes):
        seeds.append({
            "id": gene["id"],
            "score": 1.0 - (i * 0.1),  # Decreasing relevance
            "type": "Gene",
            "name": gene.get("symbol", gene.get("name", "")),
            "description": gene.get("description", ""),
        })

    for i, pub in enumerate(publications):
        seeds.append({
            "id": pub["id"],
            "score": 0.8 - (i * 0.05),  # Slightly lower than genes
            "type": "Publication",
            "name": pub.get("title", ""),
            "description": pub.get("abstract", "")[:500],
        })

    return seeds[:top_k]
