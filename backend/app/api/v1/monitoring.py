"""
Health check and monitoring endpoints
"""
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse, PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from pydantic import BaseModel
from typing import Optional
import time
from datetime import datetime

from app.core.database import get_db
from app.config import get_settings

router = APIRouter()
settings = get_settings()


class HealthStatus(BaseModel):
    """Health status response"""
    status: str  # "healthy", "degraded", "unhealthy"
    timestamp: str
    version: str
    environment: str
    checks: dict


class DatabaseHealth(BaseModel):
    """Database health check result"""
    status: str
    response_time_ms: Optional[float] = None
    error: Optional[str] = None


async def check_database(db: AsyncSession) -> DatabaseHealth:
    """Check database connectivity and response time"""
    try:
        start_time = time.time()
        result = await db.execute(text("SELECT 1"))
        result.scalar()
        response_time = (time.time() - start_time) * 1000  # Convert to ms
        
        return DatabaseHealth(
            status="healthy",
            response_time_ms=round(response_time, 2)
        )
    except Exception as e:
        return DatabaseHealth(
            status="unhealthy",
            error=str(e)
        )


@router.get("/health", response_model=HealthStatus, status_code=status.HTTP_200_OK)
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    Comprehensive health check endpoint.
    Returns overall system health and individual component status.
    """
    # Check database
    db_health = await check_database(db)
    
    # Determine overall status
    if db_health.status == "unhealthy":
        overall_status = "unhealthy"
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    elif db_health.status == "degraded":
        overall_status = "degraded"
        status_code = status.HTTP_200_OK
    else:
        overall_status = "healthy"
        status_code = status.HTTP_200_OK
    
    return HealthStatus(
        status=overall_status,
        timestamp=datetime.utcnow().isoformat() + "Z",
        version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT,
        checks={
            "database": db_health.dict(),
        }
    )


@router.get("/health/liveness", status_code=status.HTTP_200_OK)
async def liveness_check():
    """
    Liveness probe for Kubernetes/container orchestration.
    Returns 200 if the application is running.
    """
    return {"status": "alive"}


@router.get("/health/readiness", status_code=status.HTTP_200_OK)
async def readiness_check(db: AsyncSession = Depends(get_db)):
    """
    Readiness probe for Kubernetes/container orchestration.
    Returns 200 if the application is ready to serve traffic.
    """
    # Check if database is accessible
    db_health = await check_database(db)
    
    if db_health.status != "healthy":
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "not ready", "reason": "database unavailable"}
        )
    
    return {"status": "ready"}


class MetricsResponse(BaseModel):
    """Metrics response for monitoring"""
    uptime_seconds: float
    requests_total: int
    requests_per_second: float
    database_pool_size: int
    database_pool_checked_out: int


# Track application start time
app_start_time = time.time()


@router.get("/metrics", response_model=MetricsResponse)
async def get_metrics(db: AsyncSession = Depends(get_db)):
    """
    Application metrics endpoint for monitoring systems.
    Can be scraped by Prometheus or similar tools.
    """
    uptime = time.time() - app_start_time
    
    # Get database pool stats
    from app.core.database import engine
    pool = engine.pool
    
    return MetricsResponse(
        uptime_seconds=round(uptime, 2),
        requests_total=0,  # TODO: Implement request counter
        requests_per_second=0.0,  # TODO: Calculate from counter
        database_pool_size=pool.size(),
        database_pool_checked_out=pool.checkedout()
    )


# Prometheus-compatible metrics format
@router.get("/metrics/prometheus", response_class=PlainTextResponse)
async def prometheus_metrics(db: AsyncSession = Depends(get_db)):
    """
    Metrics in Prometheus exposition format.
    """
    from app.core.database import engine
    pool = engine.pool
    uptime = time.time() - app_start_time
    
    metrics = []
    
    # Application info
    metrics.append('# HELP app_info Application information')
    metrics.append('# TYPE app_info gauge')
    metrics.append(f'app_info{{version="{settings.APP_VERSION}",environment="{settings.ENVIRONMENT}"}} 1')
    
    # Uptime
    metrics.append('# HELP app_uptime_seconds Application uptime in seconds')
    metrics.append('# TYPE app_uptime_seconds counter')
    metrics.append(f'app_uptime_seconds {uptime:.2f}')
    
    # Database pool
    metrics.append('# HELP db_pool_size Database connection pool size')
    metrics.append('# TYPE db_pool_size gauge')
    metrics.append(f'db_pool_size {pool.size()}')
    
    metrics.append('# HELP db_pool_checked_out Database connections currently in use')
    metrics.append('# TYPE db_pool_checked_out gauge')
    metrics.append(f'db_pool_checked_out {pool.checkedout()}')
    
    return '\n'.join(metrics) + '\n'
