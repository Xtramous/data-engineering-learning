# Data Engineering Architecture Design

## Executive Summary

This document outlines a modern, scalable data platform architecture designed for production-grade data processing, real-time analytics, and business intelligence. The architecture follows a medallion lakehouse pattern with clear separation of concerns, enabling data quality, governance, and scalability across all layers.

**Target Scale:** Up to 1TB/day throughput | **Latency:** Real-time (sub-second) to batch (hourly) | **Availability:** 99.9%

---

## 1. Architecture Overview

### High-Level Data Flow

```
Data Sources
    ↓
┌─────────────────────────────────────────────────┐
│ INGESTION LAYER (Real-time & Batch)             │
│ ├─ Kafka (streaming)                            │
│ ├─ Batch APIs (REST, webhooks)                  │
│ └─ File uploads (S3, local)                     │
└─────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────┐
│ BRONZE LAYER (Raw Data)                         │
│ ├─ Schema: Minimal validation                   │
│ ├─ Format: Parquet (partitioned by date)        │
│ ├─ Storage: Local filesystem (scalable to S3)   │
│ └─ Retention: 90 days                           │
└─────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────┐
│ SILVER LAYER (Cleaned & Deduplicated)           │
│ ├─ Schema: Explicit schemas with validation     │
│ ├─ Format: Parquet (columnar, compressed)       │
│ ├─ Quality: Data quality checks (GX framework)  │
│ └─ Retention: 1 year                            │
└─────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────┐
│ GOLD LAYER (Aggregated & Business Logic)        │
│ ├─ Schema: Business-domain specific             │
│ ├─ Format: Parquet + Iceberg (ACID support)     │
│ ├─ Structure: Star schema for analytics         │
│ └─ Retention: 5 years (compliance)              │
└─────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────┐
│ CONSUMPTION LAYER                               │
│ ├─ BI Tools (Dashboards, reports)               │
│ ├─ ML Pipelines (Feature engineering)           │
│ └─ APIs (REST endpoints for applications)       │
└─────────────────────────────────────────────────┘
```

---

## 2. Technology Stack

### Core Technologies

| Layer | Component | Technology | Rationale |
|-------|-----------|-----------|-----------|
| **Ingestion** | Streaming | Apache Kafka | Horizontal scalability, durability, replay capability |
| **Ingestion** | Batch | Airflow | Orchestration, retry logic, monitoring |
| **Processing** | Compute | Apache Spark | Distributed computing, SQL support, ecosystem |
| **Storage** | Data Lake | Parquet/Iceberg | Columnar format, compression, ACID (Iceberg) |
| **Transformation** | ELT Framework | dbt | Version control, testing, documentation, lineage |
| **Orchestration** | Workflow | Apache Airflow | DAG-based, rich monitoring, extensible |
| **Quality** | Data QA | Great Expectations | Declarative assertions, documentation |
| **Containerization** | Deployment | Docker | Reproducibility, scalability, environment parity |

---

## 3. Detailed Component Architecture

### 3.1 Ingestion Layer

#### Streaming (Kafka)
```
Producers
  ├─ Application logs
  ├─ User events
  └─ API webhooks
         ↓
    Kafka Cluster
  (3 brokers, replication=2)
         ↓
Consumers
  ├─ Spark Streaming (real-time processor)
  └─ Kafka Connect (to Bronze layer)
```

**Design Decisions:**
- **Topic partitioning:** By `tenant_id` or `source_system` (ensures ordering per source)
- **Retention:** 7 days (cost vs. replay capability tradeoff)
- **Replication factor:** 2 (durability with acceptable overhead)
- **Compression:** Snappy (balance of compression ratio and CPU)

#### Batch
```
External APIs / Files
         ↓
    Airflow DAGs
  (daily/hourly schedules)
         ↓
  Load to Bronze Layer
```

**Approach:**
- API calls → Pandas DataFrame → Parquet to Bronze
- File uploads → Spark read → Parquet to Bronze
- Retry logic: 3 attempts with exponential backoff

---

### 3.2 Storage Architecture

#### Medallion Lakehouse Pattern

