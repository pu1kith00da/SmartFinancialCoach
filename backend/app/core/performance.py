"""
Performance optimization utilities - Caching, compression, query optimization
"""
from functools import wraps
from typing import Optional, Callable, Any
from datetime import timedelta
import hashlib
import json
import time

from fastapi import Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
import gzip


# Simple in-memory cache (use Redis in production)
_cache = {}
_cache_timestamps = {}


class Cache:
    """Simple cache implementation with TTL support"""
    
    @staticmethod
    def get(key: str) -> Optional[Any]:
        """Get value from cache"""
        if key not in _cache:
            return None
        
        # Check if expired
        if key in _cache_timestamps:
            timestamp, ttl = _cache_timestamps[key]
            if ttl and time.time() - timestamp > ttl:
                # Expired
                del _cache[key]
                del _cache_timestamps[key]
                return None
        
        return _cache[key]
    
    @staticmethod
    def set(key: str, value: Any, ttl: Optional[int] = None):
        """Set value in cache with optional TTL (seconds)"""
        _cache[key] = value
        _cache_timestamps[key] = (time.time(), ttl)
    
    @staticmethod
    def delete(key: str):
        """Delete value from cache"""
        if key in _cache:
            del _cache[key]
        if key in _cache_timestamps:
            del _cache_timestamps[key]
    
    @staticmethod
    def clear():
        """Clear entire cache"""
        _cache.clear()
        _cache_timestamps.clear()
    
    @staticmethod
    def generate_key(*args, **kwargs) -> str:
        """Generate cache key from arguments"""
        key_data = {
            'args': args,
            'kwargs': kwargs
        }
        key_string = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.md5(key_string.encode()).hexdigest()


def cached(ttl: int = 300, key_prefix: str = ""):
    """
    Decorator to cache function results.
    
    Args:
        ttl: Time to live in seconds (default: 5 minutes)
        key_prefix: Prefix for cache key
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{key_prefix}:{func.__name__}:{Cache.generate_key(*args, **kwargs)}"
            
            # Try to get from cache
            cached_result = Cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Call function
            result = await func(*args, **kwargs)
            
            # Store in cache
            Cache.set(cache_key, result, ttl)
            
            return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{key_prefix}:{func.__name__}:{Cache.generate_key(*args, **kwargs)}"
            
            # Try to get from cache
            cached_result = Cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Call function
            result = func(*args, **kwargs)
            
            # Store in cache
            Cache.set(cache_key, result, ttl)
            
            return result
        
        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


class CompressionMiddleware(BaseHTTPMiddleware):
    """
    Middleware to compress HTTP responses.
    Compresses responses larger than min_size bytes.
    """
    
    def __init__(self, app, min_size: int = 1024, compression_level: int = 6):
        super().__init__(app)
        self.min_size = min_size
        self.compression_level = compression_level
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Check if client accepts gzip
        accept_encoding = request.headers.get("accept-encoding", "")
        if "gzip" not in accept_encoding.lower():
            return response
        
        # Skip if already compressed
        if response.headers.get("content-encoding"):
            return response
        
        # Skip if content is too small
        content_length = response.headers.get("content-length")
        if content_length and int(content_length) < self.min_size:
            return response
        
        # Compress response body
        # Note: This is a simplified implementation
        # For production, use fastapi.middleware.gzip.GZipMiddleware
        
        return response


class QueryOptimizer:
    """
    Helper class for database query optimization.
    Provides utilities for analyzing and optimizing queries.
    """
    
    @staticmethod
    async def explain_query(db, query):
        """
        Run EXPLAIN ANALYZE on a query to see execution plan.
        Useful for development/debugging.
        """
        from sqlalchemy import text
        
        explain_query = f"EXPLAIN ANALYZE {query}"
        result = await db.execute(text(explain_query))
        return result.fetchall()
    
    @staticmethod
    def get_optimization_hints() -> dict:
        """
        Return common query optimization hints.
        """
        return {
            "indexes": [
                "Create indexes on frequently queried columns",
                "Consider composite indexes for multi-column queries",
                "Use partial indexes for filtered queries",
                "Monitor index usage with pg_stat_user_indexes"
            ],
            "eager_loading": [
                "Use joinedload() for one-to-one and many-to-one relationships",
                "Use selectinload() for one-to-many and many-to-many relationships",
                "Avoid N+1 queries by loading related data upfront"
            ],
            "pagination": [
                "Always use LIMIT and OFFSET for large result sets",
                "Consider cursor-based pagination for better performance",
                "Use window functions for complex pagination"
            ],
            "caching": [
                "Cache frequently accessed, rarely changing data",
                "Use query result caching for expensive queries",
                "Implement cache invalidation strategy",
                "Consider Redis for distributed caching"
            ]
        }


# Database query optimization utilities

def optimize_pagination_query(query, page: int = 1, page_size: int = 50):
    """
    Optimize pagination query with LIMIT and OFFSET.
    """
    offset = (page - 1) * page_size
    return query.limit(page_size).offset(offset)


def add_eager_loading(query, *relationships):
    """
    Add eager loading to query to prevent N+1 queries.
    
    Example:
        from sqlalchemy.orm import joinedload
        query = add_eager_loading(
            query,
            joinedload(User.transactions),
            joinedload(User.accounts)
        )
    """
    for relationship in relationships:
        query = query.options(relationship)
    return query


# Performance monitoring decorator

def monitor_performance(threshold_ms: float = 1000):
    """
    Decorator to monitor function execution time.
    Logs warning if execution time exceeds threshold.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            result = await func(*args, **kwargs)
            duration_ms = (time.time() - start_time) * 1000
            
            if duration_ms > threshold_ms:
                from app.core.logging import get_logger
                logger = get_logger(__name__)
                logger.warning(
                    f"Slow operation: {func.__name__} took {duration_ms:.2f}ms",
                    extra={"extra_fields": {
                        "function": func.__name__,
                        "duration_ms": duration_ms,
                        "threshold_ms": threshold_ms
                    }}
                )
            
            return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            duration_ms = (time.time() - start_time) * 1000
            
            if duration_ms > threshold_ms:
                from app.core.logging import get_logger
                logger = get_logger(__name__)
                logger.warning(
                    f"Slow operation: {func.__name__} took {duration_ms:.2f}ms",
                    extra={"extra_fields": {
                        "function": func.__name__,
                        "duration_ms": duration_ms,
                        "threshold_ms": threshold_ms
                    }}
                )
            
            return result
        
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


