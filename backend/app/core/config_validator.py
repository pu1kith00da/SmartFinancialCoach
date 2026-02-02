"""
Environment configuration validation and hardening
"""
import os
import sys
from typing import Optional, Any
from pathlib import Path
from dotenv import load_dotenv

# Load .env file if it exists
env_file = Path(__file__).parent.parent.parent / '.env'
if env_file.exists():
    load_dotenv(env_file)


class ConfigurationError(Exception):
    """Raised when configuration is invalid"""
    pass


class EnvironmentValidator:
    """Validates required environment variables and configurations"""
    
    # Required environment variables for all environments
    REQUIRED_VARS = {
        'DATABASE_URL': 'Database connection URL',
        'SECRET_KEY': 'Secret key for JWT and encryption (min 32 characters)',
        'PLAID_CLIENT_ID': 'Plaid API client ID',
        'PLAID_SECRET': 'Plaid API secret key',
    }
    
    # Optional but recommended environment variables
    RECOMMENDED_VARS = {
        'REDIS_URL': 'Redis connection URL for caching',
        'OPENAI_API_KEY': 'OpenAI API key for AI features',
        'SENDGRID_API_KEY': 'SendGrid API key for email',
    }
    
    # Production-specific required variables
    PRODUCTION_REQUIRED = {
        'ENVIRONMENT': 'Must be set to "production"',
        'ALLOWED_HOSTS': 'Comma-separated list of allowed hostnames',
    }
    
    @classmethod
    def validate_all(cls, environment: str = None) -> dict[str, Any]:
        """
        Validate all environment variables and configuration.
        Returns dict with validation results.
        """
        if environment is None:
            environment = os.getenv('ENVIRONMENT', 'development')
        
        results = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'environment': environment
        }
        
        # Check required variables
        for var_name, description in cls.REQUIRED_VARS.items():
            value = os.getenv(var_name)
            if not value:
                results['valid'] = False
                results['errors'].append(f"Missing required variable: {var_name} ({description})")
            else:
                # Validate specific variables
                if var_name == 'SECRET_KEY':
                    if len(value) < 32:
                        results['valid'] = False
                        results['errors'].append(
                            f"SECRET_KEY must be at least 32 characters (current: {len(value)})"
                        )
                
                if var_name == 'DATABASE_URL':
                    if not value.startswith(('postgresql://', 'postgresql+asyncpg://')):
                        results['warnings'].append(
                            "DATABASE_URL should use PostgreSQL (postgresql:// or postgresql+asyncpg://)"
                        )
        
        # Check production-specific requirements
        if environment == 'production':
            for var_name, description in cls.PRODUCTION_REQUIRED.items():
                value = os.getenv(var_name)
                if not value:
                    results['valid'] = False
                    results['errors'].append(
                        f"Missing production-required variable: {var_name} ({description})"
                    )
            
            # Additional production checks
            if os.getenv('DEBUG', 'false').lower() == 'true':
                results['valid'] = False
                results['errors'].append("DEBUG must be false in production")
        
        # Check recommended variables
        for var_name, description in cls.RECOMMENDED_VARS.items():
            value = os.getenv(var_name)
            if not value:
                results['warnings'].append(
                    f"Missing recommended variable: {var_name} ({description})"
                )
        
        # Validate specific configurations
        cls._validate_database_url(results)
        cls._validate_security_settings(results, environment)
        cls._validate_api_keys(results)
        
        return results
    
    @classmethod
    def _validate_database_url(cls, results: dict):
        """Validate database URL format"""
        db_url = os.getenv('DATABASE_URL')
        if db_url:
            # Check for password in URL
            if '@' in db_url and ':' in db_url:
                # Extract password portion
                try:
                    password_part = db_url.split('://')[1].split('@')[0].split(':')[1]
                    if len(password_part) < 8:
                        results['warnings'].append("Database password should be at least 8 characters")
                except IndexError:
                    pass
            
            # Warn about SQLite in production
            if 'sqlite' in db_url.lower():
                results['warnings'].append("SQLite is not recommended for production use")
    
    @classmethod
    def _validate_security_settings(cls, results: dict, environment: str):
        """Validate security-related settings"""
        secret_key = os.getenv('SECRET_KEY', '')
        
        # Check for weak/default secret keys
        weak_keys = ['secret', 'password', 'changeme', 'default', '12345']
        if any(weak in secret_key.lower() for weak in weak_keys):
            results['valid'] = False
            results['errors'].append("SECRET_KEY appears to be a weak/default value")
        
        # Check JWT algorithm
        jwt_algorithm = os.getenv('JWT_ALGORITHM', 'HS256')
        if jwt_algorithm not in ['HS256', 'HS384', 'HS512', 'RS256', 'RS384', 'RS512']:
            results['warnings'].append(f"Unusual JWT algorithm: {jwt_algorithm}")
        
        # Check token expiration
        access_token_expire = os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', '30')
        try:
            expire_minutes = int(access_token_expire)
            if expire_minutes > 60:
                results['warnings'].append(
                    f"ACCESS_TOKEN_EXPIRE_MINUTES is high ({expire_minutes}). Consider shorter expiration."
                )
        except ValueError:
            results['warnings'].append("ACCESS_TOKEN_EXPIRE_MINUTES should be a number")
        
        # Production HTTPS check
        if environment == 'production':
            cors_origins = os.getenv('CORS_ORIGINS', '')
            if 'http://' in cors_origins:
                results['warnings'].append("CORS_ORIGINS contains HTTP URLs in production")
    
    @classmethod
    def _validate_api_keys(cls, results: dict):
        """Validate API key formats"""
        # Check Plaid keys format
        plaid_client_id = os.getenv('PLAID_CLIENT_ID', '')
        if plaid_client_id and len(plaid_client_id) < 20:
            results['warnings'].append("PLAID_CLIENT_ID appears to be invalid (too short)")
        
        plaid_secret = os.getenv('PLAID_SECRET', '')
        if plaid_secret and len(plaid_secret) < 20:
            results['warnings'].append("PLAID_SECRET appears to be invalid (too short)")
        
        # Check OpenAI key format
        openai_key = os.getenv('OPENAI_API_KEY', '')
        if openai_key and not openai_key.startswith('sk-'):
            results['warnings'].append("OPENAI_API_KEY format appears invalid")
    
    @classmethod
    def validate_or_exit(cls, environment: str = None):
        """
        Validate configuration and exit if invalid.
        Use this on application startup.
        """
        results = cls.validate_all(environment)
        
        if results['warnings']:
            print("\n⚠️  Configuration Warnings:")
            for warning in results['warnings']:
                print(f"  - {warning}")
        
        if not results['valid']:
            print("\n❌ Configuration Errors:")
            for error in results['errors']:
                print(f"  - {error}")
            print("\n💡 Fix the above errors before starting the application.\n")
            sys.exit(1)
        
        print(f"✅ Configuration validated successfully ({results['environment']} environment)")
        if results['warnings']:
            print(f"⚠️  {len(results['warnings'])} warning(s) - see above")
        print()
        
        return results


