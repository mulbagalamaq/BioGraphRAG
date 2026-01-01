"""
BioGraphRAG - Streamlit App for Free Deployment
A simplified biomedical question answering system using Graph RAG.

This version runs locally without AWS dependencies (Neptune, OpenSearch).
"""

import json
import logging
import os
from pathlib import Path

import streamlit as st
import requests
from sentence_transformers import SentenceTransformer

# Set page config
st.set_page_config(
    page_title="BioGraphRAG - Biomedical Q&A",
    page_icon="🧬",
    layout="wide"
)

# Initialize logging
logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)


# Cache the model and data
@st.cache_resource
def load_model():
    """Load the sentence transformer model."""
    return SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')


@st.cache_data
def load_graph_data():
    """Load the sample biomedical knowledge graph."""
    graph_file = Path("data/local/sample_graph.json")

    if not graph_file.exists():
        st.error(f"Sample graph file not found: {graph_file}")
        return {"nodes": [], "edges": []}

    with open(graph_file, "r", encoding="utf-8") as f:
        return json.load(f)


def create_node_embeddings(nodes, model):
    """Create embeddings for all nodes."""
    texts = [f"{node['name']}: {node.get('description', '')}" for node in nodes]
    embeddings = model.encode(texts, show_progress_bar=False)
    return embeddings, texts


def search_similar_nodes(query, model, nodes, embeddings, top_k=3):
    """Search for nodes similar to the query."""
    query_embedding = model.encode([query], show_progress_bar=False)[0]

    # Compute cosine similarity
    import numpy as np
    from sklearn.metrics.pairwise import cosine_similarity

    similarities = cosine_similarity([query_embedding], embeddings)[0]

    # Get top-k indices
    top_indices = np.argsort(similarities)[::-1][:top_k]

    results = []
    for idx in top_indices:
        results.append({
            "node": nodes[idx],
            "score": float(similarities[idx])
        })

    return results


def expand_graph_from_seeds(seed_ids, graph_data, hops=1):
    """Expand the graph from seed nodes."""
    nodes = graph_data["nodes"]
    edges = graph_data["edges"]

    # Build adjacency
    node_map = {node["id"]: node for node in nodes}
    expanded_node_ids = set(seed_ids)

    for _ in range(hops):
        new_nodes = set()
        for edge in edges:
            if edge["source"] in expanded_node_ids:
                new_nodes.add(edge["target"])
            if edge["target"] in expanded_node_ids:
                new_nodes.add(edge["source"])
        expanded_node_ids.update(new_nodes)

    # Get expanded nodes and edges
    expanded_nodes = [node_map[nid] for nid in expanded_node_ids if nid in node_map]
    expanded_edges = [
        edge for edge in edges
        if edge["source"] in expanded_node_ids and edge["target"] in expanded_node_ids
    ]

    return expanded_nodes, expanded_edges


def build_context_from_graph(nodes, edges):
    """Build a textual context from graph nodes and edges."""
    context_parts = []

    # Add nodes
    context_parts.append("### Relevant Biomedical Entities:\n")
    for node in nodes:
        pmids = node.get("properties", {}).get("pmids", [])
        pmid_str = ", ".join(pmids) if pmids else "No PMIDs"
        context_parts.append(
            f"- **{node['name']}** ({node['type']}): {node.get('description', '')}\n"
            f"  PMIDs: {pmid_str}\n"
        )

    # Add edges
    context_parts.append("\n### Relationships:\n")
    for edge in edges:
        pmids = edge.get("properties", {}).get("pmids", [])
        pmid_str = ", ".join(pmids) if pmids else "No PMIDs"
        context_parts.append(
            f"- {edge['source']} → **{edge['relation']}** → {edge['target']}\n"
            f"  {edge.get('description', '')}\n"
            f"  PMIDs: {pmid_str}\n"
        )

    return "\n".join(context_parts)


