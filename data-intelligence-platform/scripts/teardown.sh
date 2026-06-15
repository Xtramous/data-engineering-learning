#!/bin/bash
# Data Intelligence Platform - Teardown Script

set -e

echo "🛑 Shutting down Data Intelligence Platform..."
echo ""

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose is not installed."
    exit 1
fi

# Confirm before deleting
read -p "Are you sure you want to stop all services? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 0
fi

read -p "Also remove volumes and data? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🗑️  Stopping containers and removing volumes..."
    docker-compose down -v
else
    echo "🛑 Stopping containers (keeping volumes)..."
    docker-compose down
fi

echo "✅ Shutdown complete!"
echo ""
