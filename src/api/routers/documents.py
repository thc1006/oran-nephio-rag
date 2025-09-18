"""
Document management endpoints
"""

import logging
import time
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status

from ..auth import get_current_user
from ..models import (
    APIResponse,
    DocumentListResponse,
    DocumentRequest,
    DocumentResponse,
    UpdateDatabaseRequest,
    UpdateDatabaseResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=DocumentListResponse)
async def list_documents(
    request: Request,
    source_type: Optional[str] = None,
    enabled_only: bool = True,
    current_user: Optional[dict] = Depends(get_current_user),
):
    """
    List all configured document sources

    Returns information about all document sources configured in the system,
    including their status, priority, and metadata.

    - **source_type**: Filter by source type (nephio, oran_sc)
    - **enabled_only**: Show only enabled sources (default: true)
    """
    try:
        # Get config from app state
        config = request.app.state.config

        # Get all sources
        all_sources = config.OFFICIAL_SOURCES

        # Apply filters
        filtered_sources = []
        for source in all_sources:
            # Filter by enabled status
            if enabled_only and not source.enabled:
                continue

            # Filter by source type
            if source_type and source.source_type != source_type:
                continue

            filtered_sources.append(source)

        # Convert to response format
        documents = []
        for i, source in enumerate(filtered_sources):
            doc_response = DocumentResponse(
                id=str(i),
                url=source.url,
                source_type=source.source_type,
                description=source.description,
                priority=source.priority,
                enabled=source.enabled,
                last_updated=None,  # Could be enhanced to track actual update times
                content_length=None,  # Could be enhanced to track content length
                status="configured",
            )
            documents.append(doc_response)

        # Count by source type
        by_source_type = {}
        for doc in documents:
            source_type_count = by_source_type.get(doc.source_type, 0)
            by_source_type[doc.source_type] = source_type_count + 1

        # Create response
        response = DocumentListResponse(
            documents=documents,
            total=len(documents),
            enabled=len([d for d in documents if d.enabled]),
            by_source_type=by_source_type,
        )

        logger.info(f"Listed {len(documents)} documents")
        return response

    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list documents",
        )


@router.post("/", response_model=APIResponse)
async def add_document_source(
    request: Request,
    document: DocumentRequest,
    current_user: Optional[dict] = Depends(get_current_user),
):
    """
    Add a new document source to the configuration

    Adds a new document source to the system configuration.
    The document will be included in future database rebuilds.

    - **url**: Document URL (required)
    - **source_type**: Source type - nephio or oran_sc (required)
    - **description**: Human-readable description (required)
    - **priority**: Priority level 1-5 (default: 3)
    - **enabled**: Whether the source is enabled (default: true)
    """
    try:
        # Get config from app state
        config = request.app.state.config

        # Check if URL already exists
        existing_urls = [source.url for source in config.OFFICIAL_SOURCES]
        if document.url in existing_urls:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Document source with this URL already exists",
            )

        # Create new document source
        from ...config import DocumentSource

        new_source = DocumentSource(
            url=document.url,
            source_type=document.source_type,
            description=document.description,
            priority=document.priority,
            enabled=document.enabled,
        )

        # Add to configuration
        config.add_custom_source(new_source)

        logger.info(f"Added new document source: {document.description}")

        return APIResponse(
            success=True,
            message="Document source added successfully",
            data={
                "url": document.url,
                "source_type": document.source_type,
                "description": document.description,
                "requires_rebuild": True,
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding document source: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add document source",
        )


@router.put("/{document_id}/enable", response_model=APIResponse)
async def enable_document_source(
    request: Request,
    document_id: str,
    current_user: Optional[dict] = Depends(get_current_user),
):
    """
    Enable a document source

    Enables a previously disabled document source.
    The document will be included in future database rebuilds.
    """
    try:
        # Get config from app state
        config = request.app.state.config

        # Find document by ID (using index as ID)
        try:
            doc_index = int(document_id)
            if 0 <= doc_index < len(config.OFFICIAL_SOURCES):
                source = config.OFFICIAL_SOURCES[doc_index]
                source.enabled = True

                logger.info(f"Enabled document source: {source.description}")

                return APIResponse(
                    success=True,
                    message="Document source enabled successfully",
                    data={"url": source.url, "enabled": True},
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Document source not found",
                )
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid document ID",
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error enabling document source: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to enable document source",
        )


