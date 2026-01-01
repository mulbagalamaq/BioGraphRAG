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

# Configuration path - use realtime config for live API data
CONFIG_PATH = str(Path(__file__).parent.parent / "configs" / "realtime.yaml")


@app.on_event("startup")
async def startup_event():
    """Initialize backend (no setup needed for realtime mode)."""
    from src.utils.config import load_config
    cfg = load_config(CONFIG_PATH)
    backend = cfg.get("graph.backend", "").lower()

    if backend == "realtime":
        logger.info("Using real-time API mode - fetching live data from PubMed, NCBI Gene, etc.")
        logger.info("No pre-initialization required - data fetched on-demand")
    else:
        # Initialize FAISS vector store for local mode
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
        "message": "BioGraphRAG API - Real-time Biomedical GraphRAG",
        "version": "2.0.0",
        "data_source": "Real-time APIs (PubMed, NCBI Gene, Europe PMC)",
        "pipeline": {
            "data_fetching": "Real-time API calls",
            "embedding": "SentenceTransformers",
            "sources": ["PubMed E-utilities", "NCBI Gene", "Europe PMC"],
            "gnn": "PyTorch Geometric",
            "pruning": "PCST-based",
            "llm": "Groq (free tier)"
        },
        "features": [
            "Live biomedical data from PubMed",
            "Gene information from NCBI",
            "Literature mining and citations",
            "Disease-gene associations",
            "No pre-loaded data required"
        ]
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
    """Get API configuration and capabilities."""
    from src.utils.config import load_config

    try:
        cfg = load_config(CONFIG_PATH)

        return {
            "mode": "real-time",
            "description": "Fetches live biomedical data from public APIs",
            "data_sources": {
                "pubmed": {
                    "name": "PubMed E-utilities",
                    "url": "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/",
                    "provides": "Biomedical publications, abstracts, citations",
                    "rate_limit": "3 requests/second (10/sec with API key)"
                },
                "ncbi_gene": {
                    "name": "NCBI Gene Database",
                    "url": "https://www.ncbi.nlm.nih.gov/gene",
                    "provides": "Gene information, sequences, descriptions",
                    "rate_limit": "3 requests/second (10/sec with API key)"
                },
                "europe_pmc": {
                    "name": "Europe PMC",
                    "url": "https://www.ebi.ac.uk/europepmc/",
                    "provides": "Biomedical literature search",
                    "rate_limit": "Unlimited"
                }
            },
            "pipeline_config": {
                "backend": cfg.get("graph.backend"),
                "vector_store": cfg.get("vector_store.backend"),
                "gnn_enabled": cfg.get("pyg_rag.enabled", True),
                "pruning": "PCST",
                "llm_provider": cfg.get("llm.provider"),
                "llm_model": cfg.get("llm.model_name")
            },
            "capabilities": [
                "Real-time gene search",
                "PubMed literature retrieval",
                "Disease-gene association mining",
                "Drug-target relationship extraction",
                "Citation-based evidence linking"
            ],
            "no_data_storage": "All data fetched on-demand from APIs"
        }

    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
