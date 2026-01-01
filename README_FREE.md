# 🧬 BioGraphRAG - Free Deployment Version

<div align="center">

![BioGraphRAG](https://img.shields.io/badge/BioGraphRAG-Free%20Version-brightgreen)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.37.0-red.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

**Biomedical Question Answering powered by Graph RAG - Deploy FREE in minutes!**

[🚀 Quick Start](#quick-start) • [☁️ Deploy Free](#deploy-free) • [📖 Docs](DEPLOYMENT.md) • [🎮 Demo](#example-usage)

</div>

---

## 🎯 What is BioGraphRAG?

BioGraphRAG is a **biomedical question-answering system** that uses **Graph Retrieval-Augmented Generation (RAG)** to provide accurate, grounded answers about genes, diseases, and drugs.

### 🌟 Key Features

- ✅ **100% FREE** - No AWS costs, no paid APIs required
- 🚀 **One-Click Deploy** - Deploy to Streamlit Cloud or Hugging Face Spaces
- 🧬 **Biomedical Knowledge** - Pre-loaded with genes, diseases, and drugs
- 🔍 **Smart Search** - Semantic search finds relevant entities
- 📊 **Graph RAG** - Explores knowledge graph relationships
- 📝 **Grounded Answers** - LLM answers based on retrieved context
- 🔗 **Citations** - Includes PMID references

## 🆚 Two Versions Available

### 🆓 Free Version (This Branch)
- **Perfect for**: Demos, learning, personal projects
- **Infrastructure**: Runs locally or on free cloud platforms
- **Database**: NetworkX (in-memory graph)
- **Vector Store**: FAISS (local)
- **LLM**: Groq API (free tier)
- **Data**: Sample biomedical graph included
- **Cost**: $0 💰

### 💼 Production Version (Main Branch)
- **Perfect for**: Production deployments, large datasets
- **Infrastructure**: AWS (Neptune, OpenSearch, S3)
- **Database**: Amazon Neptune
- **Vector Store**: Amazon OpenSearch
- **LLM**: Any OpenAI-compatible API
- **Data**: Full PrimeKG + PubMedKG
- **Cost**: AWS service fees apply

---

## 🚀 Quick Start

### 1️⃣ Clone the Repository

```bash
git clone <your-repo-url>
cd BioGraphRAG
```

### 2️⃣ Install Dependencies

```bash
pip install -r requirements-streamlit.txt
```

### 3️⃣ Get Free API Key

1. Go to [Groq Console](https://console.groq.com) 🔗
2. Sign up (it's free!)
3. Create an API key
4. Copy your key

### 4️⃣ Run the App

**Option A: Using environment variable**
```bash
export GROQ_API_KEY="your-api-key-here"
streamlit run app.py
```

**Option B: Using the run script**
```bash
./run_app.sh
```

**Option C: Using secrets file**
```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Edit .streamlit/secrets.toml and add your API key
streamlit run app.py
```

🎉 **That's it!** The app will open at `http://localhost:8501`

---

## ☁️ Deploy Free

### Streamlit Cloud (Recommended)

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Deploy BioGraphRAG"
   git push origin main
   ```

2. **Deploy**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with GitHub
   - Click "New app"
   - Select your repository
   - Main file: `app.py`
   - Add secret in advanced settings:
     ```toml
     GROQ_API_KEY = "your-key-here"
     ```
   - Click "Deploy"

3. **Done!** Your app is live at `https://your-app.streamlit.app`

### Hugging Face Spaces

1. Create a new Space at [huggingface.co/spaces](https://huggingface.co/spaces)
2. Select "Streamlit" as SDK
3. Upload: `app.py`, `requirements-streamlit.txt` (rename to `requirements.txt`), `data/local/sample_graph.json`
4. Add secret: `GROQ_API_KEY`
5. Your app is live!

---

## 🎮 Example Usage

### Try These Questions:

1. **Gene-Disease Associations**
   ```
   "Which genes are associated with colon cancer?"
   ```

2. **Drug Targets**
   ```
   "What drugs target EGFR?"
   ```

3. **Disease Relationships**
   ```
   "How is BRCA1 related to breast cancer?"
   ```

4. **Treatment Options**
   ```
   "What is the relationship between KRAS and colon cancer treatment?"
   ```

### 📸 Screenshot

```
┌─────────────────────────────────────────────┐
│  🧬 BioGraphRAG                             │
├─────────────────────────────────────────────┤
│  Question:                                  │
│  Which genes are associated with colon      │
│  cancer?                                    │
│                                             │
│  🔍 Search & Answer                         │
├─────────────────────────────────────────────┤
│  📝 Answer:                                 │
│  Based on the knowledge graph, several      │
│  genes are associated with colon cancer:    │
│                                             │
│  • EGFR (PMID:12345678) - overexpressed    │
│  • KRAS (PMID:56789012) - mutations in 40% │
│  • TP53 (PMID:34567890) - mutations common │
└─────────────────────────────────────────────┘
```

---

## 📊 Sample Data Included

The app comes with a **biomedical knowledge graph** containing:

### Nodes (10)
- **Genes**: EGFR, TP53, KRAS, BRCA1
- **Diseases**: Colon Cancer, Lung Cancer, Breast Cancer
- **Drugs**: Erlotinib, Cetuximab, Olaparib

### Edges (11)
- Gene → Disease associations
- Drug → Gene targets
- Drug → Disease treatments
- Relationships with PMID citations

---

## 🔧 Customization

### Add Your Own Data

Edit `data/local/sample_graph.json`:

```json
{
  "nodes": [
    {
      "id": "GENE_YOUR_GENE",
      "type": "Gene",
      "name": "Gene Name",
      "description": "What this gene does...",
      "properties": {
        "pmids": ["PMID:12345678"]
      }
    }
  ],
  "edges": [
    {
      "source": "GENE_YOUR_GENE",
      "target": "DISEASE_SOME_DISEASE",
      "relation": "ASSOCIATED_WITH",
      "description": "How they're related...",
      "properties": {
        "pmids": ["PMID:12345678"]
      }
    }
  ]
}
```

### Change LLM Provider

Modify the `query_llm()` function in `app.py` to use:
- OpenAI
- Hugging Face Inference API
- Anthropic Claude
- Ollama (fully local!)

### Customize Theme

Edit `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#YOUR_COLOR"
backgroundColor = "#FFFFFF"
```

---

## 🆓 Free Tier Limits

### Groq API
- ✅ 30 requests/minute
- ✅ 6,000 requests/day
- ✅ Multiple models (Llama 3.1, Mixtral, etc.)
- ✅ More than enough for demos!

### Streamlit Cloud
- ✅ Unlimited public apps
- ✅ 1GB memory
- ✅ Enough for this app!

### Hugging Face Spaces
- ✅ Unlimited public spaces
- ✅ CPU/GPU options
- ✅ Free tier available

---

## 🛠️ Tech Stack

| Component | Technology | Why? |
|-----------|-----------|------|
| **UI** | Streamlit | Fast, beautiful, Python-based |
| **Embeddings** | Sentence Transformers | Free, runs locally |
| **Vector Store** | FAISS | Fast, local, no setup |
| **Graph** | NetworkX | Simple, powerful, pure Python |
| **LLM** | Groq API | Free tier, fast inference |
| **Deploy** | Streamlit Cloud | Free hosting, one-click |

---

## 📚 Documentation

- 📖 [Full Deployment Guide](DEPLOYMENT.md)
- 🔬 [Original README](README.md) - For AWS production version
- 🎓 [GraphRAG Concepts](https://developer.nvidia.com/blog/boosting-qa-accuracy-with-graphrag-using-pyg-and-graph-databases/)

---

## 🐛 Troubleshooting

### App won't start?
```bash
# Reinstall dependencies
pip install -r requirements-streamlit.txt --upgrade
```

### No API key?
You can still use the app! It will show you the retrieved context without generating an LLM answer.

### Graph not loading?
Make sure `data/local/sample_graph.json` exists in your repository.

### Still stuck?
Open an issue on GitHub with:
- Error message
- Steps to reproduce
- Your environment (OS, Python version)

---

## 🤝 Contributing

We welcome contributions! Here's how:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Ideas for Contributions
- 🗄️ Add more sample biomedical data
- 🎨 Improve UI/UX
- 🔌 Add more LLM providers
- 📊 Add visualization of the graph
- 🧪 Add unit tests
- 📝 Improve documentation

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgements

- **GraphRAG concepts** from [NVIDIA Technical Blog](https://developer.nvidia.com/blog/boosting-qa-accuracy-with-graphrag-using-pyg-and-graph-databases/)
- **G-Retriever** paper ([arXiv:2402.07630](https://arxiv.org/pdf/2402.07630))
- **PrimeKG** biomedical knowledge graph ([Nature Scientific Data](https://www.nature.com/articles/s41597-023-02094-0))
- **Groq** for free, fast LLM inference
- **Streamlit** for amazing free hosting

---

## ⭐ Star Us!

If you find this project helpful, please give it a star! It helps others discover the project.

---

## 📧 Contact

Questions? Feedback? Open an issue or reach out!

---

<div align="center">

**Built with ❤️ for the biomedical community**

[🚀 Deploy Now](https://share.streamlit.io) • [📖 Read Docs](DEPLOYMENT.md) • [⭐ Star on GitHub](#)

</div>
