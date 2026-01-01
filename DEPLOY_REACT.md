# 🚀 React + FastAPI Deployment Guide

## Greek Mythology Sea Theme with Glassmorphism ✨

This guide will help you deploy the beautiful BioGraphRAG React app with FastAPI backend **completely FREE**.

---

## 🎨 Features

### Frontend (React + Vite)
- ⚡ **Beautiful Greek Mythology Theme** - Sea green & white glassmorphism
- 🏛️ **Animated Decorations** - Greek temples, DNA helixes, wave patterns
- 📊 **Interactive Graph Visualization** - Force-directed graph with D3
- 🎭 **Smooth Animations** - Framer Motion transitions
- 📱 **Fully Responsive** - Works on all devices

### Backend (FastAPI + Python)
- 🚀 **Fast API** - Lightning-fast Python backend
- 🧬 **Local Graph Processing** - No AWS required
- 📚 **Simple Search** - Keyword-based biomedical search
- 🔍 **Graph Exploration** - Navigate genes, diseases, drugs

---

## 🆓 Free Deployment Options

### Option 1: Vercel (Frontend) + Railway (Backend) ⭐ RECOMMENDED

#### Deploy Backend to Railway (FREE)

1. **Create Railway Account**
   - Go to [railway.app](https://railway.app)
   - Sign up with GitHub (free)

2. **Deploy Backend**
   ```bash
   cd backend
   railway login
   railway init
   railway up
   ```

3. **Get Backend URL**
   - Railway will give you a URL like: `https://your-app.railway.app`
   - Copy this URL

#### Deploy Frontend to Vercel (FREE)

1. **Update Frontend API URL**
   ```bash
   cd frontend
   # Edit vercel.json and replace "your-backend-url" with your Railway URL
   ```

2. **Deploy to Vercel**
   ```bash
   npm install -g vercel
   vercel login
   vercel --prod
   ```

3. **Done!** Your app is live at: `https://your-app.vercel.app`

---

### Option 2: Render (Both Frontend + Backend) FREE

1. **Create Render Account**
   - Go to [render.com](https://render.com)
   - Sign up (free tier available)

2. **Deploy Backend**
   - New Web Service
   - Connect GitHub repo
   - Build Command: `pip install -r backend/requirements.txt`
   - Start Command: `uvicorn backend.app:app --host 0.0.0.0 --port $PORT`

3. **Deploy Frontend**
   - New Static Site
   - Build Command: `cd frontend && npm install && npm run build`
   - Publish Directory: `frontend/dist`

4. **Connect Them**
   - Add environment variable to frontend: `VITE_API_URL=<backend-url>`

---

### Option 3: Docker (Local or Any Cloud)

```bash
# Build and run with Docker Compose
docker-compose up --build

# Frontend: http://localhost:3000
# Backend: http://localhost:8000
```

---

## 🏃 Local Development

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Backend runs on: `http://localhost:8000`

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on: `http://localhost:3000`

---

## 🎨 Customization

### Change Color Theme

Edit `frontend/src/styles/App.css`:

```css
:root {
  --sea-deep: #0a4f5c;        /* Main dark color */
  --sea-medium: #1a7a8a;      /* Medium sea color */
  --sea-light: #2d9caa;       /* Light sea color */
  --sea-foam: #6ec1cc;        /* Accent color */
  --gold-accent: #d4af37;     /* Gold Greek accents */
}
```

### Add More Graph Data

Edit `data/local/sample_graph.json`:

```json
{
  "nodes": [
    {
      "id": "YOUR_ID",
      "type": "Gene/Disease/Drug",
      "name": "Entity Name",
      "description": "Description...",
      "properties": {
        "pmids": ["PMID:12345"]
      }
    }
  ],
  "edges": [
    {
      "source": "NODE_1",
      "target": "NODE_2",
      "relation": "RELATION_TYPE",
      "description": "Relationship..."
    }
  ]
}
```

---

## 🌐 Environment Variables

### Frontend (.env)
```env
VITE_API_URL=http://localhost:8000
```

### Backend (.env)
```env
# No environment variables needed for basic deployment
# The backend uses the local sample_graph.json file
```

---

## 📊 Tech Stack

| Component | Technology |
|-----------|-----------|
| **Frontend Framework** | React 18 + Vite |
| **Styling** | Custom CSS with Glassmorphism |
| **Animations** | Framer Motion |
| **Graph Viz** | React Force Graph 2D + D3 |
| **Backend** | FastAPI (Python) |
| **Data** | JSON (local file) |
| **Deployment** | Vercel + Railway (FREE) |

---

## 🔧 API Endpoints

### GET /
Health check and API info

### GET /health
Simple health check

### POST /api/qa
Question answering endpoint

**Request:**
```json
{
  "question": "Which genes are associated with colon cancer?"
}
```

**Response:**
```json
{
  "question": "...",
  "answer": "Based on the biomedical knowledge graph...",
  "nodes": [...],
  "edges": [...],
  "evidence": [...]
}
```

### GET /api/graph
Get full graph data

### GET /api/stats
Get graph statistics

---

## 🐛 Troubleshooting

### Frontend won't build
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run build
```

### Backend errors
```bash
cd backend
pip install -r requirements.txt --upgrade
python app.py
```

### CORS errors
- Make sure backend has CORS middleware enabled
- Check that frontend is using correct API URL
- In production, update CORS origins in `backend/app.py`

### Graph not showing
- Check browser console for errors
- Verify `data/local/sample_graph.json` exists
- Try refreshing the page

---

## 🎯 Performance Tips

1. **Enable gzip** - Nginx config includes gzip compression
2. **Use CDN** - Vercel and Railway automatically use CDNs
3. **Lazy loading** - Components load on demand
4. **Optimized builds** - Vite production builds are optimized

---

## 📱 Mobile Optimization

The app is fully responsive and works great on:
- 📱 Mobile phones (320px+)
- 📱 Tablets (768px+)
- 💻 Laptops (1024px+)
- 🖥️ Desktops (1440px+)

---

## 🔒 Security Notes

For production deployment:

1. **Update CORS origins** in `backend/app.py`:
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["https://your-frontend.vercel.app"],
       ...
   )
   ```

2. **Add rate limiting** (optional)
3. **Use HTTPS** (automatic on Vercel/Railway)
4. **Environment variables** for sensitive data

---

## 📈 Scaling

### Free Tiers:
- **Vercel**: Unlimited deployments, 100GB bandwidth/month
- **Railway**: 500 hours/month, $5 credit
- **Render**: 750 hours/month

### Upgrade Options:
- Add real vector search (FAISS, Pinecone)
- Connect to real LLM API (OpenAI, Groq)
- Scale to larger datasets
- Add authentication

---

## 🙏 Credits

- **Design**: Greek Mythology Sea Theme
- **Colors**: Sea greens, golds, whites
- **Icons**: React Icons
- **Fonts**: Inter (Google Fonts)
- **Framework**: React + FastAPI

---

## 📝 License

MIT License - Free to use and modify!

---

## 🎉 You're Ready!

Deploy your beautiful BioGraphRAG app and share it with the world!

**Questions?** Open an issue on GitHub!

---

<div align="center">

**Built with ❤️ and Greek wisdom** 🏛️

[Deploy on Vercel](https://vercel.com) • [Deploy on Railway](https://railway.app) • [Deploy on Render](https://render.com)

</div>
