# Data Intelligence Platform - Complete Learning Guide

## Table of Contents
1. [Introduction](#introduction)
2. [Problem & Solution](#problem--solution)
3. [Architecture Overview](#architecture-overview)
4. [Component Deep Dive](#component-deep-dive)
5. [Data Flow](#data-flow)
6. [Backend Deep Dive](#backend-deep-dive)
7. [Frontend Deep Dive](#frontend-deep-dive)
8. [Ingestion Pipeline](#ingestion-pipeline)
9. [Docker & Deployment](#docker--deployment)
10. [Setup Instructions](#setup-instructions)
11. [Key Learnings](#key-learnings)

---

## Introduction

Welcome to the most comprehensive learning guide for the **Data Intelligence Platform**. This guide will teach you:

✅ How to design a complete metadata discovery system
✅ How different databases work together
✅ How to build REST APIs with FastAPI
✅ How to create interactive UIs with React
✅ How to extract and process metadata at scale
✅ How to build production-ready systems with Docker

### Your Goal
Master this project deeply enough to explain every component, database table, API endpoint, and feature—even in your sleep!

### Project Statistics
| Metric | Value |
|--------|-------|
| Total Files | 38 |
| Lines of Code | 3,285+ |
| Databases | 4 |
| API Endpoints | 15+ |
| Frontend Pages | 6 |
| Ingestion Stages | 7 |
| Sample Data Rows | 660,000+ |
| Docker Services | 6 |

---

## Problem & Solution

### The Real Problem

Imagine you're a data engineer at a company with:
- Hundreds of data tables across multiple systems
- Dozens of dashboards and reports
- Complex ETL pipelines (Airflow DAGs)
- Data flowing from source → transformation → consumption
- Multiple teams managing different assets

**Questions you need to answer:**
- "What feeds the customer_fact table?"
- "Which dashboards use sales data?"
- "Who owns this table and when was it last updated?"
- "Can I safely modify this column?"
- "What's the impact if this table goes down?"

**Traditional solutions:** Ask people (slow), search Excel sheets (unreliable), read docs (outdated)

### Our Solution

We built an automated system that:
✅ Discovers all data assets automatically
✅ Maps complete data lineage (source → target)
✅ Makes data searchable and discoverable
✅ Provides an AI assistant to answer questions
✅ Runs completely locally (no cloud bills, complete privacy)

---

## Architecture Overview

### The Big Picture

```
┌─────────────────────────────────────────────────────┐
│           Frontend (React, Port 3000)                │
│    Search │ Catalog │ Lineage │ Chat                │
└──────────────────┬──────────────────────────────────┘
                   │ REST API (JSON)
┌──────────────────▼──────────────────────────────────┐
│         Backend (FastAPI, Port 8000)                 │
│  /search │ /lineage │ /catalog │ /chat │ /health    │
└──────┬────────┬──────────┬──────────┬────────────────┘
       │        │          │          │
       ▼        ▼          ▼          ▼
   PostgreSQL  Neo4j   OpenSearch   Ollama
   (Data)    (Graph)   (Search)     (LLM)
```

### Three-Tier Architecture

| Tier | Technology | Purpose | Port |
|------|-----------|---------|------|
| **Presentation** | React + TypeScript | User interface | 3000 |
| **Application** | FastAPI (Python) | Business logic & API | 8000 |
| **Data** | PostgreSQL, Neo4j, OpenSearch, Ollama | Store & process data | 5432, 7687, 9200, 11434 |

### Key Principle

**Separation of Concerns:** Each layer has a specific responsibility. 
- Frontend doesn't talk directly to databases
- Backend doesn't create UI
- Databases don't know about API

This makes the system flexible and maintainable.

---

## Component Deep Dive

### 4 Major Components

#### 1️⃣ Data Layer (4 Databases)

**PostgreSQL** - Relational Data Warehouse
- Stores facts and dimensions
- 5 main tables: customer_dim, product_dim, sales_fact, order_fact, inventory_fact
- ~660K total rows of sample data
- Used for operational queries

**Neo4j** - Graph Database for Lineage
- Stores lineage relationships
- Nodes: Tables, Columns, Dashboards, Jobs
- Relationships: FEEDS_INTO, USED_BY, DEPENDS_ON, OWNS
- Fast traversal for impact analysis

**OpenSearch** - Full-Text & Vector Search
- Full-text search (keyword matching)
- Vector search (semantic similarity)
- 4 indices: tables, columns, dashboards, documentation
- Powers the search functionality

**Ollama** - Local LLM
- Llama 3 model (~4GB)
- Two uses: embeddings and chat
- Completely local, no external API calls
- Powers the AI assistant

#### 2️⃣ Backend API

- 15+ REST endpoints
- 5 endpoint groups:
  - `/search` - Find assets
  - `/lineage` - Trace data flows
  - `/catalog` - Browse tables/dashboards
  - `/chat` - Ask AI questions
  - `/health` - Service status

#### 3️⃣ Frontend UI

6 main pages:
1. **Search** - Semantic search across all assets
2. **Table Catalog** - Browse and filter tables
3. **Dashboard Catalog** - Discover dashboards
4. **Lineage Explorer** - Interactive graph visualization
5. **Chat Assistant** - AI-powered Q&A
6. **Asset Details** - Complete metadata for any asset

#### 4️⃣ Ingestion Pipeline

7 stages to populate databases:
1. Generate sample data in PostgreSQL
2. Extract table metadata
3. Ingest dashboard metadata
4. Parse Airflow DAGs
5. Generate lineage graphs in Neo4j
6. Create semantic embeddings
7. Generate markdown documentation

---

## Data Flow

### Flow 1: Initial Setup (One-Time)

```
1. Generate Sample Data
   └→ Insert 660K+ rows into PostgreSQL

2. Extract Metadata
   └→ Query PostgreSQL schema
   └→ Analyze tables and columns
   └→ Store metadata

3. Parse DAGs & Dashboards
   └→ Read configuration files
   └→ Extract structure

4. Generate Lineage
   └→ Parse SQL and DAG configs
   └→ Create relationships
   └→ Insert into Neo4j

5. Create Embeddings
   └→ Use Ollama to vectorize
   └→ Index in OpenSearch

6. Generate Documentation
   └→ Create markdown files
```

### Flow 2: User Search (Runtime)

```
User enters search query
    ↓
Frontend calls: POST /api/search?q=customer
    ↓
Backend queries OpenSearch
    ├─ Full-text search on table names
    ├─ Semantic search on descriptions
    └─ Combine and rank results
    ↓
OpenSearch returns matching documents
    ↓
Backend formats response
    ↓
Frontend renders result cards
    ↓
User sees search results
```

### Flow 3: Lineage Query (Runtime)

```
User selects table
    ↓
Frontend calls: GET /api/lineage/customer_dim?direction=downstream
    ↓
Backend queries Neo4j
    ├─ Find table node
    ├─ Traverse FEEDS_INTO relationships
    └─ Return all upstream/downstream tables
    ↓
Neo4j returns nodes and edges
    ↓
Backend converts to graph format
    ↓
Frontend renders interactive graph with Cytoscape.js
    ↓
User explores lineage visually
```

### Flow 4: Chat Query (Runtime)

```
User asks: "What feeds customer_fact?"
    ↓
Backend receives question
    ↓
Backend queries Neo4j for FEEDS_INTO relationships
    ↓
Neo4j returns upstream tables
    ↓
Backend calls Ollama with context
    ↓
Ollama generates human-readable response
    ↓
Frontend displays answer with source attribution
    ↓
User understands the data flow
```

---

## Backend Deep Dive

### FastAPI Basics

**What is FastAPI?**
A modern Python framework for building APIs. It's the middleware between your databases and frontend.

**Why FastAPI?**
- Fast: Built on async/await
- Modern: Uses Python 3.7+ features
- Type Safe: Built-in validation
- Auto Documentation: Swagger UI out of the box
- Easy to Learn: Clear, intuitive API

### Project Structure

```
backend/
├── app.py              ← Main FastAPI application
├── requirements.txt    ← Python dependencies
├── Dockerfile          ← Container configuration
├── api/
│   ├── __init__.py
│   ├── search.py      ← Search endpoints
│   ├── lineage.py     ← Lineage endpoints
│   ├── catalog.py     ← Catalog endpoints
│   ├── chat.py        ← Chat endpoints
│   └── health.py      ← Health check
├── models/
│   ├── __init__.py
│   ├── database.py    ← PostgreSQL connection
│   ├── vectordb.py    ← OpenSearch client
│   └── schemas.py     ← Pydantic models
├── services/
│   ├── __init__.py
│   └── (business logic layer)
└── utils/
    ├── __init__.py
    └── config.py      ← Configuration
```

### API Endpoint Groups

#### Search Group

```
GET /api/search?q=customer&type=table&limit=20
Returns: List[SearchResult]

GET /api/search/tables?q=customer
Returns: List[TableResult]

GET /api/search/dashboards?q=sales
Returns: List[DashboardResult]

GET /api/search/autocomplete?q=cust
Returns: List[str] (suggestions)
```

#### Lineage Group

```
GET /api/lineage/customer_dim?direction=downstream&depth=3
Returns: LineageGraph with nodes and edges

GET /api/lineage/path/raw_customers/sales_fact
Returns: Shortest path between two tables
```

#### Catalog Group

```
GET /api/tables
Returns: List[TableMetadata] (paginated)

GET /api/tables/customer_dim
Returns: Full table metadata with columns

GET /api/dashboards
Returns: List[DashboardMetadata] (paginated)

GET /api/dashboards/sales_dashboard
Returns: Full dashboard metadata

GET /api/ownership
Returns: Ownership mapping
```

#### Chat Group

```
POST /api/chat
Body: {query: string, context_assets: optional}
Returns: ChatResponse with answer and sources

POST /api/ask-about/table/customer_dim
Returns: AI explanation of the table
```

#### Health Group

```
GET /health
Returns: Service health status

GET /health/db
Returns: Database connectivity status
```

### Request-Response Pattern

```
Frontend Request:
{
  "method": "GET",
  "path": "/api/search",
  "query": {
    "q": "customer",
    "type": "table",
    "limit": 20
  }
}

Backend Processing:
1. Validate query parameters (FastAPI does this automatically with Pydantic)
2. Query OpenSearch
3. Format results
4. Enrich with metadata from PostgreSQL/Neo4j if needed

Response JSON:
{
  "status": "success",
  "count": 5,
  "results": [
    {
      "id": "customer_dim",
      "name": "customer_dim",
      "type": "table",
      "score": 0.95,
      "metadata": {
        "owner": "analytics-team",
        "row_count": 10000
      }
    }
  ]
}
```

---

## Frontend Deep Dive

### React Basics

**What is React?**
A JavaScript library for building user interfaces with components that update automatically when data changes.

**Why React?**
- Component-based: Reusable UI pieces
- Virtual DOM: Efficient updates
- Rich ecosystem: Tools and libraries
- Large community: Lots of help available
- TypeScript support: Type safety for JavaScript

### Project Structure

```
frontend/
├── Dockerfile
├── package.json        ← Dependencies and scripts
├── tsconfig.json       ← TypeScript configuration
└── src/
    ├── index.tsx       ← Entry point
    ├── App.tsx         ← Main app component with routing
    ├── pages/
    │   ├── Search.tsx           ← Search page
    │   ├── TableCatalog.tsx      ← Table browser
    │   ├── DashboardCatalog.tsx  ← Dashboard browser
    │   ├── LineageExplorer.tsx   ← Lineage graph
    │   ├── ChatAssistant.tsx     ← Chat interface
    │   └── AssetDetails.tsx      ← Detail pages
    ├── components/
    │   ├── SearchBar.tsx
    │   ├── LineageGraph.tsx      ← Cytoscape graph
    │   ├── MetadataCard.tsx
    │   ├── ChatMessage.tsx
    │   └── ...
    ├── services/
    │   ├── api.ts              ← API calls
    │   ├── search.ts           ← Search logic
    │   └── cache.ts            ← Caching
    ├── types/
    │   └── index.ts            ← TypeScript types
    ├── styles/
    │   ├── global.css
    │   └── components.css
    └── utils/
        ├── formatters.ts       ← Formatting helpers
        └── helpers.ts          ← Utility functions
```

### Key Pages Explained

#### 1. Search Page

```
[Search Bar with autocomplete]
     ↓
[Filter by Type dropdown]
     ↓
[Results Grid]
  - Each result is a card with:
    - Name
    - Type (table/dashboard/column)
    - Description
    - Owner
    - Relevance score
    - Click → Go to details
```

#### 2. Table Catalog

```
[Table Header: Name | Owner | Size | Last Updated]
     ↓
[Sortable List of Tables]
     ↓
[Click on table → See:]
  - Full column list with types
  - Related dashboards
  - Lineage graph
  - Data quality metrics
```

#### 3. Lineage Explorer

```
[Select table from dropdown or search]
     ↓
[Toggle: Upstream / Downstream / Both]
     ↓
[Interactive Graph Visualization]
  - Nodes: Tables, dashboards, jobs
  - Edges: Relationships with labels
  - Hover: See metadata
  - Click: Navigate to asset
  - Zoom/Pan: Explore large graphs
```

#### 4. Chat Assistant

```
[Message History Area]
     ↓
[Input Box: "Ask me about your data"]
     ↓
[Submit Button]
     ↓
[System displays:]
  - Question
  - Thinking... (loading state)
  - Answer
  - Sources (with links)
  - Confidence score
```

### Component Interaction

```
User clicks in Search Bar
    ↓
SearchBar component captures input
    ↓
Component calls api.search() service
    ↓
Service makes HTTP request to backend
    ↓
Backend returns results
    ↓
Component updates state with results
    ↓
React re-renders SearchResults component
    ↓
User sees results displayed
```

---

## Ingestion Pipeline

### What is the Ingestion Pipeline?

A series of Python scripts that populate the databases with metadata. It runs once during setup and can be re-run to refresh metadata.

### Stage 1: Generate Sample Data

**Script:** `01_generate_sample_data.py`

**What it does:**
- Creates realistic data in PostgreSQL
- Generates 10,000 customers
- Generates 5,000 products
- Generates 500,000 sales transactions
- Generates 100,000 orders
- Generates 50,000 inventory records

**Why realistic data?**
- Tests the system with production-like volume
- Shows performance characteristics
- Makes visualizations meaningful
- Demonstrates lineage at scale

### Stage 2: Extract Table Metadata

**Script:** `02_extract_table_metadata.py`

**What it does:**
- Connects to PostgreSQL
- Queries the information_schema (PostgreSQL's metadata)
- Extracts:
  - Table names and schemas
  - Column names and types
  - Column nullability
  - Row counts
  - Size on disk

**Why important?**
- Populates the catalog
- Powers search
- Used for lineage relationships
- Enables impact analysis

### Stage 3: Extract Dashboard Metadata

**Script:** `03_extract_dashboard_metadata.py`

**What it does:**
- Reads 20 dashboard JSON configuration files
- Extracts:
  - Dashboard name and description
  - Owner (which team)
  - Source tables (which tables does it query?)
  - Metrics and KPIs
  - Creation/update dates

**Why important?**
- Connects dashboards to source data
- Enables impact analysis ("if I drop this table, which dashboards break?")
- Shows data consumption patterns

### Stage 4: Parse DAG Metadata

**Script:** `04_parse_dag_metadata.py`

**What it does:**
- Reads 10 Airflow DAG Python files
- Extracts:
  - DAG ID and description
  - Owner (which team)
  - Schedule (daily? hourly?)
  - Task names and dependencies
  - Source and target tables

**Why important?**
- Shows data processing workflows
- Enables lineage tracing through ETL
- Shows job dependencies
- Helps understand refresh frequency

### Stage 5: Generate Lineage

**Script:** `05_generate_lineage.py`

**What it does:**
- Analyzes SQL files and DAG configs
- Creates relationships:
  - raw_customers → customer_dim (via customer_etl DAG)
  - customer_dim → sales_fact (used in transformation)
  - sales_fact → sales_dashboard (used in dashboard)
- Populates Neo4j with:
  - Table nodes
  - Relationship edges
  - Metadata on relationships

**Result in Neo4j:**
```
raw_customers ─FEEDS_INTO→ customer_dim ─FEEDS_INTO→ sales_fact ─USED_BY→ sales_dashboard
```

### Stage 6: Generate Embeddings

**Script:** `06_generate_embeddings.py`

**What it does:**
- For each asset (table, column, dashboard):
  1. Get description
  2. Call Ollama to generate vector embedding
  3. Store vector in OpenSearch

**Why important?**
- Enables semantic search ("find tables about money" → returns revenue-related tables)
- Makes search smarter
- Requires LLM intelligence

**Example:**
```
Input: "customer dimension table with customer details"
    ↓
Ollama processes
    ↓
Output: [0.123, 0.456, 0.789, ..., 0.234] (1024 numbers)
    ↓
Stored in OpenSearch for similarity search
```

### Stage 7: Generate Documentation

**Script:** `07_create_documentation.py`

**What it does:**
- Creates 50+ markdown files:
  - Table documentation (one file per table)
  - Data dictionary
  - Business glossary
  - Process documentation
  - Metric definitions

**Why important?**
- Provides human-readable documentation
- Searchable in OpenSearch
- Helps new team members understand data
- Version control friendly (markdown in git)

---

## Docker & Deployment

### What is Docker?

Docker is containerization software. Think of it as shipping containers for software:
- Each service (PostgreSQL, Neo4j, etc.) is packaged in a container
- Containers include all dependencies
- Containers run the same way on any machine

### Why Docker?

✅ **Reproducibility:** Same environment everywhere
✅ **Isolation:** Each service is isolated
✅ **Simplicity:** One command to start everything
✅ **Scalability:** Easy to add more instances
✅ **Cleanup:** Easy to remove everything

### Our Services

| Service | Image | Port | Purpose |
|---------|-------|------|---------|
| PostgreSQL | postgres:15-alpine | 5432 | Data warehouse |
| Neo4j | neo4j:5.18 | 7687, 7474 | Lineage graph |
| OpenSearch | opensearchproject/opensearch:2.11.1 | 9200 | Search engine |
| Ollama | ollama/ollama:latest | 11434 | Local LLM |
| Backend | Custom Python image | 8000 | FastAPI app |
| Frontend | Custom Node image | 3000 | React app |

### Docker Compose

**File:** `docker-compose.yml`

```yaml
version: '3.9'

services:
  postgres:
    image: postgres:15-alpine
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./data/sql:/docker-entrypoint-initdb.d
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U dataeng"]

  neo4j:
    image: neo4j:5.18-community
    ports:
      - "7687:7687"
      - "7474:7474"
    volumes:
      - neo4j_data:/var/lib/neo4j/data

  # ... more services

volumes:
  postgres_data:
  neo4j_data:
  # ... more volumes

networks:
  dip_network:
    driver: bridge
```

**Key Concepts:**
- **services:** Each container definition
- **ports:** Map container ports to host ports
- **volumes:** Persist data beyond container lifecycle
- **healthcheck:** Verify service is ready
- **networks:** Allow containers to communicate

---

## Setup Instructions

### Prerequisites

- Docker & Docker Compose installed
- 16GB RAM
- 20GB disk space
- ~15 minutes for first run

### Step-by-Step Setup

#### 1. Clone Repository

```bash
cd data-engineering-learning/data-intelligence-platform
```

#### 2. Create Environment File

```bash
cp .env.example .env
```

Edit `.env` if needed (defaults usually work fine):
```
POSTGRES_USER=dataeng
POSTGRES_PASSWORD=secure123
NEO4J_USER=neo4j
NEO4J_PASSWORD=secure123
```

#### 3. Start Services

```bash
bash scripts/startup.sh
```

This will:
- Pull Docker images
- Start all 6 services
- Wait for health checks
- Report when ready

**Expected output:**
```
✅ PostgreSQL is ready
✅ Neo4j is ready
✅ OpenSearch is ready
✅ Ollama is ready
✅ All services started!

📊 Access points:
   Frontend:     http://localhost:3000
   Backend API:  http://localhost:8000
   API Docs:     http://localhost:8000/docs
   Neo4j:        http://localhost:7474
   OpenSearch:   http://localhost:9200
```

#### 4. Run Ingestion

```bash
bash scripts/ingest.sh
```

This will:
- Generate 660K+ sample rows
- Extract metadata
- Create lineage
- Generate embeddings
- Take ~5 minutes

#### 5. Verify Installation

```bash
# Check services are running
docker-compose ps

# Test backend API
curl http://localhost:8000/health

# Open in browser
# Frontend: http://localhost:3000
# API Docs: http://localhost:8000/docs
```

### Troubleshooting

**Services not starting?**
```bash
# View detailed logs
docker-compose logs postgres
docker-compose logs neo4j
docker-compose logs opensearch

# Rebuild images
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

**High memory usage?**
Reduce in `docker-compose.yml`:
```yaml
opensearch:
  environment:
    OPENSEARCH_JAVA_OPTS: "-Xms1g -Xmx1g"  # Instead of 2g-4g
```

**Ollama not downloading model?**
```bash
# Pull manually
docker-compose exec ollama ollama pull llama3

# Check available models
docker-compose exec ollama ollama list
```

---

## Key Learnings

### Learning Path

**Week 1: Foundations**
- Understand the problem and solution
- Learn each database technology (SQL, Graph, Search, LLM)
- Understand REST APIs

**Week 2: Architecture**
- Study system architecture
- Trace data flows end-to-end
- Understand each component's role

**Week 3: Implementation**
- Deep dive into backend code
- Learn API design patterns
- Understand database schemas

**Week 4: Frontend & Operations**
- Study React components
- Learn Docker and containerization
- Understand deployment

### Knowledge Checkpoints

After each section, ask yourself:
✓ What problem does this component solve?
✓ How does it interact with other components?
✓ What are the key data structures?
✓ What are the main algorithms/logic?
✓ How would I explain this to a colleague?

### Common Mistakes to Avoid

❌ **Don't just read code**
✅ **Do:** Draw diagrams, explain out loud, modify code, trace examples

❌ **Don't memorize details**
✅ **Do:** Understand concepts and patterns

❌ **Don't skip the boring parts**
✅ **Do:** Understand configuration and setup—they're crucial for production

### Pro Tips

💡 **Read multiple times:** Each reading reveals new insights
💡 **Teach others:** Best way to solidify understanding
💡 **Build variations:** Modify the code and see what breaks
💡 **Document as you learn:** Reinforce your understanding

---

## Summary

You now have a complete understanding of the Data Intelligence Platform:

✅ **What it is:** A metadata discovery and lineage system
✅ **Why it exists:** Solve real data governance challenges
✅ **How it's built:** 4 databases + APIs + React UI + ingestion
✅ **How it works:** Data flows through layers
✅ **How to run it:** Docker Compose + scripts
✅ **How to modify it:** Clear separation of concerns

**Next Steps:**
1. Set up the project locally
2. Run the ingestion pipeline
3. Explore the UI
4. Study the code
5. Make modifications
6. Teach someone else

You're now ready to dive deep! 🚀
