"""
Custom validators for Pydantic models
"""
import re
from typing import Any
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
from pydantic import field_validator, ValidationInfo


class ValidationPatterns:
    """Regex patterns for common validation needs"""
    
    # Email: RFC 5322 simplified
    EMAIL = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    
    # Phone: US format with optional country code
    PHONE_US = re.compile(r'^\+?1?\s*\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})$')
    
    # Password: Min 12 chars, 1 uppercase, 1 lowercase, 1 digit, 1 special char
    PASSWORD_STRONG = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{12,}$')
    
    # UUID v4
    UUID = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$', re.IGNORECASE)
    
    # URL
    URL = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # or IP
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE
    )
    
    # Alphanumeric with spaces
    ALPHANUMERIC_SPACE = re.compile(r'^[a-zA-Z0-9\s]+$')
    
    # Category code (lowercase letters, numbers, underscores)
    CATEGORY_CODE = re.compile(r'^[a-z0-9_]+$')


def validate_email(value: str) -> str:
    """Validate email format"""
    if not value:
        raise ValueError("Email is required")
    
    value = value.strip().lower()
    
    if not ValidationPatterns.EMAIL.match(value):
        raise ValueError("Invalid email format")
    
    if len(value) > 254:  # RFC 5321
        raise ValueError("Email address too long")
    
    return value


def validate_password(value: str) -> str:
    """Validate password strength"""
    if not value:
        raise ValueError("Password is required")
    
    if len(value) < 12:
        raise ValueError("Password must be at least 12 characters long")
    
    if not any(c.isupper() for c in value):
        raise ValueError("Password must contain at least one uppercase letter")
    
    if not any(c.islower() for c in value):
        raise ValueError("Password must contain at least one lowercase letter")
    
    if not any(c.isdigit() for c in value):
        raise ValueError("Password must contain at least one digit")
    
    if not any(c in '@$!%*?&' for c in value):
        raise ValueError("Password must contain at least one special character (@$!%*?&)")
    
    return value


def validate_phone(value: str) -> str:
    """Validate and normalize US phone number"""
    if not value:
        return value
    
    # Remove common formatting characters
    cleaned = re.sub(r'[\s\-\(\)\.]', '', value)
    
    # Remove country code if present
    if cleaned.startswith('+1'):
        cleaned = cleaned[2:]
    elif cleaned.startswith('1') and len(cleaned) == 11:
        cleaned = cleaned[1:]
    
    if len(cleaned) != 10:
        raise ValueError("Phone number must be 10 digits")
    
    if not cleaned.isdigit():
        raise ValueError("Phone number must contain only digits")
    
    # Format as (XXX) XXX-XXXX
    return f"({cleaned[:3]}) {cleaned[3:6]}-{cleaned[6:]}"


def validate_currency_amount(value: Any) -> Decimal:
    """Validate and convert currency amount to Decimal"""
    if value is None:
        raise ValueError("Amount is required")
    
    try:
        # Convert to Decimal for precise financial calculations
        if isinstance(value, str):
            # Remove currency symbols and commas
            value = value.replace('$', '').replace(',', '').strip()
        
        amount = Decimal(str(value))
        
        # Check reasonable bounds
        if amount < Decimal('-999999999.99'):
            raise ValueError("Amount is too small")
        
        if amount > Decimal('999999999.99'):
            raise ValueError("Amount is too large")
        
        # Ensure max 2 decimal places for currency
        if amount.as_tuple().exponent < -2:
            raise ValueError("Amount cannot have more than 2 decimal places")
        
        return amount
        
    except (InvalidOperation, ValueError) as e:
        raise ValueError(f"Invalid amount format: {str(e)}")


def validate_positive_amount(value: Any) -> Decimal:
    """Validate positive currency amount"""
    amount = validate_currency_amount(value)
    
    if amount <= 0:
        raise ValueError("Amount must be positive")
    
    return amount


def validate_non_negative_amount(value: Any) -> Decimal:
    """Validate non-negative currency amount"""
    amount = validate_currency_amount(value)
    
    if amount < 0:
        raise ValueError("Amount cannot be negative")
    
    return amount


def validate_percentage(value: Any) -> Decimal:
    """Validate percentage value (0-100)"""
    try:
        percentage = Decimal(str(value))
        
        if percentage < 0 or percentage > 100:
            raise ValueError("Percentage must be between 0 and 100")
        
        return percentage
        
    except (InvalidOperation, ValueError):
        raise ValueError("Invalid percentage format")


