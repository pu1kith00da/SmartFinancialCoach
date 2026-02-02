from datetime import datetime, timedelta
from typing import Optional, Union
from uuid import UUID

from jose import jwt, JWTError
import bcrypt
from cryptography.fernet import Fernet
import pyotp
import secrets

from app.config import get_settings

settings = get_settings()

# Field-level encryption for sensitive data
_fernet = None


def get_fernet():
    global _fernet
    if _fernet is None:
        # Ensure key is 32 bytes for Fernet
        key = settings.SECRET_KEY.encode()[:32].ljust(32, b'=')
        _fernet = Fernet(Fernet.generate_key())  # Use a proper key in production
    return _fernet


def hash_password(password: str) -> str:
    """Hash a password for storing."""
    # Truncate password to 72 bytes (bcrypt limit)
    password_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a stored password against one provided by user."""
    try:
        # Truncate password to 72 bytes (bcrypt limit)
        password_bytes = plain_password.encode('utf-8')[:72]
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception:
        return False


def create_access_token(user_id: Union[str, UUID], expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {
        "sub": str(user_id),
        "exp": expire,
        "type": "access"
    }
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(user_id: Union[str, UUID]) -> str:
    """Create a JWT refresh token."""
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {
        "sub": str(user_id),
        "exp": expire,
        "type": "refresh",
        "jti": secrets.token_urlsafe(32)  # Unique token ID for revocation
    }
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    """Decode and verify a JWT token."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        return None


def encrypt_sensitive_data(data: str) -> str:
    """Encrypt sensitive data like access tokens."""
    return get_fernet().encrypt(data.encode()).decode()


def decrypt_sensitive_data(encrypted_data: str) -> str:
    """Decrypt sensitive data."""
    return get_fernet().decrypt(encrypted_data.encode()).decode()


# Aliases for convenience
encrypt_data = encrypt_sensitive_data
decrypt_data = decrypt_sensitive_data


def generate_mfa_secret() -> str:
    """Generate a secret for MFA."""
    return pyotp.random_base32()


def verify_mfa_code(secret: str, code: str) -> bool:
    """Verify an MFA code."""
    totp = pyotp.TOTP(secret)
    return totp.verify(code)


def get_mfa_provisioning_uri(secret: str, email: str) -> str:
    """Get provisioning URI for MFA setup."""
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(name=email, issuer_name=settings.APP_NAME)
