"""SentenceTransformer embedding wrapper with cosine ranking."""

from __future__ import annotations

from functools import lru_cache
from typing import List

import numpy as np


@lru_cache(maxsize=2)
def _load_model(model_name: str):
    """Load and cache a SentenceTransformer model (thread-safe, read-only)."""
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(model_name)


class EmbeddingModel:
    """Thin wrapper around SentenceTransformer for query / document encoding."""

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model_name = model_name

    def _model(self):
        return _load_model(self.model_name)

    def embed_query(self, text: str) -> np.ndarray:
        """Encode a single query string → 1-D float32 vector."""
        vec = self._model().encode(
            text, show_progress_bar=False, convert_to_numpy=True, normalize_embeddings=True
        )
        return np.asarray(vec, dtype=np.float32).flatten()

    def embed_texts(self, texts: List[str]) -> np.ndarray:
        """Encode a list of strings → (N, dim) float32 matrix."""
        if not texts:
            return np.empty((0, 0), dtype=np.float32)
        mat = self._model().encode(
            texts, show_progress_bar=False, convert_to_numpy=True, normalize_embeddings=True
        )
        return np.asarray(mat, dtype=np.float32)

    def cosine_rank(self, query_vec: np.ndarray, text_matrix: np.ndarray) -> List[int]:
        """Return indices sorted by descending cosine similarity."""
        if query_vec.size == 0 or text_matrix.size == 0:
            return list(range(text_matrix.shape[0]))
        q = _safe_normalize(query_vec)
        M = _normalize_rows(text_matrix)
        scores = M @ q
        return np.argsort(scores)[::-1].tolist()


def _normalize_rows(matrix: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(matrix, axis=1, keepdims=True) + 1e-12
    return matrix / norms


def _safe_normalize(vec: np.ndarray) -> np.ndarray:
    arr = np.asarray(vec, dtype=np.float32).flatten()
    norm = float(np.linalg.norm(arr))
    return arr / norm if norm > 0 else arr
