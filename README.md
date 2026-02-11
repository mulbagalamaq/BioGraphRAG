# BioGraphRAG

Biomedical question answering powered by **Knowledge Graphs + LLM + GNN fusion**.

Ask questions about genes, diseases, and drugs. Get grounded answers from live PubMed data, structured knowledge graphs, and optional GNN-enhanced fact ranking.

## Architecture

```
Question
  → Embed (SentenceTransformer)
  → Fetch biomedical data (PubMed / NCBI Gene — live, free APIs)
  → Build Knowledge Graph (NetworkX)
  → Prune subgraph (prize-collecting greedy)
  → [Optional] GNN rank facts (Node2Vec / GraphSAGE via PyG)
  → Build prompt with graph context
  → LLM answer (Groq API — free tier)
  → Return answer + KG + evidence
```

## Quickstart

### 1. Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Optional: GNN-enhanced ranking
pip install -r requirements-gnn.txt

# Set your Groq API key (free at https://console.groq.com)
export GROQ_API_KEY=gsk_your_key_here

# Run the API
cd .. && python -m uvicorn backend.main:app --reload --port 8000
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000 — the Vite dev server proxies `/api` to the backend on port 8000.

### 3. Docker Compose

```bash
export GROQ_API_KEY=gsk_your_key_here
docker compose up
```

Backend at http://localhost:8000, frontend at http://localhost:3000.

## API

### `POST /api/qa`

```json
{ "question": "Which genes are associated with colon cancer?" }
```

Returns: `{ question, answer, nodes, edges, evidence, metadata }`

### `GET /health`

Returns: `{ status, gnn_available, model_loaded }`

### `GET /api/stats`

Returns: `{ mode, data_sources, llm, gnn_available, embedding_model }`

## Project Structure

```
├── config.yaml                  # Single config file
├── docker-compose.yml           # 2 services: backend + frontend
├── backend/
│   ├── main.py                  # FastAPI entry point
│   ├── pipeline.py              # Orchestrates the full RAG pipeline
│   ├── pubmed.py                # Async PubMed/NCBI API client
│   ├── graph.py                 # NetworkX KG construction + pruning
│   ├── embeddings.py            # SentenceTransformer wrapper
│   ├── gnn.py                   # Optional PyG GNN ranker
│   ├── llm.py                   # Async Groq LLM client
│   ├── prompt.py                # Prompt template builder
│   ├── config.py                # YAML config loader
│   ├── models.py                # Pydantic schemas
│   ├── Dockerfile
│   ├── requirements.txt         # Core deps
│   ├── requirements-gnn.txt     # Optional PyTorch Geometric
│   └── tests/
└── frontend/
    ├── src/
    │   ├── App.jsx              # Main app with state management
    │   └── components/
    │       ├── Header.jsx
    │       ├── SearchBar.jsx
    │       ├── ExampleQuestions.jsx
    │       ├── ResultsPanel.jsx # Tabbed answer/entities/evidence
    │       └── GraphVisualization.jsx  # Force-graph 2D
    ├── Dockerfile
    ├── nginx.conf
    └── package.json             # 6 deps (trimmed from 11)
```

## Free Deployment

**Backend** — [Railway](https://railway.app) (free tier):
- Root directory: project root
- Start command: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
- Env var: `GROQ_API_KEY`

**Frontend** — [Vercel](https://vercel.com) (free tier):
- Root directory: `frontend/`
- Framework: Vite
- Env var: `VITE_API_URL` = your Railway backend URL

## Data Sources (all free, no AWS required)

- **PubMed E-utilities** — biomedical publications and abstracts
- **NCBI Gene** — gene information, descriptions, disease associations
- **Groq API** — free LLM inference (Llama 3.1 8B)
- **SentenceTransformers** — local embedding (all-MiniLM-L6-v2)

## Tests

```bash
pip install pytest
pytest backend/tests/ -v
```

## Methods

BioGraphRAG bridges biomedical data and publication knowledge graphs with GraphRAG, based upon the G-retriever architecture, to ensure that natural language responses are generated from factual biomedical knowledge.

Given a question, the pipeline:
1. Embeds the question with SentenceTransformer
2. Fetches relevant genes, publications, and disease associations from live NCBI/PubMed APIs
3. Constructs a heterogeneous knowledge graph (Gene, Disease, Drug, Publication nodes)
4. Prunes via a prize-collecting greedy algorithm (type-based prizes + degree bonus)
5. Optionally ranks facts using PyG structural embeddings (Node2Vec/GraphSAGE) fused with text embeddings
6. Builds a structured prompt with the pruned subgraph context
7. Generates a grounded answer via LLM

### References

- [NVIDIA: Boosting Q&A Accuracy with GraphRAG](https://developer.nvidia.com/blog/boosting-qa-accuracy-with-graphrag-using-pyg-and-graph-databases/)
- [G-Retriever (arXiv:2402.07630)](https://arxiv.org/pdf/2402.07630)
- [STaRK: Benchmarking LLM Retrieval](https://arxiv.org/abs/2404.13207)

## License

MIT License. See `LICENSE` for the full text.
