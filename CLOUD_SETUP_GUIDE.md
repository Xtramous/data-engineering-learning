# Cloud Setup Guide: From Local to AWS (Free Tier)

## Quick Decision Tree

```
Want to follow the 30-day plan?
├─ Days 1-20: Build locally (no changes needed) ✅
├─ Days 21-30: Add AWS (this guide) 📖
│   ├─ Already have AWS account? → Skip to "Spark Code Changes"
│   └─ Don't have AWS account? → Start at "Step 1: AWS Account Setup"
└─ Optional: Impress in interviews → Full cloud demo (Day 30)
```

---

## Step 1: AWS Account Setup (15 minutes) - **$0**

### 1.1 Create Free Tier AWS Account

```bash
1. Go to: https://aws.amazon.com/free/
2. Click "Create AWS Account"
3. Email: nitinkamal132@gmail.com
4. Password: [strong password]
5. Verify email
6. Add payment method (won't be charged for free tier usage)
7. Verify phone number
8. Choose "Basic Support Plan" (free)
```

### 1.2 Enable Free Tier Alerts

This prevents accidental charges:

```bash
1. AWS Console → Billing Dashboard
2. Click "Preferences"
3. Check: "Receive Free Tier Usage Alerts"
4. Check: "Receive Billing Alerts"
5. Set alert threshold: $5 (you'll get email if close to limit)
```

### 1.3 Set Up S3 Bucket

```bash
1. AWS Console → S3
2. Click "Create Bucket"
3. Bucket name: your-de-bucket-unique-name
   (must be globally unique, so add date: your-de-bucket-20260611)
4. Region: us-east-1 (free tier region)
5. Block public access: ON (security)
6. Create bucket
```

**Your bucket is now ready!** 🎉

---

## Step 2: AWS Credentials Setup (10 minutes)

### 2.1 Create IAM User (Best Practice)

Don't use root account! Create a limited user:

```bash
1. AWS Console → IAM
2. Click "Users" → "Create User"
3. Username: spark-user
4. Next: Add permissions
5. Attach policy: "AmazonS3FullAccess"
6. Create user
7. Click on user → "Security Credentials"
8. "Create Access Key"
9. Download CSV (save safely!)
```

**CSV contains:**
```
Access Key ID:     AKIA...
Secret Access Key: ...
```

### 2.2 Configure AWS CLI on Your Laptop

```bash
# Install AWS CLI
pip install awscli

# Configure credentials
aws configure

# It will ask:
AWS Access Key ID: [paste from CSV]
AWS Secret Access Key: [paste from CSV]
Default region: us-east-1
Default output format: json

# Verify it works
aws s3 ls
# Should list your bucket: s3://your-de-bucket-20260611
```

---

## Step 3: Modify Your Spark Code (2 minutes per file)

### Before (Local Storage)

```python
# jobs/bronze_to_silver.py
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("bronze_to_silver").getOrCreate()

# Read from local
df = spark.read.parquet("/Users/nitinkamal/code/projects/data-engineering/data/bronze/events")

# Transform
df_clean = df.dropDuplicates(["event_id"])

# Write to local
df_clean.write.parquet("/Users/nitinkamal/code/projects/data-engineering/data/silver/events_clean")
```

### After (AWS S3 Storage)

```python
# jobs/bronze_to_silver.py
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("bronze_to_silver").getOrCreate()

# Read from S3 (same API, different path!)
df = spark.read.parquet("s3://your-de-bucket-20260611/bronze/events")

# Transform (no changes)
df_clean = df.dropDuplicates(["event_id"])

# Write to S3 (same API, different path!)
df_clean.write.mode("overwrite").parquet("s3://your-de-bucket-20260611/silver/events_clean")
```

**That's it!** 🎉 Your code now uses cloud storage.

---

## Step 4: Configure Spark for S3 (5 minutes)

### Add S3 Credentials to Spark

**Option A: Environment Variables** (Easy)

```bash
# Add to your shell profile (~/.zprofile or ~/.bashrc)
export AWS_ACCESS_KEY_ID="AKIA..."
export AWS_SECRET_ACCESS_KEY="..."
export AWS_DEFAULT_REGION="us-east-1"

# Source it
source ~/.zprofile
```

**Option B: In Docker Compose** (Better for reproducibility)

```yaml
# docker-compose.yml
services:
  spark:
    image: bitnami/spark:latest
    environment:
      AWS_ACCESS_KEY_ID: "AKIA..."
      AWS_SECRET_ACCESS_KEY: "..."
      AWS_DEFAULT_REGION: "us-east-1"
```

**Option C: In Spark Job** (Hardcode in code - NOT RECOMMENDED for production)

```python
spark._jsc.hadoopConfiguration().set("fs.s3a.access.key", "AKIA...")
spark._jsc.hadoopConfiguration().set("fs.s3a.secret.key", "...")
```

**Use Option A or B, never Option C in production!**

---

## Step 5: Test Connection (5 minutes)

### Test 1: AWS CLI

```bash
# Write a test file
aws s3 cp test.txt s3://your-de-bucket-20260611/

# Read it back
aws s3 ls s3://your-de-bucket-20260611/

# Delete it
aws s3 rm s3://your-de-bucket-20260611/test.txt
```

