"""
Rate limiting middleware for API endpoints
"""
from datetime import datetime, timedelta
from typing import Dict, Optional
from collections import defaultdict
import time

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


class InMemoryRateLimiter:
    """
    In-memory rate limiter using sliding window algorithm.
    Stores request timestamps per client identifier.
    """
    
    def __init__(self):
        # Format: {client_id: [(timestamp, endpoint), ...]}
        self.requests: Dict[str, list] = defaultdict(list)
        self.last_cleanup = time.time()
    
    def cleanup_old_requests(self, current_time: float, window_seconds: int = 3600):
        """Remove request records older than the window"""
        if current_time - self.last_cleanup > 300:  # Cleanup every 5 minutes
            cutoff_time = current_time - window_seconds
            for client_id in list(self.requests.keys()):
                self.requests[client_id] = [
                    (ts, ep) for ts, ep in self.requests[client_id] 
                    if ts > cutoff_time
                ]
                if not self.requests[client_id]:
                    del self.requests[client_id]
            self.last_cleanup = current_time
    
    def is_rate_limited(
        self, 
        client_id: str, 
        limit: int, 
        window_seconds: int,
        endpoint: str = ""
    ) -> tuple[bool, dict]:
        """
        Check if client has exceeded rate limit.
        
        Args:
            client_id: Unique identifier for the client (IP or user ID)
            limit: Maximum number of requests allowed
            window_seconds: Time window in seconds
            endpoint: Optional endpoint identifier for per-endpoint limits
            
        Returns:
            (is_limited, info_dict)
        """
        current_time = time.time()
        self.cleanup_old_requests(current_time, window_seconds)
        
        # Filter requests within the time window
        cutoff_time = current_time - window_seconds
        recent_requests = [
            (ts, ep) for ts, ep in self.requests[client_id]
            if ts > cutoff_time
        ]
        
        # Count requests for this endpoint (or all if endpoint is empty)
        if endpoint:
            request_count = sum(1 for ts, ep in recent_requests if ep == endpoint)
        else:
            request_count = len(recent_requests)
        
        # Calculate time until limit resets
        if recent_requests:
            oldest_request_time = min(ts for ts, _ in recent_requests)
            reset_time = int(oldest_request_time + window_seconds)
        else:
            reset_time = int(current_time + window_seconds)
        
        info = {
            "limit": limit,
            "remaining": max(0, limit - request_count),
            "reset": reset_time,
            "retry_after": max(0, int(reset_time - current_time))
        }
        
        is_limited = request_count >= limit
        
        if not is_limited:
            # Record this request
            self.requests[client_id].append((current_time, endpoint))
        
        return is_limited, info


# Global rate limiter instance
rate_limiter = InMemoryRateLimiter()


class RateLimitConfig:
    """Configuration for rate limiting rules"""
    
    # Default limits: (requests, window_seconds)
    DEFAULT_AUTHENTICATED = (100, 60)  # 100 requests per minute
    DEFAULT_UNAUTHENTICATED = (20, 60)  # 20 requests per minute
    
    # Endpoint-specific limits
    ENDPOINT_LIMITS = {
        # Authentication endpoints (stricter limits)
        "/api/v1/auth/register": (5, 300),  # 5 per 5 minutes
        "/api/v1/auth/login": (10, 300),  # 10 per 5 minutes
        "/api/v1/auth/refresh": (20, 300),  # 20 per 5 minutes
        "/api/v1/auth/forgot-password": (3, 3600),  # 3 per hour
        "/api/v1/auth/reset-password": (5, 3600),  # 5 per hour
        
        # AI endpoints (higher cost)
        "/api/v1/insights": (30, 60),  # 30 per minute
        "/api/v1/insights/generate": (10, 60),  # 10 per minute
        
        # Expensive operations
        "/api/v1/plaid/link": (10, 300),  # 10 per 5 minutes
        "/api/v1/plaid/sync": (20, 60),  # 20 per minute
        
        # Export endpoints
        "/api/v1/reports/export": (5, 300),  # 5 per 5 minutes
    }
    
    @classmethod
    def get_limit(cls, path: str, is_authenticated: bool) -> tuple[int, int]:
        """Get rate limit for a specific endpoint"""
        # Check for endpoint-specific limit
        if path in cls.ENDPOINT_LIMITS:
            return cls.ENDPOINT_LIMITS[path]
        
        # Use default based on authentication status
        if is_authenticated:
            return cls.DEFAULT_AUTHENTICATED
        else:
            return cls.DEFAULT_UNAUTHENTICATED


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware for FastAPI.
    Applies different limits based on authentication status and endpoint.
    """
    
    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health check and docs
        if request.url.path in ["/health", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)
        
        # Determine client identifier
        client_id = self._get_client_id(request)
        
        # Check if user is authenticated
        is_authenticated = self._is_authenticated(request)
        
        # Get rate limit for this endpoint
        limit, window = RateLimitConfig.get_limit(
            request.url.path, 
            is_authenticated
        )
        
        # Check rate limit
        is_limited, info = rate_limiter.is_rate_limited(
            client_id=client_id,
            limit=limit,
            window_seconds=window,
            endpoint=request.url.path
        )
        
        if is_limited:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "Rate limit exceeded",
                    "limit": info["limit"],
                    "window_seconds": window,
                    "retry_after": info["retry_after"]
                },
                headers={
                    "X-RateLimit-Limit": str(info["limit"]),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(info["reset"]),
                    "Retry-After": str(info["retry_after"])
                }
            )
        
        # Process request and add rate limit headers to response
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(info["limit"])
        response.headers["X-RateLimit-Remaining"] = str(info["remaining"])
        response.headers["X-RateLimit-Reset"] = str(info["reset"])
        
        return response
    
    def _get_client_id(self, request: Request) -> str:
        """
        Get unique identifier for the client.
        Prefers user ID if authenticated, falls back to IP address.
        """
        # Try to get user ID from request state (set by auth middleware)
        user_id = getattr(request.state, "user_id", None)
        if user_id:
            return f"user:{user_id}"
        
        # Fall back to IP address
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Get the first IP in the chain
            ip = forwarded_for.split(",")[0].strip()
        else:
            ip = request.client.host if request.client else "unknown"
        
        return f"ip:{ip}"
    
    def _is_authenticated(self, request: Request) -> bool:
        """Check if request has valid authentication"""
        # Check for Authorization header
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            return True
        
        # Check if user is set in request state
        return hasattr(request.state, "user_id")


def get_rate_limit_status(client_id: str, endpoint: str = "") -> dict:
    """
    Get current rate limit status for a client.
    Useful for monitoring and debugging.
    """
    if endpoint:
        limit, window = RateLimitConfig.ENDPOINT_LIMITS.get(
            endpoint, 
            RateLimitConfig.DEFAULT_AUTHENTICATED
        )
    else:
        limit, window = RateLimitConfig.DEFAULT_AUTHENTICATED
    
    current_time = time.time()
    cutoff_time = current_time - window
    
    recent_requests = [
        (ts, ep) for ts, ep in rate_limiter.requests.get(client_id, [])
        if ts > cutoff_time
    ]
    
    if endpoint:
        request_count = sum(1 for ts, ep in recent_requests if ep == endpoint)
    else:
        request_count = len(recent_requests)
    
    return {
        "client_id": client_id,
        "endpoint": endpoint or "all",
        "limit": limit,
        "window_seconds": window,
        "current_usage": request_count,
        "remaining": max(0, limit - request_count),
        "percentage_used": round((request_count / limit) * 100, 2) if limit > 0 else 0
    }
