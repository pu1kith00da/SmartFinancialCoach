# Phase 3 - Transaction Management Testing Guide

## ✅ What Was Built

Phase 3 adds complete transaction management with:
- Automatic transaction syncing from Plaid
- Smart category mapping
- Recurring transaction detection
- Advanced filtering and search
- Transaction statistics and analytics
- Bulk operations

## Prerequisites

1. **Server Running**: Make sure your backend server is running
2. **Bank Account Connected**: You need at least one bank connected via Plaid
3. **Access Token**: Get a fresh auth token (expires after 30 minutes)

## Testing Steps

### Step 1: Get Access Token

**First, register a user if you haven't already:**
```bash
curl -s -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email":"testuser@fincoach.com",
    "password":"SecurePass123!",
    "first_name":"Test",
    "last_name":"User"
  }' | python3 -m json.tool
```

**Then login to get your token:**
```bash
TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"testuser@fincoach.com","password":"SecurePass123!"}' | \
  grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

echo "✓ Access Token obtained: ${TOKEN:0:50}..."
```

**Note:** Registration requires `first_name` and `last_name` fields (not `full_name`). Password must be at least 12 characters with uppercase, lowercase, digit, and special character.

### Step 2: List Transactions (Initially Empty)

```bash
curl -s "http://localhost:8000/api/v1/transactions/" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

**⚠️ Important:** Note the trailing slash `/` - it's required for all transaction endpoints.

**Expected Response:**
```json
{
  "transactions": [],
  "total": 0,
  "limit": 100,
  "offset": 0,
  "has_more": false
}
```

### Step 3: Get Transaction Statistics

```bash
curl -s "http://localhost:8000/api/v1/transactions/stats/summary" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

**Expected Response:**
```json
{
  "total_count": 0,
  "total_income": 0.0,
  "total_expenses": 0.0,
  "net_amount": 0.0,
  "average_transaction": 0.0,
  "categories_breakdown": {},
  "monthly_trend": {}
}
```

---

## To Get Real Transaction Data

### Option 1: Sync from Connected Bank

If you've already connected a bank via Plaid:

```bash
# 1. Get your institution_id
curl -s "http://localhost:8000/api/v1/plaid/institutions/" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

# 2. Copy the institution "id" from response, then sync
INSTITUTION_ID="your-institution-uuid-here"

curl -s -X POST "http://localhost:8000/api/v1/plaid/sync/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"institution_id\": \"$INSTITUTION_ID\"}" | python3 -m json.tool
```

**Expected Sync Response:**
```json
{
  "institution_id": "uuid...",
  "accounts_updated": 2,
  "transactions_added": 45,
  "last_synced_at": "2026-01-31T...",
  "success": true
}
```

### Option 2: Connect Bank via Plaid First

See [PLAID_TESTING_GUIDE.md](PLAID_TESTING_GUIDE.md) for full Plaid connection flow.

---

## Advanced Transaction Queries

### Filter by Date Range

```bash
curl -s "http://localhost:8000/api/v1/transactions/?start_date=2026-01-01&end_date=2026-01-31" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

### Search by Merchant/Name

```bash
# Search for coffee shops
curl -s "http://localhost:8000/api/v1/transactions/?search=coffee" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

# Search for Amazon
curl -s "http://localhost:8000/api/v1/transactions/?search=amazon" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

### Filter by Category

```bash
# Get all Food & Dining transactions
curl -s "http://localhost:8000/api/v1/transactions/?category=Food%20%26%20Dining" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

# Get all Shopping transactions
curl -s "http://localhost:8000/api/v1/transactions/?category=Shopping" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

### Filter by Amount Range

```bash
# Transactions between $10 and $100
curl -s "http://localhost:8000/api/v1/transactions/?min_amount=10&max_amount=100" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

# Large transactions over $500
curl -s "http://localhost:8000/api/v1/transactions/?min_amount=500" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

### Filter by Transaction Type

```bash
# Only expenses (debit)
curl -s "http://localhost:8000/api/v1/transactions/?type=debit" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

# Only income (credit)
curl -s "http://localhost:8000/api/v1/transactions/?type=credit" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

### Get Recurring Transactions

```bash
curl -s "http://localhost:8000/api/v1/transactions/?is_recurring=true" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

### Pagination

```bash
# First 20 transactions
curl -s "http://localhost:8000/api/v1/transactions/?limit=20&offset=0" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

# Next 20 transactions
curl -s "http://localhost:8000/api/v1/transactions/?limit=20&offset=20" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

---

## Transaction Operations

### Get Single Transaction

```bash
TRANSACTION_ID="transaction-uuid-from-list"

