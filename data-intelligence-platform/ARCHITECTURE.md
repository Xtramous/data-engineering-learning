# Data Intelligence Platform - Technical Architecture

## System Overview

The Data Intelligence Platform is a comprehensive, local-first metadata discovery and data lineage system. It enables data engineers and analysts to discover, understand, and explore their data assets without cloud dependencies.

## Architecture Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                     Frontend Layer                           │
│                     (React + TypeScript)                     │
│  ┌──────────────┬──────────────┬──────────────┐              │
│  │  Search     │  Catalog     │  Lineage     │  Chat        │
│  │  Page       │  Pages       │  Explorer    │  Assistant   │
│  └──────────────┴──────────────┴──────────────┘              │
└──────────────────────────────────────────────────────────────┘
                        ↓ (REST API)
┌──────────────────────────────────────────────────────────────┐
│                    API Layer (FastAPI)                       │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ /api/search     /api/lineage    /api/tables            │ │
│  │ /api/dashboards /api/chat       /api/health            │ │
│  └─────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
              ↓           ↓            ↓           ↓
    ┌──────────────┬──────────────┬──────────────┬──────────────┐
    │  PostgreSQL  │   Neo4j      │  OpenSearch  │   Ollama     │
    │              │              │              │              │
    │ Warehouse    │ Lineage      │ Full-text    │ Embeddings   │
    │ Facts &      │ Graph        │ Search &     │ & Chat LLM   │
    │ Dimensions   │ Relations    │ Vectors      │              │
    └──────────────┴──────────────┴──────────────┴──────────────┘
           ↓              ↓              ↓              ↓
    ┌──────────────────────────────────────────────────────────┐
    │          Metadata Ingestion Pipeline (Python)            │
    │  • Extract table/column metadata                         │
    │  • Parse DAG configurations                              │
    │  • Generate lineage graphs                               │
    │  • Create semantic embeddings                            │
    │  • Generate documentation                                │
    └──────────────────────────────────────────────────────────┘