# Common database indexes to add

DATABASE_INDEXES = """
-- User indexes
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);

-- Transaction indexes
CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_transactions_account_id ON transactions(account_id);
CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(date);
CREATE INDEX IF NOT EXISTS idx_transactions_category ON transactions(category);
CREATE INDEX IF NOT EXISTS idx_transactions_user_date ON transactions(user_id, date DESC);

-- Account indexes
CREATE INDEX IF NOT EXISTS idx_accounts_user_id ON accounts(user_id);
CREATE INDEX IF NOT EXISTS idx_accounts_plaid_account_id ON accounts(plaid_account_id);

-- Goal indexes
CREATE INDEX IF NOT EXISTS idx_goals_user_id ON goals(user_id);
CREATE INDEX IF NOT EXISTS idx_goals_status ON goals(status);
CREATE INDEX IF NOT EXISTS idx_goals_target_date ON goals(target_date);

-- Subscription indexes
CREATE INDEX IF NOT EXISTS idx_subscriptions_user_id ON subscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_status ON subscriptions(status);
CREATE INDEX IF NOT EXISTS idx_subscriptions_next_billing ON subscriptions(next_billing_date);

-- Bill indexes
CREATE INDEX IF NOT EXISTS idx_bills_user_id ON bills(user_id);
CREATE INDEX IF NOT EXISTS idx_bills_due_date ON bills(due_date);
CREATE INDEX IF NOT EXISTS idx_bills_status ON bills(status);

-- Insight indexes
CREATE INDEX IF NOT EXISTS idx_insights_user_id ON insights(user_id);
CREATE INDEX IF NOT EXISTS idx_insights_type ON insights(type);
CREATE INDEX IF NOT EXISTS idx_insights_created_at ON insights(created_at);

-- Gamification indexes
CREATE INDEX IF NOT EXISTS idx_user_achievements_user_id ON user_achievements(user_id);
CREATE INDEX IF NOT EXISTS idx_user_challenges_user_id ON user_challenges(user_id);
CREATE INDEX IF NOT EXISTS idx_user_challenges_status ON user_challenges(status);
CREATE INDEX IF NOT EXISTS idx_streaks_user_id ON streaks(user_id);
CREATE INDEX IF NOT EXISTS idx_xp_history_user_id ON xp_history(user_id);

-- Composite indexes for common queries
CREATE INDEX IF NOT EXISTS idx_transactions_user_category_date ON transactions(user_id, category, date DESC);
CREATE INDEX IF NOT EXISTS idx_insights_user_type_created ON insights(user_id, type, created_at DESC);
"""


# Example usage:
"""
from app.core.performance import cached, monitor_performance, Cache

# Cache expensive function results
@cached(ttl=300, key_prefix="user_stats")
async def get_user_statistics(user_id: str):
    # Expensive computation
    return calculate_stats(user_id)

# Monitor slow operations
@monitor_performance(threshold_ms=500)
async def process_transactions(transactions):
    # Processing logic
    pass

# Manual cache operations
Cache.set("key", value, ttl=60)
value = Cache.get("key")
Cache.delete("key")

# In main.py, add compression middleware:
from fastapi.middleware.gzip import GZIPMiddleware
app.add_middleware(GZIPMiddleware, minimum_size=1024)
"""
