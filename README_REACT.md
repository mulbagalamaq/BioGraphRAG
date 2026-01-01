# 🏛️ BioGraphRAG - React Edition

<div align="center">

![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)
![React](https://img.shields.io/badge/React-18.2.0-61DAFB?logo=react)
![FastAPI](https://img.shields.io/badge/FastAPI-0.112.2-009688?logo=fastapi)
![License](https://img.shields.io/badge/license-MIT-green.svg)

**The Oracle of Biomedical Knowledge**

*Navigate vast seas of biomedical research with the wisdom of ancient Greece*

[🚀 Live Demo](#) • [📖 Documentation](DEPLOY_REACT.md) • [🎨 Features](#features) • [💻 Deploy](#deployment)

![Greek Mythology Sea Theme](https://img.shields.io/badge/Theme-Greek%20Mythology-gold)
![Glassmorphism](https://img.shields.io/badge/Design-Glassmorphism-sea green)

</div>

---

## ✨ Features

### 🎨 Stunning UI/UX
- **Greek Mythology Theme** - Inspired by ancient Greek wisdom
- **Sea Green & White Palette** - Rustic, professional, chic colors
- **Glassmorphism Design** - Modern glass-effect cards with blur
- **Smooth Animations** - Powered by Framer Motion
- **Floating Decorations** - Greek temples, DNA helixes, wave patterns
- **Responsive Design** - Perfect on all devices

### 🧬 Powerful Features
- **Biomedical Q&A** - Ask questions about genes, diseases, drugs
- **Graph Visualization** - Interactive force-directed graph
- **PMID Citations** - Grounded in scientific literature
- **Real-time Search** - Instant keyword-based search
- **Entity Explorer** - Browse genes, diseases, treatments
- **Evidence Panel** - See all supporting evidence

### 🚀 Technical Excellence
- ⚡ **Lightning Fast** - Vite build system
- 🔒 **Secure** - CORS-enabled, HTTPS-ready
- 📦 **Lightweight** - Optimized bundle size
- 🐳 **Docker Ready** - One command deployment
- ☁️ **Cloud Native** - Deploy to Vercel/Railway for FREE

---

## 🎬 Quick Start

### Prerequisites
- Node.js 18+
- Python 3.11+
- npm or yarn

### Clone & Install

```bash
# Clone repository
git clone https://github.com/your-username/BioGraphRAG.git
cd BioGraphRAG

# Install frontend dependencies
cd frontend
npm install

# Install backend dependencies
cd ../backend
pip install -r requirements.txt
```

### Run Locally

```bash
# Terminal 1 - Backend
cd backend
python app.py
# Backend: http://localhost:8000

# Terminal 2 - Frontend
cd frontend
npm run dev
# Frontend: http://localhost:3000
```

### Using Docker

```bash
# Build and run
docker-compose up --build

# Frontend: http://localhost:3000
# Backend: http://localhost:8000
```

---

## 🎨 Design System

### Color Palette

```css
/* Greek Sea Colors */
--sea-deep: #0a4f5c      /* Deep ocean */
--sea-medium: #1a7a8a    /* Mediterranean */
--sea-light: #2d9caa     /* Aegean Sea */
--sea-foam: #6ec1cc      /* Sea foam */
--sea-crystal: #b8e6ed   /* Crystal waters */

/* Greek Accents */
--gold-accent: #d4af37   /* Olympic gold */
--bronze-accent: #cd7f32 /* Ancient bronze */
--marble-white: #fafafa  /* Marble temples */
```

### Typography
- **Font**: Inter (Google Fonts)
- **Headings**: 700 weight, gradient fill
- **Body**: 400-500 weight
- **Accents**: Gold dividers, Greek symbols

### Components
- **Glass Cards**: rgba(255, 255, 255, 0.15) with backdrop blur
- **Buttons**: Gradient backgrounds with gold borders
- **Inputs**: Frosted glass effect
- **Animations**: Float, pulse, fade, wave effects

---

## 📊 Architecture

```
┌─────────────────────────────────────────────┐
│           Frontend (React + Vite)           │
│  ┌──────────────────────────────────────┐  │
│  │  Greek Mythology UI Components       │  │
│  │  - Header with animated temples      │  │
│  │  - Glassmorphism search bar          │  │
│  │  - Interactive graph viz (D3)        │  │
│  │  - Results with tabs & animations    │  │
│  └──────────────────────────────────────┘  │
│                    ↓↑                       │
│           API Calls (Axios)                 │
└─────────────────────────────────────────────┘
                     ↓↑
┌─────────────────────────────────────────────┐
│          Backend (FastAPI)                  │
│  ┌──────────────────────────────────────┐  │
│  │  /api/qa - Question answering        │  │
│  │  /api/graph - Full graph data        │  │
│  │  /api/stats - Statistics             │  │
│  └──────────────────────────────────────┘  │
│                    ↓↑                       │
│      Local Graph Processing                 │
│  ┌──────────────────────────────────────┐  │
│  │  data/local/sample_graph.json        │  │
│  │  - 10 biomedical entities            │  │
│  │  - 11 relationships                  │  │
│  │  - PMID citations                    │  │
│  └──────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
```

---

## 🌐 Deployment

### ☁️ FREE Hosting Options

| Platform | Component | Cost | Limits |
|----------|-----------|------|--------|
| **Vercel** | Frontend | $0 | 100GB bandwidth/month |
| **Railway** | Backend | $0 | 500 hours/month |
| **Render** | Both | $0 | 750 hours/month |
| **Netlify** | Frontend | $0 | 100GB bandwidth/month |

### Deploy to Vercel + Railway

```bash
# 1. Deploy backend to Railway
cd backend
railway login
railway up

# 2. Update frontend/vercel.json with Railway URL

# 3. Deploy frontend to Vercel
cd frontend
vercel --prod
```

**Full guide:** See [DEPLOY_REACT.md](DEPLOY_REACT.md)

---

## 🎮 Usage Examples

### Example Questions

1. **Gene-Disease Association**
   ```
   "Which genes are associated with colon cancer?"
   ```

2. **Drug Targets**
   ```
   "What drugs target EGFR?"
   ```

3. **Treatment Relationships**
   ```
   "What is the relationship between KRAS and colon cancer treatment?"
   ```

4. **Disease Mechanisms**
   ```
   "How is BRCA1 related to breast cancer?"
   ```

### API Usage

```bash
# Question answering
curl -X POST http://localhost:8000/api/qa \
  -H "Content-Type: application/json" \
  -d '{"question": "Which genes are associated with colon cancer?"}'

# Get graph stats
curl http://localhost:8000/api/stats

# Get full graph
curl http://localhost:8000/api/graph
```

---

## 📁 Project Structure

```
BioGraphRAG/
├── frontend/                 # React application
│   ├── src/
│   │   ├── components/      # React components
│   │   │   ├── Header.jsx
│   │   │   ├── SearchBar.jsx
│   │   │   ├── GraphVisualization.jsx
│   │   │   ├── ResultsPanel.jsx
│   │   │   ├── ExampleQuestions.jsx
│   │   │   └── GreekDecorations.jsx
│   │   ├── styles/
│   │   │   └── App.css      # Greek mythology theme
│   │   ├── App.jsx          # Main app component
│   │   └── main.jsx         # Entry point
│   ├── package.json
│   ├── vite.config.js
│   └── Dockerfile
│
├── backend/                 # FastAPI application
│   ├── app.py              # Main FastAPI app
│   ├── requirements.txt
│   └── Dockerfile
│
├── data/local/
│   └── sample_graph.json   # Biomedical knowledge graph
│
├── docker-compose.yml      # Docker orchestration
├── DEPLOY_REACT.md         # Deployment guide
└── README_REACT.md         # This file
```

---

## 🧬 Sample Data

The app includes a curated biomedical knowledge graph:

### Nodes (10)
- **4 Genes**: EGFR, TP53, KRAS, BRCA1
- **3 Diseases**: Colon Cancer, Lung Cancer, Breast Cancer
- **3 Drugs**: Erlotinib, Cetuximab, Olaparib

### Relationships (11)
- Gene-disease associations
- Drug-target interactions
- Treatment relationships
- All with PMID citations

---

## 🛠️ Development

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Run dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

### Backend Development

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run dev server
python app.py

# Or with auto-reload
uvicorn app:app --reload
```

### Add More Data

Edit `data/local/sample_graph.json`:

```json
{
  "nodes": [
    {
      "id": "GENE_YOUR_GENE",
      "type": "Gene",
      "name": "Your Gene",
      "description": "Gene description...",
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
      "description": "Association details...",
      "properties": {
        "pmids": ["PMID:12345678"]
      }
    }
  ]
}
```

---

## 🎯 Roadmap

- [ ] Add real vector search (FAISS/Pinecone)
- [ ] Integrate LLM API (OpenAI/Groq)
- [ ] User authentication
- [ ] Save search history
- [ ] Export results to PDF
- [ ] Mobile app (React Native)
- [ ] Multi-language support
- [ ] Voice search
- [ ] Dark mode toggle

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

---

## 📄 License

MIT License - See [LICENSE](LICENSE)

---

## 🙏 Acknowledgements

- **Design Inspiration**: Ancient Greek architecture and mythology
- **GraphRAG Concepts**: NVIDIA Technical Blog, G-Retriever paper
- **Icons**: React Icons
- **Fonts**: Google Fonts (Inter)
- **Framework**: React team, FastAPI team

---

## 📧 Support

- 📖 **Documentation**: [DEPLOY_REACT.md](DEPLOY_REACT.md)
- 🐛 **Issues**: [GitHub Issues](https://github.com/your-username/BioGraphRAG/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/your-username/BioGraphRAG/discussions)

---

<div align="center">

### 🏛️ Built with Ancient Wisdom and Modern Technology 🧬

**Navigate the seas of biomedical knowledge**

[⭐ Star us on GitHub](https://github.com/your-username/BioGraphRAG) • [🚀 Deploy Now](DEPLOY_REACT.md) • [📖 Read Docs](DEPLOY_REACT.md)

---

**Made with ❤️ for the biomedical community**

*May Athena guide your queries and Apollo light your discoveries* 🌟

</div>
