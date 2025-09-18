"""
Health check and monitoring endpoints
"""

import logging
import os
import time
from datetime import datetime

from fastapi import APIRouter, Request
from psutil import virtual_memory

from ..models import APIResponse, HealthResponse

logger = logging.getLogger(__name__)

router = APIRouter()

# Track startup time for uptime calculation
startup_time = time.time()


@router.get("/", response_model=HealthResponse)
async def health_check(request: Request):
    """
    Basic health check endpoint

    Returns the overall health status of the API and its components.
    This endpoint should be used by load balancers and monitoring systems.

    Returns:
    - **status**: Overall health status (healthy, degraded, unhealthy)
    - **version**: API version
    - **uptime**: Service uptime in seconds
    - **components**: Health status of individual components
    """
    try:
        uptime = time.time() - startup_time

        # Check component health
        components = {}

        # Check RAG system
        rag_system = getattr(request.app.state, "rag_system", None)
        if rag_system:
            if getattr(rag_system, "is_ready", False):
                components["rag_system"] = "healthy"
            else:
                components["rag_system"] = "degraded"
        else:
            components["rag_system"] = "unhealthy"

        # Check vector database
        if rag_system and hasattr(rag_system, "vector_manager"):
            try:
                db_info = rag_system.vector_manager.get_database_info()
                if db_info.get("database_ready", False):
                    components["vector_database"] = "healthy"
                else:
                    components["vector_database"] = "degraded"
            except Exception:
                components["vector_database"] = "unhealthy"
        else:
            components["vector_database"] = "unknown"

        # Check query processor
        if rag_system and hasattr(rag_system, "query_processor"):
            if rag_system.query_processor:
                components["query_processor"] = "healthy"
            else:
                components["query_processor"] = "degraded"
        else:
            components["query_processor"] = "unknown"

        # Determine overall status
        if all(status == "healthy" for status in components.values()):
            overall_status = "healthy"
        elif any(status == "unhealthy" for status in components.values()):
            overall_status = "unhealthy"
        else:
            overall_status = "degraded"

        return HealthResponse(
            status=overall_status,
            version="1.0.0",
            uptime=uptime,
            components=components,
        )

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="unhealthy",
            version="1.0.0",
            uptime=time.time() - startup_time,
            components={"error": str(e)},
        )


@router.get("/ready", response_model=APIResponse)
async def readiness_check(request: Request):
    """
    Readiness check endpoint

    Indicates whether the service is ready to accept traffic.
    Returns 200 if ready, 503 if not ready.
    """
    try:
        rag_system = getattr(request.app.state, "rag_system", None)

        if not rag_system:
            return APIResponse(
                success=False,
                message="RAG system not initialized",
                data={"ready": False, "reason": "rag_system_missing"},
            )

        if not getattr(rag_system, "is_ready", False):
            return APIResponse(
                success=False,
                message="RAG system not ready",
                data={"ready": False, "reason": "rag_system_not_ready"},
            )

        # Check if vector database is accessible
        try:
            db_info = rag_system.vector_manager.get_database_info()
            if not db_info.get("database_ready", False):
                return APIResponse(
                    success=False,
                    message="Vector database not ready",
                    data={"ready": False, "reason": "vector_db_not_ready"},
                )
        except Exception as e:
            return APIResponse(
                success=False,
                message="Vector database check failed",
                data={"ready": False, "reason": f"vector_db_error: {str(e)}"},
            )

        return APIResponse(
            success=True,
            message="Service is ready",
            data={"ready": True},
        )

    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return APIResponse(
            success=False,
            message="Readiness check failed",
            data={"ready": False, "reason": f"check_error: {str(e)}"},
        )


@router.get("/live", response_model=APIResponse)
async def liveness_check():
    """
    Liveness check endpoint

    Indicates whether the service is alive and responsive.
    This is a lightweight check that should always return 200
    unless the service is completely unresponsive.
    """
    return APIResponse(
        success=True,
        message="Service is alive",
        data={
            "alive": True,
            "timestamp": datetime.now().isoformat(),
            "uptime": time.time() - startup_time,
        },
    )


@router.get("/detailed", response_model=APIResponse)
async def detailed_health_check(request: Request):
    """
    Detailed health check with comprehensive system information

    Provides detailed information about system components,
    memory usage, and performance metrics.
    """
    try:
        uptime = time.time() - startup_time
        memory = virtual_memory()

        # Get RAG system details
        rag_details = {}
        rag_system = getattr(request.app.state, "rag_system", None)

        if rag_system:
            try:
                status = rag_system.get_system_status()
                rag_details = {
                    "system_ready": status.get("system_ready", False),
                    "vectordb_ready": status.get("vectordb_ready", False),
                    "qa_chain_ready": status.get("qa_chain_ready", False),
                    "document_count": status.get("vectordb_info", {}).get("document_count", 0),
                    "total_sources": status.get("total_sources", 0),
                    "enabled_sources": status.get("enabled_sources", 0),
                    "last_build_time": status.get("last_build_time"),
                    "constraint_compliant": status.get("constraint_compliant", True),
                }
            except Exception as e:
                rag_details = {"error": str(e)}

        # System information
        system_info = {
            "uptime_seconds": uptime,
            "memory_total_gb": round(memory.total / (1024**3), 2),
            "memory_available_gb": round(memory.available / (1024**3), 2),
            "memory_used_percent": memory.percent,
            "pid": os.getpid(),
            "environment": {
                "api_mode": os.getenv("API_MODE", "browser"),
                "api_debug": os.getenv("API_DEBUG", "false"),
                "python_version": f"{os.sys.version_info.major}.{os.sys.version_info.minor}.{os.sys.version_info.micro}",
            },
        }

        return APIResponse(
            success=True,
            message="Detailed health information",
            data={
                "health": "healthy" if rag_details.get("system_ready", False) else "degraded",
                "rag_system": rag_details,
                "system": system_info,
                "timestamp": datetime.now().isoformat(),
            },
        )

    except Exception as e:
        logger.error(f"Detailed health check failed: {e}")
        return APIResponse(
            success=False,
            message="Detailed health check failed",
            data={"error": str(e)},
        )