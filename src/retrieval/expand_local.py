"""Local graph expansion using NetworkX instead of Neptune.

This module provides graph expansion functionality for local deployment
without requiring AWS Neptune. It loads a sample biomedical knowledge graph
from a JSON file and uses NetworkX for graph operations.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Dict, List

import networkx as nx

from src.utils.config import load_config

LOGGER = logging.getLogger(__name__)

# Global graph cache
_GRAPH_CACHE: nx.DiGraph | None = None


def load_local_graph(config_path: str) -> nx.DiGraph:
    """Load the local sample graph from JSON into NetworkX.

    Parameters
    ----------
    config_path:
        Path to configuration file containing the sample graph path.

    Returns
    -------
    nx.DiGraph
        A directed graph with nodes and edges from the sample data.
    """
    global _GRAPH_CACHE

    if _GRAPH_CACHE is not None:
        return _GRAPH_CACHE

    cfg = load_config(config_path)
    graph_file = cfg.get("paths.sample_graph", "data/local/sample_graph.json")

    if not Path(graph_file).exists():
        LOGGER.warning(f"Sample graph file not found: {graph_file}")
        _GRAPH_CACHE = nx.DiGraph()
        return _GRAPH_CACHE

    with open(graph_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    G = nx.DiGraph()

    # Add nodes
    for node in data.get("nodes", []):
        node_id = node["id"]
        G.add_node(
            node_id,
            **{
                "~id": node_id,
                "~labels": [node["type"]],
                "name": node["name"],
                "description": node.get("description", ""),
                "type": node["type"],
                "properties": node.get("properties", {}),
            }
        )

    # Add edges
    for edge in data.get("edges", []):
        source = edge["source"]
        target = edge["target"]
        relation = edge["relation"]
        G.add_edge(
            source,
            target,
            **{
                "~from": source,
                "~to": target,
                "~type": relation,
                "relation": relation,
                "description": edge.get("description", ""),
                "properties": edge.get("properties", {}),
            }
        )

    LOGGER.info(f"Loaded local graph with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")
    _GRAPH_CACHE = G
    return G


def expand_subgraph(
    config_path: str,
    seed_ids: List[str],
    hops: int = 2,
    max_degree: int = 10
) -> List[Dict]:
    """Expand a subgraph from seed nodes using NetworkX.

    Parameters
    ----------
    config_path:
        Path to configuration file.
    seed_ids:
        List of node IDs to start expansion from.
    hops:
        Number of hops to expand from each seed.
    max_degree:
        Maximum number of neighbors to include per node.

    Returns
    -------
    List[Dict]
        List containing a single dict with 'nodes' and 'rels' keys.
    """
    G = load_local_graph(config_path)

    if not seed_ids:
        return [{"nodes": [], "rels": []}]

    # Find all nodes within hops of seeds
    expanded_nodes = set(seed_ids)
    current_layer = set(seed_ids)

    for _ in range(hops):
        next_layer = set()
        for node_id in current_layer:
            if node_id not in G:
                continue

            # Get neighbors (both incoming and outgoing)
            successors = list(G.successors(node_id))[:max_degree]
            predecessors = list(G.predecessors(node_id))[:max_degree]

            next_layer.update(successors)
            next_layer.update(predecessors)

        expanded_nodes.update(next_layer)
        current_layer = next_layer

    # Build subgraph
    subgraph = G.subgraph(expanded_nodes)

    # Convert to expected format
    nodes = []
    for node_id in subgraph.nodes():
        node_data = G.nodes[node_id]
        nodes.append({
            "~id": node_data.get("~id", node_id),
            "~labels": node_data.get("~labels", []),
            "name": node_data.get("name", ""),
            "description": node_data.get("description", ""),
            "type": node_data.get("type", ""),
            **node_data.get("properties", {})
        })

    rels = []
    for source, target in subgraph.edges():
        edge_data = G.edges[source, target]
        rels.append({
            "~from": edge_data.get("~from", source),
            "~to": edge_data.get("~to", target),
            "~type": edge_data.get("~type", "RELATED_TO"),
            "relation": edge_data.get("relation", "RELATED_TO"),
            "description": edge_data.get("description", ""),
            **edge_data.get("properties", {})
        })

    LOGGER.info(f"Expanded {len(seed_ids)} seeds to {len(nodes)} nodes and {len(rels)} edges")

    return [{"nodes": nodes, "rels": rels}]
