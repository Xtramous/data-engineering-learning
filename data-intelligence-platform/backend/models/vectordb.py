from opensearchpy import OpenSearch
from utils.config import get_settings
import logging

logger = logging.getLogger(__name__)

settings = get_settings()


def get_opensearch_client() -> OpenSearch:
    """Get OpenSearch client"""
    try:
        client = OpenSearch(
            hosts=[{"host": settings.opensearch_host, "port": settings.opensearch_port}],
            http_auth=None,
            use_ssl=False,
            verify_certs=False,
            ssl_show_warn=False,
        )
        logger.info("OpenSearch connection successful")
        return client
    except Exception as e:
        logger.error(f"OpenSearch connection failed: {str(e)}")
        return None


def create_indices():
    """Create OpenSearch indices"""
    client = get_opensearch_client()
    if not client:
        return False

    indices = {
        "tables_index": {
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
                    "embedding": {"type": "knn_vector", "dimension": 1024},
                }
            }
        },
        "dashboards_index": {
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0,
            },
            "mappings": {
                "properties": {
                    "name": {"type": "text"},
                    "owner": {"type": "keyword"},
                    "description": {"type": "text"},
                    "tables": {"type": "keyword"},
                }
            }
        }
    }

    try:
        for index_name, index_config in indices.items():
            if not client.indices.exists(index_name):
                client.indices.create(index=index_name, body=index_config)
                logger.info(f"Created index: {index_name}")
        return True
    except Exception as e:
        logger.error(f"Failed to create indices: {str(e)}")
        return False
