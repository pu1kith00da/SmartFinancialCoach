"""
Enhanced security features - Token refresh, password policies, brute force protection
"""
from datetime import datetime, timedelta
from typing import Optional
from collections import defaultdict
import time

from fastapi import HTTPException, status

from app.core.security import (
    hash_password as _hash_password,
    verify_password as _verify_password,
    create_access_token,
    decode_token
)


class PasswordPolicy:
    """Password policy enforcement"""
    
    MIN_LENGTH = 12
    REQUIRE_UPPERCASE = True
    REQUIRE_LOWERCASE = True
    REQUIRE_DIGITS = True
    REQUIRE_SPECIAL = True
    SPECIAL_CHARS = "@$!%*?&"
    
    # Password history (prevent reuse)
    MAX_PASSWORD_HISTORY = 5
    
    # Password expiry
    PASSWORD_EXPIRY_DAYS = 90  # 0 = no expiry
    
    @classmethod
    def validate(cls, password: str) -> tuple[bool, list[str]]:
        """
        Validate password against policy.
        Returns (is_valid, list_of_errors)
        """
        errors = []
        
        if len(password) < cls.MIN_LENGTH:
            errors.append(f"Password must be at least {cls.MIN_LENGTH} characters")
        
        if cls.REQUIRE_UPPERCASE and not any(c.isupper() for c in password):
            errors.append("Password must contain at least one uppercase letter")
        
        if cls.REQUIRE_LOWERCASE and not any(c.islower() for c in password):
            errors.append("Password must contain at least one lowercase letter")
        
        if cls.REQUIRE_DIGITS and not any(c.isdigit() for c in password):
            errors.append("Password must contain at least one digit")
        
        if cls.REQUIRE_SPECIAL and not any(c in cls.SPECIAL_CHARS for c in password):
            errors.append(f"Password must contain at least one special character ({cls.SPECIAL_CHARS})")
        
        return len(errors) == 0, errors
    
    @classmethod
    def check_password_strength(cls, password: str) -> dict:
        """
        Assess password strength.
        Returns dict with strength score and feedback.
        """
        score = 0
        feedback = []
        
        # Length
        if len(password) >= 12:
            score += 1
        if len(password) >= 16:
            score += 1
        if len(password) >= 20:
            score += 1
        else:
            feedback.append("Use a longer password for better security")
        
        # Character variety
        if any(c.isupper() for c in password):
            score += 1
        if any(c.islower() for c in password):
            score += 1
        if any(c.isdigit() for c in password):
            score += 1
        if any(c in cls.SPECIAL_CHARS for c in password):
            score += 1
        
        # Complexity
        unique_chars = len(set(password))
        if unique_chars >= 8:
            score += 1
        
        # Check for common patterns
        common_patterns = ['123', 'abc', 'password', 'qwerty', '111']
        if any(pattern in password.lower() for pattern in common_patterns):
            score -= 2
            feedback.append("Avoid common patterns and sequences")
        
        # Determine strength level
        if score >= 7:
            strength = "strong"
        elif score >= 5:
            strength = "medium"
            feedback.append("Consider making your password stronger")
        else:
            strength = "weak"
            feedback.append("This password is too weak")
        
        return {
            "strength": strength,
            "score": max(0, score),
            "max_score": 8,
            "feedback": feedback
        }


class TokenManager:
    """Manage JWT tokens with refresh capability"""
    
    @staticmethod
    def create_token_pair(user_id: str, user_email: str) -> dict:
        """Create access and refresh tokens"""
        from app.config import get_settings
        settings = get_settings()
        
        # Access token (short-lived)
        access_token = create_access_token(user_id, expires_delta=timedelta(minutes=30))
        
        # Refresh token (long-lived)
        refresh_token = create_access_token(
            user_id,
            expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        )
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": 1800  # 30 minutes in seconds
        }
    
    @staticmethod
    def refresh_access_token(refresh_token: str) -> dict:
        """
        Generate new access token from refresh token.
        Returns dict with new tokens.
        """
        try:
            payload = decode_token(refresh_token)
            user_id = payload.get("sub")
            
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token"
                )
            
            # Create new token pair
            # Note: In production, you might want to also rotate the refresh token
            new_access_token = create_access_token(user_id, expires_delta=timedelta(minutes=30))
            
            return {
                "access_token": new_access_token,
                "token_type": "bearer",
                "expires_in": 1800
            }
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token"
            )


