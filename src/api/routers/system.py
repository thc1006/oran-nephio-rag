"""
System management and monitoring endpoints
"""

import logging
import os
import time
from datetime import datetime

from fastapi import APIRouter, Depends, Request
from psutil import Process, virtual_memory

from ..auth import get_current_user
from ..models import (
    APIResponse,
    ConfigResponse,
    MetricsResponse,
    SystemStatusResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter()

# Track startup time for metrics
startup_time = time.time()


@router.get("/status", response_model=SystemStatusResponse)
async def get_system_status(
    request: Request,
    current_user: dict = Depends(get_current_user),
):
    """
    Get comprehensive system status

    Returns detailed information about the RAG system status,
    including vector database health, component readiness,
    and performance metrics.
    """
    try:
        uptime = time.time() - startup_time

        # Get RAG system from app state
        rag_system = getattr(request.app.state, "rag_system", None)

        if not rag_system:
            return SystemStatusResponse(
                system_ready=False,
                vectordb_ready=False,
                qa_chain_ready=False,
                last_build_time=None,
                document_count=0,
                total_sources=0,
                enabled_sources=0,
                constraint_compliant=True,
                integration_method="browser_automation",
                uptime=uptime,
            )

        # Get detailed status from RAG system
        try:
            status = rag_system.get_system_status()

            # Parse last build time
            last_build_time = None
            if status.get("last_build_time"):
                try:
                    last_build_time = datetime.fromisoformat(status["last_build_time"])
                except (ValueError, TypeError):
                    pass

            response = SystemStatusResponse(
                system_ready=status.get("system_ready", False),
                vectordb_ready=status.get("vectordb_ready", False),
                qa_chain_ready=status.get("qa_chain_ready", False),
                last_build_time=last_build_time,
                document_count=status.get("vectordb_info", {}).get("document_count", 0),
                total_sources=status.get("total_sources", 0),
                enabled_sources=status.get("enabled_sources", 0),
                constraint_compliant=status.get("constraint_compliant", True),
                integration_method=status.get("integration_method", "browser_automation"),
                uptime=uptime,
            )

            return response

        except Exception as e:
            logger.error(f"Error getting RAG system status: {e}")
            return SystemStatusResponse(
                system_ready=False,
                vectordb_ready=False,
                qa_chain_ready=False,
                last_build_time=None,
                document_count=0,
                total_sources=0,
                enabled_sources=0,
                constraint_compliant=True,
                integration_method="browser_automation",
                uptime=uptime,
            )

    except Exception as e:
        logger.error(f"Error in system status endpoint: {e}")
        return SystemStatusResponse(
            system_ready=False,
            vectordb_ready=False,
            qa_chain_ready=False,
            last_build_time=None,
            document_count=0,
            total_sources=0,
            enabled_sources=0,
            constraint_compliant=True,
            integration_method="browser_automation",
            uptime=time.time() - startup_time,
        )


@router.get("/config", response_model=ConfigResponse)
async def get_system_config(
    request: Request,
    current_user: dict = Depends(get_current_user),
):
    """
    Get system configuration

    Returns the current system configuration including
    API mode, model settings, and processing parameters.
    """
    try:
        # Get config from app state
        config = getattr(request.app.state, "config", None)

        if not config:
            raise Exception("Configuration not available")

        # Get configuration summary
        config_summary = config.get_config_summary()

        response = ConfigResponse(
            api_mode=config_summary.get("api_mode", "unknown"),
            model_name=config_summary.get("puter_model", "unknown"),
            chunk_size=config_summary.get("chunk_size", 1024),
            chunk_overlap=config_summary.get("chunk_overlap", 200),
            max_tokens=config_summary.get("max_tokens", 4000),
            temperature=config_summary.get("temperature", 0.1),
            retriever_k=config.RETRIEVER_K,
            browser_headless=config_summary.get("browser_headless", True),
            constraint_compliant=config_summary.get("constraint_compliant", True),
        )

        return response

    except Exception as e:
        logger.error(f"Error getting system config: {e}")
        # Return default values
        return ConfigResponse(
            api_mode="unknown",
            model_name="unknown",
            chunk_size=1024,
            chunk_overlap=200,
            max_tokens=4000,
            temperature=0.1,
            retriever_k=5,
            browser_headless=True,
            constraint_compliant=True,
        )


@router.get("/metrics", response_model=MetricsResponse)
async def get_system_metrics(
    request: Request,
    current_user: dict = Depends(get_current_user),
):
    """
    Get system performance metrics

    Returns performance metrics including request counts,
    processing times, and resource usage statistics.
    """
    try:
        uptime = time.time() - startup_time

        # Get memory information
        memory = virtual_memory()
        process = Process(os.getpid())
        process_memory = process.memory_info()

        memory_usage = {
            "total_gb": round(memory.total / (1024**3), 2),
            "available_gb": round(memory.available / (1024**3), 2),
            "used_percent": memory.percent,
            "process_rss_mb": round(process_memory.rss / (1024**2), 2),
            "process_vms_mb": round(process_memory.vms / (1024**2), 2),
        }

        # These would typically come from a metrics collection system
        # For now, we'll provide placeholder values
        response = MetricsResponse(
            requests_total=0,  # Could be tracked with middleware
            queries_total=0,  # Could be tracked in query endpoints
            average_query_time=0.0,  # Could be calculated from historical data
            success_rate=1.0,  # Could be calculated from success/failure counts
            uptime=uptime,
            memory_usage=memory_usage,
        )

        return response

    except Exception as e:
        logger.error(f"Error getting system metrics: {e}")
        return MetricsResponse(
            requests_total=0,
            queries_total=0,
            average_query_time=0.0,
            success_rate=0.0,
            uptime=time.time() - startup_time,
            memory_usage={"error": str(e)},
        )


@router.post("/restart", response_model=APIResponse)
async def restart_system(
    request: Request,
    current_user: dict = Depends(get_current_user),
):
    """
    Restart the RAG system

    Reinitializes the RAG system components including
    vector database and query processing chain.
    """
    try:
        # Get RAG system from app state
        rag_system = getattr(request.app.state, "rag_system", None)

        if not rag_system:
            return APIResponse(
                success=False,
                message="RAG system not available for restart",
            )

        logger.info("Restarting RAG system...")

        # Try to reinitialize the system
        success = rag_system.initialize_system(force_rebuild=False)

        if success:
            logger.info("RAG system restarted successfully")
            return APIResponse(
                success=True,
                message="RAG system restarted successfully",
                data={"restart_time": datetime.now().isoformat()},
            )
        else:
            logger.error("RAG system restart failed")
            return APIResponse(
                success=False,
                message="RAG system restart failed",
            )

    except Exception as e:
        logger.error(f"Error restarting system: {e}")
        return APIResponse(
            success=False,
            message="System restart failed",
            data={"error": str(e)},
        )


@router.post("/rebuild", response_model=APIResponse)
async def rebuild_database(
    request: Request,
    current_user: dict = Depends(get_current_user),
):
    """
    Force rebuild the vector database

    Forces a complete rebuild of the vector database
    by reloading all documents from sources.
    This operation may take several minutes.
    """
    try:
        # Get RAG system from app state
        rag_system = getattr(request.app.state, "rag_system", None)

        if not rag_system:
            return APIResponse(
                success=False,
                message="RAG system not available for rebuild",
            )

        logger.info("Starting database rebuild...")
        start_time = time.time()

        # Force rebuild
        success = rag_system.initialize_system(force_rebuild=True)

        rebuild_time = time.time() - start_time

        if success:
            logger.info(f"Database rebuild completed in {rebuild_time:.2f}s")
            return APIResponse(
                success=True,
                message="Database rebuilt successfully",
                data={
                    "rebuild_time": rebuild_time,
                    "completed_at": datetime.now().isoformat(),
                },
            )
        else:
            logger.error(f"Database rebuild failed after {rebuild_time:.2f}s")
            return APIResponse(
                success=False,
                message="Database rebuild failed",
                data={"rebuild_time": rebuild_time},
            )

    except Exception as e:
        logger.error(f"Error rebuilding database: {e}")
        return APIResponse(
            success=False,
            message="Database rebuild failed",
            data={"error": str(e)},
        )


@router.get("/info", response_model=APIResponse)
async def get_system_info(request: Request):
    """
    Get basic system information

    Returns basic information about the API including
    version, environment, and capability information.
    """
    try:
        # Get config from app state
        config = getattr(request.app.state, "config", None)

        info = {
            "name": "O-RAN × Nephio RAG API",
            "version": "1.0.0",
            "description": "Developer-friendly REST API for O-RAN and Nephio knowledge retrieval",
            "api_mode": getattr(config, "API_MODE", "unknown") if config else "unknown",
            "constraint_compliant": True,
            "integration_method": "browser_automation",
            "supported_models": ["claude-sonnet-4", "claude-opus-4", "claude-sonnet-3.7"],
            "capabilities": [
                "document_retrieval",
                "question_answering",
                "semantic_search",
                "document_management",
                "system_monitoring",
            ],
            "endpoints": {
                "health": "/health",
                "docs": "/docs",
                "query": "/api/v1/query",
                "documents": "/api/v1/documents",
                "system": "/api/v1/system",
            },
        }

        return APIResponse(
            success=True,
            message="System information",
            data=info,
        )

    except Exception as e:
        logger.error(f"Error getting system info: {e}")
        return APIResponse(
            success=False,
            message="Failed to get system information",
            data={"error": str(e)},
        )