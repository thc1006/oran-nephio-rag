"""
Custom middleware for the API
"""

import logging
import time
import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging HTTP requests and responses
    """

    def __init__(self, app: Callable):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        # Log request
        start_time = time.time()
        client_ip = self.get_client_ip(request)

        logger.info(
            f"Request started - {request_id} - {request.method} {request.url} - Client: {client_ip}"
        )

        # Log request body for debugging (only for non-GET requests and smaller payloads)
        if request.method in ["POST", "PUT", "PATCH"] and hasattr(request, "body"):
            try:
                # Only log if content length is reasonable
                content_length = request.headers.get("content-length")
                if content_length and int(content_length) < 10000:  # 10KB limit
                    body = await request.body()
                    if body:
                        logger.debug(f"Request body - {request_id}: {body.decode('utf-8')[:500]}...")
            except Exception as e:
                logger.debug(f"Could not log request body - {request_id}: {e}")

        try:
            # Process request
            response = await call_next(request)

            # Calculate processing time
            process_time = time.time() - start_time

            # Log response
            logger.info(
                f"Request completed - {request_id} - "
                f"Status: {response.status_code} - "
                f"Time: {process_time:.3f}s"
            )

            # Add custom headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = f"{process_time:.3f}"

            return response

        except Exception as e:
            # Log error
            process_time = time.time() - start_time
            logger.error(
                f"Request failed - {request_id} - "
                f"Error: {str(e)} - "
                f"Time: {process_time:.3f}s",
                exc_info=True
            )
            raise

    def get_client_ip(self, request: Request) -> str:
        """Get the real client IP address"""
        # Check for forwarded headers
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # Fall back to direct connection
        if request.client:
            return request.client.host

        return "unknown"


class SecurityMiddleware(BaseHTTPMiddleware):
    """
    Middleware for adding security headers and basic security checks
    """

    def __init__(self, app: Callable):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Basic security checks
        if not self.is_request_safe(request):
            logger.warning(f"Potentially unsafe request blocked: {request.url}")
            return Response(
                content="Request blocked for security reasons",
                status_code=400,
                headers={"Content-Type": "text/plain"}
            )

        # Process request
        response = await call_next(request)

        # Add security headers
        self.add_security_headers(response)

        return response

    def is_request_safe(self, request: Request) -> bool:
        """Perform basic security checks on the request"""

        # Check for suspicious patterns in URL
        suspicious_patterns = [
            "../",  # Path traversal
            "..\\",  # Windows path traversal
            "<script",  # XSS attempts
            "javascript:",  # JavaScript protocol
            "data:",  # Data protocol
        ]

        url_str = str(request.url).lower()
        for pattern in suspicious_patterns:
            if pattern in url_str:
                return False

        # Check User-Agent (basic bot detection)
        user_agent = request.headers.get("User-Agent", "").lower()
        suspicious_agents = [
            "sqlmap",
            "nikto",
            "nmap",
            "masscan",
            "dirb",
            "dirbuster",
        ]

        for agent in suspicious_agents:
            if agent in user_agent:
                return False

        # Check for excessively large headers
        for name, value in request.headers.items():
            if len(value) > 8192:  # 8KB limit per header
                return False

        return True

    def add_security_headers(self, response: Response) -> None:
        """Add security headers to the response"""

        # Basic security headers
        security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Content-Security-Policy": (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data:; "
                "font-src 'self'; "
                "connect-src 'self'; "
                "frame-ancestors 'none';"
            ),
        }

        # Add headers
        for name, value in security_headers.items():
            if name not in response.headers:
                response.headers[name] = value


class CacheMiddleware(BaseHTTPMiddleware):
    """
    Middleware for adding cache headers
    """

    def __init__(self, app: Callable):
        super().__init__(app)
        self.cache_patterns = {
            # Static content - cache for 1 hour
            "/docs": 3600,
            "/redoc": 3600,
            "/openapi.json": 3600,

            # Health checks - cache for 30 seconds
            "/health": 30,
            "/health/live": 10,
            "/health/ready": 30,

            # System info - cache for 5 minutes
            "/api/v1/system/info": 300,
            "/api/v1/system/config": 300,
        }

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)

        # Add cache headers based on path
        path = request.url.path
        cache_duration = self.get_cache_duration(path)

        if cache_duration > 0:
            response.headers["Cache-Control"] = f"public, max-age={cache_duration}"
        else:
            # No cache for dynamic content
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"

        return response

    def get_cache_duration(self, path: str) -> int:
        """Get cache duration for a given path"""

        # Exact matches
        if path in self.cache_patterns:
            return self.cache_patterns[path]

        # Pattern matches
        for pattern, duration in self.cache_patterns.items():
            if path.startswith(pattern):
                return duration

        # Default: no cache
        return 0


class CompressionMiddleware(BaseHTTPMiddleware):
    """
    Middleware for response compression (works with GZipMiddleware)
    """

    def __init__(self, app: Callable):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)

        # Add compression hints
        if "Content-Type" in response.headers:
            content_type = response.headers["Content-Type"]

            # Suggest compression for text-based content
            if any(ct in content_type for ct in ["text/", "application/json", "application/xml"]):
                if "Content-Encoding" not in response.headers:
                    response.headers["Vary"] = "Accept-Encoding"

        return response


class MetricsMiddleware(BaseHTTPMiddleware):
    """
    Middleware for collecting basic metrics
    """

    def __init__(self, app: Callable):
        super().__init__(app)
        # In production, you would use a proper metrics collection system
        self.metrics = {
            "requests_total": 0,
            "requests_by_method": {},
            "requests_by_status": {},
            "response_times": [],
        }

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()

        try:
            response = await call_next(request)

            # Record metrics
            process_time = time.time() - start_time
            self.record_metrics(request.method, response.status_code, process_time)

            return response

        except Exception as e:
            # Record error metrics
            process_time = time.time() - start_time
            self.record_metrics(request.method, 500, process_time)
            raise

    def record_metrics(self, method: str, status_code: int, response_time: float):
        """Record request metrics"""
        self.metrics["requests_total"] += 1

        # Count by method
        if method in self.metrics["requests_by_method"]:
            self.metrics["requests_by_method"][method] += 1
        else:
            self.metrics["requests_by_method"][method] = 1

        # Count by status
        status_group = f"{status_code // 100}xx"
        if status_group in self.metrics["requests_by_status"]:
            self.metrics["requests_by_status"][status_group] += 1
        else:
            self.metrics["requests_by_status"][status_group] = 1

        # Record response time (keep last 1000 entries)
        self.metrics["response_times"].append(response_time)
        if len(self.metrics["response_times"]) > 1000:
            self.metrics["response_times"] = self.metrics["response_times"][-1000:]

    def get_metrics(self) -> dict:
        """Get collected metrics"""
        avg_response_time = 0
        if self.metrics["response_times"]:
            avg_response_time = sum(self.metrics["response_times"]) / len(self.metrics["response_times"])

        return {
            "requests_total": self.metrics["requests_total"],
            "requests_by_method": self.metrics["requests_by_method"].copy(),
            "requests_by_status": self.metrics["requests_by_status"].copy(),
            "average_response_time": avg_response_time,
            "recent_response_times": len(self.metrics["response_times"]),
        }