#!/bin/bash
# Start the FastAPI backend server

echo "🚀 Starting Git Quest API..."
echo "================================"

# Make sure we're in the backend directory
if [ ! -f "app/main.py" ]; then
    echo "❌ Error: Please run this script from the backend/ directory"
    echo "   cd backend && ./run.sh"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    uv venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
uv pip install -r requirements.txt

# Run the server from backend directory
echo "🌐 Starting server on http://localhost:8000"
echo "📖 API docs available at http://localhost:8000/api/docs"
echo "================================"

# Important: Run from backend directory so Python can find 'app' module
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
