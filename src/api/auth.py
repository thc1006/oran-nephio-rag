"""
Authentication and authorization middleware
"""

import logging
import os
import time
from typing import Optional

from fastapi import HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-super-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

# API Key Configuration
API_KEY = os.getenv("API_KEY", "")
API_KEY_HEADER = "X-API-Key"

# Authentication mode
AUTH_MODE = os.getenv("AUTH_MODE", "optional")  # "required", "optional", "disabled"

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer for JWT tokens
security = HTTPBearer(auto_error=False)


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Authentication middleware that handles API keys and JWT tokens
    """

    def __init__(self, app):
        super().__init__(app)
        self.public_paths = {
            "/",
            "/health",
            "/health/live",
            "/health/ready",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/metrics",
        }

    async def dispatch(self, request: Request, call_next):
        # Skip authentication for public paths
        if request.url.path in self.public_paths:
            return await call_next(request)

        # Skip authentication if disabled
        if AUTH_MODE == "disabled":
            return await call_next(request)

        # Check authentication
        authenticated = False
        user_info = None

        try:
            # Try API key authentication first
            api_key = request.headers.get(API_KEY_HEADER)
            if api_key and API_KEY and api_key == API_KEY:
                authenticated = True
                user_info = {"type": "api_key", "user": "api_user"}
                logger.debug("Authenticated via API key")

            # Try JWT authentication if API key failed
            if not authenticated:
                auth_header = request.headers.get("Authorization")
                if auth_header and auth_header.startswith("Bearer "):
                    token = auth_header.split(" ")[1]
                    user_info = verify_jwt_token(token)
                    if user_info:
                        authenticated = True
                        logger.debug(f"Authenticated via JWT: {user_info.get('sub')}")

        except Exception as e:
            logger.warning(f"Authentication error: {e}")

        # Store authentication info in request state
        request.state.authenticated = authenticated
        request.state.user = user_info

        # Check if authentication is required
        if AUTH_MODE == "required" and not authenticated:
            return HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Add security headers
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"

        return response


def verify_jwt_token(token: str) -> Optional[dict]:
    """
    Verify JWT token and return user information
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None

        # Add token expiration check
        exp = payload.get("exp")
        if exp and time.time() > exp:
            return None

        return {
            "type": "jwt",
            "user": username,
            "exp": exp,
            "iat": payload.get("iat"),
        }

    except JWTError as e:
        logger.debug(f"JWT verification failed: {e}")
        return None


def create_access_token(data: dict) -> str:
    """
    Create a new JWT access token
    """
    to_encode = data.copy()
    expire = time.time() + (ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    to_encode.update({"exp": expire, "iat": time.time()})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password
    """
    return pwd_context.hash(password)


async def get_current_user(request: Request) -> Optional[dict]:
    """
    Dependency to get current authenticated user
    """
    # Return user info if authenticated
    if hasattr(request.state, "user") and request.state.user:
        return request.state.user

    # Return None if authentication is optional
    if AUTH_MODE == "optional":
        return None

    # Raise exception if authentication is required
    if AUTH_MODE == "required":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return None


def require_authentication(request: Request) -> dict:
    """
    Dependency that requires authentication
    """
    if not hasattr(request.state, "authenticated") or not request.state.authenticated:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return request.state.user


# Example user database (in production, use a real database)
DEMO_USERS = {
    "demo": {
        "username": "demo",
        "hashed_password": get_password_hash("demo123"),
        "email": "demo@example.com",
        "full_name": "Demo User",
        "disabled": False,
    },
    "admin": {
        "username": "admin",
        "hashed_password": get_password_hash("admin123"),
        "email": "admin@example.com",
        "full_name": "Admin User",
        "disabled": False,
    },
}


def authenticate_user(username: str, password: str) -> Optional[dict]:
    """
    Authenticate a user with username and password
    """
    user = DEMO_USERS.get(username)
    if not user:
        return None

    if not verify_password(password, user["hashed_password"]):
        return None

    if user.get("disabled", False):
        return None

    return user


# Rate limiting helpers
def get_user_identifier(request: Request) -> str:
    """
    Get a unique identifier for rate limiting
    """
    # Use authenticated user if available
    if hasattr(request.state, "user") and request.state.user:
        user_info = request.state.user
        if user_info["type"] == "jwt":
            return f"user:{user_info['user']}"
        elif user_info["type"] == "api_key":
            return "api_key:user"

    # Fall back to IP address
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return f"ip:{forwarded_for.split(',')[0].strip()}"

    client_host = request.client.host if request.client else "unknown"
    return f"ip:{client_host}"


# API Key validation helper
def validate_api_key(api_key: str) -> bool:
    """
    Validate an API key
    """
    # In production, validate against a database or external service
    return API_KEY and api_key == API_KEY


# Token blacklist (in production, use Redis or database)
TOKEN_BLACKLIST = set()


def is_token_blacklisted(token: str) -> bool:
    """
    Check if a token is blacklisted
    """
    return token in TOKEN_BLACKLIST


def blacklist_token(token: str) -> None:
    """
    Add a token to the blacklist
    """
    TOKEN_BLACKLIST.add(token)


# Security utilities
def check_permissions(user: dict, required_permission: str) -> bool:
    """
    Check if user has required permission
    """
    # Simple permission system - can be extended
    user_permissions = user.get("permissions", [])
    return required_permission in user_permissions or "admin" in user_permissions


def get_auth_info() -> dict:
    """
    Get authentication configuration information
    """
    return {
        "auth_mode": AUTH_MODE,
        "jwt_algorithm": ALGORITHM,
        "token_expire_minutes": ACCESS_TOKEN_EXPIRE_MINUTES,
        "api_key_header": API_KEY_HEADER,
        "api_key_configured": bool(API_KEY),
        "supported_methods": ["api_key", "jwt"],
    }