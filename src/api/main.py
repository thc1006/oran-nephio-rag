"""
FastAPI Main Application for O-RAN × Nephio RAG System
Developer-friendly REST API with comprehensive features
"""

import logging
import os
import time
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional

import uvicorn
from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import Counter, Histogram, generate_latest
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from ..config import Config
from ..oran_nephio_rag import ORANNephioRAG
from .auth import AuthMiddleware, get_current_user
from .error_handlers import create_error_handlers
from .middleware import LoggingMiddleware, SecurityMiddleware
from .models import (
    APIResponse,
    ErrorResponse,
    HealthResponse,
    QueryRequest,
    QueryResponse,
    SystemStatusResponse,
)
from .routers import documents, health, queries, system

# Configure logging
logger = logging.getLogger(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter(
    "http_requests_total", "Total HTTP requests", ["method", "endpoint", "status"]
)
REQUEST_DURATION = Histogram(
    "http_request_duration_seconds", "HTTP request duration", ["method", "endpoint"]
)
RAG_QUERY_COUNT = Counter("rag_queries_total", "Total RAG queries", ["status"])
RAG_QUERY_DURATION = Histogram("rag_query_duration_seconds", "RAG query duration")

# Rate limiter
limiter = Limiter(key_func=get_remote_address)

# Global RAG system instance
rag_system: Optional[ORANNephioRAG] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global rag_system

    # Startup
    logger.info("🚀 Starting O-RAN × Nephio RAG API")

    try:
        config = Config()
        config.validate()

        # Initialize RAG system
        rag_system = ORANNephioRAG(config)

        # Try to load existing database
        if not rag_system.initialize_system():
            logger.warning("⚠️ Failed to initialize RAG system with existing database")
            # Could try to rebuild here if needed
        else:
            logger.info("✅ RAG system initialized successfully")

        # Store system instance for routes
        app.state.rag_system = rag_system
        app.state.config = config

    except Exception as e:
        logger.error(f"❌ Failed to initialize RAG system: {e}")
        raise RuntimeError(f"Failed to initialize RAG system: {e}")

    yield

    # Shutdown
    logger.info("🛑 Shutting down O-RAN × Nephio RAG API")
    if rag_system:
        try:
            # Cleanup resources if needed
            del rag_system
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""

    app = FastAPI(
        title="O-RAN × Nephio RAG API",
        description="Developer-friendly REST API for O-RAN and Nephio knowledge retrieval",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # Add middleware
    setup_middleware(app)

    # Add error handlers
    setup_error_handlers(app)

    # Include routers
    setup_routers(app)

    return app


def setup_middleware(app: FastAPI) -> None:
    """Setup application middleware"""

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Compression middleware
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    # Security middleware
    app.add_middleware(SecurityMiddleware)

    # Authentication middleware
    app.add_middleware(AuthMiddleware)

    # Logging middleware
    app.add_middleware(LoggingMiddleware)

    # Rate limiting
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # Metrics middleware
    @app.middleware("http")
    async def metrics_middleware(request: Request, call_next):
        start_time = time.time()

        response = await call_next(request)

        # Record metrics
        process_time = time.time() - start_time
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code,
        ).inc()
        REQUEST_DURATION.labels(
            method=request.method, endpoint=request.url.path
        ).observe(process_time)

        # Add performance headers
        response.headers["X-Process-Time"] = str(process_time)

        return response


def setup_error_handlers(app: FastAPI) -> None:
    """Setup error handlers"""
    create_error_handlers(app)


def setup_routers(app: FastAPI) -> None:
    """Setup API routers"""

    # Health check endpoints
    app.include_router(health.router, prefix="/health", tags=["Health"])

    # Query endpoints
    app.include_router(queries.router, prefix="/api/v1/query", tags=["Queries"])

    # Document management
    app.include_router(documents.router, prefix="/api/v1/documents", tags=["Documents"])

    # System management
    app.include_router(system.router, prefix="/api/v1/system", tags=["System"])

    # Metrics endpoint
    @app.get("/metrics", response_class=Response)
    def get_metrics():
        """Prometheus metrics endpoint"""
        return Response(generate_latest(), media_type="text/plain")

    # Root endpoint
    @app.get("/", response_model=APIResponse)
    def root():
        """API root endpoint"""
        return APIResponse(
            success=True,
            message="O-RAN × Nephio RAG API",
            data={
                "version": "1.0.0",
                "docs": "/docs",
                "health": "/health",
                "api": "/api/v1",
            },
        )


# Create the application instance
app = create_app()

# CLI for running the server
if __name__ == "__main__":
    # Load configuration
    port = int(os.getenv("API_PORT", "8000"))
    host = os.getenv("API_HOST", "0.0.0.0")
    workers = int(os.getenv("API_WORKERS", "1"))

    # Development vs production
    debug = os.getenv("API_DEBUG", "false").lower() == "true"

    if debug:
        # Development mode
        uvicorn.run(
            "src.api.main:app",
            host=host,
            port=port,
            reload=True,
            log_level="debug",
        )
    else:
        # Production mode
        uvicorn.run(
            app,
            host=host,
            port=port,
            workers=workers,
            log_level="info",
        )