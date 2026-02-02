from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import os

from app.config import get_settings
from app.core.database import engine
from app.api.v1 import auth, users, plaid, transactions, insights, goals, subscriptions, bills, analytics, gamification, monitoring, gdpr, budgets, chat
from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.security import SecurityHeadersMiddleware, CORSConfig, RequestSizeLimitMiddleware
from app.core.logging import setup_logging, RequestLoggingMiddleware, get_logger
from app.core.exceptions import register_exception_handlers
from app.core.config_validator import validate_configuration_on_startup

settings = get_settings()
environment = os.getenv("ENVIRONMENT", "development")

# Validate configuration on startup
try:
    validate_configuration_on_startup()
except SystemExit:
    # Configuration validation failed, exit
    raise

# Setup logging
setup_logging(
    level="DEBUG" if settings.DEBUG else "INFO",
    json_format=environment == "production",
)

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("🚀 Starting Smart Financial Coach API", extra={"extra_fields": {"environment": environment}})
    yield
    # Shutdown
    await engine.dispose()
    logger.info("👋 Shutting down Smart Financial Coach API")


# Create FastAPI app
app = FastAPI(
    title="Smart Financial Coach API",
    description="AI-powered personal financial management platform",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS with environment-specific settings
cors_config = CORSConfig.get_cors_config(environment)
app.add_middleware(CORSMiddleware, **cors_config)

# Add compression middleware (compress responses > 1KB)
app.add_middleware(GZipMiddleware, minimum_size=1024)

# Add security headers middleware
app.add_middleware(
    SecurityHeadersMiddleware,
    config={
        "enable_hsts": environment == "production",
    }
)

# Add request size limit middleware (10MB max)
app.add_middleware(RequestSizeLimitMiddleware, max_size=10 * 1024 * 1024)

# Add rate limiting middleware
app.add_middleware(RateLimitMiddleware)

# Add request logging middleware
app.add_middleware(RequestLoggingMiddleware, logger=logger)


# Register exception handlers
register_exception_handlers(app)


# Include routers
app.include_router(monitoring.router, tags=["Monitoring"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(plaid.router, prefix="/api/v1/plaid", tags=["Plaid"])
app.include_router(transactions.router, prefix="/api/v1/transactions", tags=["Transactions"])
app.include_router(insights.router, prefix="/api/v1/insights", tags=["Insights"])
app.include_router(goals.router, prefix="/api/v1/goals", tags=["Goals"])
app.include_router(subscriptions.router, prefix="/api/v1/subscriptions", tags=["Subscriptions"])
app.include_router(bills.router, prefix="/api/v1/bills", tags=["Bills"])
app.include_router(budgets.router, prefix="/api/v1/budgets", tags=["Budgets"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["Analytics"])
app.include_router(gamification.router, prefix="/api/v1/gamification", tags=["Gamification"])
app.include_router(gdpr.router, prefix="/api/v1/gdpr", tags=["GDPR Compliance"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["Chat"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to Smart Financial Coach API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }
