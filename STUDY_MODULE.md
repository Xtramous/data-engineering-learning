# Data Engineering Study Module - Complete Learning Guide

**30-Day Intensive Program | Full-Stack Data Engineer | Staff-Level Capabilities**

---

## Part 1: Core Concepts & Architecture

### 1.1 Medallion Lakehouse Pattern (Understanding the Foundation)

The medallion pattern organizes data into three layers:

```
Raw Data (Any Source)
        ↓
┌──────────────────────┐
│  BRONZE LAYER        │
│  (Raw Data Store)    │
│  ✓ Minimal cleaning  │
│  ✓ Full fidelity     │
│  ✓ Source schema     │
│  ✓ Append-only       │
└──────────────────────┘
        ↓ (Transform)
┌──────────────────────┐
│  SILVER LAYER        │
│  (Cleaned Data)      │
│  ✓ Deduplicated      │
│  ✓ Validated         │
│  ✓ Business schema   │
│  ✓ Quality gates     │
└──────────────────────┘
        ↓ (Aggregate)
┌──────────────────────┐
│  GOLD LAYER          │
│  (Analytics Ready)   │
│  ✓ Aggregated        │
│  ✓ Dimensional       │
│  ✓ Business metrics  │
│  ✓ High performance  │
└──────────────────────┘
        ↓
   BI/Analytics/ML
```

**Why This Pattern?**
- **Separation of Concerns:** Each layer has one responsibility
- **Quality Gates:** Catch issues early (Bronze → Silver)
- **Recovery:** Corrupted Gold? Regenerate from Silver
- **Scalability:** Each layer can be optimized independently
- **Governance:** Track lineage (source → analytics)

---

### 1.2 Data Pipeline Fundamentals

#### Three Types of Data Processing

**1. Batch Processing (Scheduled)**
```
Data accumulates → Scheduled time → Process all at once → Results

Example: Daily report at 2 AM
- Input: 1 day of accumulated events
- Processing: 30 minutes
- Output: Yesterday's metrics
- Latency: 26+ hours

When to use: Reports, aggregations, non-urgent analytics
```

**2. Streaming Processing (Real-time)**
```
Data arrives → Process immediately → Results in real-time

Example: Real-time dashboard
- Input: Events as they happen
- Processing: Continuous
- Output: Metrics updated every second
- Latency: <1 second

When to use: Dashboards, alerts, fraud detection
```

**3. Hybrid (Batch + Streaming)**
```
Real-time: Dashboard updates every second
Batch: Daily aggregations, reports, ML training

Best of both worlds!

When to use: Production systems (most use this)
```

---

### 1.3 Data Formats & Storage

#### Parquet (Columnar Format)

Why Parquet instead of CSV?

```
CSV (Row-based):
name,age,city
Alice,30,NYC
Bob,25,LA
Charlie,35,NYC

✓ Human readable
✗ Large file size (text overhead)
✗ Slow queries (must read entire rows)
✗ Can't compress well


PARQUET (Columnar):
Column1 (names): [Alice, Bob, Charlie]
Column2 (ages): [30, 25, 35]
Column3 (cities): [NYC, LA, NYC]

✓ Compact (column compression)
✓ Fast queries (read only needed columns)
✓ Compression built-in (10x smaller than CSV)
✓ Type safety (schema enforcement)
```

**File Size Example:**
```
100MB CSV → 10MB Parquet (10x compression!)
```

**Query Performance:**
```
CSV: "Find average age" → Read all rows (100MB)
Parquet: "Find average age" → Read only age column (1MB)
Speed improvement: 100x faster!
```

---

### 1.4 Partitioning Strategy

Why partition data?

```
Problem: 5TB of events data
- Query: "Get events from June 11"
- Without partitioning: Read all 5TB to find June data (slow!)
- With partitioning: Read only June folder (~20GB)
- Speed: 250x faster!

Partitioning Structure:
s3://bucket/events/
├── year=2026/
│   └── month=06/
│       ├── day=10/
│       │   └── hour=*/events.parquet
│       ├── day=11/
│       │   └── hour=*/events.parquet
│       └── day=12/
│           └── hour=*/events.parquet
└── year=2025/
    └── ... (previous year)

When querying for day=11:
Spark automatically reads only day=11 folder
Result: 250x speed improvement, same code!
```

**Partitioning Best Practices:**
- Partition by time (year, month, day, hour)
- Add tenant_id if multi-tenant (separate data cleanly)
- Avoid too many partitions (<10,000 per table)
- Don't partition by high-cardinality columns (e.g., user_id)

---

## Part 2: Technology Deep Dives

### 2.1 Apache Spark

#### What is Spark?

Distributed data processing engine. Think of it as:

```
Traditional Python:
data = read_csv("data.csv")  # Loads in memory (limited by RAM)
result = process(data)
write_csv(result, "output.csv")

Spark:
df = spark.read.parquet("data.parquet")  # Lazy (doesn't load yet)
df = df.filter(df.age > 30)              # Lazy (builds plan)
df = df.groupBy("city").count()          # Lazy (builds plan)
df.write.parquet("output")               # Trigger (executes plan)

Advantages:
✓ Distributed (100 machines process in parallel)
✓ Lazy evaluation (optimized execution plan)
✓ Works with 100TB+ (not limited by RAM)
✓ SQL support (like database queries)
```

#### Spark Architecture

```
Driver (Your Laptop)
├─ Maintains SparkSession
├─ Plans execution
└─ Collects results

        ↓ (Task distribution)

Executors (4 on your laptop, 1000 in cloud)
├─ Execute tasks in parallel
├─ Each has 4GB RAM, 4 cores
└─ Return results to driver
```

#### Key Spark Concepts

**1. RDD vs DataFrame**
```
RDD (Resilient Distributed Dataset):
- Low-level, unstructured
- df_rdd = spark.sparkContext.parallelize(data)
- Use: Almost never in modern Spark

DataFrame (Structured):
- High-level, like SQL table
- df = spark.read.parquet("data.parquet")
- Use: 99% of the time (optimized, fast)
```

**2. Lazy Evaluation**
```
# These don't execute immediately:
df = spark.read.parquet("data")        # Lazy
df = df.filter(df.age > 30)            # Lazy
df = df.select("name", "age")          # Lazy

# This TRIGGERS execution:
df.show()                              # Execute!
df.write.parquet("output")             # Execute!
result = df.collect()                  # Execute!
```

**3. Transformations vs Actions**
```
Transformation (Lazy):
- map(), filter(), select(), join(), groupBy()
- Builds execution plan
- Cost: $0 (nothing happens yet)

Action (Triggers Execution):
- show(), write(), collect(), count(), first()
- Executes the plan
- Cost: Time, compute

Remember: Transformations are free (no execution), 
Actions cost money (actual execution)
```

#### Common Spark Operations

```python
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("my_app").getOrCreate()

# Read
df = spark.read.parquet("bronze/events")

# Transform
df = df.filter(df.event_type == "click")           # Filter rows
df = df.select("user_id", "timestamp", "value")    # Select columns
df = df.withColumn("date", to_date(df.timestamp))  # Add column
df = df.dropDuplicates(["event_id"])               # Remove duplicates

# Aggregate
df = df.groupBy("user_id").agg(count("*").alias("event_count"))

# Join
df_users = spark.read.parquet("bronze/users")
df = df.join(df_users, "user_id")

# Write
df.write.mode("overwrite").parquet("silver/events_clean")
```

---

### 2.2 Apache Kafka

#### What is Kafka?

Event streaming platform. Think of it as:

```
Traditional API:
POST /api/event {user_id: 123, action: "click"}
→ Direct to database
→ Other systems miss data before processing

Kafka:
1. Event → Kafka Topic
2. Kafka stores event (durable)
3. Multiple systems read from Kafka:
   - System A: Real-time dashboard
   - System B: Data lake (Bronze)
   - System C: ML feature store
   - All get the same event
```

#### Kafka Concepts

```
Producer (sends events):
├─ Your app: POST /event → Kafka

Topic (event stream):
├─ "user.events" (all user activity)
├─ "orders" (all purchase events)
└─ "payments" (all payment events)

Partition (parallel processing):
├─ Topic: "user.events"
├─ Partition 0: events from user_id 0-999
├─ Partition 1: events from user_id 1000-1999
├─ Partition 2: events from user_id 2000-2999
└─ Consumer processes each partition in parallel

Consumer (reads events):
├─ Spark Streaming
├─ Data pipeline
└─ Multiple consumers can read same topic

Retention (durability):
├─ Keep events for 7 days
├─ Can replay events (reprocess history)
└─ Built-in fault tolerance
```

