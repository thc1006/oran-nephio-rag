"""
Pydantic models for API request/response validation
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, validator


class APIResponse(BaseModel):
    """Base API response model"""

    success: bool = Field(..., description="Whether the request was successful")
    message: str = Field(..., description="Response message")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")


class ErrorResponse(BaseModel):
    """Error response model"""

    success: bool = Field(False, description="Always false for errors")
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Error details")
    timestamp: datetime = Field(default_factory=datetime.now, description="Error timestamp")


class HealthResponse(BaseModel):
    """Health check response"""

    status: str = Field(..., description="Health status")
    version: str = Field(..., description="API version")
    uptime: float = Field(..., description="Uptime in seconds")
    components: Dict[str, str] = Field(..., description="Component health status")


class QueryRequest(BaseModel):
    """RAG query request model"""

    query: str = Field(..., min_length=1, max_length=1000, description="The question to ask")
    k: Optional[int] = Field(5, ge=1, le=20, description="Number of documents to retrieve")
    model: Optional[str] = Field(None, description="Model to use for generation")
    stream: Optional[bool] = Field(False, description="Whether to stream the response")
    include_sources: Optional[bool] = Field(True, description="Whether to include source documents")
    context_length: Optional[int] = Field(None, ge=100, le=8000, description="Maximum context length")

    @validator("query")
    def query_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError("Query cannot be empty")
        return v.strip()


class SourceDocument(BaseModel):
    """Source document model"""

    content: str = Field(..., description="Document content excerpt")
    metadata: Dict[str, Any] = Field(..., description="Document metadata")
    similarity_score: Optional[float] = Field(None, description="Similarity score")
    source_type: Optional[str] = Field(None, description="Source type (nephio, oran_sc)")
    url: Optional[str] = Field(None, description="Source URL")


class QueryResponse(BaseModel):
    """RAG query response model"""

    answer: str = Field(..., description="Generated answer")
    sources: List[SourceDocument] = Field(default_factory=list, description="Source documents")
    query_time: float = Field(..., description="Query processing time in seconds")
    context_used: int = Field(..., description="Number of context documents used")
    retrieval_scores: List[float] = Field(default_factory=list, description="Retrieval similarity scores")
    generation_method: str = Field(..., description="Method used for generation")
    constraint_compliant: bool = Field(True, description="Whether response is constraint compliant")


class DocumentRequest(BaseModel):
    """Document upload/update request"""

    url: str = Field(..., description="Document URL")
    source_type: str = Field(..., description="Source type (nephio, oran_sc)")
    description: str = Field(..., description="Document description")
    priority: int = Field(3, ge=1, le=5, description="Priority level (1-5)")
    enabled: bool = Field(True, description="Whether document is enabled")

    @validator("source_type")
    def validate_source_type(cls, v):
        valid_types = ["nephio", "oran_sc"]
        if v not in valid_types:
            raise ValueError(f"source_type must be one of: {valid_types}")
        return v


class DocumentResponse(BaseModel):
    """Document information response"""

    id: str = Field(..., description="Document ID")
    url: str = Field(..., description="Document URL")
    source_type: str = Field(..., description="Source type")
    description: str = Field(..., description="Document description")
    priority: int = Field(..., description="Priority level")
    enabled: bool = Field(..., description="Whether document is enabled")
    last_updated: Optional[datetime] = Field(None, description="Last update time")
    content_length: Optional[int] = Field(None, description="Content length in characters")
    status: str = Field(..., description="Document status")


class DocumentListResponse(BaseModel):
    """Document list response"""

    documents: List[DocumentResponse] = Field(..., description="List of documents")
    total: int = Field(..., description="Total number of documents")
    enabled: int = Field(..., description="Number of enabled documents")
    by_source_type: Dict[str, int] = Field(..., description="Count by source type")


class SystemStatusResponse(BaseModel):
    """System status response"""

    system_ready: bool = Field(..., description="Whether system is ready")
    vectordb_ready: bool = Field(..., description="Whether vector database is ready")
    qa_chain_ready: bool = Field(..., description="Whether Q&A chain is ready")
    last_build_time: Optional[datetime] = Field(None, description="Last database build time")
    document_count: int = Field(..., description="Number of documents in database")
    total_sources: int = Field(..., description="Total number of sources")
    enabled_sources: int = Field(..., description="Number of enabled sources")
    constraint_compliant: bool = Field(True, description="Whether system is constraint compliant")
    integration_method: str = Field(..., description="Integration method used")
    uptime: float = Field(..., description="System uptime in seconds")


class UpdateDatabaseRequest(BaseModel):
    """Database update request"""

    force_rebuild: bool = Field(False, description="Whether to force rebuild")
    source_urls: Optional[List[str]] = Field(None, description="Specific URLs to update")
    source_types: Optional[List[str]] = Field(None, description="Specific source types to update")


class UpdateDatabaseResponse(BaseModel):
    """Database update response"""

    success: bool = Field(..., description="Whether update was successful")
    documents_processed: int = Field(..., description="Number of documents processed")
    documents_added: int = Field(..., description="Number of documents added")
    documents_updated: int = Field(..., description="Number of documents updated")
    processing_time: float = Field(..., description="Processing time in seconds")
    errors: List[str] = Field(default_factory=list, description="Any errors encountered")


class RateLimitInfo(BaseModel):
    """Rate limit information"""

    limit: int = Field(..., description="Rate limit")
    remaining: int = Field(..., description="Remaining requests")
    reset_time: datetime = Field(..., description="Reset time")
    retry_after: Optional[int] = Field(None, description="Retry after seconds")


class SearchRequest(BaseModel):
    """Advanced search request"""

    query: str = Field(..., min_length=1, description="Search query")
    filters: Optional[Dict[str, Any]] = Field(None, description="Search filters")
    source_types: Optional[List[str]] = Field(None, description="Filter by source types")
    priority_range: Optional[List[int]] = Field(None, description="Priority range [min, max]")
    k: Optional[int] = Field(10, ge=1, le=50, description="Number of results")
    score_threshold: Optional[float] = Field(0.0, ge=0.0, le=1.0, description="Minimum similarity score")


class SearchResponse(BaseModel):
    """Advanced search response"""

    results: List[SourceDocument] = Field(..., description="Search results")
    total_found: int = Field(..., description="Total number of results found")
    query_time: float = Field(..., description="Search time in seconds")
    filters_applied: Dict[str, Any] = Field(..., description="Filters that were applied")


class BulkQueryRequest(BaseModel):
    """Bulk query request for batch processing"""

    queries: List[str] = Field(..., min_items=1, max_items=10, description="List of queries")
    k: Optional[int] = Field(5, ge=1, le=20, description="Number of documents per query")
    include_sources: Optional[bool] = Field(False, description="Whether to include sources")


class BulkQueryResponse(BaseModel):
    """Bulk query response"""

    results: List[QueryResponse] = Field(..., description="Query results")
    total_processed: int = Field(..., description="Total queries processed")
    total_time: float = Field(..., description="Total processing time")
    average_time: float = Field(..., description="Average time per query")


class ConfigResponse(BaseModel):
    """Configuration response"""

    api_mode: str = Field(..., description="API mode")
    model_name: str = Field(..., description="Model name")
    chunk_size: int = Field(..., description="Chunk size")
    chunk_overlap: int = Field(..., description="Chunk overlap")
    max_tokens: int = Field(..., description="Maximum tokens")
    temperature: float = Field(..., description="Temperature setting")
    retriever_k: int = Field(..., description="Default retriever K")
    browser_headless: bool = Field(..., description="Browser headless mode")
    constraint_compliant: bool = Field(True, description="Constraint compliance")


class MetricsResponse(BaseModel):
    """Metrics response"""

    requests_total: int = Field(..., description="Total requests")
    queries_total: int = Field(..., description="Total queries")
    average_query_time: float = Field(..., description="Average query time")
    success_rate: float = Field(..., description="Success rate")
    uptime: float = Field(..., description="Uptime in seconds")
    memory_usage: Dict[str, float] = Field(..., description="Memory usage statistics")