def query_llm(question, context, api_key, model_name="llama-3.1-8b-instant"):
    """Query LLM with the context and question."""

    if not api_key or api_key == "YOUR_GROQ_API_KEY_HERE":
        return (
            "⚠️ **Please set your Groq API key in the sidebar.**\n\n"
            "Get a free API key at https://console.groq.com\n\n"
            "For demo purposes, here's what the system would do:\n"
            "1. Retrieved relevant biomedical entities from the knowledge graph\n"
            "2. Expanded the graph to find related concepts\n"
            "3. Built context from nodes and edges\n"
            "4. Would query the LLM with this context to generate an answer\n\n"
            f"**Context Retrieved:**\n{context}"
        )

    prompt = f"""You are a biomedical assistant. Answer the question based ONLY on the provided context.
Include relevant PMIDs and experiment IDs as citations.

Context:
{context}

Question: {question}

Answer (be concise and cite PMIDs):"""

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": model_name,
                "messages": [
                    {"role": "system", "content": "You are a biomedical assistant. Provide concise answers with PMIDs as citations."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.2,
                "max_tokens": 512
            },
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]

    except Exception as e:
        return f"Error querying LLM: {str(e)}\n\nYou can still see the retrieved context below."


def main():
    """Main Streamlit app."""

    st.title("🧬 BioGraphRAG - Biomedical Question Answering")
    st.markdown("""
    Ask biomedical questions and get answers grounded in a knowledge graph of genes, diseases, and drugs.
    """)

    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")

        api_key = st.text_input(
            "Groq API Key",
            type="password",
            value=os.getenv("GROQ_API_KEY", ""),
            help="Get your free API key at https://console.groq.com"
        )

        st.markdown("---")
        st.markdown("### About")
        st.markdown("""
        This app uses:
        - **Graph RAG**: Retrieval-Augmented Generation with Knowledge Graphs
        - **Sample KG**: Genes, Diseases, Drugs
        - **Local Processing**: No AWS required
        - **Free LLM**: Groq API (free tier)
        """)

        st.markdown("---")
        top_k = st.slider("Search Results", 1, 5, 3)
        hops = st.slider("Graph Expansion Hops", 0, 2, 1)

    # Load model and data
    with st.spinner("Loading model and data..."):
        model = load_model()
        graph_data = load_graph_data()

        if not graph_data["nodes"]:
            st.error("Failed to load graph data. Please check data/local/sample_graph.json")
            return

        node_embeddings, node_texts = create_node_embeddings(graph_data["nodes"], model)

    # Example questions
    st.markdown("### 💡 Example Questions")
    example_questions = [
        "Which genes are associated with colon cancer?",
        "What drugs target EGFR?",
        "How is BRCA1 related to breast cancer?",
        "What is the relationship between KRAS and colon cancer treatment?"
    ]

    cols = st.columns(2)
    for i, eq in enumerate(example_questions):
        if cols[i % 2].button(eq, key=f"example_{i}"):
            st.session_state["question"] = eq

    # Question input
    st.markdown("### ❓ Ask a Question")
    question = st.text_area(
        "Enter your biomedical question:",
        value=st.session_state.get("question", "Which experiments report elevated EGFR expression in colon cancer?"),
        height=100
    )

    if st.button("🔍 Search & Answer", type="primary"):
        if not question.strip():
            st.warning("Please enter a question.")
            return

        with st.spinner("Searching knowledge graph..."):
            # Step 1: Search similar nodes
            similar_results = search_similar_nodes(
                question, model, graph_data["nodes"], node_embeddings, top_k=top_k
            )

            seed_ids = [r["node"]["id"] for r in similar_results]

            # Step 2: Expand graph
            expanded_nodes, expanded_edges = expand_graph_from_seeds(
                seed_ids, graph_data, hops=hops
            )

            # Step 3: Build context
            context = build_context_from_graph(expanded_nodes, expanded_edges)

        # Step 4: Query LLM
        with st.spinner("Generating answer..."):
            answer = query_llm(question, context, api_key)

        # Display results
        st.markdown("---")
        st.markdown("### 📝 Answer")
        st.markdown(answer)

        st.markdown("---")

        # Display in tabs
        tab1, tab2, tab3 = st.tabs(["📊 Retrieved Nodes", "🔗 Relationships", "📄 Full Context"])

        with tab1:
            st.markdown(f"Found **{len(expanded_nodes)}** relevant entities:")
            for node in expanded_nodes:
                with st.expander(f"{node['name']} ({node['type']})"):
                    st.markdown(f"**Description:** {node.get('description', 'N/A')}")
                    if node.get("properties"):
                        st.json(node["properties"])

        with tab2:
            st.markdown(f"Found **{len(expanded_edges)}** relationships:")
            for edge in expanded_edges:
                st.markdown(f"- **{edge['source']}** → `{edge['relation']}` → **{edge['target']}**")
                if edge.get("description"):
                    st.caption(edge["description"])

        with tab3:
            st.text_area("Full Context Sent to LLM:", context, height=400)


if __name__ == "__main__":
    main()
