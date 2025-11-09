#!/bin/bash

# Git Quest - Unified Python Environment Setup
# This script creates a single virtual environment for the entire project

set -e  # Exit on error

echo "================================"
echo "Git Quest - Environment Setup"
echo "================================"
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo "✓ Found Python $PYTHON_VERSION"

# Create virtual environment at root level
echo ""
echo "Creating virtual environment at .venv..."
python3 -m venv .venv

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip --quiet

# Install all dependencies
echo ""
echo "Installing dependencies from requirements.txt..."
pip install -r requirements.txt

echo ""
echo "================================"
echo "✓ Setup Complete!"
echo "================================"
echo ""
echo "To activate the environment:"
echo "  source .venv/bin/activate"
echo ""
echo "To run backend server:"
echo "  source .venv/bin/activate"
echo "  cd backend"
echo "  python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"
echo ""
echo "To generate curriculum:"
echo "  source .venv/bin/activate"
echo "  export ANTHROPIC_API_KEY=your-key-here"
echo "  python data-pipeline/scripts/generate_curriculum.py"
echo ""