**Bronze Layer (Raw)**
- Purpose: Immutable raw data store
- Schema: Minimal (source schema + ingestion metadata)
- Partitioning: `year=YYYY/month=MM/day=DD/hour=HH`
- Retention: 90 days (cost optimization)
- Compaction: Weekly (merge small files)
- Example path: `s3://lake/bronze/events/year=2026/month=06/day=11/events.parquet`

**Silver Layer (Cleaned)**
- Purpose: Single source of truth after cleaning
- Transformations:
  - Deduplication (by `unique_id`)
  - Schema validation
  - Type casting
  - Null handling
  - Outlier detection
- Partitioning: Same as Bronze
- Format: Parquet with snappy compression
- Quality: GX expectations for each table

**Gold Layer (Analytics Ready)**
- Purpose: Business-domain curated data
- Organization:
  - `gold/marts/finance/` - Financial metrics
  - `gold/marts/marketing/` - Campaign analytics
  - `gold/marts/operations/` - Operational metrics
- Schema: Star schema (facts + dimensions)
- Format: Iceberg tables (ACID compliance for updates)
- SLA: 99.9% availability

---

### 3.3 Processing Engine (Spark)

#### Spark Architecture
```
Spark Driver (orchestration)
         ↓
┌────────────────────────────┐
│  Executor 1  │ Executor 2  │ (Distributed processing)
├──────────────┼────────────┤
│  Task Task   │  Task Task │ (Parallelized workload)
└────────────────────────────┘
         ↓
    Distributed Storage
```

**Configuration:**
- **Master:** Local (development) → Spark Cluster (production)
- **Partitions:** Auto-detect, but min 4 per executor
- **Executor Memory:** 4GB (dev) → 16GB (prod)
- **Shuffle partitions:** 200 (adjust based on data volume)
- **Serialization:** Kryo (faster than default)

#### Processing Patterns
1. **ETL (Extract-Transform-Load)**
   - Bronze → Silver: Cleaning and deduplication
   - Silver → Gold: Aggregations and business logic

2. **Streaming (Real-time)**
   - Kafka → Spark Streaming → Silver (with micro-batch intervals)
   - Latency SLA: <5 minutes end-to-end

3. **Incremental Processing**
   - Use `__timestamp` or `__date` for incremental reads
   - Avoid full-table scans (unless necessary)

---

### 3.4 Transformation Framework (dbt)

#### Project Structure
```
dbt_project/
├── models/
│   ├── bronze/          (Raw data models, minimal transformation)
│   ├── silver/          (Cleaned data models, business rules)
│   └── gold/            (Analytics-ready models, aggregates)
├── tests/               (Data quality tests)
├── macros/              (Reusable SQL functions)
├── seeds/               (Reference data, CSV files)
├── documentation.md     (Lineage and metadata)
└── dbt_project.yml      (Configuration)
```

#### dbt Workflow
```
Raw Data (Bronze)
    ↓
dbt run (models execute in order)
    ↓
dbt test (data quality assertions)
    ↓
dbt docs (auto-generate documentation)
    ↓
Transformation Complete (lineage tracked)
```

**Key Features:**
- Version control (git) for all transformations
- Testing framework (uniqueness, not-null, relationships)
- Documentation auto-generation
- Lineage tracking (source → model → downstream)

---

### 3.5 Orchestration (Airflow)

#### DAG Structure
```
airflow_dags/
├── bronze_layer/
│   ├── kafka_to_bronze.py
│   └── api_to_bronze.py
├── silver_layer/
│   ├── bronze_to_silver.py
│   └── quality_checks.py
├── gold_layer/
│   ├── silver_to_gold.py
│   └── aggregations.py
└── utils/
    ├── spark_operators.py
    └── notifications.py
```

#### Example DAG Flow
```
start_task
    ↓
extract_from_kafka (Operator: Spark)
    ↓
load_to_bronze (Operator: SparkSubmitOperator)
    ↓
run_quality_checks (Operator: Python)
    ├─ [Success] → bronze_to_silver
    └─ [Failure] → notify_slack + retry
         ↓
    silver_to_gold
         ↓
    refresh_dashboards
         ↓
    end_task
```

