"""Local FAISS-based vector store for free deployment.

This module provides vector search functionality using FAISS instead of
AWS OpenSearch, enabling free local deployment.
"""

from __future__ import annotations

import json
import logging
import pickle
from pathlib import Path
from typing import Dict, List

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from src.utils.config import load_config

LOGGER = logging.getLogger(__name__)

# Global caches
_INDEX_CACHE: faiss.IndexFlatL2 | None = None
_METADATA_CACHE: List[Dict] | None = None
_MODEL_CACHE: SentenceTransformer | None = None


def initialize_local_vector_store(config_path: str) -> None:
    """Initialize FAISS index from local sample graph.

    Parameters
    ----------
    config_path:
        Path to configuration file.
    """
    cfg = load_config(config_path)

    # Load graph data
    graph_file = cfg.get("paths.sample_graph", "data/local/sample_graph.json")
    if not Path(graph_file).exists():
        LOGGER.warning(f"Sample graph file not found: {graph_file}")
        return

    with open(graph_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    nodes = data.get("nodes", [])
    if not nodes:
        LOGGER.warning("No nodes found in sample graph")
        return

    # Get embedding model
    model_name = cfg.get("embedding_model.node_model", "sentence-transformers/all-MiniLM-L6-v2")
    model = SentenceTransformer(model_name)

    # Create embeddings for all nodes
    texts = []
    metadata = []

    for node in nodes:
        # Combine name and description for richer embeddings
        text = f"{node['name']}: {node.get('description', '')}"
        texts.append(text)

        metadata.append({
            "id": node["id"],
            "type": node["type"],
            "name": node["name"],
            "description": node.get("description", ""),
            "text": text
        })

    LOGGER.info(f"Creating embeddings for {len(texts)} nodes...")
    embeddings = model.encode(texts, show_progress_bar=False)

    # Create FAISS index
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings.astype(np.float32))

    # Save index and metadata
    index_dir = Path(cfg.get("paths.embeddings_dir", "data/embeddings"))
    index_dir.mkdir(parents=True, exist_ok=True)

    index_path = index_dir / "faiss_index.bin"
    metadata_path = index_dir / "metadata.pkl"

    faiss.write_index(index, str(index_path))

    with open(metadata_path, "wb") as f:
        pickle.dump(metadata, f)

    LOGGER.info(f"Saved FAISS index to {index_path}")
    LOGGER.info(f"Saved metadata to {metadata_path}")

    # Update cache
    global _INDEX_CACHE, _METADATA_CACHE
    _INDEX_CACHE = index
    _METADATA_CACHE = metadata


def load_local_vector_store(config_path: str) -> tuple[faiss.IndexFlatL2, List[Dict]]:
    """Load FAISS index and metadata from disk.

    Parameters
    ----------
    config_path:
        Path to configuration file.

    Returns
    -------
    tuple[faiss.IndexFlatL2, List[Dict]]
        FAISS index and list of node metadata.
    """
    global _INDEX_CACHE, _METADATA_CACHE

    if _INDEX_CACHE is not None and _METADATA_CACHE is not None:
        return _INDEX_CACHE, _METADATA_CACHE

    cfg = load_config(config_path)
    index_dir = Path(cfg.get("paths.embeddings_dir", "data/embeddings"))
    index_path = index_dir / "faiss_index.bin"
    metadata_path = index_dir / "metadata.pkl"

    if not index_path.exists() or not metadata_path.exists():
        LOGGER.info("FAISS index not found, initializing...")
        initialize_local_vector_store(config_path)
        return load_local_vector_store(config_path)

    index = faiss.read_index(str(index_path))

    with open(metadata_path, "rb") as f:
        metadata = pickle.load(f)

    _INDEX_CACHE = index
    _METADATA_CACHE = metadata

    LOGGER.info(f"Loaded FAISS index with {index.ntotal} vectors")
    return index, metadata


def query_local_vectors(config_path: str, query_vector: List[float], top_k: int = 5) -> List[Dict]:
    """Search FAISS index for similar nodes.

    Parameters
    ----------
    config_path:
        Path to configuration file.
    query_vector:
        Query embedding vector.
    top_k:
        Number of results to return.

    Returns
    -------
    List[Dict]
        List of matching nodes with metadata.
    """
    index, metadata = load_local_vector_store(config_path)

    if index.ntotal == 0:
        return []

    # Search
    query_array = np.array([query_vector], dtype=np.float32)
    distances, indices = index.search(query_array, min(top_k, index.ntotal))

    # Prepare results
    results = []
    for i, idx in enumerate(indices[0]):
        if idx < len(metadata):
            result = metadata[idx].copy()
            result["score"] = float(distances[0][i])
            results.append(result)

    return results