def validate_date_not_future(value: date) -> date:
    """Validate date is not in the future"""
    if not value:
        raise ValueError("Date is required")
    
    if value > date.today():
        raise ValueError("Date cannot be in the future")
    
    return value


def validate_date_future(value: date) -> date:
    """Validate date is in the future"""
    if not value:
        raise ValueError("Date is required")
    
    if value <= date.today():
        raise ValueError("Date must be in the future")
    
    return value


def validate_date_range(start_date: date, end_date: date) -> tuple[date, date]:
    """Validate date range"""
    if not start_date or not end_date:
        raise ValueError("Both start and end dates are required")
    
    if end_date < start_date:
        raise ValueError("End date must be after start date")
    
    return start_date, end_date


def sanitize_string(value: str, max_length: int = 1000, allow_html: bool = False) -> str:
    """Sanitize string input to prevent injection attacks"""
    if not value:
        return value
    
    # Strip whitespace
    value = value.strip()
    
    # Check length
    if len(value) > max_length:
        raise ValueError(f"Input too long (max {max_length} characters)")
    
    # Remove null bytes
    value = value.replace('\x00', '')
    
    # If HTML not allowed, remove HTML tags
    if not allow_html:
        value = re.sub(r'<[^>]*>', '', value)
    
    # Remove control characters except newlines and tabs
    value = ''.join(char for char in value if char == '\n' or char == '\t' or ord(char) >= 32)
    
    return value


def validate_category_code(value: str) -> str:
    """Validate category code format"""
    if not value:
        raise ValueError("Category code is required")
    
    value = value.strip().lower()
    
    if not ValidationPatterns.CATEGORY_CODE.match(value):
        raise ValueError("Category code can only contain lowercase letters, numbers, and underscores")
    
    if len(value) < 2 or len(value) > 50:
        raise ValueError("Category code must be between 2 and 50 characters")
    
    return value


def validate_url(value: str) -> str:
    """Validate URL format"""
    if not value:
        return value
    
    value = value.strip()
    
    if not ValidationPatterns.URL.match(value):
        raise ValueError("Invalid URL format")
    
    if len(value) > 2048:
        raise ValueError("URL too long")
    
    return value


def validate_uuid(value: str) -> str:
    """Validate UUID format"""
    if not value:
        raise ValueError("UUID is required")
    
    value = value.strip().lower()
    
    if not ValidationPatterns.UUID.match(value):
        raise ValueError("Invalid UUID format")
    
    return value


def validate_enum_value(value: str, allowed_values: list[str], case_sensitive: bool = False) -> str:
    """Validate value is in allowed enum values"""
    if not value:
        raise ValueError("Value is required")
    
    value = value.strip()
    
    if not case_sensitive:
        value = value.lower()
        allowed_values = [v.lower() for v in allowed_values]
    
    if value not in allowed_values:
        raise ValueError(f"Invalid value. Must be one of: {', '.join(allowed_values)}")
    
    return value


# Pydantic field validator decorators for common use cases

class EmailValidator:
    """Email field validator"""
    @field_validator('email')
    @classmethod
    def validate_email_field(cls, v: str) -> str:
        return validate_email(v)


class PasswordValidator:
    """Password field validator"""
    @field_validator('password')
    @classmethod
    def validate_password_field(cls, v: str) -> str:
        return validate_password(v)


class PhoneValidator:
    """Phone field validator"""
    @field_validator('phone', 'phone_number')
    @classmethod
    def validate_phone_field(cls, v: str) -> str:
        return validate_phone(v) if v else v


class AmountValidator:
    """Currency amount field validator"""
    @field_validator('amount', 'target_amount', 'current_amount', 'balance')
    @classmethod
    def validate_amount_field(cls, v: Any) -> Decimal:
        return validate_currency_amount(v)


# Example usage in Pydantic models:
"""
from app.core.validators import (
    validate_email, validate_password, validate_currency_amount,
    sanitize_string, EmailValidator, PasswordValidator
)
from pydantic import BaseModel, field_validator

class UserCreate(BaseModel):
    email: str
    password: str
    first_name: str
    last_name: str
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        return validate_email(v)
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        return validate_password(v)
    
    @field_validator('first_name', 'last_name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        return sanitize_string(v, max_length=100)

# Or use mixin classes:
class UserCreate(BaseModel, EmailValidator, PasswordValidator):
    email: str
    password: str
    first_name: str
    last_name: str
"""
