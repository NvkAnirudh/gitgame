#!/bin/bash
# Start the FastAPI backend server

echo "🚀 Starting Git Quest API..."
echo "================================"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Run the server
echo "🌐 Starting server on http://localhost:8000"
echo "📖 API docs available at http://localhost:8000/api/docs"
echo "================================"

python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
