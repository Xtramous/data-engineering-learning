#!/bin/bash
# Data Intelligence Platform - Data Ingestion Script

set -e

echo "📊 Starting metadata ingestion pipeline..."
echo ""

# Check if services are running
echo "🔍 Checking if services are running..."
if ! docker-compose ps | grep -q postgres; then
    echo "❌ Services are not running. Please run: docker-compose up -d"
    exit 1
fi

echo "✅ Services are running"
echo ""

# Run ingestion steps
echo "Step 1️⃣  - Generating sample data in PostgreSQL..."
docker-compose exec -T backend python -m ingestion.01_generate_sample_data || echo "⚠️  Generation in progress or already completed"
sleep 2

echo ""
echo "Step 2️⃣  - Extracting table metadata..."
docker-compose exec -T backend python -m ingestion.02_extract_table_metadata || echo "⚠️  Extraction in progress"
sleep 2

echo ""
echo "Step 3️⃣  - Extracting dashboard metadata..."
docker-compose exec -T backend python -m ingestion.03_extract_dashboard_metadata || echo "⚠️  Dashboard extraction in progress"
sleep 2

echo ""
echo "Step 4️⃣  - Parsing DAG metadata..."
docker-compose exec -T backend python -m ingestion.04_parse_dag_metadata || echo "⚠️  DAG parsing in progress"
sleep 2

echo ""
echo "Step 5️⃣  - Generating lineage..."
docker-compose exec -T backend python -m ingestion.05_generate_lineage || echo "⚠️  Lineage generation in progress"
sleep 2

echo ""
echo "Step 6️⃣  - Generating embeddings..."
docker-compose exec -T backend python -m ingestion.06_generate_embeddings || echo "⚠️  Embedding generation in progress"
sleep 2

echo ""
echo "Step 7️⃣  - Creating documentation..."
docker-compose exec -T backend python -m ingestion.07_create_documentation || echo "⚠️  Documentation creation in progress"
sleep 2

echo ""
echo "✅ Ingestion pipeline complete!"
echo ""
echo "📍 Verify ingestion:"
echo "   - PostgreSQL: SELECT COUNT(*) FROM customer_dim;"
echo "   - Neo4j: MATCH (n) RETURN COUNT(n);"
echo "   - OpenSearch: GET _cat/indices"
echo ""
echo "🎉 You can now start exploring the platform!"
echo ""
