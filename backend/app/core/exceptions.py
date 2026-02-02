"""
Custom exceptions and error handlers for Smart Financial Coach API
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError, OperationalError
from typing import Any, Dict, Optional
import logging

from app.core.logging import get_logger, log_with_context

logger = get_logger(__name__)


# Custom Exception Classes

class AppException(Exception):
    """Base exception for application errors"""
    
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code: str = "INTERNAL_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class AuthenticationError(AppException):
    """Raised when authentication fails"""
    
    def __init__(self, message: str = "Authentication failed", details: Optional[Dict] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="AUTHENTICATION_ERROR",
            details=details
        )


class AuthorizationError(AppException):
    """Raised when user doesn't have permission"""
    
    def __init__(self, message: str = "Insufficient permissions", details: Optional[Dict] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="AUTHORIZATION_ERROR",
            details=details
        )


class ResourceNotFoundError(AppException):
    """Raised when a requested resource is not found"""
    
    def __init__(self, resource: str, resource_id: Any = None, details: Optional[Dict] = None):
        message = f"{resource} not found"
        if resource_id:
            message += f": {resource_id}"
        
        if details is None:
            details = {}
        details["resource"] = resource
        if resource_id:
            details["resource_id"] = str(resource_id)
        
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="RESOURCE_NOT_FOUND",
            details=details
        )


class DuplicateResourceError(AppException):
    """Raised when attempting to create a duplicate resource"""
    
    def __init__(self, resource: str, field: str = None, details: Optional[Dict] = None):
        message = f"{resource} already exists"
        if field:
            message += f" with this {field}"
        
        if details is None:
            details = {}
        details["resource"] = resource
        if field:
            details["field"] = field
        
        super().__init__(
            message=message,
            status_code=status.HTTP_409_CONFLICT,
            error_code="DUPLICATE_RESOURCE",
            details=details
        )


class ValidationError(AppException):
    """Raised when data validation fails"""
    
    def __init__(self, message: str = "Validation failed", details: Optional[Dict] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="VALIDATION_ERROR",
            details=details
        )


class ExternalServiceError(AppException):
    """Raised when an external service (Plaid, OpenAI, etc.) fails"""
    
    def __init__(
        self,
        service: str,
        message: str = "External service error",
        details: Optional[Dict] = None
    ):
        if details is None:
            details = {}
        details["service"] = service
        
        super().__init__(
            message=message,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            error_code="EXTERNAL_SERVICE_ERROR",
            details=details
        )


class RateLimitExceededError(AppException):
    """Raised when rate limit is exceeded"""
    
    def __init__(self, message: str = "Rate limit exceeded", retry_after: int = None):
        details = {}
        if retry_after:
            details["retry_after"] = retry_after
        
        super().__init__(
            message=message,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            error_code="RATE_LIMIT_EXCEEDED",
            details=details
        )


class InsufficientFundsError(AppException):
    """Raised for financial operations with insufficient funds"""
    
    def __init__(
        self,
        message: str = "Insufficient funds",
        required: float = None,
        available: float = None
    ):
        details = {}
        if required is not None:
            details["required_amount"] = required
        if available is not None:
            details["available_amount"] = available
        
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="INSUFFICIENT_FUNDS",
            details=details
        )


# Exception Handlers

async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Handler for custom application exceptions"""
    
    log_with_context(
        logger,
        "warning" if exc.status_code < 500 else "error",
        f"Application error: {exc.message}",
        error_code=exc.error_code,
        status_code=exc.status_code,
        path=request.url.path,
        method=request.method,
        details=exc.details
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.error_code,
                "message": exc.message,
                "details": exc.details
            }
        },
        headers={"X-Error-Code": exc.error_code}
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
) -> JSONResponse:
    """Handler for Pydantic validation errors"""
    
    # Format validation errors
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    log_with_context(
        logger,
        "warning",
        "Request validation failed",
        path=request.url.path,
        method=request.method,
        validation_errors=errors
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "details": {
                    "validation_errors": errors
                }
            }
        }
    )


async def integrity_error_handler(request: Request, exc: IntegrityError) -> JSONResponse:
    """Handler for database integrity errors (unique constraints, etc.)"""
    
    log_with_context(
        logger,
        "warning",
        "Database integrity error",
        path=request.url.path,
        method=request.method,
        error=str(exc.orig) if hasattr(exc, "orig") else str(exc)
    )
    
    # Try to extract meaningful information from the error
    error_message = str(exc.orig) if hasattr(exc, "orig") else str(exc)
    
    # Common integrity error patterns
    if "unique constraint" in error_message.lower():
        message = "A record with this information already exists"
        error_code = "DUPLICATE_RECORD"
    elif "foreign key constraint" in error_message.lower():
        message = "Referenced resource does not exist"
        error_code = "INVALID_REFERENCE"
    elif "not null constraint" in error_message.lower():
        message = "Required field is missing"
        error_code = "MISSING_FIELD"
    else:
        message = "Database constraint violation"
        error_code = "INTEGRITY_ERROR"
    
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "error": {
                "code": error_code,
                "message": message,
                "details": {}
            }
        }
    )


async def database_error_handler(request: Request, exc: OperationalError) -> JSONResponse:
    """Handler for database operational errors"""
    
    log_with_context(
        logger,
        "error",
        "Database operational error",
        path=request.url.path,
        method=request.method,
        error=str(exc)
    )
    
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "error": {
                "code": "DATABASE_ERROR",
                "message": "Database service temporarily unavailable",
                "details": {}
            }
        }
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handler for all unhandled exceptions"""
    
    # Log the full exception with traceback
    log_with_context(
        logger,
        "error",
        f"Unhandled exception: {type(exc).__name__}",
        path=request.url.path,
        method=request.method,
        error=str(exc),
        error_type=type(exc).__name__
    )
    
    logger.exception("Full traceback:")
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
                "details": {}
            }
        }
    )


def register_exception_handlers(app):
    """
    Register all exception handlers with the FastAPI app.
    Call this in main.py after creating the app.
    """
    from fastapi.exceptions import RequestValidationError
    from sqlalchemy.exc import IntegrityError, OperationalError
    
    # Custom exceptions
    app.add_exception_handler(AppException, app_exception_handler)
    
    # FastAPI/Pydantic validation errors
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    
    # Database errors
    app.add_exception_handler(IntegrityError, integrity_error_handler)
    app.add_exception_handler(OperationalError, database_error_handler)
    
    # Catch-all for unexpected errors
    app.add_exception_handler(Exception, generic_exception_handler)


# Example usage in code:
"""
from app.core.exceptions import (
    ResourceNotFoundError,
    DuplicateResourceError,
    ValidationError,
    AuthenticationError,
    AuthorizationError
)

# In your service/API code
def get_user(user_id: str):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise ResourceNotFoundError("User", user_id)
    return user

def create_user(email: str):
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        raise DuplicateResourceError("User", "email")
    # ... create user

# In main.py
from app.core.exceptions import register_exception_handlers
register_exception_handlers(app)
"""
