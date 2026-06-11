# 30-Day Learning Plan - Quick Reference

## Week 1: Foundations & First Pipeline

| Day | Date | Topic | Learning Objective (1-liner) |
|-----|------|-------|------------------------------|
| 1 | 2026-06-12 | Architecture Deep Dive | Understand medallion pattern, tech stack, and how all components work together |
| 2 | 2026-06-13 | Local Dev Environment Setup | Set up Docker Compose with Kafka, Spark, and PostgreSQL running locally |
| 3 | 2026-06-14 | First Spark Job | Build your first end-to-end pipeline: read CSV → transform with Spark → write Parquet |
| 4 | 2026-06-15 | Data Quality Checks | Add Great Expectations assertions (schema validation, null checks, row counts) |
| 5 | 2026-06-16 | dbt Project Setup | Initialize dbt, build Bronze→Silver transformation model with 2 tests |
| 6 | 2026-06-17 | Containerization | Create Dockerfile for Spark job, make everything reproducible in Docker |
| 7 | 2026-06-18 | Documentation & Blog | Write comprehensive README + first blog post about your data pipeline |

**Week 1 Goal:** Working end-to-end pipeline with quality checks, containerized, and documented ✅

---

## Week 2: Real-Time Streaming

| Day | Date | Topic | Learning Objective (1-liner) |
|-----|------|-------|------------------------------|
| 8 | 2026-06-19 | Kafka Setup | Spin up 3-broker Kafka cluster in Docker with proper configuration |
| 9 | 2026-06-20 | Kafka Producer | Build event producer that simulates realistic user events (clicks, views, purchases) |
| 10 | 2026-06-21 | Spark Streaming Consumer | Implement Kafka consumer that writes events to Bronze layer in real-time |
| 11 | 2026-06-22 | Streaming Quality Checks | Add schema validation, duplicate detection, and anomaly alerts to streaming pipeline |
| 12 | 2026-06-23 | Real-Time Silver Models | Build incremental dbt models that transform streaming Bronze data to Silver |
| 13 | 2026-06-24 | Real-Time Dashboard | Create Gold aggregations and simple visualization showing real-time metrics |
| 14 | 2026-06-25 | Documentation & Blog | Document Kafka architecture and write blog post: "Real-Time Data Pipeline with Kafka" |

**Week 2 Goal:** Full real-time pipeline (Kafka → Spark Streaming → Bronze → Silver → Gold) with visualization ✅

---

## Week 3: Orchestration & Production Patterns

| Day | Date | Topic | Learning Objective (1-liner) |
|-----|------|-------|------------------------------|
| 15 | 2026-06-26 | Airflow Setup | Set up local Airflow with PostgreSQL backend, understand DAG concepts |
| 16 | 2026-06-27 | First Airflow DAG | Build daily ETL DAG: extract → load_bronze → quality_checks → transform_silver |
| 17 | 2026-06-28 | Error Handling & Alerting | Implement retries, exponential backoff, Slack alerts, and SLA monitoring |
| 18 | 2026-06-29 | Airflow + dbt Integration | Orchestrate dbt transformations from Airflow, capture logs and handle failures |
| 19 | 2026-06-30 | Monitoring & Observability | Add comprehensive logging, track metrics, create pipeline status dashboard |
| 20 | 2026-07-01 | Advanced DAG Patterns | Implement dynamic DAG generation, cross-DAG dependencies, and conditional branching |
| 21 | 2026-07-02 | Documentation & Case Study | Document DAG design decisions, write case study about orchestrating complex pipelines |

**Week 3 Goal:** Production-grade orchestrated pipelines with monitoring, error handling, and comprehensive documentation ✅

---

## Week 4: Advanced Topics & Portfolio Polish