#### Partitioning Strategy in Kafka

```
Event Flow:
user_id=123 → hash → partition_0
user_id=456 → hash → partition_1
user_id=789 → hash → partition_0

Result: All events from user_id=123 go to partition_0
Benefit: Can reconstruct user session in order!
```

---

### 2.3 dbt (Data Build Tool)

#### What is dbt?

SQL-based transformation framework with:
- Version control (Git)
- Testing (data quality)
- Documentation (auto-generated)
- Lineage (source → model → downstream)

#### dbt Philosophy

```
Traditional SQL:
1. Write 100 SQL queries (scattered in folders)
2. Hope they work (no tests)
3. No documentation
4. No version history
5. Can't reuse code

dbt Approach:
1. Write 100 models (organized, tested)
2. Automatic documentation
3. Git version control
4. Data quality tests included
5. Macros (reusable functions)
```

#### dbt Project Structure

```
dbt_project/
├── dbt_project.yml         (project config)
├── models/
│   ├── bronze/
│   │   ├── events.sql      (raw events from Kafka)
│   │   └── users.sql       (raw users from API)
│   ├── silver/
│   │   ├── events_clean.sql (deduplicated, validated)
│   │   └── users_clean.sql
│   └── gold/
│       ├── user_metrics.sql (aggregated for analytics)
│       └── revenue_daily.sql
├── tests/
│   ├── assert_unique_event_id.sql
│   └── assert_not_null.sql
└── macros/
    └── generate_alias.sql  (reusable functions)
```

#### dbt Models

```sql
-- models/silver/events_clean.sql
{{ config(materialized='table') }}

SELECT
  event_id,
  user_id,
  event_type,
  timestamp,
  value,
  CURRENT_TIMESTAMP as ingestion_timestamp
FROM {{ source('bronze', 'events') }}
WHERE event_id IS NOT NULL
  AND timestamp >= DATE_SUB(CURRENT_DATE(), 1)
QUALIFY ROW_NUMBER() OVER (PARTITION BY event_id ORDER BY timestamp) = 1
```

Key dbt Features:
- `{{ source('bronze', 'events') }}` - Reference bronze table (linked)
- `QUALIFY ROW_NUMBER()...` - Deduplication
- `config(materialized='table')` - Store as table (not view)

#### dbt Testing

```yaml
# models/silver/events_clean.yml
models:
  - name: events_clean
    columns:
      - name: event_id
        tests:
          - unique       # No duplicates
          - not_null     # Every row has event_id
      - name: event_type
        tests:
          - accepted_values:
              values: ['click', 'view', 'purchase']
```

When you run `dbt test`, it checks:
- ✓ event_id is unique
- ✓ event_id is not null
- ✓ event_type is one of ['click', 'view', 'purchase']

---

### 2.4 Apache Airflow

#### What is Airflow?

Workflow orchestration (scheduling + monitoring).

```
Problem: Run Spark job daily at 2 AM
- What if it fails? Retry?
- What if it takes too long? Alert?
- How do you track all jobs? Manual?

Airflow Solution:
DAG (Directed Acyclic Graph) = workflow definition

DAG Example:
extract_from_api
    ↓ (depends on extraction)
load_to_bronze
    ↓ (depends on loading)
run_quality_checks
    ├─ [Success] → bronze_to_silver
    └─ [Failure] → send_slack_alert
         ↓
    refresh_dashboards
         ↓
    send_email_report
```

#### Airflow Concepts

**DAG** - Directed Acyclic Graph
```
Nodes = Tasks
Edges = Dependencies

Task 1 → Task 2 → Task 3 (sequential)
Task 1 → Task 2 ─┐
         Task 3 ─┴─→ Task 4 (parallel then merge)
```

**Operators** - Task types
```
BashOperator    → Run bash command
PythonOperator  → Run Python function
SparkOperator   → Submit Spark job
S3Operator      → Interact with S3
EmailOperator   → Send email
```

