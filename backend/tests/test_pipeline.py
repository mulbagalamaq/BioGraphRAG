"""Integration test for the pipeline (with mocked external APIs)."""

import pytest

from backend.prompt import build_prompt


def test_build_prompt_includes_question(sample_nodes, sample_edges):
    prompt = build_prompt("Which genes cause lung cancer?", sample_nodes, sample_edges)
    assert "Which genes cause lung cancer?" in prompt
    assert "EGFR" in prompt
    assert "ASSOCIATED_WITH" in prompt


def test_build_prompt_truncates_long_context():
    huge_nodes = [
        {"id": f"NODE_{i}", "type": "Gene", "name": f"Gene{i}", "description": "x" * 500}
        for i in range(100)
    ]
    prompt = build_prompt("test?", huge_nodes, [])
    assert len(prompt) <= 6200  # MAX_CONTEXT_CHARS + some slack
