"""
Production FastAPI backend for BioGraphRAG using complete GraphRAG pipeline.

This backend implements the full GraphRAG architecture:
1. Question embedding with SentenceTransformers
2. Vector-based seed retrieval (FAISS)
3. Graph expansion from seeds
4. PCST-based pruning
5. PyTorch Geometric GNN fusion
6. LLM-based answer generation

Architecture aligns with NVIDIA GraphRAG and G-Retriever papers.
"""

import logging
import sys
from pathlib import Path
from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Add parent directory to path for src imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.qa.answer import answer_question
from src.retrieval.vector_store_local import initialize_local_vector_store

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="BioGraphRAG API",
    description="Biomedical question answering using Graph RAG with GNN fusion",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration path
CONFIG_PATH = str(Path(__file__).parent.parent / "configs" / "local_free.yaml")


@app.on_event("startup")
async def startup_event():
    """Initialize FAISS vector store with embeddings on startup."""
    try:
        logger.info("Initializing FAISS vector store...")
        initialize_local_vector_store(CONFIG_PATH)
        logger.info("Vector store initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize vector store: {e}")
        logger.warning("Continuing without pre-initialized vector store")


class QuestionRequest(BaseModel):
    """Request model for question answering endpoint."""
    question: str


class QuestionResponse(BaseModel):
    """Response model for question answering endpoint."""
    question: str
    answer: str
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
    evidence: List[Dict[str, Any]]
    prompt: str


@app.get("/")
def root():
    """Root endpoint with API information."""
    return {
        "status": "ok",
        "message": "BioGraphRAG API - GraphRAG with GNN Fusion",
        "version": "2.0.0",
        "pipeline": {
            "embedding": "SentenceTransformers",
            "vector_search": "FAISS",
            "graph_backend": "Local (NetworkX)",
            "gnn": "PyTorch Geometric",
            "pruning": "PCST-based",
            "llm": "Configurable"
        }
    }


@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "ok"}


@app.post("/api/qa", response_model=QuestionResponse)
async def qa_endpoint(request: QuestionRequest):
    """
    Question answering endpoint using full GraphRAG pipeline.

    Pipeline stages:
    1. Question embedding (SentenceTransformers)
    2. Vector seed retrieval (FAISS top-k)
    3. Graph expansion (multi-hop from seeds)
    4. Subgraph pruning (PCST algorithm)
    5. GNN fusion (PyTorch Geometric)
    6. Answer generation (LLM with graph context)

    Args:
        request: QuestionRequest with user question

    Returns:
        QuestionResponse with answer, nodes, edges, evidence, and prompt

    Raises:
        HTTPException: If question is empty or processing fails
    """
    if not request.question or not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    logger.info(f"Processing question: {request.question}")

    try:
        # Run full GraphRAG pipeline
        result = answer_question(CONFIG_PATH, request.question)

        logger.info(f"Successfully processed question. Retrieved {len(result['nodes'])} nodes")

        return QuestionResponse(
            question=result["question"],
            answer=result["answer"],
            nodes=result["nodes"],
            edges=result["edges"],
            evidence=result["evidence"],
            prompt=result.get("prompt", "")
        )

    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        raise HTTPException(status_code=500, detail=f"Configuration error: {str(e)}")
    except Exception as e:
        logger.error(f"Error processing question: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")


@app.get("/api/stats")
def get_stats():
    """Get knowledge graph statistics."""
    try:
        import json

        graph_file = Path(__file__).parent.parent / "data" / "local" / "sample_graph.json"

        if not graph_file.exists():
            return {"error": "Graph file not found"}

        with open(graph_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        nodes = data.get("nodes", [])
        edges = data.get("edges", [])

        # Count by type
        node_types = {}
        for node in nodes:
            node_type = node.get("type", "Unknown")
            node_types[node_type] = node_types.get(node_type, 0) + 1

        edge_types = {}
        for edge in edges:
            edge_type = edge.get("relation", "Unknown")
            edge_types[edge_type] = edge_types.get(edge_type, 0) + 1

        return {
            "total_nodes": len(nodes),
            "total_edges": len(edges),
            "node_types": node_types,
            "edge_types": edge_types,
            "pipeline_config": {
                "backend": "local",
                "vector_store": "faiss",
                "gnn_enabled": True,
                "pruning": "PCST"
            }
        }

    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
