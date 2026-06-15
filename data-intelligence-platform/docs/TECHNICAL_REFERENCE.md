# Data Intelligence Platform - Technical Reference Guide

## Quick Reference

### System Overview

**Fully Local Metadata Discovery Platform**
- 4 Databases (PostgreSQL, Neo4j, OpenSearch, Ollama)
- REST API (FastAPI)
- React Frontend
- Python Ingestion Pipeline
- Docker Containerization

### Quick Start

```bash
cd data-intelligence-platform
cp .env.example .env
bash scripts/startup.sh    # ~2 minutes
bash scripts/ingest.sh     # ~5 minutes
# Open http://localhost:3000
```

---

## Database Reference

### PostgreSQL (Port 5432)

**Connection String:** `postgresql://dataeng:secure123@localhost:5432/datawarehouse`

**Schemas:**
```
public/
  ├─ customer_dim      (10,000 rows)
  ├─ product_dim       (5,000 rows)
  ├─ sales_fact        (500,000 rows)
  ├─ order_fact        (100,000 rows)
  └─ inventory_fact    (50,000 rows)

metadata/
  ├─ table_metadata
  └─ column_metadata
```

**Key Tables:**

**customer_dim:**
```sql
CREATE TABLE customer_dim (
    customer_id INTEGER PRIMARY KEY,
    customer_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(20),
    city VARCHAR(100),
    country VARCHAR(100),
    signup_date DATE,
    is_active BOOLEAN,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

**sales_fact:**
```sql
CREATE TABLE sales_fact (
    sales_id BIGINT PRIMARY KEY,
    customer_id INTEGER REFERENCES customer_dim,
    product_id INTEGER REFERENCES product_dim,
    sales_date DATE NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    total_amount DECIMAL(15,2) NOT NULL,
    discount_amount DECIMAL(10,2),
    tax_amount DECIMAL(10,2),
    created_at TIMESTAMP
);
```

**Common Queries:**

```sql
-- Total revenue
SELECT SUM(total_amount) as total_revenue FROM sales_fact;

-- Top 10 customers by revenue
SELECT c.customer_name, SUM(s.total_amount) as revenue
FROM customer_dim c
JOIN sales_fact s ON c.customer_id = s.customer_id
GROUP BY c.customer_id, c.customer_name
ORDER BY revenue DESC LIMIT 10;

-- Sales by date
SELECT sales_date, COUNT(*) as transaction_count, SUM(total_amount) as daily_revenue
FROM sales_fact
GROUP BY sales_date
ORDER BY sales_date DESC;
```

---

### Neo4j (Port 7687, 7474)

**Connection String:** `bolt://localhost:7687`

**Authentication:** `neo4j / secure123`

**Web UI:** http://localhost:7474

**Node Types:**

```cypher
-- Table node
CREATE (t:Table {
    name: 'customer_dim',
    schema: 'public',
    owner: 'analytics-team',
    row_count: 10000,
    description: 'Customer dimension table'
})

-- Column node
CREATE (c:Column {
    name: 'customer_id',
    table_name: 'customer_dim',
    type: 'INTEGER',
    nullable: false
})

-- Dashboard node
CREATE (d:Dashboard {
    id: 'sales_dashboard',
    name: 'Sales Dashboard',
    owner: 'bi-team',
    description: 'Real-time sales metrics'
})

-- Job node
CREATE (j:Job {
    name: 'customer_etl',
    owner: 'data-team',
    schedule: '0 2 * * *',
    description: 'Daily customer ETL'
})
```

**Relationship Types:**

```cypher
-- Data flow
MATCH (source:Table), (target:Table)
CREATE (source)-[:FEEDS_INTO {description: 'customer data flow'}]->(target)

-- Data consumption
MATCH (table:Table), (dashboard:Dashboard)
CREATE (table)-[:USED_BY {description: 'used in dashboard'}]->(dashboard)

-- Job processing
MATCH (job:Job), (table:Table)
CREATE (job)-[:PROCESSES {description: 'processes this table'}]->(table)

-- Ownership
MATCH (team:Team), (asset:Table)
CREATE (team)-[:OWNS {description: 'team owns this asset'}]->(asset)
```

**Essential Cypher Queries:**

