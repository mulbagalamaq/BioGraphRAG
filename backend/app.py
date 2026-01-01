"""Enhanced FastAPI backend for BioGraphRAG with local graph support."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import os
from pathlib import Path
from typing import List, Dict, Any
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="BioGraphRAG API",
    description="The Oracle of Biomedical Knowledge - GraphRAG API",
    version="2.0.0"
)

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QuestionRequest(BaseModel):
    question: str


class QuestionResponse(BaseModel):
    question: str
    answer: str
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
    evidence: List[Dict[str, Any]]


# Load sample graph data
def load_graph_data():
    """Load the sample biomedical graph."""
    graph_file = Path(__file__).parent.parent / "data" / "local" / "sample_graph.json"

    if not graph_file.exists():
        logger.warning(f"Graph file not found: {graph_file}")
        return {"nodes": [], "edges": []}

    with open(graph_file, "r", encoding="utf-8") as f:
        return json.load(f)


# Cache graph data
GRAPH_DATA = load_graph_data()
logger.info(f"Loaded graph with {len(GRAPH_DATA.get('nodes', []))} nodes")


def simple_search(query: str, graph_data: Dict) -> Dict[str, Any]:
    """Simple keyword-based search in the graph."""
    query_lower = query.lower()
    nodes = graph_data.get("nodes", [])
    edges = graph_data.get("edges", [])

    # Find matching nodes
    matching_nodes = []
    for node in nodes:
        node_text = f"{node.get('name', '')} {node.get('description', '')} {node.get('type', '')}".lower()
        if any(word in node_text for word in query_lower.split()):
            matching_nodes.append(node)

    # If no matches, return top 5 nodes
    if not matching_nodes:
        matching_nodes = nodes[:5]

    # Get edges between matching nodes
    node_ids = {node["id"] for node in matching_nodes}
    matching_edges = [
        edge for edge in edges
        if edge["source"] in node_ids and edge["target"] in node_ids
    ]

    # Also include edges that connect to matching nodes
    for edge in edges:
        if edge["source"] in node_ids or edge["target"] in node_ids:
            if edge not in matching_edges:
                matching_edges.append(edge)
                # Add connected nodes
                for node in nodes:
                    if node["id"] == edge["source"] or node["id"] == edge["target"]:
                        if node not in matching_nodes:
                            matching_nodes.append(node)

    return {
        "nodes": matching_nodes[:10],  # Limit to 10 nodes
        "edges": matching_edges[:15],  # Limit to 15 edges
    }


def generate_answer(question: str, nodes: List[Dict], edges: List[Dict]) -> str:
    """Generate a simple answer from the graph context."""

    if not nodes:
        return "I couldn't find relevant information in the knowledge graph to answer your question."

    # Build context
    context_parts = []

    # Describe entities
    gene_nodes = [n for n in nodes if "GENE" in n.get("type", "") or "Gene" in n.get("type", "")]
    disease_nodes = [n for n in nodes if "DISEASE" in n.get("type", "") or "Disease" in n.get("type", "")]
    drug_nodes = [n for n in nodes if "DRUG" in n.get("type", "") or "Drug" in n.get("type", "")]

    answer = "Based on the biomedical knowledge graph:\n\n"

    if gene_nodes:
        answer += f"**Genes Found ({len(gene_nodes)}):**\n"
        for node in gene_nodes[:5]:
            pmids = node.get("properties", {}).get("pmids", [])
            pmid_str = f" (PMIDs: {', '.join(pmids)})" if pmids else ""
            answer += f"- **{node['name']}**: {node.get('description', 'No description')}{pmid_str}\n"
        answer += "\n"

    if disease_nodes:
        answer += f"**Diseases Found ({len(disease_nodes)}):**\n"
        for node in disease_nodes[:5]:
            pmids = node.get("properties", {}).get("pmids", [])
            pmid_str = f" (PMIDs: {', '.join(pmids)})" if pmids else ""
            answer += f"- **{node['name']}**: {node.get('description', 'No description')}{pmid_str}\n"
        answer += "\n"

    if drug_nodes:
        answer += f"**Drugs Found ({len(drug_nodes)}):**\n"
        for node in drug_nodes[:5]:
            pmids = node.get("properties", {}).get("pmids", [])
            pmid_str = f" (PMIDs: {', '.join(pmids)})" if pmids else ""
            answer += f"- **{node['name']}**: {node.get('description', 'No description')}{pmid_str}\n"
        answer += "\n"

    if edges:
        answer += f"**Key Relationships ({len(edges)}):**\n"
        for edge in edges[:10]:
            source_name = next((n["name"] for n in nodes if n["id"] == edge["source"]), edge["source"])
            target_name = next((n["name"] for n in nodes if n["id"] == edge["target"]), edge["target"])
            pmids = edge.get("properties", {}).get("pmids", [])
            pmid_str = f" (PMIDs: {', '.join(pmids)})" if pmids else ""

            answer += f"- {source_name} **{edge['relation']}** {target_name}"
            if edge.get("description"):
                answer += f": {edge['description']}"
            answer += f"{pmid_str}\n"

    answer += "\n---\n\n"
    answer += "_This answer is grounded in the biomedical knowledge graph with PMID citations where available._"

    return answer


@app.get("/")
def root():
    """Health check endpoint."""
    return {
        "status": "ok",
        "message": "BioGraphRAG API - The Oracle of Biomedical Knowledge",
        "version": "2.0.0",
        "graph_stats": {
            "nodes": len(GRAPH_DATA.get("nodes", [])),
            "edges": len(GRAPH_DATA.get("edges", [])),
        }
    }


@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "ok"}


@app.post("/api/qa", response_model=QuestionResponse)
async def qa_endpoint(request: QuestionRequest):
    """Question answering endpoint."""

    if not request.question or not request.question.strip():
        raise HTTPException(status_code=400, detail="Question is required")

    logger.info(f"Received question: {request.question}")

    try:
        # Search graph
        search_results = simple_search(request.question, GRAPH_DATA)

        # Generate answer
        answer = generate_answer(
            request.question,
            search_results["nodes"],
            search_results["edges"]
        )

        # Create evidence list
        evidence = [
            {
                "id": node["id"],
                "name": node["name"],
                "score": 1.0,  # Placeholder score
            }
            for node in search_results["nodes"]
        ]

        return QuestionResponse(
            question=request.question,
            answer=answer,
            nodes=search_results["nodes"],
            edges=search_results["edges"],
            evidence=evidence
        )

    except Exception as e:
        logger.error(f"Error processing question: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/graph")
def get_graph():
    """Get the full graph data."""
    return GRAPH_DATA


@app.get("/api/stats")
def get_stats():
    """Get graph statistics."""
    nodes = GRAPH_DATA.get("nodes", [])
    edges = GRAPH_DATA.get("edges", [])

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
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