**Scheduling**
```
@daily          → Run every day at midnight
@hourly         → Run every hour
0 2 * * *       → Run at 2 AM daily (cron)
```

**Retry Logic**
```
task = BashOperator(
    task_id='my_task',
    bash_command='...',
    retries=3,                    # Try 3 times
    retry_delay=timedelta(minutes=5)  # Wait 5 min between retries
)
```

---

### 2.5 Docker & Containerization

#### Why Docker?

```
Problem: "Works on my laptop but not in production"
Reason: Different OS, different Python version, different libraries

Docker Solution:
Package app + dependencies + OS in a container

Your Laptop:
├─ Ubuntu 22.04
├─ Python 3.11
├─ Spark 3.4.0
└─ Kafka 3.5.0

Production:
├─ Ubuntu 22.04
├─ Python 3.11
├─ Spark 3.4.0
└─ Kafka 3.5.0

Same environment = works the same!
```

#### Docker Compose

Define multiple containers:

```yaml
version: '3'
services:
  # Kafka
  kafka:
    image: confluentinc/cp-kafka:latest
    environment:
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
    
  # Spark
  spark:
    build: ./docker/spark
    volumes:
      - ./data:/data
    
  # Airflow
  airflow:
    image: apache/airflow:latest
    environment:
      AIRFLOW_HOME: /airflow
```

One command spins everything up:
```bash
docker-compose up
# Kafka running
# Spark running
# Airflow running
# All networked together
```

---

## Part 3: Data Quality & Governance

### 3.1 Great Expectations

Data quality validation framework.

```
Problem: Data arrives, you process it, insights wrong
Cause: Null values, duplicates, wrong types, outliers

Great Expectations Solution:
Define what "good data" looks like
Validate before processing

Bad data:
  → Alert & fail pipeline (don't process garbage)
  
Good data:
  → Continue processing
```

#### Types of Expectations

```python
# Table-level
expect_table_row_count_to_be_between(min_value=1000, max_value=1000000)
expect_table_columns_to_match_ordered_list(column_list=['id', 'name', 'age'])

# Column-level
expect_column_values_to_not_be_null('event_id')
expect_column_values_to_be_unique('event_id')
expect_column_values_to_be_in_set(['click', 'view', 'purchase'])
expect_column_values_to_be_between(column='age', min_value=0, max_value=150)

# Multi-column
expect_compound_columns_to_be_unique(['user_id', 'timestamp'])
```

---

### 3.2 Data Quality Strategy

By Layer:

**Bronze Layer** (Minimal checks)
```
- Row count validation (10% variance acceptable)
- Schema validation (correct data types)
- Null checks (expected nulls vs unexpected)
- Freshness (data should be recent)
```

**Silver Layer** (Strict checks)
```
- Uniqueness on key columns (no duplicates)
- Referential integrity (FK relationships valid)
- Range checks (values in expected bounds)
- Business logic validation
```

**Gold Layer** (Aggregate checks)
```
- Completeness (no missing dates in time series)
- Consistency (facts match dimensions)
- Accuracy (derived metrics match calculations)
```

---

## Part 4: Performance & Optimization

### 4.1 Spark Optimization Principles

#### 1. Partitioning

```python
# Bad: 1 partition, 1 executor works, others idle
df = spark.read.parquet("data")
df.write.parquet("output")  # 1 task runs

# Good: 100 partitions, 8 executors work in parallel
df = spark.read.parquet("data")
df = df.repartition(100)
df.write.parquet("output")  # 100 tasks run in parallel
```

**Partition count rule:**
```
Number of partitions = CPU cores × 3 to 4
(Allows load balancing, some variance)
```

#### 2. Caching

```python
# Without cache: Read source 3 times
df = spark.read.parquet("source")
count1 = df.count()  # Read source
count2 = df.filter(...).count()  # Read source again!
count3 = df.select(...).count()  # Read source again!

# With cache: Read source 1 time
df = spark.read.parquet("source")
df.cache()  # Keep in memory
count1 = df.count()  # Read source
count2 = df.filter(...).count()  # Use cache
count3 = df.select(...).count()  # Use cache
df.unpersist()  # Free memory when done
```

#### 3. Broadcast Join