| Day | Date | Topic | Learning Objective (1-liner) |
|-----|------|-------|------------------------------|
| 22 | 2026-07-03 | Incremental Processing | Implement efficient incremental loads (only process new data), benchmark vs full refresh |
| 23 | 2026-07-04 | Data Quality Framework | Expand Great Expectations suite, implement data contracts, build quality scorecards |
| 24 | 2026-07-05 | Performance Optimization | Profile Spark jobs, optimize partitioning/caching/joins, reduce execution time by 50% |
| 25 | 2026-07-06 | Advanced Transformations | Implement slowly changing dimensions (SCD Type 2), late-arriving dimensions, complex aggregations |
| 26 | 2026-07-07 | System Design Deep Dive | Design scaling architecture for 10x data volume, document trade-offs, create DR plan |
| 27 | 2026-07-08 | Scaling & Migration | Create detailed migration roadmap (local → cloud), design disaster recovery strategy |
| 28 | 2026-07-09 | Portfolio Polish Part 1 | Update main README, create case-studies directory with 3 detailed write-ups |
| 29 | 2026-07-10 | Portfolio Polish Part 2 | Write enterprise blog post, create architecture diagrams, record demo video |
| 30 | 2026-07-11 | Final Review & Launch | Code review all 30 days of work, verify tests pass, ensure documentation complete, live demo ready |

**Week 4 Goal:** Professional, comprehensive data engineering portfolio demonstrating staff-level skills ✅

---

## Daily Checklist Template

Use this for each day:

```
Day X: [Topic]
------
Learning: [Key concept you'll understand]
Build: [What you'll create]
Test: [How you'll verify it works]
Commit: [Git commit message]
Time: [Estimated hours]
Deliverable: [What's complete by end of day]
```

---

## Quick Progress Tracker

Copy and paste this, update daily:

```
Week 1 Progress:
  Day 1: [ ] Architecture Deep Dive
  Day 2: [ ] Local Dev Setup
  Day 3: [ ] First Spark Job
  Day 4: [ ] Quality Checks
  Day 5: [ ] dbt Project
  Day 6: [ ] Containerization
  Day 7: [ ] Documentation
  Status: [ ] Week 1 Complete

Week 2 Progress:
  Day 8: [ ] Kafka Setup
  Day 9: [ ] Kafka Producer
  Day 10: [ ] Spark Streaming
  Day 11: [ ] Streaming Quality
  Day 12: [ ] Silver Models
  Day 13: [ ] Dashboard
  Day 14: [ ] Documentation
  Status: [ ] Week 2 Complete

Week 3 Progress:
  Day 15: [ ] Airflow Setup
  Day 16: [ ] First DAG
  Day 17: [ ] Error Handling
  Day 18: [ ] Airflow + dbt
  Day 19: [ ] Monitoring
  Day 20: [ ] Advanced DAGs
  Day 21: [ ] Case Study
  Status: [ ] Week 3 Complete

Week 4 Progress:
  Day 22: [ ] Incremental Processing
  Day 23: [ ] Quality Framework
  Day 24: [ ] Performance Opt
  Day 25: [ ] Advanced Transforms
  Day 26: [ ] System Design
  Day 27: [ ] Scaling & DR
  Day 28: [ ] Portfolio Part 1
  Day 29: [ ] Portfolio Part 2
  Day 30: [ ] Final Review
  Status: [ ] Week 4 Complete ✅
```

---

## Skills You'll Gain (by week)

**Week 1 (Fundamentals):**
- Spark data processing, Parquet format, basic data quality, dbt models, Docker

**Week 2 (Real-Time):**
- Kafka pub-sub, Spark Streaming, windowing/watermarking, incremental transformations

**Week 3 (Orchestration):**
- Airflow DAGs, task dependencies, error handling, monitoring, production thinking

**Week 4 (Advanced):**
- System design, scaling, optimization, SCD Type 2, DR planning, mentorship

---

## By End of Day 30, You Will:

✅ Have 50+ Git commits showing progressive skill development
✅ Understand every layer of a modern data stack
✅ Have built 4 production-grade data pipelines
✅ Write 5+ blog posts/case studies documenting your learning
✅ Demonstrate staff-level architecture thinking
✅ Be ready to interview as a senior data engineer
✅ Have a portfolio that proves end-to-end ownership
✅ Be capable of mentoring junior data engineers

---

**Remember:** Quality over speed. A well-documented, production-grade pipeline showcases more than 10 half-baked projects.

**Print this page, check off daily, track your 30-day journey.** 🚀
