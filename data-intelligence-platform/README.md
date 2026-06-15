# Data Intelligence Platform

A comprehensive, open-source metadata discovery and lineage system inspired by Select Star. Discover datasets, understand data flows, search metadata, and interact with an AI assistant—all running locally on your laptop.

## Features

✨ **Real-time Metadata Discovery**
- Automatic table, column, and ownership extraction
- Dashboard and DAG metadata ingestion
- Data quality and freshness tracking

🔗 **Interactive Lineage Exploration**
- Multi-level upstream/downstream lineage
- Visual graph exploration
- Ownership chain tracking

🔍 **Powerful Search**
- Full-text search across all assets
- Semantic search with embeddings
- Fast relevance ranking

🤖 **AI Assistant**
- RAG-powered metadata Q&A
- Local Llama 3 (no cloud dependencies)
- Context-aware responses

📊 **Beautiful UI**
- Search page with autocomplete
- Table/Dashboard catalogs
- Interactive lineage graph
- AI chat interface

## Quick Start

### Prerequisites
- Docker & Docker Compose
- 16GB RAM
- 20GB disk space
- ~15 minutes for initial setup

### One-Command Setup

```bash
# Clone the repository (if not already done)
cd data-engineering-learning/data-intelligence-platform

# Copy environment file
cp .env.example .env

# Start all services
docker-compose up -d

# Wait for services to be healthy (2-3 minutes)
docker-compose ps

# Run ingestion pipeline
bash scripts/ingest.sh

# Open in browser
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000/docs
# Neo4j: http://localhost:7474
# OpenSearch: http://localhost:9200
```

### Verify Installation

```bash
# Check all services are running
docker-compose ps

# Test backend API
curl http://localhost:8000/health

# View backend logs
docker-compose logs -f backend

# View frontend logs
docker-compose logs -f frontend
```

## Project Structure

```
data-intelligence-platform/
├── backend/              # FastAPI backend
│   ├── api/             # REST endpoints
│   ├── models/          # Data models & DB clients
│   ├── services/        # Business logic
│   └── utils/           # Utilities
├── frontend/            # React frontend
│   └── src/
│       ├── pages/       # React pages
│       ├── components/  # Reusable components
│       └── services/    # API clients
├── ingestion/           # Metadata ingestion pipeline
│   ├── 01_*.py         # Data generation & extraction
│   ├── templates/       # Sample DAGs, dashboards, docs
│   └── config/          # Connection configs
├── data/               # Database initialization
│   ├── sql/            # PostgreSQL init scripts
│   └── neo4j/          # Neo4j init scripts
├── scripts/            # Utility scripts
│   ├── startup.sh
│   ├── teardown.sh
│   └── ingest.sh
└── docker-compose.yml  # All services definition
```

## Architecture

### Data Layer
- **PostgreSQL** (5432): Data warehouse with facts and dimensions
- **Neo4j** (7687): Graph database for lineage relationships
- **OpenSearch** (9200): Full-text search + embeddings
- **Ollama** (11434): Local Llama 3 LLM

### Backend
- **FastAPI** (8000): REST API with 5 endpoint groups
  - Search: `/api/search`
  - Lineage: `/api/lineage`
  - Catalog: `/api/tables`, `/api/dashboards`
  - Chat: `/api/chat`
  - Health: `/api/health`

### Frontend
- **React + TypeScript** (3000)
  - Search page with semantic search
  - Table & Dashboard catalogs
  - Interactive lineage explorer
  - AI chat assistant
  - Asset detail pages

### Ingestion Pipeline
- Extract table metadata from PostgreSQL
- Parse Airflow DAG configurations
- Ingest dashboard metadata
- Generate SQL lineage graphs
- Create semantic embeddings
- Auto-generate documentation

## Usage Examples

### Search Assets
```bash
curl "http://localhost:8000/api/search?q=customer&type=table"
```

### Get Lineage
```bash
curl "http://localhost:8000/api/lineage/customer_dim?direction=downstream"
```