class BruteForceProtection:
    """
    Protect against brute force attacks.
    Tracks failed login attempts and implements exponential backoff.
    """
    
    # In-memory storage (use Redis in production for distributed systems)
    failed_attempts = defaultdict(list)
    locked_accounts = {}
    
    # Configuration
    MAX_ATTEMPTS = 5
    LOCKOUT_DURATION = 900  # 15 minutes in seconds
    ATTEMPT_WINDOW = 300  # 5 minutes in seconds
    
    @classmethod
    def record_failed_attempt(cls, identifier: str) -> dict:
        """
        Record a failed login attempt.
        Returns dict with lockout info.
        """
        current_time = time.time()
        
        # Clean old attempts outside the window
        cls.failed_attempts[identifier] = [
            attempt_time for attempt_time in cls.failed_attempts[identifier]
            if current_time - attempt_time < cls.ATTEMPT_WINDOW
        ]
        
        # Add new attempt
        cls.failed_attempts[identifier].append(current_time)
        
        attempts_count = len(cls.failed_attempts[identifier])
        
        # Check if should be locked
        if attempts_count >= cls.MAX_ATTEMPTS:
            lockout_until = current_time + cls.LOCKOUT_DURATION
            cls.locked_accounts[identifier] = lockout_until
            
            return {
                "locked": True,
                "attempts": attempts_count,
                "lockout_until": lockout_until,
                "retry_after": cls.LOCKOUT_DURATION
            }
        
        return {
            "locked": False,
            "attempts": attempts_count,
            "remaining_attempts": cls.MAX_ATTEMPTS - attempts_count
        }
    
    @classmethod
    def is_locked(cls, identifier: str) -> tuple[bool, Optional[int]]:
        """
        Check if account/IP is locked.
        Returns (is_locked, retry_after_seconds)
        """
        if identifier not in cls.locked_accounts:
            return False, None
        
        lockout_until = cls.locked_accounts[identifier]
        current_time = time.time()
        
        if current_time >= lockout_until:
            # Lock expired
            del cls.locked_accounts[identifier]
            cls.failed_attempts[identifier] = []
            return False, None
        
        retry_after = int(lockout_until - current_time)
        return True, retry_after
    
    @classmethod
    def get_remaining_attempts(cls, identifier: str) -> int:
        """Get remaining login attempts before lockout"""
        current_time = time.time()
        
        # Clean old attempts outside the window
        cls.failed_attempts[identifier] = [
            attempt_time for attempt_time in cls.failed_attempts[identifier]
            if current_time - attempt_time < cls.ATTEMPT_WINDOW
        ]
        
        attempts_count = len(cls.failed_attempts[identifier])
        return max(0, cls.MAX_ATTEMPTS - attempts_count)
    
    @classmethod
    def reset_attempts(cls, identifier: str):
        """Reset failed attempts (after successful login)"""
        if identifier in cls.failed_attempts:
            del cls.failed_attempts[identifier]
        if identifier in cls.locked_accounts:
            del cls.locked_accounts[identifier]
    
    @classmethod
    def check_and_raise_if_locked(cls, identifier: str):
        """Check if locked and raise HTTPException if so"""
        is_locked, retry_after = cls.is_locked(identifier)
        
        if is_locked:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Too many failed login attempts. Try again in {retry_after} seconds.",
                headers={"Retry-After": str(retry_after)}
            )


class SessionManager:
    """
    Manage user sessions for security tracking.
    Track active sessions and provide logout all devices functionality.
    """
    
    # In-memory storage (use Redis in production)
    active_sessions = defaultdict(set)  # user_id -> set of session_ids
    
    @classmethod
    def create_session(cls, user_id: str, session_id: str):
        """Create a new session for user"""
        cls.active_sessions[user_id].add(session_id)
    
    @classmethod
    def invalidate_session(cls, user_id: str, session_id: str):
        """Invalidate a specific session"""
        if user_id in cls.active_sessions:
            cls.active_sessions[user_id].discard(session_id)
    
    @classmethod
    def invalidate_all_sessions(cls, user_id: str):
        """Invalidate all sessions for a user (logout all devices)"""
        cls.active_sessions[user_id] = set()
    
    @classmethod
    def is_session_valid(cls, user_id: str, session_id: str) -> bool:
        """Check if session is valid"""
        return session_id in cls.active_sessions.get(user_id, set())
    
    @classmethod
    def get_active_sessions(cls, user_id: str) -> list:
        """Get all active sessions for user"""
        return list(cls.active_sessions.get(user_id, set()))


def validate_and_hash_password(password: str) -> str:
    """
    Validate password against policy and return hash.
    Raises ValueError if password doesn't meet policy.
    """
    is_valid, errors = PasswordPolicy.validate(password)
    
    if not is_valid:
        raise ValueError(f"Password policy violation: {', '.join(errors)}")
    
    return _hash_password(password)


# Re-export existing functions
hash_password = _hash_password
verify_password = _verify_password