```python
# Without broadcast: Network shuffle (expensive!)
users = spark.read.parquet("large_user_table")     # 100GB
orders = spark.read.parquet("order_table")         # 50GB
result = orders.join(users, "user_id")             # Shuffle both!

# With broadcast: Send small table to all executors (fast!)
users = spark.read.parquet("small_lookup_table")   # 100MB
orders = spark.read.parquet("order_table")         # 50GB
from pyspark.sql.functions import broadcast
result = orders.join(broadcast(users), "user_id")  # No shuffle!

Rule: Broadcast if one table < 1GB
```

---

## Part 5: System Design Patterns

### 5.1 Slowly Changing Dimensions (SCD Type 2)

Track dimension changes over time.

```
User dimension changes:
- 2026-01-01: Alice lives in NYC
- 2026-06-01: Alice moves to LA

SCD Type 2 (track history):
┌─────────────┬──────┬────┬──────────────┬──────────────┐
│ user_id     │ name │ city│ valid_from   │ valid_to     │
├─────────────┼──────┼────┼──────────────┼──────────────┤
│ 123         │ Alice│ NYC│ 2026-01-01   │ 2026-05-31   │
│ 123         │ Alice│ LA │ 2026-06-01   │ 9999-12-31   │
└─────────────┴──────┴────┴──────────────┴──────────────┘

When joining facts with dimensions:
SELECT * FROM orders o
JOIN users u ON o.user_id = u.user_id 
               AND o.order_date BETWEEN u.valid_from AND u.valid_to
→ Each order joins with correct user address on that date
```

### 5.2 Late-Arriving Dimensions

Fact arrives before dimension.

```
Order arrived at 2026-06-11 10:00 AM
User dimension updated at 2026-06-11 2:00 PM (late!)

Solution:
1. Insert fact with unknown dimension key (e.g., -1)
2. Later, update fact when dimension arrives
3. Ensure JOIN includes update records
```

---

## Part 6: Monitoring & Operations

### 6.1 Key Metrics

**Pipeline Health:**
- Task success rate: Target >99%
- Pipeline duration: Trend over time (detect slowdowns)
- Data freshness: Lag between source and lake
- Quality score: % of checks passing

**System Metrics:**
- CPU/Memory utilization
- Spark executor health
- Kafka consumer lag
- Disk usage

**Business Metrics:**
- Records processed (daily/hourly)
- Processing cost per record
- End-to-end latency

### 6.2 Alerting Strategy

```
Severity 1 (Critical):
- Pipeline failure
- Data corruption detected
- Quality check < 80%
Action: Page on-call engineer immediately

Severity 2 (Warning):
- Task running >2x normal time
- Disk usage >80%
- Quality check < 95%
Action: Email alert, investigate within 1 hour

Severity 3 (Info):
- Task completed
- Metrics updated
- Drift detected
Action: Log, check in morning standup
```

---

## Part 7: Common Patterns & Anti-Patterns

### 7.1 Good Patterns

✅ **One tool per responsibility**
- Kafka for ingestion
- Spark for processing
- dbt for transformation
- Airflow for orchestration

✅ **Immutable bronze layer**
- Never modify raw data
- Always append-only
- Can replay from source

✅ **Test data quality early**
- Bronze layer: Minimal tests
- Silver layer: Strict tests
- Fail fast, don't process bad data

✅ **Monitor everything**
- Track metrics at each layer
- Alert on anomalies
- Build trust in data

### 7.2 Anti-Patterns (Avoid!)

❌ **Processing data without validation**
- "If it's in the system, it must be good"
- Reality: Lots of bad data sneaks in
- Solution: Always validate

❌ **Modifying bronze layer**
- "We'll fix data at the source"
- Reality: Lost ability to replay
- Solution: Immutable bronze, clean in silver

❌ **No monitoring**
- "Code works locally, so it works in production"
- Reality: Data quality issues show up weeks later
- Solution: Comprehensive monitoring & alerts

❌ **One huge pipeline**
- "One job does everything"
- Reality: Debugging nightmare
- Solution: Small, focused jobs with clear boundaries

---

## Part 8: Troubleshooting Guide

### Common Issues & Solutions

