import os
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class ConnectionConfig:
    """Database and service connection configuration"""

    # PostgreSQL
    PG_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    PG_PORT: int = int(os.getenv("POSTGRES_PORT", 5432))
    PG_USER: str = os.getenv("POSTGRES_USER", "dataeng")
    PG_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "secure123")
    PG_DATABASE: str = os.getenv("POSTGRES_DB", "datawarehouse")

    # Neo4j
    NEO4J_URI: str = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USER: str = os.getenv("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD: str = os.getenv("NEO4J_PASSWORD", "secure123")

    # OpenSearch
    OS_HOST: str = os.getenv("OPENSEARCH_HOST", "localhost")
    OS_PORT: int = int(os.getenv("OPENSEARCH_PORT", 9200))

    # Ollama
    OLLAMA_HOST: str = os.getenv("OLLAMA_HOST", "localhost")
    OLLAMA_PORT: int = int(os.getenv("OLLAMA_PORT", 11434))
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3")

    @classmethod
    def get_postgres_url(cls) -> str:
        """Get PostgreSQL connection string"""
        return f"postgresql://{cls.PG_USER}:{cls.PG_PASSWORD}@{cls.PG_HOST}:{cls.PG_PORT}/{cls.PG_DATABASE}"

    @classmethod
    def get_neo4j_uri(cls) -> str:
        """Get Neo4j URI"""
        return cls.NEO4J_URI

    @classmethod
    def get_opensearch_host(cls) -> str:
        """Get OpenSearch host:port"""
        return f"{cls.OS_HOST}:{cls.OS_PORT}"

    @classmethod
    def get_ollama_url(cls) -> str:
        """Get Ollama base URL"""
        return f"http://{cls.OLLAMA_HOST}:{cls.OLLAMA_PORT}"


def log_config():
    """Log current configuration"""
    logger.info(f"PostgreSQL: {ConnectionConfig.PG_HOST}:{ConnectionConfig.PG_PORT}/{ConnectionConfig.PG_DATABASE}")
    logger.info(f"Neo4j: {ConnectionConfig.NEO4J_URI}")
    logger.info(f"OpenSearch: {ConnectionConfig.OS_HOST}:{ConnectionConfig.OS_PORT}")
    logger.info(f"Ollama: {ConnectionConfig.get_ollama_url()}")
