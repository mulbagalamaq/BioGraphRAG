# 🚀 BioGraphRAG - Free Deployment Guide

Deploy this biomedical Q&A app **completely free** using Streamlit Cloud, Hugging Face Spaces, or run it locally!

## ✨ What's New - Free Version

This is a **simplified, free-to-deploy** version of BioGraphRAG that:
- ✅ **No AWS required** - Runs entirely locally or on free cloud platforms
- ✅ **No Neptune** - Uses NetworkX for graph operations
- ✅ **No OpenSearch** - Uses FAISS for vector search
- ✅ **Free LLM** - Uses Groq API (free tier available)
- ✅ **Sample Data** - Includes biomedical knowledge graph (genes, diseases, drugs)
- ✅ **One-Click Deploy** - Deploy to Streamlit Cloud in minutes

## 🎯 Quick Start (Local)

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd BioGraphRAG
```

### 2. Install Dependencies

```bash
# Using pip
pip install -r requirements-streamlit.txt

# Or using the original requirements (includes all features)
pip install -r requirements.txt
```

### 3. Get Free API Key

Get a free Groq API key:
1. Go to https://console.groq.com
2. Sign up (free)
3. Create an API key
4. Copy the key

### 4. Set API Key

**Option A: Environment Variable**
```bash
export GROQ_API_KEY="your-api-key-here"
```

**Option B: Secrets File**
```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Edit .streamlit/secrets.toml and add your API key
```

### 5. Run the App

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## ☁️ Deploy to Streamlit Cloud (FREE)

### Step 1: Fork/Push to GitHub

1. Create a new GitHub repository
2. Push this code to your repository:

```bash
git add .
git commit -m "Initial commit - BioGraphRAG app"
git push origin main
```

### Step 2: Deploy to Streamlit Cloud

1. Go to https://share.streamlit.io
2. Sign in with GitHub
3. Click "New app"
4. Select your repository
5. Set main file path: `app.py`
6. Click "Advanced settings"
7. Add secrets:
   ```toml
   GROQ_API_KEY = "your-groq-api-key-here"
   ```
8. Click "Deploy"

**That's it!** Your app will be live at `https://your-app.streamlit.app`

## 🤗 Deploy to Hugging Face Spaces (FREE)

### Step 1: Create a Space

1. Go to https://huggingface.co/spaces
2. Click "Create new Space"
3. Select "Streamlit" as the SDK
4. Name your space

### Step 2: Upload Files

Upload these files to your space:
- `app.py`
- `requirements-streamlit.txt` (rename to `requirements.txt`)
- `data/local/sample_graph.json`
- `.streamlit/config.toml`

### Step 3: Add Secrets

1. Go to Settings → Repository secrets
2. Add secret:
   - Name: `GROQ_API_KEY`
   - Value: your Groq API key

**Your app is now live!** 🎉

## 🎮 Using the App

### Example Questions

Try asking:
- "Which genes are associated with colon cancer?"
- "What drugs target EGFR?"
- "How is BRCA1 related to breast cancer?"
- "What is the relationship between KRAS and colon cancer treatment?"

### Features

1. **Smart Search** - Uses semantic search to find relevant entities
2. **Graph Expansion** - Explores relationships in the knowledge graph
3. **Grounded Answers** - LLM answers based only on retrieved context
4. **Citations** - Includes PMID references from the knowledge graph

## 🔧 Configuration

Edit the search behavior in the sidebar:
- **Search Results** (1-5) - Number of initial nodes to retrieve
- **Graph Expansion Hops** (0-2) - How many relationship hops to explore

## 📊 Sample Data

The app includes a sample biomedical knowledge graph with:
- **10 nodes**: Genes (EGFR, TP53, KRAS, BRCA1), Diseases (Colon Cancer, Lung Cancer, Breast Cancer), Drugs (Erlotinib, Cetuximab, Olaparib)
- **11 edges**: Gene-disease associations, drug-target interactions, treatment relationships
- **PMID references**: Sample PubMed IDs for citations

### Adding Your Own Data

To use your own biomedical data:

1. Edit `data/local/sample_graph.json`
2. Follow the same structure:

```json
{
  "nodes": [
    {
      "id": "GENE_YOUR_GENE",
      "type": "Gene",
      "name": "Gene Name",
      "description": "Description...",
      "properties": {
        "pmids": ["PMID:12345678"]
      }
    }
  ],
  "edges": [
    {
      "source": "NODE_ID_1",
      "target": "NODE_ID_2",
      "relation": "RELATION_TYPE",
      "description": "Description...",
      "properties": {
        "pmids": ["PMID:12345678"]
      }
    }
  ]
}
```

## 🆓 Free Tier Limits

### Groq API (Free Tier)
- **30 requests/minute**
- **6,000 requests/day**
- Multiple models available (Llama 3.1, Mixtral, etc.)
- More than enough for demos and personal use!

### Alternative Free LLM Options

You can modify `app.py` to use:
- **OpenAI** (has free tier credits)
- **Hugging Face Inference API** (free tier)
- **Ollama** (fully local, no API key needed)

## 🐛 Troubleshooting

### "Module not found" error
```bash
pip install -r requirements-streamlit.txt
```

### "Sample graph file not found"
Make sure `data/local/sample_graph.json` exists in your repository.

### "LLM API error"
- Check your API key is set correctly
- Verify you're within free tier limits
- Check internet connection

### App won't start on Streamlit Cloud
- Verify all files are pushed to GitHub
- Check secrets are set correctly
- Look at deployment logs for errors

## 🎨 Customization

### Change Theme

Edit `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#YOUR_COLOR"
backgroundColor = "#FFFFFF"
```

### Use Different LLM

Edit the `query_llm()` function in `app.py` to use your preferred LLM API.

### Add More Data

Expand `data/local/sample_graph.json` with more biomedical entities and relationships.

## 📚 Learn More

- [Streamlit Documentation](https://docs.streamlit.io)
- [Groq API Docs](https://console.groq.com/docs)
- [Sentence Transformers](https://www.sbert.net/)
- [NetworkX Graph Library](https://networkx.org/)

## 🤝 Contributing

Found a bug? Want to add features? PRs welcome!

## 📄 License

MIT License - See LICENSE file

## 🙏 Acknowledgements

- Built on GraphRAG concepts from NVIDIA and G-Retriever
- Uses sample biomedical data inspired by PrimeKG
- Powered by free tools: Streamlit, Groq, Sentence Transformers

---

**Enjoy your free biomedical Q&A app!** 🧬✨
