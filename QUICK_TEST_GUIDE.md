# Quick Test Guide - Smart Financial Coach API

## Prerequisites
- Backend server running on `http://localhost:8000`
- PostgreSQL and Redis running (via Docker or locally)

## Start the Server

```bash
# Option 1: Using the startup script
./start-dev.sh

# Option 2: Manual start
cd backend
source venv/bin/activate
alembic upgrade head
uvicorn app.main:app --reload
```

## API Testing with curl

### 1. Health Check
```bash
curl http://localhost:8000/health
```

Expected Response:
```json
{
  "status": "healthy",
  "service": "Smart Financial Coach API",
  "version": "1.0.0"
}
```

### 2. Register a New User
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john.doe@example.com",
    "password": "SecurePass123!",
    "first_name": "John",
    "last_name": "Doe"
  }'
```

Expected Response:
```json
{
  "id": "uuid-here",
  "email": "john.doe@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "is_active": true,
  "is_verified": false,
  "created_at": "2024-01-15T10:00:00Z"
}
```

### 3. Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john.doe@example.com",
    "password": "SecurePass123!"
  }'
```

Expected Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Save the access_token for subsequent requests!**

### 4. Get Current User Info
```bash
# Replace YOUR_ACCESS_TOKEN with the token from login
curl http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

Expected Response:
```json
{
  "id": "uuid-here",
  "email": "john.doe@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "is_active": true,
  "is_verified": false,
  "created_at": "2024-01-15T10:00:00Z",
  "last_login_at": "2024-01-15T10:05:00Z"
}
```

### 5. Get User Preferences
```bash
curl http://localhost:8000/api/v1/users/preferences \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

Expected Response:
```json
{
  "user_id": "uuid-here",
  "theme": "light",
  "currency": "USD",
  "language": "en",
  "timezone": "UTC",
  "notification_email": true,
  "notification_push": true,
  "notification_insights": true,
  "notification_goals": true,
  "notification_bills": true,
  "budget_alerts": true,
  "weekly_summary": true
}
```

### 6. Update User Preferences
```bash
curl -X PUT http://localhost:8000/api/v1/users/preferences \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "theme": "dark",
    "currency": "EUR",
    "notification_email": false
  }'
```

Expected Response:
```json
{
  "user_id": "uuid-here",
  "theme": "dark",
  "currency": "EUR",
  "language": "en",
  "timezone": "UTC",
  "notification_email": false,
  "notification_push": true,
  "notification_insights": true,
  "notification_goals": true,
  "notification_bills": true,
  "budget_alerts": true,
  "weekly_summary": true
}
```

### 7. Refresh Access Token
```bash
# Replace YOUR_REFRESH_TOKEN with the refresh token from login
curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d 'YOUR_REFRESH_TOKEN'
```

Expected Response:
```json
{
  "access_token": "new_access_token_here",
  "refresh_token": "new_refresh_token_here",
  "token_type": "bearer"
}
```

### 8. Logout
```bash
curl -X POST http://localhost:8000/api/v1/auth/logout
```

Expected Response:
```json
{
  "message": "Successfully logged out"
}
```

## Testing with Python

```python
import requests

BASE_URL = "http://localhost:8000"

# Register
response = requests.post(
    f"{BASE_URL}/api/v1/auth/register",
    json={
        "email": "test@example.com",
        "password": "TestPass123!",
        "first_name": "Test",
        "last_name": "User"
    }
)
print("Register:", response.json())

# Login
response = requests.post(
    f"{BASE_URL}/api/v1/auth/login",
    json={
        "email": "test@example.com",
        "password": "TestPass123!"
    }
)
tokens = response.json()
access_token = tokens["access_token"]
print("Login successful!")

# Get current user
headers = {"Authorization": f"Bearer {access_token}"}
response = requests.get(f"{BASE_URL}/api/v1/users/me", headers=headers)
print("User info:", response.json())

# Update preferences
response = requests.put(
    f"{BASE_URL}/api/v1/users/preferences",
    headers=headers,
    json={"theme": "dark", "currency": "GBP"}
)
print("Updated preferences:", response.json())
```

## Interactive API Documentation

Visit http://localhost:8000/docs for Swagger UI with:
- Full API documentation
- Interactive request testing
- Schema definitions
- Try-it-out functionality

## Common Issues

### 1. "Could not connect to database"
```bash
# Check if PostgreSQL is running
docker-compose ps

# Start PostgreSQL
docker-compose up -d postgres
```

### 2. "Module not found" errors
```bash
# Install dependencies
cd backend
pip install -r requirements.txt
```

### 3. "Unauthorized" when accessing protected routes
- Ensure you're including the Bearer token in the Authorization header
- Token may have expired (30 min validity) - refresh or login again

### 4. "User already exists"
- Email addresses must be unique
- Try a different email or check existing users in database

## Database Access

```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U fincoach -d fincoach

# View users
SELECT id, email, first_name, last_name, created_at FROM users;

# View preferences
SELECT * FROM user_preferences;
```

## Running Tests

```bash
cd backend
pytest tests/ -v

# Run specific test file
pytest tests/test_auth.py -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html
```

## Next Steps

After verifying the authentication system works:

1. **Phase 2**: Implement Plaid bank integration
2. **Phase 3**: Build transaction management
3. **Phase 4**: Develop AI insights engine
4. **Phase 5**: Create goal tracking system
5. **Phase 6**: Build the frontend with Next.js

---

Happy testing! 🚀
