# BioGraphRAG React App - Deployment Guide

Deploy the BioGraphRAG React application to Railway (backend) and Vercel (frontend) for free.

## Prerequisites

- GitHub account
- Groq API key (free at https://console.groq.com/keys)
- Railway account (https://railway.app)
- Vercel account (https://vercel.com)

## Backend Deployment (Railway)

### Step 1: Fork/Clone Repository
Ensure you have this repository in your GitHub account.

### Step 2: Deploy to Railway

1. Go to https://railway.app and sign in with GitHub
2. Click **New Project**
3. Select **Deploy from GitHub repo**
4. Choose the `BioGraphRAG` repository
5. Railway will auto-detect the Python app in the `backend/` directory

### Step 3: Configure Environment Variables

In Railway project settings, add the following environment variable:

```
GROQ_API_KEY=your_groq_api_key_here
```

Get your free Groq API key at: https://console.groq.com/keys

### Step 4: Configure Root Directory

1. In Railway project settings, go to **Settings**
2. Set **Root Directory** to: `backend`
3. Railway will use the `railway.toml` configuration automatically

### Step 5: Deploy

Railway will automatically deploy your backend. Once deployed:

1. Note the public URL (e.g., `https://biographrag-production.up.railway.app`)
2. You'll use this URL in the frontend configuration

## Frontend Deployment (Vercel)

### Step 1: Deploy to Vercel

1. Go to https://vercel.com and sign in with GitHub
2. Click **Add New Project**
3. Import the `BioGraphRAG` repository
4. Vercel will auto-detect the React app

### Step 2: Configure Build Settings

In the Vercel project settings:

- **Framework Preset**: Vite
- **Root Directory**: `frontend`
- **Build Command**: `npm run build`
- **Output Directory**: `dist`

### Step 3: Update API Proxy

Before deploying, update `frontend/vercel.json` with your Railway backend URL:

```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "devCommand": "npm run dev",
  "installCommand": "npm install",
  "framework": "vite",
  "rewrites": [
    {
      "source": "/api/(.*)",
      "destination": "https://YOUR-RAILWAY-URL.up.railway.app/api/$1"
    }
  ]
}
```

Replace `YOUR-RAILWAY-URL.up.railway.app` with your actual Railway backend URL.

### Step 4: Deploy

Click **Deploy**. Vercel will build and deploy your frontend.

## Access Your Application

Once both deployments are complete:

1. Open your Vercel URL (e.g., `https://biographrag.vercel.app`)
2. The frontend will automatically proxy API requests to your Railway backend
3. You can access the app from any device, including your phone

## Architecture

```
┌─────────────────┐
│  Vercel         │
│  (Frontend)     │
│  React + Vite   │
└────────┬────────┘
         │ /api/*
         ▼
┌─────────────────┐
│  Railway        │
│  (Backend)      │
│  FastAPI        │
│  GraphRAG       │
└─────────────────┘
```

## GraphRAG Pipeline

The backend runs the full GraphRAG pipeline:

1. **Question Embedding** - SentenceTransformers converts question to vector
2. **Vector Search** - FAISS finds semantically similar nodes
3. **Graph Expansion** - NetworkX expands subgraph from seed nodes
4. **Subgraph Pruning** - PCST algorithm selects most relevant facts
5. **GNN Fusion** - PyTorch Geometric ranks and scores evidence
6. **Answer Generation** - Groq LLM generates response with citations

## Troubleshooting

### Backend Issues

- Check Railway logs for errors
- Verify `GROQ_API_KEY` is set correctly
- Ensure Python dependencies installed (Railway handles this automatically)

### Frontend Issues

- Verify `vercel.json` has correct Railway URL
- Check browser console for API errors
- Ensure CORS is enabled (FastAPI has this configured)

### API Key Issues

- Verify Groq API key is valid at https://console.groq.com/keys
- Check Railway environment variables are set correctly

## Cost

This deployment is **FREE**:

- **Railway**: Free tier includes 500 hours/month
- **Vercel**: Free tier for personal projects
- **Groq**: Free tier with rate limits

No credit card required for basic usage.
