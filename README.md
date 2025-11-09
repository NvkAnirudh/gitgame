# 🎮 Git Quest: An Interactive Git Learning Adventure

Transform Git learning into an epic, story-driven adventure! Git Quest combines comprehensive Git tutorials with gamification, interactive challenges, and a full-scale Data Engineering project.

## 🎯 Project Overview

**Git Quest** is a web-based interactive learning platform where players become "Version Control Guardians" protecting a fictional tech company (Nexus Labs) from code chaos. Each Git concept becomes a power to unlock through narrative-driven scenarios.

### Key Features

- **📚 25 Interactive Tutorials** - From Git basics to advanced workflows
- **🎭 Story-Driven Learning** - Engaging narrative across 3 difficulty arcs
- **⚔️ 50+ Challenges** - Crisis scenarios, command mastery, quizzes, boss battles
- **🏆 Achievement System** - Badges, XP, leaderboards, customization
- **📊 Real-Time Analytics** - Track learning patterns and progress
- **🔬 Git Visualization Lab** - Interactive repository explorer
- **💻 Terminal Emulator** - Sandboxed Git environment

### Tech Stack

**Backend (Python)**
- FastAPI, SQLAlchemy, Pydantic, GitPython
- JWT authentication (python-jose, passlib)

**Data Engineering**
- Apache Airflow (orchestration)
- dbt (data transformation)
- Great Expectations (data quality)
- PostgreSQL (OLTP), DuckDB (OLAP), Redis (cache)

**Frontend (JavaScript)**
- React, TypeScript, TailwindCSS
- xterm.js (terminal), D3.js (visualizations)

**Analytics**
- Metabase/Superset dashboards
- Jupyter notebooks

---

## 📁 Project Structure

```
git-quest/
├── data-pipeline/          # ETL & Data Orchestration
│   ├── scripts/            # Python ETL scripts
│   ├── airflow/            # Airflow DAGs
│   ├── dbt/                # dbt models
│   └── great_expectations/ # Data quality tests
├── backend/                # FastAPI application (Coming in Phase 2)
├── frontend/               # React application (Coming in Phase 4)
├── content/                # Parsed tutorial content
│   ├── raw/                # Original .txt transcripts
│   └── parsed/             # Structured JSON files
├── Introduction/           # Beginner tutorials (7)
├── Intermediate/           # Intermediate tutorials (7)
├── Advanced/               # Advanced tutorials (11)
└── IMPLEMENTATION_PLAN.md  # Full 8-phase roadmap
```

---

## 🚀 Implementation Progress

### ✅ Phase 1: Data Foundation & ETL Pipeline - COMPLETE!

**Completed:**
- ✅ Tutorial content parser (LLM-enhanced Git extraction)
- ✅ PostgreSQL database schema (12 tables, 2 views)
- ✅ Docker Compose (PostgreSQL + Redis + pgAdmin)
- ✅ Database loader script
- ✅ Data quality validation (725 tests, 100% pass rate)

---

### ✅ Phase 2: Backend API & Game Engine (In Progress)

**Completed:**
- ✅ FastAPI application setup
- ✅ SQLAlchemy models (12 models, ~400 lines)
- ✅ JWT authentication system (bcrypt + token rotation)
- ✅ Authentication API (7 endpoints)
  - Register, login, logout, refresh token
  - Password reset, get current user
- ✅ Lessons API (6 endpoints)
  - List/get lessons, start/complete
  - Track player progress
- ✅ Players API (2 endpoints)
  - Profile & statistics

**In Progress:**
- 🔨 Game engine core logic
- 🔨 Git command simulator

**Next Up:**
- Challenge API endpoints
- Game session management

### 📊 Content Statistics

| Level | Tutorials | Sections | Status |
|-------|-----------|----------|--------|
| Introduction | 7 | ~78 | ✅ Parsed |
| Intermediate | 7 | ~95 | ✅ Parsed |
| Advanced | 11 | ~91 | ✅ Parsed |
| **Total** | **25** | **264** | **✅ Parsed** |

---

## 🛠️ Quick Start (Phase 1)

### 1. Run the Tutorial Parser

```bash
# Parse all tutorials and generate JSON
python3 data-pipeline/scripts/parse_tutorials.py

# Output location
ls content/parsed/
```

**Output:**
- `content/parsed/*.json` - Individual tutorial files (25 tutorials, 264 sections)
- `content/parsed/summary.json` - Statistics and metadata

### 2. Start the Database Infrastructure

```bash
# Start PostgreSQL + Redis with Docker Compose
docker-compose up -d

# Verify services are running
docker-compose ps

# Access pgAdmin at http://localhost:5050
# Email: admin@gitquest.com | Password: admin
```

