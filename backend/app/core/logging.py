"""
Structured logging configuration for Smart Financial Coach API
"""
import logging
import sys
import json
from datetime import datetime
from typing import Any, Dict
import uuid
from contextvars import ContextVar

# Context variable for request ID (correlation ID)
request_id_var: ContextVar[str] = ContextVar("request_id", default="")


class StructuredFormatter(logging.Formatter):
    """
    Custom formatter that outputs JSON-structured logs.
    Includes timestamp, level, message, request_id, and any extra fields.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        # Add request ID if available
        request_id = request_id_var.get()
        if request_id:
            log_data["request_id"] = request_id
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add any extra fields
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)
        
        # Add standard fields
        log_data.update({
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        })
        
        return json.dumps(log_data)


class RequestIDFilter(logging.Filter):
    """Filter that adds request ID to log records"""
    
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_var.get()
        return True


def setup_logging(
    level: str = "INFO",
    json_format: bool = False,
    log_file: str = None
) -> None:
    """
    Configure application logging.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_format: If True, use structured JSON logging
        log_file: Optional file path for logging
    """
    # Convert string level to logging constant
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    # Create formatter
    if json_format:
        formatter = StructuredFormatter()
    else:
        formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(request_id)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    console_handler.addFilter(RequestIDFilter())
    root_logger.addHandler(console_handler)
    
    # File handler (optional)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        file_handler.addFilter(RequestIDFilter())
        root_logger.addHandler(file_handler)
    
    # Configure third-party loggers
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the given name"""
    return logging.getLogger(name)


def log_with_context(
    logger: logging.Logger,
    level: str,
    message: str,
    **kwargs
) -> None:
    """
    Log a message with additional context fields.
    
    Args:
        logger: Logger instance
        level: Log level (debug, info, warning, error, critical)
        message: Log message
        **kwargs: Additional context fields
    """
    log_method = getattr(logger, level.lower())
    
    # Create a LogRecord with extra fields
    extra = {"extra_fields": kwargs}
    log_method(message, extra=extra)


# Middleware for request logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import Message
import time


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log all HTTP requests and responses.
    Adds correlation ID to each request.
    """
    
    def __init__(self, app, logger: logging.Logger = None):
        super().__init__(app)
        self.logger = logger or get_logger(__name__)
    
    async def dispatch(self, request: Request, call_next):
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        request_id_var.set(request_id)
        
        # Add request ID to request state
        request.state.request_id = request_id
        
        # Log incoming request
        start_time = time.time()
        
        log_with_context(
            self.logger,
            "info",
            f"Request started: {request.method} {request.url.path}",
            method=request.method,
            path=request.url.path,
            query_params=dict(request.query_params),
            client_host=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate request duration
            duration = time.time() - start_time
            
            # Log response
            log_with_context(
                self.logger,
                "info",
                f"Request completed: {request.method} {request.url.path}",
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration_seconds=round(duration, 3),
            )
            
            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            
            return response
            
        except Exception as exc:
            # Log error
            duration = time.time() - start_time
            
            log_with_context(
                self.logger,
                "error",
                f"Request failed: {request.method} {request.url.path}",
                method=request.method,
                path=request.url.path,
                duration_seconds=round(duration, 3),
                error=str(exc),
                error_type=type(exc).__name__,
            )
            
            raise


# Utility function to sanitize sensitive data from logs
def sanitize_log_data(data: dict, sensitive_keys: set = None) -> dict:
    """
    Remove or mask sensitive information from log data.
    
    Args:
        data: Dictionary containing log data
        sensitive_keys: Set of keys to sanitize
        
    Returns:
        Sanitized dictionary
    """
    if sensitive_keys is None:
        sensitive_keys = {
            "password",
            "token",
            "secret",
            "api_key",
            "access_token",
            "refresh_token",
            "authorization",
            "credit_card",
            "ssn",
            "social_security",
        }
    
    sanitized = {}
    for key, value in data.items():
        if any(sensitive in key.lower() for sensitive in sensitive_keys):
            sanitized[key] = "***REDACTED***"
        elif isinstance(value, dict):
            sanitized[key] = sanitize_log_data(value, sensitive_keys)
        elif isinstance(value, list):
            sanitized[key] = [
                sanitize_log_data(item, sensitive_keys) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            sanitized[key] = value
    
    return sanitized


# Example usage:
"""
from app.core.logging import setup_logging, get_logger, log_with_context

# In main.py startup
setup_logging(
    level="INFO",
    json_format=True,  # Use JSON for production
    log_file="logs/app.log"  # Optional file logging
)

# In your code
logger = get_logger(__name__)

# Simple logging
logger.info("User logged in")

# Logging with context
log_with_context(
    logger,
    "info",
    "Transaction created",
    user_id=user.id,
    transaction_amount=100.50,
    category="food"
)

# In main.py, add the middleware
from app.core.logging import RequestLoggingMiddleware
app.add_middleware(RequestLoggingMiddleware)
"""