### Test 2: Spark Job

```python
# test_s3_connection.py
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("test_s3") \
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
    .getOrCreate()

# Create sample data
data = [("id1", "value1"), ("id2", "value2")]
df = spark.createDataFrame(data, ["id", "value"])

# Write to S3
df.write.mode("overwrite").parquet("s3://your-de-bucket-20260611/test")

# Read back from S3
df_read = spark.read.parquet("s3://your-de-bucket-20260611/test")

# Show results
df_read.show()
print("✅ S3 connection working!")
```

**Run it:**
```bash
spark-submit test_s3_connection.py
```

---

## Step 6: Update Your dbt Project (5 minutes per model)

### Before (Local Parquet)

```yaml
# dbt/profiles.yml
your_project:
  target: dev
  outputs:
    dev:
      type: spark
      host: localhost
      port: 7077
      user: spark
      schema: bronze
      database: /Users/nitinkamal/code/projects/data-engineering/data/bronze
```

### After (S3 + Spark)

```yaml
# dbt/profiles.yml
your_project:
  target: prod
  outputs:
    prod:
      type: spark
      host: localhost
      port: 7077
      user: spark
      schema: s3://your-de-bucket-20260611/silver
      database: s3://your-de-bucket-20260611
```

**Or use DuckDB adapter** (newer, easier):

```yaml
your_project:
  target: prod
  outputs:
    prod:
      type: duckdb
      path: s3://your-de-bucket-20260611/
      database: data_lake
```

---

## Step 7: Update Airflow DAGs (Optional)

### Add S3 Operators to Airflow

```python
# airflow_dags/bronze_to_silver_dag.py
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.operators.s3 import S3ListOperator
from datetime import datetime

dag = DAG(
    'bronze_to_silver_s3',
    start_date=datetime(2026, 6, 21),
    schedule_interval='@daily'
)

# Check if new data in S3
check_s3 = S3ListOperator(
    task_id='check_s3_bronze',
    bucket='your-de-bucket-20260611',
    prefix='bronze/events',
    aws_conn_id='aws_default'
)

# Run Spark job
run_spark = BashOperator(
    task_id='run_spark_transformation',
    bash_command='spark-submit /jobs/bronze_to_silver.py'
)

# Simple dependency
check_s3 >> run_spark
```

---

## Step 8: Monitor S3 Costs (Stay Free!)

### AWS Free Tier Limits

```
S3 Storage:     5GB total
Data Transfer:  100GB outbound/month
API Calls:      Included in free tier

Your 30-day usage (estimate):
- Days 1-20: Local (0GB on S3)
- Days 21-30: S3 (~500MB max)
- Total: <1GB ✅ (well under 5GB limit)

Cost: $0 ✅
```

### Set Up Billing Alert

```bash
AWS Console → CloudWatch → Alarms
├─ Create alarm
├─ Metric: Estimated charges (USD)
├─ Threshold: $5
├─ Action: Send email to nitinkamal132@gmail.com
└─ Create alarm

Now you'll get email if charges approach $5
```

---

## File Structure After Cloud Setup

### Local (Your Laptop)

```
~/code/projects/data-engineering/
├── jobs/              (Spark jobs - same code)
├── dbt_project/       (dbt models - same code)
├── airflow_dags/      (Airflow DAGs - same code)
└── data/              (Not used, can delete)
```

### Cloud (AWS S3)

```
s3://your-de-bucket-20260611/
├── bronze/
│   ├── events/year=2026/month=06/day=21/
│   │   └─ *.parquet
│   └── users/year=2026/month=06/day=21/
│       └─ *.parquet
├── silver/
│   ├── events_clean/
│   └── users_clean/
└── gold/
    ├── user_metrics/
    └── revenue_daily/
```

---

## Comparison: Local vs Cloud

### Local (Days 1-20)

```python
# Read from local disk
df = spark.read.parquet("/local/path/bronze")

# Process (all on laptop)
df_clean = df.dropDuplicates()

# Write to local disk
df_clean.write.parquet("/local/path/silver")

Storage: Your laptop SSD
Cost: Electricity only (~$0.02/day)
Speed: Fast (local disk)
Scale: Limited to laptop capacity (~100GB)
```

### Cloud (Days 21-30)

```python
# Read from cloud (same code!)
df = spark.read.parquet("s3://bucket/bronze")

# Process (still on laptop, but data from cloud)
df_clean = df.dropDuplicates()

# Write to cloud (same code!)
df_clean.write.parquet("s3://bucket/silver")

Storage: AWS S3 (5GB free)
Cost: $0 (free tier)
Speed: Slightly slower (network latency)
Scale: Unlimited (cloud storage)
```

---

## Day 21+ Workflow

### Morning (Same as Before)

```bash
# Navigate to your project
cd ~/code/projects/data-engineering/

# Start local services (Kafka, Airflow, etc)
docker-compose up

# AWS credentials already in environment
# Your Spark jobs now read/write to S3
```

### Run a Job