class SecretsManager:
    """
    Manage secrets and sensitive configuration.
    In production, integrate with AWS Secrets Manager, HashiCorp Vault, etc.
    """
    
    @staticmethod
    def get_secret(key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get secret value. Can be extended to support external secret managers.
        """
        # For now, just read from environment
        # In production, integrate with your secret manager:
        # - AWS Secrets Manager
        # - HashiCorp Vault
        # - Azure Key Vault
        # - Google Secret Manager
        value = os.getenv(key, default)
        return value
    
    @staticmethod
    def rotate_secret(key: str, new_value: str):
        """
        Rotate a secret value.
        This should be implemented based on your secret management strategy.
        """
        raise NotImplementedError("Secret rotation should be implemented per environment")


class ProductionChecklist:
    """Production deployment checklist"""
    
    CHECKLIST = [
        {
            'category': 'Environment',
            'checks': [
                'ENVIRONMENT set to "production"',
                'DEBUG set to false',
                'SECRET_KEY is strong (min 32 chars, random)',
                'All required environment variables set',
            ]
        },
        {
            'category': 'Database',
            'checks': [
                'PostgreSQL configured (not SQLite)',
                'Database password is strong',
                'Connection pooling configured',
                'Migrations applied',
                'Backups configured',
            ]
        },
        {
            'category': 'Security',
            'checks': [
                'HTTPS/TLS configured',
                'HSTS enabled',
                'CORS origins limited to production domains',
                'Rate limiting enabled',
                'Security headers configured',
                'Secrets stored securely (not in code)',
            ]
        },
        {
            'category': 'Monitoring',
            'checks': [
                'Health check endpoints accessible',
                'Logging configured (structured JSON)',
                'Error tracking enabled (Sentry/similar)',
                'Metrics collection enabled',
                'Alerting configured',
            ]
        },
        {
            'category': 'Performance',
            'checks': [
                'Database indexes created',
                'Query optimization done',
                'Caching configured',
                'CDN configured for static assets',
            ]
        },
        {
            'category': 'API Keys',
            'checks': [
                'Plaid production keys configured',
                'OpenAI API key set (if using AI features)',
                'SendGrid API key set (if sending emails)',
                'All API keys rotated from development',
            ]
        }
    ]
    
    @classmethod
    def print_checklist(cls):
        """Print production deployment checklist"""
        print("\n" + "="*60)
        print("PRODUCTION DEPLOYMENT CHECKLIST")
        print("="*60 + "\n")
        
        for section in cls.CHECKLIST:
            print(f"📋 {section['category']}")
            print("-" * 60)
            for check in section['checks']:
                print(f"  [ ] {check}")
            print()
        
        print("="*60)
        print("Complete all items before deploying to production!")
        print("="*60 + "\n")


def validate_configuration_on_startup():
    """
    Call this function on application startup to validate configuration.
    """
    environment = os.getenv('ENVIRONMENT', 'development')
    
    print("\n" + "="*60)
    print(f"🔧 Validating Configuration ({environment} environment)")
    print("="*60 + "\n")
    
    # Validate environment
    results = EnvironmentValidator.validate_or_exit(environment)
    
    # Print production checklist if in production
    if environment == 'production':
        ProductionChecklist.print_checklist()
    
    return results


# Example usage in main.py:
"""
from app.core.config_validator import validate_configuration_on_startup

# At application startup (in lifespan or before creating app)
validate_configuration_on_startup()
"""