curl -s "http://localhost:8000/api/v1/transactions/$TRANSACTION_ID/" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

### Update Transaction

```bash
# Add custom category and notes
curl -s -X PUT "http://localhost:8000/api/v1/transactions/$TRANSACTION_ID/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_category": "Business Expenses",
    "user_notes": "Client lunch meeting",
    "is_excluded": false
  }' | python3 -m json.tool
```

### Bulk Categorize

```bash
# Categorize multiple transactions at once
curl -s -X POST "http://localhost:8000/api/v1/transactions/bulk-categorize/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_ids": [
      "uuid-1",
      "uuid-2",
      "uuid-3"
    ],
    "category": "Entertainment"
  }' | python3 -m json.tool
```

---

## Analytics & Statistics

### Get Spending Summary

```bash
# Last 30 days (default)
curl -s "http://localhost:8000/api/v1/transactions/stats/summary" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

# Custom date range
curl -s "http://localhost:8000/api/v1/transactions/stats/summary?start_date=2026-01-01&end_date=2026-01-31" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

**Response includes:**
- Total transaction count
- Total income
- Total expenses
- Net amount (income - expenses)
- Average transaction amount
- Spending breakdown by category
- Monthly trends

---

## Automatic Features

### Smart Category Mapping

Transactions are automatically categorized based on Plaid's categories:
- "Food and Drink" → "Food & Dining"
- "Groceries" → "Groceries"
- "Transportation" → "Transportation"
- "Shopping" → "Shopping"
- "Entertainment" → "Entertainment"
- etc.

### Recurring Transaction Detection

The system automatically detects recurring transactions by:
- Finding similar transactions (same merchant, same amount)
- Analyzing frequency (monthly, weekly, etc.)
- Marking transactions with `is_recurring: true`

---

## Interactive API Documentation

**Best way to test:** Open in browser:
```
http://localhost:8000/docs
```

This gives you:
- Interactive Swagger UI
- Try all endpoints with one click
- See request/response schemas
- No need to write curl commands

### Key Sections in API Docs:
1. **Authentication** - Login/register
2. **Plaid** - Bank connections
3. **Transactions** - All transaction operations (NEW!)
4. **Users** - User profile and preferences

---

## Sample Transaction Response

```json
{
  "id": "transaction-uuid",
  "account_id": "account-uuid",
  "date": "2026-01-30",
  "authorized_date": "2026-01-29",
  "name": "STARBUCKS STORE #12345",
  "merchant_name": "Starbucks",
  "amount": 6.75,
  "currency": "USD",
  "type": "debit",
  "status": "posted",
  "category": "Food & Dining",
  "category_detailed": "Coffee Shop",
  "user_category": null,
  "user_notes": null,
  "is_excluded": false,
  "location_city": "San Francisco",
  "payment_channel": "in store",
  "is_recurring": true,
  "recurring_frequency": "occasional",
  "created_at": "2026-01-31T01:23:45Z",
  "updated_at": "2026-01-31T01:23:45Z"
}
```

---

## Troubleshooting

### "No transactions found"
- Make sure you've connected a bank via Plaid
- Run the sync endpoint to fetch transactions
- Plaid sandbox accounts have test transactions

### "Could not validate credentials"
- Your access token expired (30 min lifetime)
- Get a fresh token by logging in again

### "Institution not found"
- Check you have the correct institution_id
- List institutions first with GET /api/v1/plaid/institutions

### Sync fails
- Check Plaid credentials in .env
- Verify institution is still active
- Check server logs: `tail -f backend/server.log`

---

## Full Testing Workflow

```bash
# 1. Login
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "SecurePass123!"}' | \
  python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

# 2. Check connected institutions
curl -s http://localhost:8000/api/v1/plaid/institutions \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

# 3. Sync transactions (replace with your institution_id)
curl -s -X POST http://localhost:8000/api/v1/plaid/sync \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"institution_id": "your-institution-uuid"}' | python3 -m json.tool

# 4. List recent transactions
curl -s "http://localhost:8000/api/v1/transactions?limit=10" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

# 5. Get spending statistics
curl -s http://localhost:8000/api/v1/transactions/stats/summary \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

---

## What's Working

✅ Transaction model with 25+ fields
✅ Automatic syncing from Plaid
✅ Smart category mapping
✅ Recurring transaction detection
✅ Advanced filtering (date, amount, category, merchant, etc.)
✅ Search functionality
✅ Transaction statistics and analytics
✅ User customization (categories, notes, exclusions)
✅ Bulk operations
✅ Pagination support
✅ REST API with full CRUD

Phase 3 is **complete and ready for use!**
