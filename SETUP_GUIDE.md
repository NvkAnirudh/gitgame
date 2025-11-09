# Git Quest - Setup Guide

This project uses a **unified Python virtual environment** at the root level. No need to install dependencies separately in each folder!

## Quick Start

### 1. One-Time Setup

```bash
# From the project root
./setup.sh
```

This creates `.venv/` at the root and installs all dependencies from `requirements.txt`.

### 2. Activate Environment

```bash
source .venv/bin/activate
```

You'll see `(.venv)` in your terminal prompt.

### 3. Set Environment Variables

```bash
# Create .env file at root
cat > .env << EOF
# Database
DATABASE_URL=postgresql://gitquest:gitquest_dev_password@localhost:5432/gitquest

# Backend
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# LLM (for curriculum generation)
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
EOF
```

## Running Different Components

### Backend API Server

```bash
cd backend
./run.sh
```

API will be available at:
- http://localhost:8000/api/docs (Swagger UI)
- http://localhost:8000/api/redoc (ReDoc)

### Frontend (React)

```bash
cd frontend
npm install  # First time only
npm run dev
```

App will be available at http://localhost:5173

### Database

```bash
docker-compose up -d
```

Access pgAdmin at http://localhost:5050
- Email: admin@gitquest.com
- Password: admin

### Generate Curriculum (Transform Transcripts)

```bash
# Make sure ANTHROPIC_API_KEY is set in .env
source .venv/bin/activate
python data-pipeline/scripts/generate_curriculum.py
```

### Load Data into Database

```bash
source .venv/bin/activate
python data-pipeline/scripts/load_to_db.py
```

## Project Structure

```
gitgame/
├── .venv/                    # Unified virtual environment (gitignored)
├── requirements.txt          # All Python dependencies
├── setup.sh                  # Setup script
├── .env                      # Environment variables (gitignored)
│
├── backend/                  # FastAPI backend
│   ├── run.sh               # Start backend server
│   ├── app/
│   │   ├── main.py
│   │   ├── api/             # API endpoints
│   │   ├── models/          # SQLAlchemy models
│   │   └── ...
│
├── frontend/                 # React frontend
│   ├── src/
│   ├── package.json
│   └── ...
│
├── data-pipeline/            # ETL & curriculum generation
│   ├── scripts/
│   │   ├── generate_curriculum.py
│   │   └── load_to_db.py
│   └── lesson_mappings.json
│
├── database/                 # Database schema
│   └── schema.sql
│
├── docker-compose.yml        # PostgreSQL + Redis + pgAdmin
│
└── Introduction/             # Tutorial transcripts
    Intermediate/
    Advanced/
```

## Common Tasks

### Add a New Python Dependency

```bash
# Add to requirements.txt
echo "new-package>=1.0.0" >> requirements.txt

# Reinstall
source .venv/bin/activate
pip install -r requirements.txt
```

### Reset Environment

```bash
# Delete old environment
rm -rf .venv

# Recreate
./setup.sh
```

### Run Tests

```bash
source .venv/bin/activate
pytest
```

## Troubleshooting

### "ModuleNotFoundError: No module named 'X'"

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### "Virtual environment not found"

```bash
./setup.sh
```

### Backend can't find 'app' module

Make sure you're running from the `backend/` directory:

```bash
cd backend
./run.sh
```

### Database connection refused

```bash
# Start database
docker-compose up -d

# Check if running
docker-compose ps
```

## Development Workflow

```bash
# 1. Start database
docker-compose up -d

# 2. Activate environment
source .venv/bin/activate

# 3. Start backend (in one terminal)
cd backend && ./run.sh

# 4. Start frontend (in another terminal)
cd frontend && npm run dev

# 5. Open browser
# Backend: http://localhost:8000/api/docs
# Frontend: http://localhost:5173
```

## Why Unified Environment?

**Before:**
```
backend/.venv/          # FastAPI dependencies
data-pipeline/.venv/    # Anthropic, pandas, etc.
database/venv/          # psycopg2
# Install dependencies 3 times!
```

**After:**
```
.venv/                  # All dependencies
requirements.txt        # Single source of truth
# Install once, use everywhere!
```

**Benefits:**
- ✅ Install dependencies once
- ✅ Easier to manage versions
- ✅ Smaller disk usage
- ✅ Simpler CI/CD
- ✅ Less confusion

## Next Steps

1. Run `./setup.sh` to create the environment
2. Set up `.env` with your API keys
3. Start database with `docker-compose up -d`
4. Generate curriculum with `python data-pipeline/scripts/generate_curriculum.py`
5. Start backend with `cd backend && ./run.sh`
6. Start frontend with `cd frontend && npm run dev`

Happy coding! 🚀