```

## Component Architecture

### 1. Data Layer

#### PostgreSQL (Port 5432)
**Purpose**: Source data warehouse

**Tables**:
- Dimension Tables: customer_dim, product_dim
- Fact Tables: sales_fact, order_fact, inventory_fact
- Metadata Tables: metadata.table_metadata, metadata.column_metadata

**Features**:
- Full ACID compliance
- Indexing on key columns for performance
- Metadata storage alongside operational data
- Support for complex joins and aggregations

**Data Volume**:
- customer_dim: 10,000 rows
- product_dim: 5,000 rows
- sales_fact: 500,000 rows
- order_fact: 100,000 rows
- inventory_fact: 50,000 rows

#### Neo4j (Port 7687, 7474)
**Purpose**: Data lineage and relationship modeling

**Node Types**:
- Table: Represents data tables with metadata
- Column: Represents table columns with data types
- Dashboard: Represents BI dashboards
- Job/DAG: Represents ETL processes

**Relationship Types**:
- FEEDS_INTO: Table→Table (data flow)
- USED_BY: Table→Dashboard (dashboard dependencies)
- DEPENDS_ON: Job→Table (process dependencies)
- OWNS: Team→Asset (ownership)

**Capabilities**:
- Multi-level lineage traversal
- Path finding between assets
- Impact analysis
- Reverse dependency tracking

#### OpenSearch (Port 9200)
**Purpose**: Full-text search and vector similarity search

**Indices**:
- `tables_index`: Table metadata with embeddings
- `columns_index`: Column-level metadata
- `dashboards_index`: Dashboard catalog
- `documentation_index`: Full-text documentation search

**Features**:
- BM25 full-text ranking
- k-NN vector search for semantic similarity
- Faceted search with filters
- Real-time indexing
- Scalable to millions of documents

#### Ollama (Port 11434)
**Purpose**: Local LLM for embeddings and chat

**Model**: Llama 3
**Capabilities**:
- Text embedding generation (1024-dim vectors)
- Natural language understanding
- RAG-powered question answering
- No external API calls (completely local)
- ~6GB VRAM requirement

### 2. API Layer (FastAPI, Port 8000)

**Architecture**: Modular, endpoint-based design

**API Groups**:

#### Search Endpoints
```
GET  /api/search                  Query all assets
GET  /api/search/tables           Query tables only
GET  /api/search/dashboards       Query dashboards only
GET  /api/search/autocomplete     Autocomplete suggestions
```

#### Lineage Endpoints
```
GET  /api/lineage/{table_id}      Get upstream/downstream lineage
GET  /api/lineage/path/{src}/{tgt}  Find path between assets
```

#### Catalog Endpoints
```
GET  /api/tables                  List all tables with pagination
GET  /api/tables/{table_id}       Get full table metadata
GET  /api/dashboards              List all dashboards
GET  /api/dashboards/{dash_id}    Get dashboard details
GET  /api/ownership               Get ownership mappings
```

#### Chat Endpoints
```
POST /api/chat                    Ask AI a metadata question
POST /api/chat/history            Get chat history
POST /api/ask-about/{type}/{id}   Ask about specific asset
```

#### Health Endpoints
```
GET  /health                      Service health check
GET  /health/db                   Database connectivity check
```

**Request/Response Format**:
- JSON request/response bodies
- Standard HTTP status codes
- Error messages with context
- Pagination support (limit, offset)

**Middleware**:
- CORS enabled for cross-origin requests
- Request logging
- Error handling and validation

### 3. Frontend Layer (React + TypeScript, Port 3000)

**Technology Stack**:
- React 18 for UI framework
- TypeScript for type safety
- React Router for navigation
- Axios for API communication
- Cytoscape.js for graph visualization
- Recharts for data visualization
- Tailwind CSS for styling

**Pages**:

#### Search Page (/)
- Semantic search interface
- Filter by asset type
- Quick preview cards
- Direct navigation to details

#### Table Catalog (/tables)
- Sortable table list
- Column metadata view
- Related dashboards
- Data lineage visualization

#### Dashboard Catalog (/dashboards)
- Grid view of all dashboards
- Owner and description
- Referenced table tracking
- Last refresh timestamp

#### Lineage Explorer (/lineage/:tableId)
- Interactive graph visualization
- Upstream/downstream toggle
- Hover for metadata preview
- Click to navigate
- Full path display

#### Chat Assistant (/chat)
- Message history interface
- Context-aware suggestions
- Source attribution
- Conversation export

#### Asset Details (/asset/:type/:id)
- Complete metadata view
- Related assets section
- Ownership information
- Data quality metrics

**State Management**:
- React Context for global state
- Local component state for UI
- API caching to reduce requests

**API Client**:
- Centralized `api.ts` service
- Automatic error handling
- Request/response interceptors
- Base URL configuration

### 4. Metadata Ingestion Pipeline (Python)

**Execution**: One-time setup + scheduled refreshes

**Stages**:

#### Stage 1: Data Generation (01_generate_sample_data.py)
- Create realistic fact and dimension tables
- 660,000+ total rows across 5 tables
- Full referential integrity
- Sample timestamps and values

#### Stage 2: Metadata Extraction (02_extract_table_metadata.py)
- Connect to PostgreSQL information_schema
- Extract table and column metadata
- Calculate table sizes and row counts
- Store in metadata schema

#### Stage 3: Dashboard Ingestion (03_extract_dashboard_metadata.py)
- Parse dashboard JSON configurations
- Extract title, description, owner
- Link to source tables
- Create 20 sample dashboards

#### Stage 4: DAG Parsing (04_parse_dag_metadata.py)
- Read Airflow DAG Python files
- Extract task dependencies
- Map source and target tables
- Create 10 sample DAGs

#### Stage 5: Lineage Generation (05_generate_lineage.py)
- Parse SQL to identify table relationships
- Build multi-level dependency graphs
- Populate Neo4j with nodes and relationships
- Create 50+ lineage connections

#### Stage 6: Embedding Generation (06_generate_embeddings.py)
- Call Ollama for semantic embeddings
- Embed tables, columns, dashboards
- Index vectors in OpenSearch
- Enable semantic search

#### Stage 7: Documentation Generation (07_create_documentation.py)
- Generate markdown for all tables
- Create data dictionary
- Build business glossary
- Document processes
- Create 50+ markdown files

## Data Flow

### Ingestion Flow
```
PostgreSQL      DAG Files       Dashboard JSON
     ↓               ↓                ↓
     └───────────────┴────────────────┘
                     ↓
         Ingestion Pipeline (Python)
                     ↓
    ┌────────────────┼────────────────┐
    ↓                ↓                ↓
Neo4j           OpenSearch        Files
(Lineage)      (Search Index)   (Docs)
```

### Query Flow
```
Frontend Request
     ↓
FastAPI Endpoint
     ↓
   Service Layer
     ↓
┌───┴────┬────────┬──────────┐
↓        ↓        ↓          ↓
PG    Neo4j   OpenSearch  Ollama
↓        ↓        ↓          ↓
└───┬────┴────────┴──────────┘
    ↓
Response JSON
    ↓
