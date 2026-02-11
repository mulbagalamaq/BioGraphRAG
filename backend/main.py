"""FastAPI entry point for BioGraphRAG."""

from __future__ import annotations

import logging
import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.config import load_config
from backend.gnn import GNN_AVAILABLE
from backend.models import QuestionRequest, QuestionResponse, MetadataSchema
from backend.pipeline import answer_question

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(name)-25s  %(levelname)-7s  %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="BioGraphRAG API",
    description="Biomedical Q&A with Knowledge Graphs, LLM, and optional GNN fusion",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_config = None


@app.on_event("startup")
async def startup() -> None:
    global _config
    _config = load_config()
    logger.info("Config loaded.  GNN available: %s", GNN_AVAILABLE)

    # Pre-download embedding model so first request isn't slow
    try:
        from backend.embeddings import EmbeddingModel

        model_name = _config.get("embedding.model", "sentence-transformers/all-MiniLM-L6-v2")
        EmbeddingModel(model_name).embed_query("warmup")
        logger.info("Embedding model ready: %s", model_name)
    except Exception as exc:
        logger.warning("Embedding model pre-load failed: %s", exc)


@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "BioGraphRAG API",
        "version": "1.0.0",
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "gnn_available": GNN_AVAILABLE,
        "model_loaded": True,
    }


@app.post("/api/qa", response_model=QuestionResponse)
async def qa_endpoint(request: QuestionRequest):
    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    logger.info("Processing: %s", question)
    try:
        result = await answer_question(question, _config)
        return QuestionResponse(
            question=result["question"],
            answer=result["answer"],
            nodes=result["nodes"],
            edges=result["edges"],
            evidence=result["evidence"],
            metadata=MetadataSchema(**result.get("metadata", {})),
        )
    except Exception as exc:
        logger.error("Pipeline error: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/api/stats")
def stats():
    return {
        "mode": "realtime",
        "data_sources": ["PubMed E-utilities", "NCBI Gene"],
        "llm": _config.get("llm.model", "llama-3.1-8b-instant") if _config else "unknown",
        "gnn_available": GNN_AVAILABLE,
        "embedding_model": _config.get("embedding.model", "unknown") if _config else "unknown",
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
