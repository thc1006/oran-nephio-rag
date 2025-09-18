"""
O-RAN × Nephio RAG API Package

Developer-friendly REST API for querying the RAG system with:
- Comprehensive query endpoints
- Document management
- Health monitoring
- Rate limiting and authentication
- Request/response validation
- Error handling and logging
"""

from .main import app, create_app

__version__ = "1.0.0"
__author__ = "O-RAN × Nephio RAG Development Team"

__all__ = ["app", "create_app"]