```bash
# Old code:
spark-submit jobs/bronze_to_silver.py

# Your code now:
# 1. Reads from S3: s3://bucket/bronze/events
# 2. Processes locally (on laptop)
# 3. Writes to S3: s3://bucket/silver/events_clean

# No code changes needed - paths just use S3!
```

### Monitor Progress

```bash
# Check S3 bucket
aws s3 ls s3://your-de-bucket-20260611/silver --recursive

# Check file sizes
aws s3 ls s3://your-de-bucket-20260611/silver --recursive --summarize

# Expected output:
# Total Objects: ~10
# Total Size: ~200MB
# Cost: $0 (free tier)
```

---

## Cost Checkpoints (Stay Alert!)

### Week 3 Check
```bash
AWS Console → Billing Dashboard
Expected charges: $0-1

If > $1:
  ├─ Check S3 usage (should be <500MB)
  ├─ Check data transfer (should be <500MB)
  └─ Stop any runaway processes
```

### Week 4 Check
```bash
Expected charges: $0-2

If > $2:
  ├─ Delete unnecessary S3 objects
  ├─ Check for accidentally running EC2 instances
  └─ Review CloudTrail for unexpected API calls
```

---

## Optional: Day 30 Cloud Demo (Impress Interviewers)

### What is AWS Glue?

Managed Spark in the cloud. Same Spark jobs, AWS runs them.

```python
# Same job code!
# But run on AWS Glue cluster (24 cores, 96GB RAM)
# Processes 10x faster than your laptop
# Then shut down (no ongoing costs)
```

### How to Run Demo

```bash
# Step 1: Upload your Spark job to S3
aws s3 cp jobs/bronze_to_silver.py s3://bucket/scripts/

# Step 2: AWS Glue creates cluster, runs job
AWS Console → Glue → Jobs → Create Job
├─ Name: bronze_to_silver_demo
├─ Type: Spark
├─ Script location: s3://bucket/scripts/bronze_to_silver.py
├─ Max capacity: 2 DPU (cheapest)
└─ Run

# Step 3: Monitor execution
AWS Console → Glue → Jobs → Run history
├─ Shows: 2GB processed in 10 seconds
├─ Performance: 10x faster than laptop
└─ Cost: ~$1 (shut down immediately after)

# Step 4: Screenshot for portfolio
"Successfully ran Spark job on AWS Glue"
"Processed 2GB in 10 seconds (10x faster than laptop)"
"Cost: $1 for demo"
```

---

## Summary Table

| Phase | Duration | Location | Storage | Cost | What You Learn |
|-------|----------|----------|---------|------|---|
| Phase 1 | Days 1-20 | Local | Laptop disk | $0 | Fundamentals |
| Phase 2 | Days 21-27 | Local + S3 | AWS S3 | $0 | Cloud storage |
| Phase 3 | Day 28-30 | AWS Glue | S3 | $0-2 | Cloud compute |

---

## Troubleshooting

### S3 Connection Fails

```bash
# Check credentials
aws sts get-caller-identity

# Should show your AWS account ID
# If error: credentials not configured

# Fix: Re-run aws configure
aws configure
# Paste Access Key ID
# Paste Secret Access Key
```

### Spark Job Slow with S3

```bash
# Normal (network latency adds ~2-5 seconds)
# Avoid: Thousands of small files (use partitioning)
# Optimize: Increase number of partitions

# Code:
df.repartition(100).write.parquet("s3://bucket/silver")
```

### Accidentally High Charges

```bash
1. AWS Glue jobs left running?
   → AWS Console → Glue → Jobs → Stop any running

2. EC2 instances running?
   → AWS Console → EC2 → Instances → Terminate unused

3. Wrong region (not us-east-1)?
   → S3 data transfer costs money between regions
   → Use us-east-1 (free tier region)

4. Set up budget alert (should have done this!)
   → AWS Console → Budgets → Create alert for $5
```

---

## Next Steps

1. **Day 20:** Follow this guide (1 hour setup)
2. **Day 21:** Modify Spark code (all files, 15 min each)
3. **Day 22:** Verify S3 reads/writes (test_s3_connection.py)
4. **Day 23-27:** Continue 30-day plan using S3
5. **Day 30:** Optional cloud demo with Glue

**Cost check:** Should still be $0-2 for entire month ✅

Ready to go hybrid (local + cloud)? 🚀

---

## One More Thing: Git Secrets

**NEVER commit AWS credentials to GitHub!**

```bash
# Good ✅
export AWS_ACCESS_KEY_ID="..." # In ~/.zprofile, not in git
aws_conn_id: aws_default  # Reference, not actual credential

# BAD ❌
AWS_ACCESS_KEY_ID = "AKIA..." # In code file, pushed to GitHub
AWS_SECRET_KEY = "..." # Exposed!
```

**If you accidentally committed:**

```bash
# IMMEDIATELY rotate credentials
AWS Console → IAM → Users → spark-user → Security Credentials
├─ Delete old key
├─ Create new key
├─ Update ~/.zprofile
└─ Verify works: aws s3 ls

# Then remove from git history
git filter-branch --tree-filter 'rm -f sensitive_file' HEAD
```

**You're now ready for hybrid cloud development!** 🎉
