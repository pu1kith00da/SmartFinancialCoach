from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta

from app.core.database import get_db
from app.core.security import create_access_token, create_refresh_token, decode_token
from app.core.security_enhanced import BruteForceProtection, PasswordPolicy
from app.services.auth_service import AuthService
from app.schemas.auth import (
    UserRegister, 
    UserLogin, 
    TokenResponse, 
    UserResponse
)
from app.config import get_settings
from app.core.logging import get_logger, log_with_context

router = APIRouter()
settings = get_settings()
logger = get_logger(__name__)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    db: AsyncSession = Depends(get_db)
):
    """Register a new user account."""
    auth_service = AuthService(db)
    
    # Validate password strength
    password_policy = PasswordPolicy()
    try:
        password_policy.validate(user_data.password)
    except ValueError as e:
        logger.warning(f"Password validation failed for {user_data.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    # Check if user already exists
    existing_user = await auth_service.get_user_by_email(user_data.email)
    if existing_user:
        logger.warning(f"Registration attempt for existing email: {user_data.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    # Create user
    logger.info(f"Creating new user account: {user_data.email}")
    user = await auth_service.create_user(user_data)
    
    return UserResponse(
        id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        is_active=user.is_active,
        is_verified=user.is_verified,
        created_at=user.created_at
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """Login with email and password."""
    auth_service = AuthService(db)
    brute_force = BruteForceProtection()
    
    # Check for brute force attempts
    try:
        brute_force.check_and_raise_if_locked(credentials.email)
    except ValueError as e:
        logger.warning(f"Brute force lockout for {credentials.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(e)
        )
    
    # Authenticate user
    user = await auth_service.authenticate_user(
        credentials.email, 
        credentials.password
    )
    
    if not user:
        # Record failed attempt
        brute_force.record_failed_attempt(credentials.email)
        attempts_left = brute_force.get_remaining_attempts(credentials.email)
        logger.warning(f"Failed login attempt for {credentials.email}, {attempts_left} attempts remaining")
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Incorrect email or password. {attempts_left} attempts remaining.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    if not user.is_active:
        logger.warning(f"Login attempt for inactive account: {credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )
    
    # Reset failed attempts on successful login
    brute_force.reset_attempts(credentials.email)
    
    # Update last login
    await auth_service.update_last_login(user.id)
    
    logger.info(f"Successful login for user: {credentials.email}")
    
    # Create tokens
    access_token = create_access_token(user_id=user.id)
    refresh_token = create_refresh_token(user_id=user.id)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60  # Convert to seconds
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_token: str,
    db: AsyncSession = Depends(get_db)
):
    """Refresh access token using refresh token."""
    try:
        payload = decode_token(refresh_token)
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        auth_service = AuthService(db)
        user = await auth_service.get_user_by_id(user_id)
        
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Create new tokens
        new_access_token = create_access_token(user_id=user.id)
        new_refresh_token = create_refresh_token(user_id=user.id)
        
        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60  # Convert to seconds
        )
        
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout():
    """Logout user (client should delete tokens)."""
    return {"message": "Successfully logged out"}
