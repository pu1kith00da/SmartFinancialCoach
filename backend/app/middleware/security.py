"""
Security headers middleware for FastAPI
"""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Optional


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers to all responses.
    Implements OWASP recommended security headers.
    """
    
    def __init__(self, app, config: Optional[dict] = None):
        super().__init__(app)
        self.config = config or {}
        
        # Default security headers
        self.headers = {
            # Prevent MIME type sniffing
            "X-Content-Type-Options": "nosniff",
            
            # Enable XSS protection (for older browsers)
            "X-XSS-Protection": "1; mode=block",
            
            # Prevent clickjacking
            "X-Frame-Options": "DENY",
            
            # Referrer policy
            "Referrer-Policy": "strict-origin-when-cross-origin",
            
            # Permissions policy (formerly Feature-Policy)
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
            
            # Remove server identification
            "Server": "SmartFinCoach",
        }
        
        # HSTS header (only in production/HTTPS)
        if self.config.get("enable_hsts", False):
            # max-age=31536000 (1 year), includeSubDomains, preload
            self.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains; preload"
            )
        
        # Content Security Policy
        csp_directives = self._build_csp()
        if csp_directives:
            self.headers["Content-Security-Policy"] = csp_directives
    
    def _build_csp(self) -> str:
        """Build Content Security Policy header"""
        # Default CSP directives
        directives = {
            "default-src": ["'self'"],
            "script-src": ["'self'"],
            "style-src": ["'self'", "'unsafe-inline'"],  # Allow inline styles for UI frameworks
            "img-src": ["'self'", "data:", "https:"],
            "font-src": ["'self'", "data:"],
            "connect-src": ["'self'"],
            "frame-ancestors": ["'none'"],
            "base-uri": ["'self'"],
            "form-action": ["'self'"],
            "object-src": ["'none'"],
            "upgrade-insecure-requests": [],  # Flag directive (no value)
        }
        
        # Allow custom CSP configuration
        if "csp_overrides" in self.config:
            directives.update(self.config["csp_overrides"])
        
        # Build CSP string
        csp_parts = []
        for directive, values in directives.items():
            if values:
                csp_parts.append(f"{directive} {' '.join(values)}")
            else:
                csp_parts.append(directive)
        
        return "; ".join(csp_parts)
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Add security headers to response
        for header_name, header_value in self.headers.items():
            response.headers[header_name] = header_value
        
        return response


class CORSConfig:
    """
    Configuration for CORS (Cross-Origin Resource Sharing).
    Use FastAPI's built-in CORSMiddleware with these settings.
    """
    
    @staticmethod
    def get_allowed_origins(environment: str = "development") -> list:
        """Get allowed origins based on environment"""
        if environment == "production":
            return [
                "https://smartfincoach.com",
                "https://www.smartfincoach.com",
                "https://app.smartfincoach.com",
            ]
        elif environment == "staging":
            return [
                "https://staging.smartfincoach.com",
                "https://staging-app.smartfincoach.com",
            ]
        else:  # development
            return [
                "http://localhost:3000",
                "http://localhost:3001",
                "http://127.0.0.1:3000",
                "http://127.0.0.1:3001",
            ]
    
    @staticmethod
    def get_cors_config(environment: str = "development") -> dict:
        """Get complete CORS configuration"""
        return {
            "allow_origins": CORSConfig.get_allowed_origins(environment),
            "allow_credentials": True,
            "allow_methods": ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
            "allow_headers": [
                "Authorization",
                "Content-Type",
                "X-Requested-With",
                "Accept",
                "Origin",
                "Access-Control-Request-Method",
                "Access-Control-Request-Headers",
                "X-Request-ID",
            ],
            "expose_headers": [
                "X-RateLimit-Limit",
                "X-RateLimit-Remaining",
                "X-RateLimit-Reset",
                "X-Request-ID",
            ],
            "max_age": 3600,  # Cache preflight requests for 1 hour
        }


class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware to limit request body size.
    Protects against large payload attacks.
    """
    
    def __init__(self, app, max_size: int = 10 * 1024 * 1024):  # 10MB default
        super().__init__(app)
        self.max_size = max_size
    
    async def dispatch(self, request: Request, call_next):
        # Check Content-Length header if present
        content_length = request.headers.get("content-length")
        if content_length:
            content_length = int(content_length)
            if content_length > self.max_size:
                from fastapi.responses import JSONResponse
                return JSONResponse(
                    status_code=413,
                    content={
                        "detail": f"Request body too large. Maximum size: {self.max_size} bytes",
                        "max_size": self.max_size,
                        "received_size": content_length
                    }
                )
        
        response = await call_next(request)
        return response


# Example usage in main.py:
"""
from app.middleware.security import (
    SecurityHeadersMiddleware,
    CORSConfig,
    RequestSizeLimitMiddleware
)
from fastapi.middleware.cors import CORSMiddleware
import os

# Get environment
environment = os.getenv("ENVIRONMENT", "development")

# Add CORS
cors_config = CORSConfig.get_cors_config(environment)
app.add_middleware(CORSMiddleware, **cors_config)

# Add security headers
app.add_middleware(
    SecurityHeadersMiddleware,
    config={
        "enable_hsts": environment == "production",
    }
)

# Add request size limit
app.add_middleware(RequestSizeLimitMiddleware, max_size=10 * 1024 * 1024)  # 10MB
"""
