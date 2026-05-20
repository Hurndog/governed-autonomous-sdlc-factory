# Docker Deployment Guide

## Prerequisites

- Docker 24+
- Docker Compose 2.x

## Quick Start

```bash
# 1. Clone and configure
git clone https://github.com/your-org/governed-autonomous-sdlc-factory.git
cd governed-autonomous-sdlc-factory
cp .env.example .env
# Edit .env with your settings

# 2. Launch all services
docker-compose up -d

# 3. Run database migrations
docker-compose exec api python -m alembic upgrade head

# 4. Verify services
docker-compose ps

# 5. Open Control Tower
open http://localhost:3000
```

## Services

| Service | Port | Description | Image |
|---------|------|-------------|-------|
| api | 8000 | FastAPI backend | python:3.12-slim |
| web | 3000 | Next.js frontend | node:20-alpine |
| postgres | 5432 | PostgreSQL database | postgres:15 |
| redis | 6379 | Redis cache/queue | redis:7-alpine |
| qdrant | 6333 | Vector memory store | qdrant/qdrant:latest |
| prometheus | 9090 | Metrics collection | prom/prometheus:latest |
| grafana | 3001 | Metrics visualization | grafana/grafana:latest |

## Configuration

### Production Overrides

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  api:
    restart: always
    environment:
      - LOG_LEVEL=WARNING
      - LOG_FORMAT=json
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '2'

  web:
    restart: always
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '1'

  postgres:
    restart: always
    volumes:
      - pgdata:/var/lib/postgresql/data
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '2'

  redis:
    restart: always
    command: redis-server --appendonly yes --maxmemory 512mb

volumes:
  pgdata:
```

Launch with production overrides:

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## Backup & Restore

```bash
# Backup database
docker-compose exec postgres pg_dump -U governance sdlc_factory > backup.sql

# Restore database
cat backup.sql | docker-compose exec -T postgres psql -U governance sdlc_factory
```

## Monitoring

```bash
# View logs
docker-compose logs -f api
docker-compose logs -f web

# Check resource usage
docker stats

# Access Prometheus
open http://localhost:9090

# Access Grafana
open http://localhost:3001
```

## Troubleshooting

```bash
# Rebuild after code changes
docker-compose build api
docker-compose up -d api

# Full reset
docker-compose down -v
docker-compose up -d

# Check service health
docker-compose exec api curl -f http://localhost:8000/api/v1/health
```
