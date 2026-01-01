#!/bin/bash
# Quick start script for BioGraphRAG

echo "🧬 Starting BioGraphRAG..."

# Check if data directory exists
if [ ! -d "data/local" ]; then
    echo "Creating data directory..."
    mkdir -p data/local
fi

# Check if sample graph exists
if [ ! -f "data/local/sample_graph.json" ]; then
    echo "❌ Error: Sample graph not found at data/local/sample_graph.json"
    echo "Please make sure the sample_graph.json file exists."
    exit 1
fi

# Check if API key is set
if [ -z "$GROQ_API_KEY" ]; then
    echo "⚠️  Warning: GROQ_API_KEY not set"
    echo "You can:"
    echo "1. Set it as environment variable: export GROQ_API_KEY='your-key'"
    echo "2. Add it in .streamlit/secrets.toml"
    echo "3. Enter it in the app sidebar"
    echo ""
fi

echo "✅ Starting Streamlit app..."
streamlit run app.py
