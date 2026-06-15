from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool
from utils.config import get_settings
import logging

logger = logging.getLogger(__name__)

settings = get_settings()

# Database connection pool
engine = create_engine(
    settings.database_url,
    poolclass=NullPool,  # No connection pooling for simplicity
    echo=False,
    future=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database"""
    try:
        with engine.connect() as conn:
            logger.info("Database connection successful")
            return True
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        return False
