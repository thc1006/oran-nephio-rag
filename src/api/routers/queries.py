"""
Query endpoints for RAG system
"""

import logging
import time
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

from ..auth import get_current_user
from ..models import (
    APIResponse,
    BulkQueryRequest,
    BulkQueryResponse,
    QueryRequest,
    QueryResponse,
    SearchRequest,
    SearchResponse,
    SourceDocument,
)

logger = logging.getLogger(__name__)

router = APIRouter()

# Rate limiter
limiter = Limiter(key_func=get_remote_address)


@router.post("/", response_model=QueryResponse)
@limiter.limit("10/minute")  # Rate limit: 10 queries per minute
async def query_rag(
    request: Request,
    query_request: QueryRequest,
    current_user: Optional[dict] = Depends(get_current_user),
):
    """
    Query the RAG system with a question

    This endpoint processes natural language questions and returns
    answers based on the O-RAN and Nephio documentation.

    - **query**: The question to ask (required)
    - **k**: Number of source documents to retrieve (1-20, default: 5)
    - **model**: Model to use for generation (optional)
    - **stream**: Whether to stream the response (default: false)
    - **include_sources**: Include source documents (default: true)
    - **context_length**: Maximum context length (100-8000)
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

        # Check if system is ready
        if not rag_system.is_ready:
            # Try to initialize
            if not rag_system.initialize_system():
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="RAG system not ready and failed to initialize",
                )

        # Prepare query parameters
        query_params = {
            "k": query_request.k,
        }

        if query_request.model:
            query_params["model"] = query_request.model

        if query_request.stream:
            query_params["stream"] = query_request.stream

        if query_request.context_length:
            query_params["context_length"] = query_request.context_length

        # Execute query
        logger.info(f"Processing query: {query_request.query[:100]}...")
        result = rag_system.query(query_request.query, **query_params)

        # Check if query was successful
        if not result.get("success", True):
            error_msg = result.get("error", "Unknown error occurred")
            logger.error(f"Query failed: {error_msg}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Query processing failed: {error_msg}",
            )

        # Process sources if requested
        sources = []
        if query_request.include_sources and result.get("sources"):
            for source in result["sources"]:
                sources.append(
                    SourceDocument(
                        content=source.get("content", ""),
                        metadata=source.get("metadata", {}),
                        similarity_score=source.get("similarity_score"),
                        source_type=source.get("metadata", {}).get("source_type"),
                        url=source.get("metadata", {}).get("url"),
                    )
                )

        # Create response
        query_time = time.time() - start_time
        response = QueryResponse(
            answer=result.get("answer", ""),
            sources=sources,
            query_time=query_time,
            context_used=result.get("context_used", 0),
            retrieval_scores=result.get("retrieval_scores", []),
            generation_method=result.get("generation_method", "unknown"),
            constraint_compliant=result.get("constraint_compliant", True),
        )

        logger.info(f"Query completed in {query_time:.2f}s")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in query processing: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during query processing",
        )


@router.post("/search", response_model=SearchResponse)
@limiter.limit("20/minute")  # Higher limit for search
async def search_documents(
    request: Request,
    search_request: SearchRequest,
    current_user: Optional[dict] = Depends(get_current_user),
):
    """
    Search for documents without generating answers

    This endpoint performs similarity search in the vector database
    and returns matching documents with their similarity scores.

    - **query**: The search query (required)
    - **k**: Number of results to return (1-50, default: 10)
    - **filters**: Additional search filters
    - **source_types**: Filter by source types (nephio, oran_sc)
    - **priority_range**: Filter by priority range [min, max]
    - **score_threshold**: Minimum similarity score (0.0-1.0)
    """
    start_time = time.time()

    try:
        # Get RAG system from app state
        rag_system = request.app.state.rag_system

        if not rag_system or not rag_system.is_ready:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="RAG system not available",
            )

        # Perform similarity search
        vector_manager = rag_system.vector_manager
        similar_docs = vector_manager.search_similar(
            search_request.query, k=search_request.k
        )

        # Apply additional filters
        filtered_docs = []
        filters_applied = {}

        for doc, score in similar_docs:
            # Score threshold filter
            if (
                search_request.score_threshold
                and score < search_request.score_threshold
            ):
                continue

            # Source type filter
            if search_request.source_types:
                doc_source_type = doc.metadata.get("source_type")
                if doc_source_type not in search_request.source_types:
                    continue
                filters_applied["source_types"] = search_request.source_types

            # Priority filter
            if search_request.priority_range:
                doc_priority = doc.metadata.get("priority", 3)
                min_pri, max_pri = search_request.priority_range
                if not (min_pri <= doc_priority <= max_pri):
                    continue
                filters_applied["priority_range"] = search_request.priority_range

            # Convert to SourceDocument
            source_doc = SourceDocument(
                content=doc.page_content[:500] + "..."
                if len(doc.page_content) > 500
                else doc.page_content,
                metadata=doc.metadata,
                similarity_score=float(score),
                source_type=doc.metadata.get("source_type"),
                url=doc.metadata.get("url"),
            )
            filtered_docs.append(source_doc)

        # Apply score threshold filter
        if search_request.score_threshold:
            filters_applied["score_threshold"] = search_request.score_threshold

        query_time = time.time() - start_time

        response = SearchResponse(
            results=filtered_docs,
            total_found=len(filtered_docs),
            query_time=query_time,
            filters_applied=filters_applied,
        )

        logger.info(f"Search completed: {len(filtered_docs)} results in {query_time:.2f}s")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in document search: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during search",
        )


@router.post("/bulk", response_model=BulkQueryResponse)
@limiter.limit("2/minute")  # Lower limit for bulk operations
async def bulk_query(
    request: Request,
    bulk_request: BulkQueryRequest,
    current_user: Optional[dict] = Depends(get_current_user),
):
    """
    Process multiple queries in a single request

    This endpoint allows batch processing of multiple queries.
    Useful for evaluation or bulk processing scenarios.

    - **queries**: List of queries to process (1-10 queries max)
    - **k**: Number of documents per query (default: 5)
    - **include_sources**: Include source documents (default: false for performance)
    """
    start_time = time.time()

    try:
        # Get RAG system from app state
        rag_system = request.app.state.rag_system

        if not rag_system or not rag_system.is_ready:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="RAG system not available",
            )

        results = []
        total_processed = 0

        for query_text in bulk_request.queries:
            try:
                # Process individual query
                query_start = time.time()

                result = rag_system.query(
                    query_text,
                    k=bulk_request.k,
                )

                # Process sources if requested
                sources = []
                if bulk_request.include_sources and result.get("sources"):
                    for source in result["sources"]:
                        sources.append(
                            SourceDocument(
                                content=source.get("content", ""),
                                metadata=source.get("metadata", {}),
                                similarity_score=source.get("similarity_score"),
                                source_type=source.get("metadata", {}).get("source_type"),
                                url=source.get("metadata", {}).get("url"),
                            )
                        )

                query_time = time.time() - query_start

                query_response = QueryResponse(
                    answer=result.get("answer", ""),
                    sources=sources,
                    query_time=query_time,
                    context_used=result.get("context_used", 0),
                    retrieval_scores=result.get("retrieval_scores", []),
                    generation_method=result.get("generation_method", "unknown"),
                    constraint_compliant=result.get("constraint_compliant", True),
                )

                results.append(query_response)
                total_processed += 1

            except Exception as e:
                logger.error(f"Error processing query '{query_text}': {e}")
                # Add error response
                error_response = QueryResponse(
                    answer=f"Error processing query: {str(e)}",
                    sources=[],
                    query_time=0.0,
                    context_used=0,
                    retrieval_scores=[],
                    generation_method="error",
                    constraint_compliant=False,
                )
                results.append(error_response)

        total_time = time.time() - start_time
        average_time = total_time / max(len(results), 1)

        response = BulkQueryResponse(
            results=results,
            total_processed=total_processed,
            total_time=total_time,
            average_time=average_time,
        )

        logger.info(f"Bulk query completed: {total_processed} queries in {total_time:.2f}s")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in bulk query processing: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during bulk query processing",
        )