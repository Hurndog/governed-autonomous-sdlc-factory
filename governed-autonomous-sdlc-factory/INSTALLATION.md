# Installation & Dependencies

## Table of Contents

1. [System Requirements](#1-system-requirements)
2. [Dependency Overview](#2-dependency-overview)
3. [Backend Installation](#3-backend-installation)
4. [Frontend Installation](#4-frontend-installation)
5. [Infrastructure Installation](#5-infrastructure-installation)
6. [Model Provider Setup](#6-model-provider-setup)
7. [Verification](#7-verification)
8. [Troubleshooting](#8-troubleshooting)
9. [Dependency Reference](#9-dependency-reference)

---

## 1. System Requirements

### Minimum Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| CPU | 4 cores | 8 cores |
| RAM | 4 GB | 16 GB |
| Disk | 15 GB | 30 GB |
| OS | macOS 14 / Ubuntu 22.04 / Windows 11 (WSL2) | macOS 15 / Ubuntu 24.04 |
| Python | 3.11 | 3.12 |
| Node.js | 18 | 20 |
| PostgreSQL | 15 | 16 |
| Redis | 7 | 7 |

### Apple Silicon Specifics

- Native ARM64 Python required (not x86_64 via Rosetta)
- Ollama uses Metal GPU acceleration automatically
- Docker Desktop for Mac (Apple Silicon) for containerized services
- Minimum: M1 with 8GB RAM
- Recommended: M2 Pro with 16GB RAM

### Windows Specifics

- WSL2 (Windows Subsystem for Linux) required
- Ubuntu 22.04+ recommended in WSL2
- Docker Desktop with WSL2 backend
- Node.js and Python in WSL2, not Windows native

---

## 2. Dependency Overview

### Backend Dependencies (Python)

| Package | Version | Purpose | Required |
|---------|---------|---------|----------|
| fastapi | 0.115.0 | Web framework | ✅ Yes |
| uvicorn[standard] | 0.30.0 | ASGI server | ✅ Yes |
| sqlalchemy[asyncio] | 2.0.35 | ORM | ✅ Yes |
| asyncpg | 0.29.0 | PostgreSQL driver | ✅ Yes |
| pydantic | 2.9.0 | Data validation | ✅ Yes |
| pydantic-settings | 2.5.0 | Settings management | ✅ Yes |
| redis | 5.1.0 | Redis client | ✅ Yes |
| httpx | 0.27.0 | HTTP client | ✅ Yes |
| alembic | 1.13.0 | Database migrations | ✅ Yes |
| python-multipart | 0.0.12 | File uploads | ✅ Yes |
| structlog | 24.4.0 | Structured logging | ✅ Yes |
| python-json-logger | 2.0.7 | JSON logging | ✅ Yes |
| opentelemetry-api | 1.27.0 | Observability API | ✅ Yes |
| opentelemetry-sdk | 1.27.0 | Observability SDK | ✅ Yes |
| opentelemetry-instrumentation-fastapi | 0.48b0 | FastAPI instrumentation | ✅ Yes |
| prometheus-client | 0.21.0 | Metrics | ✅ Yes |
| openai | 1.x | OpenAI client | ❌ Optional |
| anthropic | 0.x | Anthropic client | ❌ Optional |
| google-generativeai | 0.x | Gemini client | ❌ Optional |

### Frontend Dependencies (Node.js)

| Package | Version | Purpose | Required |
|---------|---------|---------|----------|
| next | 14.2.0 | React framework | ✅ Yes |
| react | ^18.2.0 | UI library | ✅ Yes |
| react-dom | ^18.2.0 | DOM rendering | ✅ Yes |
| typescript | ^5.3.0 | Type safety | ✅ Yes |
| tailwindcss | ^3.4.0 | CSS framework | ✅ Yes |
| zustand | ^4.5.0 | State management | ✅ Yes |
| recharts | ^2.12.0 | Charts | ✅ Yes |
| framer-motion | ^12.38.0 | Animations | ✅ Yes |
| lucide-react | ^0.344.0 | Icons | ✅ Yes |
| mermaid | ^10.9.0 | Diagrams | ✅ Yes |
| react-markdown | ^9.0.1 | Markdown rendering | ✅ Yes |
| remark-gfm | ^4.0.0 | GitHub Flavored Markdown | ✅ Yes |
| clsx | ^2.1.0 | Conditional classes | ✅ Yes |
| tailwind-merge | ^2.2.0 | Tailwind class merging | ✅ Yes |
| @reactflow/core | ^11.11.4 | Flow diagrams | ✅ Yes |
| @reactflow/background | ^11.3.14 | Flow background | ✅ Yes |
| @reactflow/controls | ^11.2.14 | Flow controls | ✅ Yes |
| @reactflow/minimap | ^11.7.14 | Flow minimap | ✅ Yes |
| date-fns | ^4.1.0 | Date utilities | ✅ Yes |

### Infrastructure Dependencies

| Component | Version | Purpose | Required |
|-----------|---------|---------|----------|
| PostgreSQL | 15+ | Primary database | ✅ Yes |
| Redis | 7+ | Cache + queue | ✅ Yes |
| Qdrant | Latest | Vector memory | ❌ Optional |
| Ollama | 0.1.0+ | Local model serving | ❌ Optional |
| Prometheus | Latest | Metrics collection | ❌ Optional |
| Grafana | Latest | Metrics visualization | ❌ Optional |
| Docker | 24+ | Containerization | ❌ Optional |
| Docker Compose | 2.x | Multi-container | ❌ Optional |
| Nginx | 1.24+ | Reverse proxy | ❌ Optional |

---

## 3. Backend Installation

### Step 1: Clone Repository

```bash
git clone https://github.com/Hurndog/governed-autonomous-sdlc-factory.git
cd governed-autonomous-sdlc-factory
```

### Step 2: Create Virtual Environment

```bash
# Create
python3 -m venv venv

# Activate (macOS/Linux)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Verify
python --version  # Should show 3.11+
pip --version
```

### Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r apps/api/requirements.txt
```

### Step 4: Verify Installation

```bash
# Check all packages installed
pip list | grep -E "fastapi|uvicorn|sqlalchemy|pydantic|redis|httpx|alembic"

# Expected output:
# fastapi          0.115.0
# uvicorn          0.30.0
# sqlalchemy       2.0.35
# pydantic         2.9.0
# redis            5.1.0
# httpx            0.27.0
# alembic          1.13.0
```

### Step 5: Database Setup

```bash
# Start PostgreSQL (if not using Docker)
# macOS:
brew services start postgresql@15

# Ubuntu:
sudo systemctl start postgresql

# Create database and user
psql postgres -c "CREATE USER governance WITH PASSWORD 'forge';"
psql postgres -c "CREATE DATABASE sdlc_factory OWNER governance;"
psql postgres -c "GRANT ALL PRIVILEGES ON DATABASE sdlc_factory TO governance;"

# Run migrations
cd apps/api
python -m alembic upgrade head
cd ../..
```

### Step 6: Environment Configuration

```bash
cp .env.example .env
# Edit .env with your settings
```

Required variables:
```bash
DATABASE_URL=postgresql+asyncpg://governance:forge@localhost:5432/sdlc_factory
REDIS_URL=redis://localhost:6379/0
API_SECRET=your-secret-key-minimum-32-characters-long
API_HOST=0.0.0.0
API_PORT=8000
API_CORS_ORIGINS=http://localhost:3000
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

### Step 5: Start Backend

```bash
cd apps/api
python -m uvicorn src.main:app --reload --port 8000
```

Expected output:
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Starting Governed Autonomous SDLC Factory API
INFO:     Database initialized
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 6: Run Tests (Optional but Recommended)

```bash
cd apps/api
python -m pytest tests/ -q
# Expected: 128 passed
```

---

## 4. Frontend Installation

### Step 1: Install Node.js

```bash
# Check version
node --version  # Should show v18+ or v20+
npm --version

# If not installed:
# macOS:
brew install node@20

# Ubuntu:
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
```

### Step 2: Install Dependencies

```bash
cd apps/web

# Using npm
npm install

# Or using pnpm (recommended)
npm install -g pnpm
pnpm install
```

### Step 3: Verify Installation

```bash
# Check TypeScript
npx tsc --version  # Should show 5.3+

# Run type check
npm run typecheck
# Should show: (no output = no errors)
```

### Step 4: Start Frontend

```bash
npm run dev
```

Expected output:
```
  ▲ Next.js 14.2.0
  - Local:        http://localhost:3000
  - Network:      http://192.168.x.x:3000

 ✓ Starting...
 ✓ Ready in 2.5s
```

---

## 5. Infrastructure Installation

### Option A: Docker (Recommended)

```bash
# Install Docker
# macOS: brew install --cask docker
# Ubuntu: curl -fsSL https://get.docker.com | sh

# Start all services
docker-compose up -d

# Verify
docker-compose ps

# Expected output:
# NAME                    STATUS
# sdlc-factory-api-1      Up (healthy)
# sdlc-factory-web-1      Up (healthy)
# sdlc-factory-postgres-1 Up (healthy)
# sdlc-factory-redis-1    Up (healthy)
# sdlc-factory-qdrant-1   Up (healthy)
```

### Option B: Manual Installation

#### PostgreSQL

```bash
# macOS
brew install postgresql@15
brew services start postgresql@15

# Ubuntu
sudo apt install postgresql-15
sudo systemctl start postgresql

# Create database
sudo -u postgres psql -c "CREATE USER governance WITH PASSWORD 'forge';"
sudo -u postgres psql -c "CREATE DATABASE sdlc_factory OWNER governance;"
```

#### Redis

```bash
# macOS
brew install redis
brew services start redis

# Ubuntu
sudo apt install redis-server
sudo systemctl start redis-server

# Verify
redis-cli ping  # Should return: PONG
```

#### Qdrant (Optional)

```bash
# Docker (recommended)
docker run -d -p 6333:6333 qdrant/qdrant:latest

# Or download binary from https://qdrant.tech/documentation/guides/installation/
```

#### Ollama (Optional — for local models)

```bash
# macOS
brew install ollama
ollama serve

# Linux
curl -fsSL https://ollama.ai/install.sh | sh
ollama serve

# Pull models
ollama pull phi3
ollama pull qwen2.5-coder
ollama pull llama3.1

# Verify
ollama list
```

---

## 6. Model Provider Setup

### Ollama (Local — Free)

```bash
# Already installed in step 5

# Pull recommended models
ollama pull phi3          # 2.3GB — Fast reasoning
ollama pull qwen2.5-coder # 4.7GB — Code generation
ollama pull llama3.1      # 4.7GB — General purpose

# Configure in .env:
# OLLAMA_BASE_URL=http://localhost:11434
# DEFAULT_MODEL_PROVIDER=ollama
# LOCAL_ONLY_MODE=true
```

### OpenAI (Remote — Paid)

```bash
# Get API key from https://platform.openai.com/api-keys
# Add to .env:
# OPENAI_API_KEY=sk-...
```

### Anthropic (Remote — Paid)

```bash
# Get API key from https://console.anthropic.com/
# Add to .env:
# ANTHROPIC_API_KEY=sk-ant-...
```

### Google Gemini (Remote — Free tier available)

```bash
# Get API key from https://aistudio.google.com/app/apikey
# Add to .env:
# GOOGLE_API_KEY=...
```

### OpenRouter (Remote — Paid, 100+ models)

```bash
# Get API key from https://openrouter.ai/keys
# Add to .env:
# OPENROUTER_API_KEY=sk-or-...
```

---

## 7. Verification

### Backend Verification

```bash
# Health check
curl http://localhost:8000/api/v1/health
# Expected: {"status": "healthy", ...}

# API docs
open http://localhost:8000/docs
# Should show Swagger UI with all endpoints

# Run tests
cd apps/api
python -m pytest tests/ -v
# Expected: 128/128 passed

### Frontend Verification

```bash
# Type check
cd apps/web
npm run typecheck
# Expected: (no output = no errors)

# Build
npm run build
# Expected: ✓ Compiled successfully

# Open in browser
open http://localhost:3000
# Should show the Control Tower dashboard
```

### Infrastructure Verification

```bash
# PostgreSQL
psql -U governance -d sdlc_factory -h localhost -c "SELECT 1"
# Expected: 1 row

# Redis
redis-cli ping
# Expected: PONG

# Qdrant
curl http://localhost:6333/health
# Expected: {"title": "qdrant", "version": "..."}

# Ollama
curl http://localhost:11434/api/tags
# Expected: {"models": [...]}
```

---

## 8. Troubleshooting

### Backend Issues

**Issue: `ModuleNotFoundError: No module named 'fastapi'`**
```bash
# Ensure virtual environment is active
source venv/bin/activate
pip install -r apps/api/requirements.txt
```

**Issue: `could not connect to server: Connection refused` (PostgreSQL)**
```bash
# Check PostgreSQL is running
brew services list | grep postgresql  # macOS
sudo systemctl status postgresql      # Ubuntu

# Start if not running
brew services start postgresql@15     # macOS
sudo systemctl start postgresql       # Ubuntu
```

**Issue: `sqlalchemy.exc.OperationalError: FATAL: password authentication failed`**
```bash
# Reset password
psql postgres -c "ALTER USER governance WITH PASSWORD 'forge';"
```

**Issue: `redis.exceptions.ConnectionError: Error 61 connecting to localhost:6379`**
```bash
# Check Redis is running
brew services list | grep redis  # macOS
sudo systemctl status redis      # Ubuntu

# Start if not running
brew services start redis        # macOS
sudo systemctl start redis       # Ubuntu
```

**Issue: `alembic.util.exc.CommandError: Can't locate revision`**
```bash
# Reset migrations
cd apps/api
python -m alembic stamp head
python -m alembic upgrade head
```

### Frontend Issues

**Issue: `npm ERR! EACCES: permission denied`**
```bash
# Fix npm permissions
sudo chown -R $(whoami) ~/.npm
# Or use nvm for Node version management
```

**Issue: `Module not found: Can't resolve 'xxx'`**
```bash
# Clean reinstall
rm -rf node_modules .next
npm install
```

**Issue: `Type error: Type 'xxx' is not assignable to type 'yyy'`**
```bash
# Run type check for details
npm run typecheck
# Fix the reported type errors
```

**Issue: `ECONNREFUSED` when connecting to backend**
```bash
# Ensure backend is running on port 8000
curl http://localhost:8000/api/v1/health

# Check CORS origins in .env
# API_CORS_ORIGINS=http://localhost:3000
```

### Docker Issues

**Issue: `docker: command not found`**
```bash
# Install Docker
brew install --cask docker  # macOS
curl -fsSL https://get.docker.com | sh  # Ubuntu

# Start Docker Desktop (macOS)
open /Applications/Docker.app
```

**Issue: `port is already allocated`**
```bash
# Find what's using the port
lsof -i :8000
lsof -i :3000
lsof -i :5432

# Kill the process or change ports in .env
```

**Issue: `container is unhealthy`**
```bash
# Check logs
docker-compose logs api
docker-compose logs web

# Rebuild
docker-compose build --no-cache
docker-compose up -d
```

---

## 9. Dependency Reference

### requirements.txt (Complete)

```
# Web Framework
fastapi==0.115.0
uvicorn[standard]==0.30.0
python-multipart==0.0.12

# Database
sqlalchemy[asyncio]==2.0.35
asyncpg==0.29.0
alembic==1.13.0

# Validation
pydantic==2.9.0
pydantic-settings==2.5.0

# Cache
redis==5.1.0

# HTTP Client
httpx==0.27.0

# Logging
structlog==24.4.0
python-json-logger==2.0.7

# Observability
opentelemetry-api==1.27.0
opentelemetry-sdk==1.27.0
opentelemetry-instrumentation-fastapi==0.48b0
prometheus-client==0.21.0

# AI Providers (optional)
# openai>=1.0.0
# anthropic>=0.20.0
# google-generativeai>=0.5.0
```

### package.json Dependencies (Complete)

```json
{
  "dependencies": {
    "next": "14.2.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "typescript": "^5.3.0",
    "tailwindcss": "^3.4.0",
    "zustand": "^4.5.0",
    "recharts": "^2.12.0",
    "framer-motion": "^12.38.0",
    "lucide-react": "^0.344.0",
    "mermaid": "^10.9.0",
    "react-markdown": "^9.0.1",
    "remark-gfm": "^4.0.0",
    "clsx": "^2.1.0",
    "tailwind-merge": "^2.2.0",
    "@reactflow/core": "^11.11.4",
    "@reactflow/background": "^11.3.14",
    "@reactflow/controls": "^11.2.14",
    "@reactflow/minimap": "^11.7.14",
    "date-fns": "^4.1.0"
  },
  "devDependencies": {
    "@types/node": "^20.11.0",
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "autoprefixer": "^10.4.0",
    "postcss": "^8.4.0"
  }
}
```

### .env.example (Complete)

```bash
# ============================================================
# Governed Autonomous SDLC Factory - Environment Configuration
# ============================================================

# Database (Required)
DATABASE_URL=postgresql+asyncpg://governance:forge@localhost:5432/sdlc_factory

# Redis (Required)
REDIS_URL=redis://localhost:6379/0

# Qdrant (Optional)
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION=sdlc_memory

# API (Required)
API_SECRET=change-me-minimum-32-characters
API_HOST=0.0.0.0
API_PORT=8000
API_CORS_ORIGINS=http://localhost:3000

# Frontend (Required)
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000

# Model Providers (Optional — add keys for providers you want)
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
GOOGLE_API_KEY=
OPENROUTER_API_KEY=
OLLAMA_BASE_URL=http://localhost:11434

# Model Configuration
DEFAULT_MODEL_PROVIDER=ollama
LOCAL_ONLY_MODE=false
COST_HARD_LIMIT=50.00
COST_WARNING_THRESHOLD=0.8

# Observability (Optional)
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
PROMETHEUS_PORT=9090
GRAFANA_PORT=3001

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Storage
ARTIFACT_DIR=/tmp/cortex-artifacts
```