```cypher
-- Find all tables
MATCH (t:Table) RETURN t.name, t.owner, t.row_count

-- Get upstream lineage (what feeds into this table?)
MATCH (source:Table)-[r:FEEDS_INTO*1..3]->(target:Table {name: 'sales_fact'})
RETURN source.name as upstream

-- Get downstream lineage (what uses this table?)
MATCH (source:Table {name: 'customer_dim'})-[r:FEEDS_INTO|USED_BY*1..3]->(downstream)
RETURN downstream.name as downstream

-- Find impact (if I drop this column, what breaks?)
MATCH (c:Column {name: 'customer_id', table_name: 'customer_dim'})-[:USED_BY*1..3]->(affected)
RETURN affected.name as affected_asset

-- Get complete path from raw to dashboard
MATCH path = (raw:Table {name: 'raw_customers'})-[*]->(dashboard:Dashboard)
RETURN path

-- Count lineage levels
MATCH path = (a:Table)-[:FEEDS_INTO*]->(b:Table)
WHERE a.name = 'raw_customers' AND b.name = 'sales_fact'
RETURN length(path) as hops
```

---

### OpenSearch (Port 9200)

**Web UI:** http://localhost:9200

**Available Indices:**
- `tables_index` - Table metadata
- `columns_index` - Column metadata
- `dashboards_index` - Dashboard metadata
- `documentation_index` - Full-text docs

**Index Mapping Example:**

```json
{
  "settings": {
    "number_of_shards": 1,
    "number_of_replicas": 0
  },
  "mappings": {
    "properties": {
      "name": {"type": "text"},
      "schema": {"type": "keyword"},
      "owner": {"type": "keyword"},
      "description": {"type": "text"},
      "row_count": {"type": "integer"},
      "embedding": {
        "type": "knn_vector",
        "dimension": 1024,
        "method": {
          "name": "hnsw",
          "space_type": "l2",
          "engine": "lucene"
        }
      }
    }
  }
}
```

**Search Queries:**

```bash
# Full-text search
curl -X GET "localhost:9200/tables_index/_search" -H 'Content-Type: application/json' -d '{
  "query": {
    "match": {
      "name": "customer"
    }
  }
}'

# Vector similarity search (k-NN)
curl -X GET "localhost:9200/tables_index/_search" -H 'Content-Type: application/json' -d '{
  "query": {
    "knn": {
      "embedding": {
        "vector": [0.1, 0.2, ..., 0.8],
        "k": 5
      }
    }
  }
}'

# Combined search (full-text + vector)
curl -X GET "localhost:9200/tables_index/_search" -H 'Content-Type: application/json' -d '{
  "query": {
    "bool": {
      "should": [
        {"match": {"description": "customer"}},
        {"knn": {"embedding": {"vector": [...], "k": 10}}}
      ]
    }
  }
}'

# List all indices
curl -X GET "localhost:9200/_cat/indices?v"
```

---

### Ollama (Port 11434)

**Base URL:** `http://localhost:11434`

**Model:** Llama 3 (~4GB)

**Available Endpoints:**

```bash
# Check if running
curl http://localhost:11434/api/tags

# Generate embedding
curl -X POST http://localhost:11434/api/embeddings \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama3",
    "prompt": "customer dimension table"
  }'

# Generate text
curl -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama3",
    "prompt": "What is a data warehouse?",
    "stream": false
  }'

# Pull a model
curl -X POST http://localhost:11434/api/pull \
  -H "Content-Type: application/json" \
  -d '{"name": "llama3"}'
```

---

## API Reference

### Base URL
`http://localhost:8000`

### Authentication
None (add as needed)

### Response Format
```json
{
  "status": "success|error",
  "data": {},
  "error": null,
  "timestamp": "2024-06-15T10:30:00"
}
```

### Search Endpoints

**GET /api/search**
```
Query Parameters:
  - q: string (required) - Search query
  - type: string (optional) - Filter by type (table, column, dashboard)
  - limit: integer (optional) - Max results, default 20, max 100

Response:
{
  "status": "success",
  "results": [
    {
      "id": "customer_dim",
      "name": "customer_dim",
      "type": "table",
      "score": 0.95,
      "metadata": {
        "owner": "analytics-team",
        "schema": "public",
        "row_count": 10000
      }
    }
  ]
}
```