@router.put("/{document_id}/disable", response_model=APIResponse)
async def disable_document_source(
    request: Request,
    document_id: str,
    current_user: Optional[dict] = Depends(get_current_user),
):
    """
    Disable a document source

    Disables a document source so it won't be included in future database rebuilds.
    """
    try:
        # Get config from app state
        config = request.app.state.config

        # Find document by ID (using index as ID)
        try:
            doc_index = int(document_id)
            if 0 <= doc_index < len(config.OFFICIAL_SOURCES):
                source = config.OFFICIAL_SOURCES[doc_index]
                source.enabled = False

                logger.info(f"Disabled document source: {source.description}")

                return APIResponse(
                    success=True,
                    message="Document source disabled successfully",
                    data={"url": source.url, "enabled": False},
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Document source not found",
                )
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid document ID",
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error disabling document source: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to disable document source",
        )


@router.post("/update", response_model=UpdateDatabaseResponse)
async def update_database(
    request: Request,
    update_request: UpdateDatabaseRequest,
    current_user: Optional[dict] = Depends(get_current_user),
):
    """
    Update the vector database with latest documents

    Reloads documents from all enabled sources and rebuilds the vector database.
    This operation may take several minutes depending on the number of documents.

    - **force_rebuild**: Force complete rebuild even if database exists
    - **source_urls**: Only update specific URLs (optional)
    - **source_types**: Only update specific source types (optional)
    """
    start_time = time.time()

    try:
        # Get RAG system from app state
        rag_system = request.app.state.rag_system

        if not rag_system:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="RAG system not available",
            )

        logger.info("Starting database update...")

        # If specific sources are requested, we might need to implement filtering
        # For now, we'll do a full update
        if update_request.source_urls or update_request.source_types:
            logger.warning("Specific source filtering not yet implemented, performing full update")

        # Perform the update
        success = rag_system.update_documents()

        processing_time = time.time() - start_time

        if success:
            # Get updated statistics
            try:
                status_info = rag_system.get_system_status()
                doc_count = status_info.get("vectordb_info", {}).get("document_count", 0)
                total_sources = status_info.get("total_sources", 0)
            except Exception:
                doc_count = 0
                total_sources = 0

            response = UpdateDatabaseResponse(
                success=True,
                documents_processed=total_sources,
                documents_added=doc_count,  # Simplified - could track actual additions
                documents_updated=0,  # Could be enhanced to track updates
                processing_time=processing_time,
                errors=[],
            )

            logger.info(f"Database update completed successfully in {processing_time:.2f}s")
            return response

        else:
            response = UpdateDatabaseResponse(
                success=False,
                documents_processed=0,
                documents_added=0,
                documents_updated=0,
                processing_time=processing_time,
                errors=["Database update failed"],
            )

            logger.error(f"Database update failed after {processing_time:.2f}s")
            return response

    except HTTPException:
        raise
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(f"Error during database update: {e}")

        return UpdateDatabaseResponse(
            success=False,
            documents_processed=0,
            documents_added=0,
            documents_updated=0,
            processing_time=processing_time,
            errors=[str(e)],
        )


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document_details(
    request: Request,
    document_id: str,
    current_user: Optional[dict] = Depends(get_current_user),
):
    """
    Get details for a specific document source

    Returns detailed information about a specific document source
    including its configuration and status.
    """
    try:
        # Get config from app state
        config = request.app.state.config

        # Find document by ID (using index as ID)
        try:
            doc_index = int(document_id)
            if 0 <= doc_index < len(config.OFFICIAL_SOURCES):
                source = config.OFFICIAL_SOURCES[doc_index]

                response = DocumentResponse(
                    id=document_id,
                    url=source.url,
                    source_type=source.source_type,
                    description=source.description,
                    priority=source.priority,
                    enabled=source.enabled,
                    last_updated=None,  # Could be enhanced
                    content_length=None,  # Could be enhanced
                    status="configured",
                )

                return response

            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Document source not found",
                )

        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid document ID",
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting document details: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get document details",
        )