"""Tests for the embedding module."""

import numpy as np
import pytest

from backend.embeddings import EmbeddingModel


@pytest.fixture(scope="module")
def embedder():
    return EmbeddingModel("sentence-transformers/all-MiniLM-L6-v2")


def test_embed_query_shape(embedder):
    vec = embedder.embed_query("EGFR lung cancer")
    assert isinstance(vec, np.ndarray)
    assert vec.ndim == 1
    assert vec.shape[0] == 384  # MiniLM-L6-v2 dimension


def test_embed_texts_shape(embedder):
    texts = ["gene EGFR", "disease lung cancer", "drug erlotinib"]
    mat = embedder.embed_texts(texts)
    assert mat.shape == (3, 384)


def test_embed_empty_texts(embedder):
    mat = embedder.embed_texts([])
    assert mat.shape == (0, 0)


def test_cosine_rank(embedder):
    query = embedder.embed_query("EGFR")
    texts = ["EGFR epidermal growth factor", "diabetes treatment", "KRAS mutation"]
    mat = embedder.embed_texts(texts)
    ranked = embedder.cosine_rank(query, mat)
    # EGFR-related text should rank first
    assert ranked[0] == 0