**Configuration:**
- **Schedule:** Hourly (real-time) + daily batch (full refresh)
- **Retries:** 3 attempts with 5-minute backoff
- **Timeout:** 30 minutes per task
- **SLA:** 45 minutes (alert if not complete)
- **Monitoring:** Logs + custom metrics to DataDog/CloudWatch

---

### 3.6 Data Quality Framework

#### Great Expectations Setup

**Quality Checks by Layer:**

**Bronze Layer:**
- Row count validation (within 10% of expected)
- Null checks (identify unexpected nulls)
- Schema validation (data types match)

**Silver Layer:**
- Uniqueness (no duplicates on key columns)
- Referential integrity (FK relationships valid)
- Range checks (values within expected bounds)
- Freshness (latest record is within SLA)

**Gold Layer:**
- Completeness (no missing dates in time-series)
- Aggregate validation (sums match fact+dimension)
- Business rule compliance (derived metrics correct)

**Execution:**
```python
# In dbt tests (Silver layer example)
{{ assert_unique(table='events', column='event_id') }}
{{ assert_not_null(table='events', column='user_id') }}
{{ assert_accepted_values(table='events', column='event_type', 
                         values=['click', 'view', 'purchase']) }}
```

---

### 3.7 Containerization (Docker)

#### Docker Compose Setup
```yaml
services:
  kafka:
    image: confluentinc/cp-kafka:latest
    
  spark:
    build: ./docker/spark
    volumes:
      - ./data:/data
      - ./jobs:/jobs
    
  airflow:
    build: ./docker/airflow
    environment:
      - AIRFLOW_HOME=/airflow
    
  postgres:
    image: postgres:13
    (metadata database for Airflow)
```

**Benefits:**
- Reproducible environments (dev = prod)
- Easy scaling (docker-compose → Kubernetes)
- Version-controlled infrastructure

---

## 4. Data Flow Examples

### Example 1: User Event Pipeline

```
1. Mobile App generates event
   └─ POST /api/event {user_id, action, timestamp}

2. Event → Kafka topic "user_events"
   └─ Kafka partition by user_id (event ordering)

3. Spark Streaming (micro-batch every 60s)
   └─ Read from Kafka
   └─ Parse JSON, add ingestion_timestamp
   └─ Write to Bronze: s3://lake/bronze/events/

4. Airflow DAG (hourly)
   └─ Read Bronze events
   └─ Deduplicate by (user_id, timestamp)
   └─ Add data_quality_checks
   └─ Write to Silver: s3://lake/silver/events_cleaned/

5. dbt transformation (Silver → Gold)
   └─ Aggregate: user_daily_activity
   └─ Join with user_dim
   └─ Write to Gold: s3://lake/gold/user_analytics/

6. BI Dashboard consumes Gold
   └─ Real-time user activity visualization
```

### Example 2: Batch ETL (Daily Report)

```
1. Airflow DAG triggers at 02:00 UTC

2. Extract phase
   └─ Pull data from PostgreSQL API
   └─ Download CSV files from S3
   └─ Load to Bronze

3. Transform phase (Spark)
   └─ Join multiple sources
   └─ Aggregate by region/department
   └─ Apply business logic

4. Load phase
   └─ Write to Silver (cleaned)
   └─ Write to Gold (aggregated for dashboard)

5. Quality checks
   └─ Row count validation
   └─ Freshness check (records from last 24h)
   └─ Alert if SLA missed

6. Downstream
   └─ Trigger dashboard refresh
   └─ Send report email
   └─ Update ML feature store
```

---

## 5. Scalability & Performance

### Scaling Strategy

| Dimension | Current (Dev) | Production | Approach |
|-----------|---------------|-----------|----------|
| Data Volume | 1GB/day | 1TB/day | Repartition, optimize storage format |
| Throughput | 100 events/sec | 100K events/sec | Kafka partitions, Spark parallelism |
| Storage | Local disk | S3 (cloud) | Transition to cloud object storage |
| Compute | Single machine | Spark Cluster | Distributed computing |
| Orchestration | Local Airflow | Managed Airflow (Astronomer, Cloud Composer) | Managed services |

### Performance Optimization

