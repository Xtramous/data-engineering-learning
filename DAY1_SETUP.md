# Day 1: Architecture Deep Dive & Local Setup

**Date:** 2026-06-12  
**Duration:** 6-8 hours  
**Goal:** Understand architecture, set up local environment, get everything running

---

## Part 1: Understanding the Architecture (2 hours)

### Step 1: Read the Architecture Documents

Read these in order (take notes!):

1. **ARCHITECTURE.md** - Complete architecture design
   - Focus on: Medallion pattern, tech stack, data flow
   - Time: 45 minutes
   - Key question: "Why three layers instead of two?"

2. **STUDY_MODULE.md - Part 1 & 2** - Concepts and Kafka
   - Focus on: Medallion pattern, Spark basics, Kafka concepts
   - Time: 45 minutes
   - Key question: "What's the difference between batch and streaming?"

3. **30DAY_LEARNING_PLAN.md** - Your roadmap
   - Review: What you'll build over 30 days
   - Time: 15 minutes
   - Key question: "What does success look like on Day 30?"

### Step 2: Test Your Understanding

Answer these questions (no cheating by re-reading!):

1. What are the three layers in medallion pattern and what's the purpose of each?
2. Why use Parquet instead of CSV?
3. What's the difference between batch and streaming data processing?
4. Why do we need Kafka if Spark can read directly from APIs?
5. What's the role of dbt in the architecture?

**If you can answer 4/5, you understand enough to proceed!** ✅

---

## Part 2: Setting Up Local Environment (3-4 hours)

### Step 1: Install Prerequisites

```bash
# Verify Docker is installed
docker --version
# Should show: Docker version 24.0.0+ (or similar)

# Verify Docker Compose is installed
docker-compose --version
# Should show: Docker Compose version 2.20.0+ (or similar)
```

If not installed, follow official installation guides.

### Step 2: Start Docker Services

```bash
# Navigate to your project
cd ~/code/projects/data-engineering

# Start all services (Kafka, Spark, Airflow, PostgreSQL)
docker-compose up -d

# Check status
docker-compose ps
# Should show: all services UP

# Watch logs (optional, helpful for debugging)
docker-compose logs -f
# Press Ctrl+C to exit
```

**Expected output:**
```
NAME              STATUS
postgres          Up (healthy)
zookeeper         Up (healthy)
kafka             Up (healthy)
spark             Up (healthy)
airflow           Up (healthy)
```

### Step 3: Verify Each Service

#### Test PostgreSQL
```bash
docker exec postgres psql -U airflow -d airflow -c "SELECT 1;"
# Should return: 1
```

#### Test Zookeeper
```bash
docker exec zookeeper echo ruok | nc localhost 2181
# Should return: imok
```

#### Test Kafka
```bash
docker exec kafka kafka-topics.sh --bootstrap-server localhost:9092 --list
# Should return: (no errors, empty list ok)
```

#### Test Spark
```bash
curl http://localhost:8080
# Should return HTML (Spark UI)
```

#### Test Airflow
```bash
curl http://localhost:8081
# Should return HTML (Airflow UI)
# Access in browser: http://localhost:8081
# Login: admin / admin
```

### Step 4: Create Test Topics in Kafka

```bash
# Create test topic
docker exec kafka kafka-topics.sh \
  --bootstrap-server localhost:9092 \
  --create \
  --topic test_topic \
  --partitions 3 \
  --replication-factor 1

# Verify it exists
docker exec kafka kafka-topics.sh \
  --bootstrap-server localhost:9092 \
  --list

# Should show: test_topic
```

---

## Part 3: Verify Everything Works (1 hour)

### Test 1: Run Sample Spark Job

```bash
# Submit the CSV to Parquet job
docker exec spark spark-submit \
  --master local[4] \
  /jobs/csv_to_parquet.py

# Expected output:
# ✅ Read 20 rows from CSV
# ✅ Successfully wrote to /data/bronze/events
# 🎉 SUCCESS: CSV → Parquet transformation complete!
```

### Test 2: Verify Output Files

```bash
# Check if Parquet files were created
ls -la /Users/nitinkamal/code/projects/data-engineering/data/bronze/events/

# Should show: .parquet files (not human-readable, that's ok!)
```