Frontend Display
```

## Database Schemas

### PostgreSQL

#### public schema
```sql
customer_dim        -- Customer master data
product_dim         -- Product master data
sales_fact          -- Transaction-level sales
order_fact          -- Order-level aggregates
inventory_fact      -- Warehouse inventory
```

#### metadata schema
```sql
table_metadata      -- Table-level metadata
column_metadata     -- Column-level metadata
```

### Neo4j
```
(Table {name, schema, owner, row_count})
(Column {name, type, nullable})
(Dashboard {id, name, owner})
(Job {name, schedule, owner})

Relationships:
- Table-[FEEDS_INTO]->Table
- Table-[USED_BY]->Dashboard
- Job-[PROCESSES]->Table
```

### OpenSearch
```
tables_index
  - name (text)
  - schema (keyword)
  - owner (keyword)
  - description (text)
  - embedding (knn_vector, dim=1024)

dashboards_index
  - name (text)
  - owner (keyword)
  - tables (keyword array)
```

## Performance Characteristics

### Query Performance
- **Search**: <500ms for full-text queries
- **Lineage traversal**: <100ms for 3-level depth
- **Chat response**: 2-5 seconds (Ollama inference)
- **Table list**: <100ms with pagination

### Data Volumes
- **PostgreSQL**: ~750KB for sample data
- **Neo4j**: ~5MB for lineage graphs (50+ nodes/edges)
- **OpenSearch**: ~10MB for all indices
- **Ollama model**: ~4GB (Llama 3)

### Resource Requirements
- **RAM**: 16GB total
  - PostgreSQL: 2GB shared buffers
  - Neo4j: 2GB heap
  - OpenSearch: 4GB heap
  - Ollama: 6GB VRAM
  - Services: 2GB combined

- **Disk**: 20GB total
  - Data: 5GB (PostgreSQL)
  - Model: 4GB (Ollama)
  - Dependencies: 11GB
  - Margin: 1GB

## Security & Privacy

### Data Protection
- No external API calls (fully local)
- All data stays on localhost
- No cloud dependencies
- Full encryption at rest (filesystem)

### Access Control
- CORS enabled for localhost only (configurable)
- No authentication layer (add as needed)
- Health checks accessible
- API documentation public

### Compliance
- No PII sent to external services
- Complete data sovereignty
- Audit-friendly (all local logging)
- GDPR-friendly (no external retention)

## Extensibility Points

### Adding New Data Sources
1. Create new ingestion script in `ingestion/`
2. Add metadata extraction logic
3. Populate Neo4j and OpenSearch
4. Create documentation

### Adding New API Endpoints
1. Create new file in `backend/api/`
2. Define Pydantic models in `backend/models/schemas.py`
3. Implement service logic in `backend/services/`
4. Include router in `app.py`

### Adding New Frontend Pages
1. Create React component in `frontend/src/pages/`
2. Add route in `App.tsx`
3. Create API service in `frontend/src/services/`
4. Add navigation link

### Custom LLM Models
1. Pull different model: `ollama pull mistral`
2. Update `OLLAMA_MODEL` env var
3. Adjust request prompt/context as needed

## Deployment Considerations

### Current Deployment
- Single machine with Docker Compose
- All containers on shared network
- Persistent volumes for data
- Auto-restart on failure

### Future Enhancements
- Kubernetes deployment
- Distributed services
- Cloud-hosted data
- Multi-region setup
- Auto-scaling

## Monitoring & Logging

### Application Logs
- Backend: stdout (captured by Docker)
- Frontend: Browser console
- Ingestion: File-based logging

### Health Checks
- PostgreSQL: pg_isready
- Neo4j: HTTP health endpoint
- OpenSearch: Cluster health API
- Ollama: Model list command

### Metrics
- Query latency
- API request counts
- Lineage traversal performance
- Search result relevance

## Development Workflow

### Local Development
```bash
# Start services
docker-compose up -d

# Run ingestion
bash scripts/ingest.sh

# Frontend development
cd frontend && npm start

# Backend development
# API auto-reloads with uvicorn reload=True
```

### Testing
- Manual API testing via Swagger UI
- Frontend manual QA
- Load testing with sample data
- Lineage verification queries

### Version Control
- Git commits per component change
- Feature branches for major features
- Tags for releases
- Comprehensive commit messages

## Conclusion

The Data Intelligence Platform provides a complete, local-first solution for metadata discovery and lineage exploration. Its modular architecture allows easy extension while maintaining simplicity and performance. The combination of PostgreSQL for data, Neo4j for relationships, OpenSearch for search, and Ollama for AI creates a powerful, self-contained system that requires no cloud infrastructure or external dependencies.
