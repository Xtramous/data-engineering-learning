from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from typing import AsyncGenerator

from api import search, lineage, catalog, chat, health
from utils.config import get_settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Manage app startup and shutdown"""
    logger.info("Starting Data Intelligence Platform...")
    yield
    logger.info("Shutting down Data Intelligence Platform...")


app = FastAPI(
    title="Data Intelligence Platform",
    description="Metadata discovery and lineage system",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)
app.include_router(search.router, prefix="/api", tags=["search"])
app.include_router(lineage.router, prefix="/api", tags=["lineage"])
app.include_router(catalog.router, prefix="/api", tags=["catalog"])
app.include_router(chat.router, prefix="/api", tags=["chat"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Data Intelligence Platform",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
