"""Tests for graph construction and pruning."""

from backend.graph import build_nx_graph, prune_subgraph


def test_build_nx_graph(sample_nodes, sample_edges):
    G = build_nx_graph(sample_nodes, sample_edges)
    assert G.number_of_nodes() == 4
    assert G.number_of_edges() == 2


def test_prune_keeps_all_when_under_budget(sample_nodes, sample_edges, sample_config):
    sample_config.raw["pruning"]["max_nodes"] = 10
    nodes, edges = prune_subgraph(sample_nodes, sample_edges, sample_config)
    assert len(nodes) == 4
    assert len(edges) == 2


def test_prune_reduces_nodes(sample_nodes, sample_edges, sample_config):
    sample_config.raw["pruning"]["max_nodes"] = 2
    nodes, edges = prune_subgraph(sample_nodes, sample_edges, sample_config)
    assert len(nodes) == 2
    # Genes should be preferred (prize 3.0) over publications (1.5)
    types = {n["type"] for n in nodes}
    assert "Gene" in types


def test_prune_empty_graph(sample_config):
    nodes, edges = prune_subgraph([], [], sample_config)
    assert nodes == []
    assert edges == []
