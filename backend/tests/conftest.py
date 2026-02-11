"""Shared test fixtures."""

from __future__ import annotations

import pytest

from backend.config import AppConfig


@pytest.fixture
def sample_config() -> AppConfig:
    return AppConfig(
        raw={
            "embedding": {"model": "sentence-transformers/all-MiniLM-L6-v2"},
            "ncbi": {"email": "test@example.com"},
            "llm": {
                "api_key": "test-key",
                "api_url": "https://api.groq.com/openai/v1/chat/completions",
                "model": "llama-3.1-8b-instant",
                "temperature": 0.2,
                "max_tokens": 256,
            },
            "retrieval": {"max_publications": 5, "max_genes": 3, "max_nodes": 20},
            "pruning": {
                "max_nodes": 15,
                "prizes": {
                    "Gene": 3.0,
                    "Disease": 2.5,
                    "Drug": 2.0,
                    "Publication": 1.5,
                    "default": 1.0,
                },
            },
            "gnn": {"enabled": False, "model": "node2vec", "dim": 16, "epochs": 1},
        }
    )


@pytest.fixture
def sample_nodes():
    return [
        {
            "id": "GENE_EGFR",
            "type": "Gene",
            "name": "EGFR",
            "symbol": "EGFR",
            "description": "Epidermal growth factor receptor",
            "properties": {"source": "ncbi_gene", "ncbi_id": "1956"},
        },
        {
            "id": "GENE_KRAS",
            "type": "Gene",
            "name": "KRAS",
            "symbol": "KRAS",
            "description": "KRAS proto-oncogene, GTPase",
            "properties": {"source": "ncbi_gene", "ncbi_id": "3845"},
        },
        {
            "id": "DISEASE_LUNG_CANCER",
            "type": "Disease",
            "name": "Lung Cancer",
            "description": "Disease entity",
            "properties": {"source": "pubmed_inferred"},
        },
        {
            "id": "PMID_12345",
            "type": "Publication",
            "pmid": "12345",
            "title": "EGFR mutations in lung cancer",
            "name": "EGFR mutations in lung cancer",
            "abstract": "This study examines EGFR mutations.",
            "description": "This study examines EGFR mutations.",
            "properties": {"source": "pubmed", "url": "https://pubmed.ncbi.nlm.nih.gov/12345/"},
        },
    ]


@pytest.fixture
def sample_edges():
    return [
        {
            "source": "GENE_EGFR",
            "target": "DISEASE_LUNG_CANCER",
            "relation": "ASSOCIATED_WITH",
            "description": "EGFR associated with lung cancer",
        },
        {
            "source": "PMID_12345",
            "target": "GENE_EGFR",
            "relation": "MENTIONS",
            "description": "Publication mentions EGFR",
        },
    ]
