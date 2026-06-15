from pydantic_settings import BaseSettings
from functools import lru_cache
import logging

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://dataeng:secure123@localhost:5432/datawarehouse"

    # Neo4j
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "secure123"

    # OpenSearch
    opensearch_host: str = "localhost"
    opensearch_port: int = 9200

    # Ollama
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3"

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get settings singleton"""
    return Settings()


def log_settings():
    """Log current settings (without passwords)"""
    settings = get_settings()
    logger.info(f"Database: {settings.database_url.split('@')[1] if '@' in settings.database_url else 'unknown'}")
    logger.info(f"Neo4j: {settings.neo4j_uri}")
    logger.info(f"OpenSearch: {settings.opensearch_host}:{settings.opensearch_port}")
    logger.info(f"Ollama: {settings.ollama_base_url}")
