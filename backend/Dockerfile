FROM python:3.11-slim

WORKDIR /app

# Install core deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download embedding model so first request is fast
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"

# Optionally install GNN deps (non-fatal if they fail)
COPY requirements-gnn.txt .
RUN pip install --no-cache-dir -r requirements-gnn.txt || echo "GNN deps skipped — running without PyG"

COPY . .

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