**Storage:**
- Use Parquet (columnar, 10x compression vs CSV)
- Partition by date/tenant (prune irrelevant data)
- Use Iceberg for ACID + time-travel

**Compute:**
- Use Spark SQL (optimized planner) vs RDDs
- Cache intermediate results
- Broadcast small lookup tables

**Network:**
- Collocate compute and storage (same region)
- Use S3 Select (query without full download)

---

## 6. Monitoring & Observability

### Key Metrics

**Pipeline Health:**
- Task success rate (target: >99%)
- Pipeline duration (trend over time)
- Data freshness (lag between source and lake)
- Data quality score (% of checks passing)

**System Metrics:**
- CPU/Memory utilization
- Spark executor health
- Kafka consumer lag
- Airflow DAG duration

**Business Metrics:**
- Records processed (daily/hourly)
- End-to-end latency (source → dashboard)
- Data accuracy (validation checks)

### Alerting

```
Bronze Layer Data Freshness < 1 hour
  → Alert severity: Medium
  → On-call: Data Engineering

Silver Layer Quality Check Failure
  → Alert severity: High
  → On-call: Data Engineering + Analytics

Gold Layer Update Delay > 2 hours
  → Alert severity: High
  → On-call: Data Engineering + BI team
```

---

## 7. Security & Governance

### Access Control
- **Bronze:** Read-only for authorized services
- **Silver:** Read access for data analysts
- **Gold:** Public read access (business users)

### Data Governance
- **Lineage:** Tracked through dbt documentation
- **Glossary:** Business term definitions (dbt docs)
- **Retention:** Enforce via S3 lifecycle policies
- **Compliance:** GDPR (delete user data on request)

### Encryption
- At rest: S3 SSE-S3 (or KMS for sensitive data)
- In transit: TLS for all communications
- In application: Mask PII in logs

---

## 8. Disaster Recovery & SLA

### RTO/RPO Targets
| Scenario | RTO | RPO |
|----------|-----|-----|
| Single node failure | 5 minutes | 0 (Kafka replay) |
| Data corruption | 24 hours | 24 hours (previous day backup) |
| Complete outage | 4 hours | <1 hour (S3 versioning) |

### Backup Strategy
- **Bronze/Silver:** S3 versioning (30-day history)
- **Gold:** S3 cross-region replication
- **Metadata:** Daily Airflow database snapshots

---

## 9. Technology Evolution Roadmap

### Phase 1 (Current): Single Machine Development
- Local Spark, local Airflow
- Kafka in Docker
- Parquet on local filesystem

### Phase 2 (Month 2): Cloud Migration
- AWS S3 for storage
- EC2 for Spark clusters
- RDS for metadata
- CloudWatch for monitoring

### Phase 3 (Month 3): Production Hardening
- Kubernetes for orchestration
- Managed Airflow (AWS MWAA)
- Data Warehouse (Redshift/BigQuery) for analytics
- ML pipeline integration

---

## 10. Development Workflow

### Local Development
```bash
# 1. Spin up local stack
docker-compose up

# 2. Submit Spark job
spark-submit --master local[4] jobs/bronze_to_silver.py

# 3. Run dbt transformations
dbt run -s silver.* --select state:modified+

# 4. Validate data quality
dbt test

# 5. Push to GitHub
git add . && git commit -m "feat: add user event pipeline"
git push origin feature/user-events
```

### CI/CD
- Branch protection: All changes require code review
- Automated tests: dbt test + data quality checks
- Staging environment: Separate dbt profiles for staging vs production

---

## Summary: Decision Rationale

| Decision | Why |
|----------|-----|
| **Kafka for streaming** | Durability, scalability, replay capability |
| **Spark for processing** | SQL support, distributed computing, ecosystem |
| **dbt for transformation** | Version control, testing, documentation, lineage |
| **Medallion pattern** | Clear separation of concerns, data quality at each layer |
| **Parquet/Iceberg** | Compression, ACID support, columnar query efficiency |
| **Airflow for orchestration** | Rich monitoring, retry logic, dependency management |
| **Docker for deployment** | Reproducibility, easy scaling, environment parity |

---

**Document Version:** 1.0  
**Last Updated:** 2026-06-11  
**Next Review:** 2026-07-11