**Spark Memory Error:**
```
Error: Cannot allocate X memory
Cause: Too much data for executor RAM
Solution: 
  1. Increase partitions (smaller chunks)
  2. Increase executor memory (in config)
  3. Cache intermediate results
```

**Kafka Consumer Lag:**
```
Lag = messages behind latest
Issue: Consumer slower than producer
Solution:
  1. Increase consumer parallelism
  2. Increase batch size
  3. Profile code (find bottleneck)
```

**dbt Model Compilation Error:**
```
Error: Undefined relation
Cause: Referenced table doesn't exist
Solution:
  1. Check source definitions
  2. Run upstream models first
  3. Check materialization (table vs view)
```

**Airflow Task Timeout:**
```
Error: Task exceeded timeout
Cause: Task takes too long
Solution:
  1. Optimize underlying Spark job
  2. Increase timeout value
  3. Split into smaller tasks
```

---

## Part 9: Interview Preparation Questions

### Technical Questions (Study These!)

**1. Explain medallion pattern**
- Bronze, Silver, Gold layers
- Why each exists
- Trade-offs

**2. What's the difference between batch and streaming?**
- Latency vs complexity
- When to use each
- Hybrid approach

**3. How would you handle late-arriving data?**
- SCD Type 2
- Windowing
- Watermarking

**4. Design a data pipeline for X**
- Approach: Requirements → Architecture → Implementation
- Mention: Data quality, monitoring, scalability
- Discuss: Trade-offs

**5. What's your optimization story?**
- Identify bottleneck
- Apply optimization
- Measure improvement
- Document learnings

---

## Part 10: Quick Reference Cheat Sheet

### Spark Cheat Sheet
```python
# Read
df = spark.read.parquet("path")
df = spark.read.option("header", True).csv("file.csv")

# Transform
df = df.filter(df.col > 10)
df = df.select("col1", "col2")
df = df.dropDuplicates()

# Aggregate
df = df.groupBy("col1").agg(count("col2"))

# Window functions
from pyspark.sql.window import Window
w = Window.partitionBy("col1").orderBy("col2")
df = df.withColumn("rank", row_number().over(w))

# Write
df.write.mode("overwrite").parquet("output")
```

### dbt Cheat Sheet
```bash
dbt init my_project           # Create project
dbt run                       # Build all models
dbt run -s model_name        # Build specific model
dbt test                      # Run all tests
dbt docs generate            # Create documentation
dbt freshness                # Check source freshness
```

### Airflow Cheat Sheet
```python
from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

dag = DAG('my_dag', start_date=datetime(2026, 1, 1))

task1 = BashOperator(
    task_id='task1',
    bash_command='echo "Hello"',
    dag=dag
)

task1 >> task2  # Dependency
```

---

## Part 11: Learning Resources

### Official Documentation
- [Apache Spark](https://spark.apache.org/docs/latest/)
- [dbt Docs](https://docs.getdbt.com/)
- [Apache Airflow](https://airflow.apache.org/docs/)
- [Apache Kafka](https://kafka.apache.org/documentation/)

### Hands-On Resources
- Build projects (this course!)
- Read code on GitHub
- Write blog posts
- Teach others

### Key Insight
**Best learning = Building real systems**

This 30-day plan emphasizes doing, not just reading. Each day:
1. Understand concept (read this module)
2. Build something (hands-on)
3. Test it (verify it works)
4. Document it (teach others)
5. Commit to git (track progress)

---

## How to Use This Module

**Daily Workflow:**
1. Find your day (1-30)
2. Check "Learning Objective" in 30DAY_LEARNING_PLAN.md
3. Come back here, find relevant section
4. Read the concept
5. Apply it in code
6. Check your understanding

**Weekly Review:**
1. Reread sections you struggled with
2. Explain concepts out loud (rubber duck debugging)
3. Write them in your own words
4. Teach someone else (or pretend to)

**Troubleshooting:**
- Got an error? Check "Troubleshooting Guide" (Part 8)
- Forgot a command? Check "Quick Reference" (Part 10)
- Need to understand why? Check relevant part (1-7)

---

**Remember:** You're not just learning tools. You're learning how to think about data engineering problems. That's the staff-level skill.

Ready to apply this? Let's build! 🚀
