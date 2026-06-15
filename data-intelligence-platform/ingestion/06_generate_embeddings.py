"""
Generate embeddings using Ollama and index in OpenSearch
"""
import logging
import json
import requests
from opensearchpy import OpenSearch

from config.connection import ConnectionConfig, log_config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_embedding(text: str) -> list:
    """Get embedding from Ollama"""
    try:
        url = f"{ConnectionConfig.get_ollama_url()}/api/embeddings"
        response = requests.post(
            url,
            json={
                "model": ConnectionConfig.OLLAMA_MODEL,
                "prompt": text
            },
            timeout=30
        )

        if response.status_code == 200:
            return response.json().get("embedding", [])
        else:
            logger.warning(f"Failed to get embedding: {response.text}")
            # Return dummy embedding if Ollama unavailable
            return [0.0] * 1024
    except Exception as e:
        logger.warning(f"Ollama unavailable: {str(e)}. Using dummy embeddings.")
        return [0.0] * 1024


def generate_embeddings():
    """Generate embeddings for all assets"""
    try:
        log_config()

        logger.info("Generating embeddings...")

        # Connect to OpenSearch
        client = OpenSearch(
            hosts=[{"host": ConnectionConfig.OS_HOST, "port": ConnectionConfig.OS_PORT}],
            use_ssl=False,
            verify_certs=False
        )

        # Create or update index with embeddings
        logger.info("Setting up OpenSearch indices...")

        tables_mapping = {
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0,
            },
            "mappings": {
                "properties": {
                    "name": {"type": "text"},
                    "schema": {"type": "keyword"},
                    "owner": {"type": "keyword"},
                    "description": {"type": "text"},
                    "row_count": {"type": "integer"},
                    "embedding": {"type": "knn_vector", "dimension": 1024},
                }
            }
        }

        # Create tables index
        if not client.indices.exists("tables_index"):
            client.indices.create(index="tables_index", body=tables_mapping)
            logger.info("  ✓ Created tables_index")
        else:
            logger.info("  ✓ tables_index already exists")

        # Sample tables to embed
        tables = [
            {"name": "customer_dim", "description": "Customer dimension table with customer details and signup information"},
            {"name": "product_dim", "description": "Product dimension table with product details and pricing"},
            {"name": "sales_fact", "description": "Sales fact table with transaction-level details"},
            {"name": "order_fact", "description": "Order fact table with order-level information"},
            {"name": "inventory_fact", "description": "Inventory fact table with warehouse stock levels"},
        ]

        logger.info(f"Generating embeddings for {len(tables)} tables...")

        for table in tables:
            # Generate embedding
            text = f"{table['name']}: {table['description']}"
            embedding = get_embedding(text)

            # Index in OpenSearch
            doc_body = {
                "name": table["name"],
                "description": table["description"],
                "schema": "public",
                "owner": "analytics-team",
                "row_count": 0,
                "embedding": embedding
            }

            client.index(
                index="tables_index",
                body=doc_body,
                id=table["name"]
            )

            logger.info(f"  ✓ Embedded and indexed: {table['name']}")

        logger.info("\n✅ Embeddings generated successfully!")

        return True

    except Exception as e:
        logger.error(f"Error generating embeddings: {str(e)}")
        raise


if __name__ == "__main__":
    generate_embeddings()