### Lineage Endpoints

**GET /api/lineage/{asset_id}**
```
Path Parameters:
  - asset_id: string - Table name or dashboard ID

Query Parameters:
  - direction: string - "upstream" | "downstream" | "both"
  - depth: integer - Max traversal depth (1-10)

Response:
{
  "nodes": [
    {
      "id": "customer_dim",
      "name": "customer_dim",
      "type": "table",
      "metadata": {}
    }
  ],
  "edges": [
    {
      "source": "raw_customers",
      "target": "customer_dim",
      "relationship": "FEEDS_INTO"
    }
  ]
}
```

### Catalog Endpoints

**GET /api/tables**
```
Query Parameters:
  - limit: integer (optional) - Pagination limit
  - offset: integer (optional) - Pagination offset
  - schema: string (optional) - Filter by schema

Response:
{
  "status": "success",
  "count": 5,
  "tables": [
    {
      "id": "customer_dim",
      "name": "customer_dim",
      "schema": "public",
      "owner": "analytics-team",
      "row_count": 10000,
      "columns": [...],
      "related_dashboards": [...]
    }
  ]
}
```

**GET /api/dashboards**
```
Query Parameters:
  - limit: integer (optional)
  - offset: integer (optional)

Response:
{
  "status": "success",
  "count": 20,
  "dashboards": [
    {
      "id": "sales_dashboard",
      "name": "Sales Dashboard",
      "owner": "bi-team",
      "tables": ["sales_fact", "customer_dim"],
      "last_updated": "2024-06-15"
    }
  ]
}
```

### Chat Endpoints

**POST /api/chat**
```
Body:
{
  "query": "What feeds customer_fact?",
  "context_assets": ["customer_fact"]  // optional
}

Response:
{
  "status": "success",
  "response": "customer_fact is fed by...",
  "sources": [
    {"name": "raw_customers", "type": "table"},
    {"name": "customer_etl", "type": "dag"}
  ],
  "confidence": 0.92,
  "model": "llama3"
}
```

### Health Endpoints

**GET /health**
```
Response:
{
  "status": "healthy",
  "service": "Data Intelligence Platform",
  "version": "1.0.0"
}
```

**GET /health/db**
```
Response:
{
  "postgresql": "connected",
  "neo4j": "connected",
  "opensearch": "connected",
  "ollama": "connected"
}
```

### Swagger UI

Interactive API documentation available at:
`http://localhost:8000/docs`

---

## File Structure Reference

### Root Directory

```
data-intelligence-platform/
├── docker-compose.yml       # Service orchestration
├── .env.example             # Environment template
├── .gitignore               # Git exclusions
├── README.md                # Getting started
│
├── backend/                 # FastAPI backend
│   ├── app.py
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── api/                 # Route handlers
│   ├── models/              # Data models
│   ├── services/            # Business logic
│   └── utils/               # Utilities
│
├── frontend/                # React frontend
│   ├── package.json
│   ├── Dockerfile
│   └── src/
│       ├── pages/           # Page components
│       ├── components/      # Reusable components
│       ├── services/        # API clients
│       └── types/           # TypeScript definitions
│
├── ingestion/               # Metadata ingestion
│   ├── 01_generate_sample_data.py
│   ├── 02_extract_table_metadata.py
│   ├── 03_extract_dashboard_metadata.py
│   ├── 04_parse_dag_metadata.py
│   ├── 05_generate_lineage.py
│   ├── 06_generate_embeddings.py
│   ├── 07_create_documentation.py
│   ├── config/
│   ├── templates/
│   └── utils/
│
├── data/                    # Database initialization
│   ├── sql/                 # PostgreSQL init scripts
│   └── neo4j/               # Neo4j init scripts
│
├── scripts/                 # Utility scripts
│   ├── startup.sh           # Start services
│   ├── teardown.sh          # Stop services
│   └── ingest.sh            # Run ingestion
│
└── docs/                    # Documentation
    ├── COMPLETE_LEARNING_GUIDE.html
    ├── LEARNING_GUIDE.md
    ├── TECHNICAL_REFERENCE.md
    └── ARCHITECTURE.md
```

---

## Common Tasks

