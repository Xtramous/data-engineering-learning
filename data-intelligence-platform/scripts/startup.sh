#!/bin/bash
# Data Intelligence Platform - Startup Script

set -e

echo "🚀 Starting Data Intelligence Platform..."
echo ""

# Check if Docker is running
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker daemon is not running. Please start Docker."
    exit 1
fi

# Copy .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from .env.example..."
    cp .env.example .env
fi

# Check if docker-compose file exists
if [ ! -f docker-compose.yml ]; then
    echo "❌ docker-compose.yml not found!"
    exit 1
fi

# Start services
echo "🐳 Starting Docker containers..."
docker-compose up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be healthy (this may take a few minutes)..."
sleep 10

# Check PostgreSQL
echo "🔍 Checking PostgreSQL..."
attempt=0
max_attempts=30
while [ $attempt -lt $max_attempts ]; do
    if docker-compose exec -T postgres pg_isready -U dataeng > /dev/null 2>&1; then
        echo "✅ PostgreSQL is ready"
        break
    fi
    attempt=$((attempt + 1))
    echo "⏳ PostgreSQL still starting... ($attempt/$max_attempts)"
    sleep 2
done

if [ $attempt -eq $max_attempts ]; then
    echo "❌ PostgreSQL failed to start"
    docker-compose logs postgres
    exit 1
fi

# Check Neo4j
echo "🔍 Checking Neo4j..."
if docker-compose exec -T neo4j curl -s http://localhost:7474 > /dev/null 2>&1; then
    echo "✅ Neo4j is ready"
else
    echo "⏳ Neo4j still starting..."
fi

# Check OpenSearch
echo "🔍 Checking OpenSearch..."
if docker-compose exec -T opensearch curl -s http://localhost:9200 > /dev/null 2>&1; then
    echo "✅ OpenSearch is ready"
else
    echo "⏳ OpenSearch still starting..."
fi

# Check Ollama
echo "🔍 Checking Ollama..."
if docker-compose exec -T ollama ollama list > /dev/null 2>&1; then
    echo "✅ Ollama is ready"
else
    echo "⏳ Ollama still starting..."
fi

echo ""
echo "✅ All services started!"
echo ""
echo "📊 Access points:"
echo "   Frontend:     http://localhost:3000"
echo "   Backend API:  http://localhost:8000"
echo "   API Docs:     http://localhost:8000/docs"
echo "   Neo4j:        http://localhost:7474"
echo "   OpenSearch:   http://localhost:9200"
echo ""
echo "📝 Next steps:"
echo "   1. Run: bash scripts/ingest.sh (to populate sample data)"
echo "   2. Open http://localhost:3000 in your browser"
echo "   3. Start exploring!"
echo ""