### Test 3: Read Parquet with Spark

```bash
# Create a quick test script
cat > /tmp/read_test.py << 'EOF'
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("read_test").getOrCreate()
df = spark.read.parquet("/data/bronze/events")
print(f"✅ Read {df.count()} rows from Parquet")
df.show()
EOF

# Run it
docker exec -v /tmp/read_test.py:/tmp/read_test.py spark \
  spark-submit --master local[4] /tmp/read_test.py

# Should show: 20 rows
```

---

## Part 4: Troubleshooting

### Issue: Docker service won't start

```bash
# Check logs
docker-compose logs postgres  # or kafka, spark, etc

# Restart all services
docker-compose down
docker-compose up -d

# If still failing, check disk space
docker system df
```

### Issue: Port already in use

```bash
# Find what's using the port (e.g., 8080)
lsof -i :8080

# Kill the process
kill -9 <PID>

# Or modify docker-compose.yml ports
```

### Issue: Spark job fails with file not found

```bash
# Verify file exists
ls -la /Users/nitinkamal/code/projects/data-engineering/data/sample_events.csv

# Check Docker volume mounting
docker exec spark ls -la /data/

# Should show: sample_events.csv
```

### Issue: Permission denied

```bash
# Fix permissions
chmod -R 755 /Users/nitinkamal/code/projects/data-engineering/data/

# Restart Docker
docker-compose down
docker-compose up -d
```

---

## Part 5: First Commit

Once everything is working:

```bash
# Check what changed
git status

# Stage everything
git add .

# Commit with message
git commit -m "setup: day 1 - docker environment and initial setup

- Create docker-compose.yml with Kafka, Spark, Airflow, PostgreSQL
- Initialize project directory structure (jobs, dbt_project, airflow_dags, data)
- Create sample CSV for first Spark job
- Create STUDY_MODULE.md (comprehensive learning guide)
- Create PROGRESS.md (daily progress tracker)
- All services verified and running locally"

# Push to GitHub
git push origin main
```

---

## Part 6: Summary & Checklist

### Day 1 Completion Checklist

- [ ] Read ARCHITECTURE.md completely
- [ ] Read STUDY_MODULE.md Part 1 & 2
- [ ] Understand medallion pattern (can explain it)
- [ ] Docker installed and working
- [ ] All 5 services running (Kafka, Spark, Airflow, Postgres, Zookeeper)
- [ ] Verified each service individually
- [ ] Created Kafka test topic
- [ ] Ran Spark job successfully
- [ ] Verified Parquet output
- [ ] All files committed to git

### Skills Gained

✅ Understand data pipeline architecture  
✅ Know why we use each technology  
✅ Can set up local development environment  
✅ Understand medallion pattern (Bronze → Silver → Gold)  
✅ Know how Spark, Kafka, dbt, Airflow fit together  

### Time Spent

- Reading/Understanding: 2 hours
- Setup: 3 hours
- Verification/Troubleshooting: 1 hour
- **Total: ~6 hours**

---

## What's Next (Day 2)

Tomorrow: Finalize local environment, prepare for first real Spark job

Goals:
- [ ] Confirm everything still works after restart
- [ ] Create sample data in multiple formats
- [ ] Prepare for Day 3 (actual first Spark job)

---

## Tips for Success

1. **Don't skip reading** - Understanding why is as important as doing
2. **Test each service** - Don't assume it works, verify it
3. **Keep notes** - Write down questions, look them up later
4. **Ask me anytime** - No question is too basic
5. **Commit regularly** - Small commits are easier to understand

---

## Useful Commands (Reference)

```bash
# See all running containers
docker-compose ps

# View logs for a service
docker-compose logs kafka
docker-compose logs spark

# Execute command in container
docker exec kafka kafka-topics.sh --list

# Stop all services
docker-compose stop

# Start services again
docker-compose start

# Remove everything (careful!)
docker-compose down

# Check if port is in use
lsof -i :8080

# List all images
docker images

# Remove unused images/volumes
docker system prune
```

---

**You've got this!** 🚀  
Day 1 is foundational. Take your time understanding the architecture. It'll all make sense as you build.

See you on Day 2!
