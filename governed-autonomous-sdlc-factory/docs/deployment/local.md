# Local Deployment Guide

## Prerequisites

Before starting, ensure you have the following installed:

| Requirement | Minimum Version | Installation |
|---|---|---|
| Python | 3.11+ | [python.org](https://python.org) or `brew install python@3.12` |
| Node.js | 18+ | [nodejs.org](https://nodejs.org) or `brew install node@20` |
| PostgreSQL | 15+ | `brew install postgresql@15` |
| Redis | 7+ | `brew install redis` |
| Ollama | 0.1.0+ | [ollama.ai](https://ollama.ai) (optional, for local models) |

## Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/your-org/governed-autonomous-sdlc-factory.git
cd governed-autonomous-sdlc-factory

# 2. Copy and configure environment
cp .env.example .env
# Edit .env with your settings (see Environment Variables below)

# 3. Start infrastructure services
brew services start postgresql@15
brew services start redis

# 4. Create database
createdb sdlc_factory

# 5. Set up backend
python -m venv venv
source venv/bin/activate
pip install -r apps/api/requirements.txt

# 6. Run database migrations
cd apps/api
python -m alembic upgrade head
cd ../..

# 7. Set up frontend
cd apps/web
npm install
cd ../..

# 8. Start backend (terminal 1)
cd apps/api
python -m uvicorn src.main:app --reload --port 8000
cd ../..

# 9. Start frontend (terminal 2)
cd apps/web
npm run dev

# 10. Open Control Tower
open http://localhost:3000
```

## Detailed Setup

### 1. Database Setup

```bash
# Start PostgreSQL
brew services start postgresql@15

# Create database and user
psql postgres
```

```sql
CREATE USER governance WITH PASSWORD 'forge';
CREATE DATABASE sdlc_factory OWNER governance;
GRANT ALL PRIVILEGES ON DATABASE sdlc_factory TO governance;
\q
```

### 2. Redis Setup

```bash
# Start Redis
brew services start redis

# Verify
redis-cli ping
# Should return: PONG
```

### 3. Ollama Setup (Optional — for local models)

```bash
# Install Ollama
brew install ollama

# Start Ollama
ollama serve

# Pull recommended models
ollama pull phi3
ollama pull qwen2.5-coder
ollama pull llama3.1
```

### 4. Environment Configuration

Edit `.env` with your settings:

```bash
# Database
DATABASE_URL=postgresql+asyncpg://governance:forge@localhost:5432/sdlc_factory

# Redis
REDIS_URL=redis://localhost:6379/0

# API
API_SECRET=your-secret-key-here
API_HOST=0.0.0.0
API_PORT=8000
API_CORS_ORIGINS=http://localhost:3000

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000

# Model Providers (add keys for providers you want to use)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...
OPENROUTER_API_KEY=sk-or-...
OLLAMA_BASE_URL=http://localhost:11434

# Model Configuration
DEFAULT_MODEL_PROVIDER=ollama
LOCAL_ONLY_MODE=false
COST_HARD_LIMIT=50.00
COST_WARNING_THRESHOLD=0.8

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

### 5. Verify Installation

```bash
# Backend health check
curl http://localhost:8000/api/v1/health

# API docs
open http://localhost:8000/docs

# Frontend
open http://localhost:3000
```

## Troubleshooting

### Database Connection Issues

```bash
# Check PostgreSQL is running
brew services list | grep postgresql

# Check connection
psql -U governance -d sdlc_factory -h localhost
```

### Redis Connection Issues

```bash
# Check Redis is running
brew services list | redis

# Test connection
redis-cli ping
```

### Frontend Build Issues

```bash
# Clean and reinstall
cd apps/web
rm -rf node_modules .next
npm install
npm run build
```

### Backend Import Issues

```bash
# Ensure virtual environment is active
source venv/bin/activate

# Reinstall dependencies
pip install -r apps/api/requirements.txt --force-reinstall
```

### Port Conflicts

```bash
# Check what's using port 8000
lsof -i :8000

# Check what's using port 3000
lsof -i :3000

# Kill process if needed
kill -9 <PID>
```