### Ask AI Assistant
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"query": "What feeds customer_fact?"}'
```

### Get Table Details
```bash
curl "http://localhost:8000/api/tables/customer_dim"
```

## Sample Data

The platform includes realistic enterprise data:
- **10,000** customer records
- **5,000** product records
- **500,000** sales fact rows
- **100,000** order records
- **50,000** inventory records
- **10** Airflow DAG configurations
- **20** Dashboard metadata files
- **50** Markdown documentation files

## Development

### Add a New Service
1. Update `docker-compose.yml`
2. Add volume mounts if needed
3. Update health checks
4. Document ports and URLs

### Add Backend Endpoints
1. Create route in `backend/api/`
2. Add Pydantic model in `backend/models/schemas.py`
3. Implement service in `backend/services/`
4. Test with `curl` or Swagger UI

### Add Frontend Pages
1. Create component in `frontend/src/pages/`
2. Add route in `App.tsx`
3. Add navigation in header
4. Call backend API via `frontend/src/services/api.ts`

### Run Ingestion Manually
```bash
docker-compose exec backend python -m ingestion.01_generate_sample_data
docker-compose exec backend python -m ingestion.02_extract_table_metadata
docker-compose exec backend python -m ingestion.03_extract_dashboard_metadata
docker-compose exec backend python -m ingestion.04_parse_dag_metadata
docker-compose exec backend python -m ingestion.05_generate_lineage
docker-compose exec backend python -m ingestion.06_generate_embeddings
docker-compose exec backend python -m ingestion.07_create_documentation
```

## Troubleshooting

### Services not starting?
```bash
# View detailed logs
docker-compose logs postgres
docker-compose logs neo4j
docker-compose logs opensearch
docker-compose logs ollama

# Rebuild images
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

### High memory usage?
Reduce OpenSearch heap:
```bash
# In docker-compose.yml, change:
OPENSEARCH_JAVA_OPTS: "-Xms1g -Xmx1g"
```

### Frontend not loading?
```bash
# Check frontend logs
docker-compose logs frontend

# Verify backend is accessible
curl http://localhost:8000/health
```

### Ollama not downloading model?
```bash
# Pull model manually
docker-compose exec ollama ollama pull llama3

# Check available models
docker-compose exec ollama ollama list
```

## Performance Tuning

### Optimize for 16GB RAM
- PostgreSQL: 2GB shared_buffers
- Neo4j: 2GB heap
- OpenSearch: 4GB heap
- Ollama + Llama 3: 6GB VRAM
- Backend/Frontend: 1GB each

### Optimize Search Performance
- Index all columns in PostgreSQL
- Create Neo4j constraints
- Configure OpenSearch refresh intervals
- Use pagination (limit 100 results)

## Documentation

- [ARCHITECTURE.md](./docs/ARCHITECTURE.md) - Detailed technical architecture
- [API_REFERENCE.md](./docs/API_REFERENCE.md) - Complete API documentation
- [DEVELOPMENT.md](./docs/DEVELOPMENT.md) - Development guide
- [INGESTION.md](./docs/INGESTION.md) - Ingestion pipeline details

## Cleanup

```bash
# Stop all services
docker-compose down

# Remove volumes (deletes data)
docker-compose down -v

# Full cleanup
docker system prune -a
```

## Contributing

This is an educational project. Feel free to:
- Extend with new metadata sources
- Add more AI capabilities
- Improve UI/UX
- Optimize performance
- Add tests and documentation

## License

MIT License - See LICENSE file for details

## Support

Issues and questions? Create an issue on GitHub:
https://github.com/Xtramous/data-engineering-learning

## Next Steps

1. ✅ Start services: `docker-compose up -d`
2. ⏳ Wait for healthy status: `docker-compose ps`
3. 🔄 Run ingestion: `bash scripts/ingest.sh`
4. 🌐 Open frontend: `http://localhost:3000`
5. 🔍 Search and explore metadata
6. 💬 Chat with AI assistant

Happy exploring! 🚀