### 3. Validate Data Quality

```bash
# Run data quality validation (Great Expectations principles)
python3 data-pipeline/data_quality/validate_tutorials.py
```

**Validation Results:**
- ✅ 25 tutorials validated
- ✅ 725 tests passed (100% success rate)
- ✅ 10 validation types: schema, types, Git commands, timestamps, content completeness

### 4. Load Tutorials into Database

```bash
# Set up environment variables
cp .env.example .env

# Install database dependencies
pip install -r database/requirements.txt

# Load parsed tutorials to PostgreSQL
python3 data-pipeline/scripts/load_to_db.py
```

**Database Stats:**
- ✅ 25 lessons loaded
- ✅ 28 Git commands cataloged
- ✅ 5 default achievements seeded

### 5. Database Access

**PostgreSQL:**
- Host: `localhost:5432`
- Database: `gitquest`
- User: `gitquest`
- Password: `gitquest_dev_password`

**Redis:**
- Host: `localhost:6379`

**pgAdmin UI:**
- URL: `http://localhost:5050`
- Email: `admin@gitquest.com`
- Password: `admin`

---

## 🛠️ Quick Start (Phase 2) - Run the Backend API

### 1. Install Backend Dependencies

```bash
cd backend

# Install Python dependencies
pip install -r requirements.txt
```

### 2. Start the FastAPI Server

```bash
# Option 1: Using the run script
./run.sh

# Option 2: Direct command
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Access the API

**API Server:**
- URL: `http://localhost:8000`
- Health check: `http://localhost:8000/health`

**Interactive API Docs:**
- Swagger UI: `http://localhost:8000/api/docs`
- ReDoc: `http://localhost:8000/api/redoc`

### 4. Test the API

**Register a new user:**
```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "player@gitquest.com",
    "username": "gitmaster",
    "password": "SecurePass123",
    "display_name": "Git Master"
  }'
```

**Login:**
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=gitmaster&password=SecurePass123"
```

**Get lessons:**
```bash
curl "http://localhost:8000/api/lessons?level=introduction"
```

---

## 📖 Learning Path

### Introduction (7 Lessons)
1. Version Control Basics
2. Creating Repositories
3. Staging and Committing Files
4. Version History
5. Comparing Versions
6. Restoring and Reverting Files
7. Tips and Tricks

### Intermediate (7 Lessons)
8. Branches
9. Modifying and Comparing Branches
10. Merging Branches
11. Merge Conflicts
12. Remote Repositories
13. Pulling from Remotes
14. Pushing to Remotes

### Advanced (11 Lessons)
15. Understanding Merge Types
16. Complex Merge Scenarios
17. Git Rebasing
18. Cherry Picking
19. Trunk-Based Development
20. Git Reflog
21. Git Bisect
22. Git Submodules
23. Git Worktrees
24. Git LFS
25. Git Filter-Repo

---

## 🔒 Security Features

- **Authentication**: JWT tokens with refresh, OAuth2 password flow
- **Password Security**: Bcrypt hashing, strength requirements, account lockout
- **API Security**: Rate limiting, CORS, input validation, XSS/SQL injection prevention
- **Git Sandbox**: Isolated execution, command whitelist, resource limits

---

## 🎓 Data Engineering Learning Outcomes

By building Git Quest, you'll master:
- ETL pipeline development
- Data quality frameworks (Great Expectations)
- Analytics engineering (dbt)
- Workflow orchestration (Airflow)
- Multi-database architecture (OLTP + OLAP)
- API design for data products
- Event-driven analytics

---

## 📅 Roadmap

- [x] **Phase 1**: Data Foundation & ETL Pipeline (Week 1-2) - *In Progress*
- [ ] **Phase 2**: Backend API & Game Engine (Week 2-4)
- [ ] **Phase 3**: Story System & Content Integration (Week 4-5)
- [ ] **Phase 4**: Frontend Development (Week 5-7)
- [ ] **Phase 5**: Challenge System & Gamification (Week 7-8)
- [ ] **Phase 6**: Analytics Pipeline & Dashboards (Week 8-9)
- [ ] **Phase 7**: Advanced Features & Polish (Week 9-10)
- [ ] **Phase 8**: Testing, Documentation & Deployment (Week 10-12)

See [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) for detailed roadmap.

---

## 🤝 Contributing

This project is under active development. Phase 1 (Data Foundation) is currently in progress.

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🌟 Acknowledgments

- Tutorial content adapted from DataCamp Git courses
- Inspired by interactive learning platforms and gamification principles
- Built with ❤️ for Git learners and Data Engineering enthusiasts