### Check Service Status

```bash
# All services
docker-compose ps

# Specific service
docker-compose ps postgres
```

### View Service Logs

```bash
# All services
docker-compose logs

# Specific service
docker-compose logs backend

# Follow in real-time
docker-compose logs -f backend

# Last 100 lines
docker-compose logs --tail 100 neo4j
```

### Connect to Databases

```bash
# PostgreSQL
docker-compose exec postgres psql -U dataeng -d datawarehouse

# Neo4j Cypher Shell
docker-compose exec neo4j cypher-shell -u neo4j -p secure123

# OpenSearch (via curl)
curl localhost:9200/_cat/indices

# Ollama
docker-compose exec ollama ollama list
```

### Run Python Scripts Manually

```bash
# Generate sample data
docker-compose exec backend python -m ingestion.01_generate_sample_data

# Extract metadata
docker-compose exec backend python -m ingestion.02_extract_table_metadata

# Run all ingestion stages
bash scripts/ingest.sh
```

### Clear Data and Restart

```bash
# Stop services
docker-compose down

# Remove volumes (DELETES ALL DATA)
docker-compose down -v

# Restart
docker-compose up -d
```

### Update Configuration

Edit `.env`:
```bash
POSTGRES_PASSWORD=newpassword
NEO4J_PASSWORD=newpassword
```

Then restart:
```bash
docker-compose down
docker-compose up -d
```

---

## Performance Tuning

### Memory Allocation

Edit `docker-compose.yml`:

```yaml
postgres:
  environment:
    POSTGRES_INITDB_ARGS: "-c shared_buffers=512MB"

neo4j:
  environment:
    NEO4J_dbms_memory_heap_max__size: 2G

opensearch:
  environment:
    OPENSEARCH_JAVA_OPTS: "-Xms2g -Xmx2g"
```

### Database Optimization

**PostgreSQL:**
```sql
-- Analyze tables
ANALYZE;

-- Index on frequently queried columns
CREATE INDEX idx_sales_customer ON sales_fact(customer_id);

-- Vacuum (cleanup)
VACUUM;
```

**Neo4j:**
```cypher
-- Create index
CREATE INDEX on :Table(name);

-- Get query plan
EXPLAIN MATCH (t:Table)-[:FEEDS_INTO]->(d)
WHERE t.name = 'customer_dim'
RETURN d;
```

**OpenSearch:**
```bash
# Optimize index
curl -X POST "localhost:9200/tables_index/_forcemerge?max_num_segments=1"

# Refresh index
curl -X POST "localhost:9200/tables_index/_refresh"
```

---

## Troubleshooting Guide

### Problem: Services fail to start

**Solution:**
```bash
# Check logs
docker-compose logs

# Rebuild
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

### Problem: Out of memory

**Solution:**
Reduce heap sizes in docker-compose.yml:
```yaml
opensearch:
  environment:
    OPENSEARCH_JAVA_OPTS: "-Xms1g -Xmx1g"
```

### Problem: Database connection fails

**Solution:**
```bash
# Check if service is running
docker-compose ps

# Check logs
docker-compose logs postgres

# Wait longer
sleep 30
docker-compose ps
```

### Problem: API returns 500 error

**Solution:**
```bash
# Check backend logs
docker-compose logs backend

# Check database connectivity
curl http://localhost:8000/health/db

# Restart backend
docker-compose restart backend
```

### Problem: Frontend can't reach backend

**Solution:**
```bash
# Verify backend is running
curl http://localhost:8000/health

# Check frontend logs
docker-compose logs frontend

# Verify CORS is enabled in app.py
# Check .env file for API_BASE_URL
```

---

## Version Information

```
Python:        3.11
FastAPI:       0.104.1
React:         18.2.0
PostgreSQL:    15
Neo4j:         5.18 (Community)
OpenSearch:    2.11.1
Ollama:        Latest
Docker:        20.10+
Docker Compose: 1.29+
```

---

## Additional Resources

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Neo4j Documentation](https://neo4j.com/docs/)
- [OpenSearch Documentation](https://opensearch.org/docs/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Docker Documentation](https://docs.docker.com/)

---

**Last Updated:** June 2024
**Project:** Data Intelligence Platform
**Version:** 1.0.0
