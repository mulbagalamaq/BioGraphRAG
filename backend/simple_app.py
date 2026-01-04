"""
Minimal BioGraphRAG Backend - Standalone Version
No complex dependencies, direct API calls, guaranteed to deploy.
"""

import os
import logging
from typing import List, Dict, Any
from xml.etree import ElementTree as ET

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="BioGraphRAG API - Minimal",
    description="Biomedical Q&A using real-time PubMed and NCBI data",
    version="3.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
PUBMED_SEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
PUBMED_FETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
NCBI_GENE_SEARCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
NCBI_GENE_SUMMARY = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"


class QuestionRequest(BaseModel):
    question: str


class QuestionResponse(BaseModel):
    question: str
    answer: str
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
    evidence: List[Dict[str, Any]]
    prompt: str


def search_pubmed(query: str, max_results: int = 10) -> List[str]:
    """Search PubMed and return PMIDs."""
    try:
        params = {
            "db": "pubmed",
            "term": query,
            "retmax": max_results,
            "retmode": "json",
            "sort": "relevance"
        }
        response = requests.get(PUBMED_SEARCH_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("esearchresult", {}).get("idlist", [])
    except Exception as e:
        logger.error(f"PubMed search failed: {e}")
        return []


def fetch_pubmed_articles(pmids: List[str]) -> List[Dict]:
    """Fetch article details from PubMed."""
    if not pmids:
        return []

    try:
        params = {
            "db": "pubmed",
            "id": ",".join(pmids[:10]),
            "retmode": "xml"
        }
        response = requests.get(PUBMED_FETCH_URL, params=params, timeout=15)
        response.raise_for_status()

        root = ET.fromstring(response.content)
        articles = []

        for article in root.findall(".//PubmedArticle"):
            pmid_elem = article.find(".//PMID")
            title_elem = article.find(".//ArticleTitle")
            abstract_elem = article.find(".//AbstractText")

            pmid = pmid_elem.text if pmid_elem is not None else "Unknown"
            title = title_elem.text if title_elem is not None else "No title"
            abstract = abstract_elem.text if abstract_elem is not None else "No abstract"

            articles.append({
                "pmid": pmid,
                "title": title,
                "abstract": abstract[:500],  # Truncate for context
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
            })

        return articles
    except Exception as e:
        logger.error(f"PubMed fetch failed: {e}")
        return []


def search_genes(query: str, max_results: int = 5) -> List[Dict]:
    """Search NCBI Gene database."""
    try:
        # Search for gene IDs
        params = {
            "db": "gene",
            "term": f"{query}[Gene Name] AND Homo sapiens[Organism]",
            "retmax": max_results,
            "retmode": "json"
        }
        response = requests.get(NCBI_GENE_SEARCH, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        gene_ids = data.get("esearchresult", {}).get("idlist", [])

        if not gene_ids:
            return []

        # Fetch gene summaries
        params = {
            "db": "gene",
            "id": ",".join(gene_ids),
            "retmode": "json"
        }
        response = requests.get(NCBI_GENE_SUMMARY, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        genes = []
        for gene_id, gene_data in data.get("result", {}).items():
            if gene_id == "uids":
                continue
            genes.append({
                "id": f"GENE_{gene_data.get('name', gene_id)}",
                "symbol": gene_data.get("name", ""),
                "name": gene_data.get("description", ""),
                "summary": gene_data.get("summary", "")[:300]
            })

        return genes
    except Exception as e:
        logger.error(f"Gene search failed: {e}")
        return []


def query_groq_llm(question: str, context: str) -> str:
    """Query Groq LLM with context."""
    if not GROQ_API_KEY:
        return "Error: GROQ_API_KEY not configured"

    try:
        prompt = f"""You are a biomedical research assistant. Answer the question based on the provided context from PubMed and NCBI Gene databases.

Context:
{context}

Question: {question}

Provide a clear, accurate answer based on the context. Include relevant PMIDs or gene names when applicable."""

        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "llama-3.1-8b-instant",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,
            "max_tokens": 512
        }

        response = requests.post(GROQ_API_URL, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()

        return data["choices"][0]["message"]["content"]
    except Exception as e:
        logger.error(f"Groq API error: {e}")
        return f"Error querying LLM: {str(e)}"


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "status": "ok",
        "message": "BioGraphRAG API - Minimal Standalone",
        "version": "3.0.0",
        "mode": "real-time",
        "sources": ["PubMed E-utilities", "NCBI Gene"],
        "llm": "Groq (Llama 3.1 8B)"
    }


@app.get("/health")
def health():
    """Health check."""
    return {"status": "ok"}


@app.post("/api/qa", response_model=QuestionResponse)
async def answer_question(request: QuestionRequest):
    """
    Answer biomedical questions using real-time data from PubMed and NCBI.

    Simple pipeline:
    1. Search PubMed for relevant articles
    2. Search NCBI Gene for relevant genes
    3. Build context from results
    4. Query Groq LLM for answer
    """
    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    logger.info(f"Processing question: {question}")

    try:
        # Step 1: Search PubMed
        pmids = search_pubmed(question, max_results=10)
        articles = fetch_pubmed_articles(pmids)
        logger.info(f"Found {len(articles)} PubMed articles")

        # Step 2: Search genes
        genes = search_genes(question, max_results=5)
        logger.info(f"Found {len(genes)} genes")

        # Step 3: Build context
        context_parts = []

        if genes:
            context_parts.append("## Genes:")
            for gene in genes:
                context_parts.append(f"- {gene['symbol']}: {gene['name']}")
                if gene['summary']:
                    context_parts.append(f"  Summary: {gene['summary']}")

        if articles:
            context_parts.append("\n## Research Articles:")
            for article in articles:
                context_parts.append(f"- PMID:{article['pmid']} - {article['title']}")
                context_parts.append(f"  {article['abstract']}")

        context = "\n".join(context_parts)

        if not context:
            context = "No relevant biomedical data found for this question."

        # Step 4: Query LLM
        answer = query_groq_llm(question, context)

        # Step 5: Build response with nodes/edges for visualization
        nodes = []
        edges = []
        evidence = []

        # Add gene nodes
        for gene in genes:
            nodes.append({
                "id": gene["id"],
                "type": "Gene",
                "name": gene["symbol"],
                "description": gene["name"]
            })

        # Add publication nodes
        for article in articles:
            pub_id = f"PMID_{article['pmid']}"
            nodes.append({
                "id": pub_id,
                "type": "Publication",
                "name": article["title"],
                "description": article["abstract"]
            })

            # Link publications to genes (simple keyword matching)
            for gene in genes:
                if gene['symbol'].lower() in article['title'].lower() or \
                   gene['symbol'].lower() in article['abstract'].lower():
                    edges.append({
                        "source": pub_id,
                        "target": gene["id"],
                        "relation": "MENTIONS",
                        "description": f"Publication mentions {gene['symbol']}"
                    })

            evidence.append({
                "pmid": article["pmid"],
                "title": article["title"],
                "url": article["url"]
            })

        logger.info(f"Generated answer with {len(nodes)} nodes and {len(edges)} edges")

        return QuestionResponse(
            question=question,
            answer=answer,
            nodes=nodes,
            edges=edges,
            evidence=evidence,
            prompt=context[:500]  # Return sample of context
        )

    except Exception as e:
        logger.error(f"Error processing question: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stats")
def get_stats():
    """Get API stats."""
    return {
        "mode": "minimal-standalone",
        "description": "Simplified biomedical Q&A with real-time API data",
        "dependencies": ["requests", "fastapi", "uvicorn"],
        "data_sources": {
            "pubmed": "PubMed E-utilities API",
            "ncbi_gene": "NCBI Gene Database",
            "llm": "Groq API (Llama 3.1 8B)"
        },
        "image_size": "~800MB",
        "deployment": "Fast and simple"
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
