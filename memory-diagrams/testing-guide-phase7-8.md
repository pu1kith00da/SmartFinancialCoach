# Testing Guide: Phase 7 & 8

## Smart Financial Coach API Testing Guide
**Phases Covered**: 
- Phase 7: AI Insights Engine
- Phase 8: Analytics & Reports

**Date**: January 31, 2026  
**API Base URL**: `http://localhost:8000`

---

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Authentication Setup](#authentication-setup)
3. [Phase 7: Testing AI Insights](#phase-7-testing-ai-insights)
4. [Phase 8: Testing Analytics](#phase-8-testing-analytics)
5. [Integration Testing Scenarios](#integration-testing-scenarios)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### 1. Start the Server
```bash
cd /Users/pulkithooda/smart-fin-coach
./start-dev.sh
```

Or manually:
```bash
cd /Users/pulkithooda/smart-fin-coach/backend
source venv/bin/activate
python run.py
```

### 2. Verify Server is Running
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "Smart Financial Coach API",
  "version": "1.0.0"
}
```

### 3. Check API Documentation
Open in browser: http://localhost:8000/docs

---

## Authentication Setup

### Step 1: Register a Test User
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@fincoach.app",
    "password": "SecurePassword123!",
    "first_name": "Test",
    "last_name": "User"
  }'
```

Expected response (save the access_token):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "uuid-here",
    "email": "test@fincoach.app",
    "first_name": "Test",
    "last_name": "User"
  }
}
```

### Step 2: Login (if user already exists)
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@fincoach.app",
    "password": "SecurePassword123!"
  }'
```

### Step 3: Set Token as Environment Variable
```bash
export TOKEN="your-access-token-here"
```

### Step 4: Verify Authentication
```bash
curl http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer $TOKEN"
```

---

## Phase 7: Testing AI Insights

### 7.1 List All Insights
```bash
curl -X GET "http://localhost:8000/api/v1/insights/" \
  -H "Authorization: Bearer $TOKEN" \
  | python3 -m json.tool
```

**Query Parameters**:
- `type`: Filter by insight type (spending_alert, savings_opportunity, etc.)
- `priority`: Filter by priority (low, normal, high, urgent)
- `is_read`: Filter by read status (true/false)
- `is_dismissed`: Filter by dismissed status (true/false)
- `limit`: Number of results (default: 20, max: 100)
- `offset`: Pagination offset

Example with filters:
```bash
curl -X GET "http://localhost:8000/api/v1/insights/?is_read=false&priority=high&limit=5" \
  -H "Authorization: Bearer $TOKEN" \
  | python3 -m json.tool
```

Expected response:
```json
{
  "insights": [
    {
      "id": "uuid",
      "user_id": "uuid",
      "type": "spending_alert",
      "priority": "high",
      "title": "High Spending Alert",
      "message": "Your spending increased by 30% this month",
      "is_read": false,
      "is_dismissed": false,
      "created_at": "2026-01-31T10:00:00Z"
    }
  ],
  "total": 1,
  "limit": 5,
  "offset": 0,
  "has_more": false
}
```

### 7.2 Get Daily Nudge
Get today's most important insight:
```bash
curl -X GET "http://localhost:8000/api/v1/insights/daily" \
  -H "Authorization: Bearer $TOKEN" \
  | python3 -m json.tool
```

Expected response:
```json
{
  "insight": {
    "id": "uuid",
    "type": "savings_opportunity",
    "priority": "normal",
    "title": "Save on Dining",
    "message": "You spent $450 on dining this month. Reducing by 20% could save you $90!"
  },
  "has_insight": true
}
```

Or if no insights:
```json
{
  "insight": null,
  "has_insight": false,
  "message": "You're all caught up! Check back tomorrow for new insights."
}
```

### 7.3 Get Specific Insight
```bash
curl -X GET "http://localhost:8000/api/v1/insights/{insight_id}" \
  -H "Authorization: Bearer $TOKEN" \
  | python3 -m json.tool
```

### 7.4 Mark Insight as Read
```bash
curl -X POST "http://localhost:8000/api/v1/insights/{insight_id}/read" \
  -H "Authorization: Bearer $TOKEN" \
  | python3 -m json.tool
```

Expected response:
```json
{
  "id": "uuid",
  "is_read": true,
  "read_at": "2026-01-31T10:15:00Z",
  ...
}
```

### 7.5 Dismiss an Insight
```bash
curl -X POST "http://localhost:8000/api/v1/insights/{insight_id}/dismiss" \
  -H "Authorization: Bearer $TOKEN" \
  | python3 -m json.tool
```

Expected response:
```json
{
  "id": "uuid",
  "is_dismissed": true,
  "dismissed_at": "2026-01-31T10:20:00Z",
  ...
}
```

### 7.6 Generate Insights Manually
Trigger insight generation for testing:
```bash
curl -X POST "http://localhost:8000/api/v1/insights/generate" \
  -H "Authorization: Bearer $TOKEN" \
  | python3 -m json.tool
```

Expected response:
```json
{
  "insights": [
    {
      "id": "uuid",
      "type": "spending_alert",
      "title": "Spending Increase Detected",
      "message": "Your spending in Food & Dining increased by 45%",
      "priority": "normal"
    }
  ],
  "total": 1,
  "limit": 1,
  "offset": 0,
  "has_more": false
}
```

### 7.7 Get Insight Analytics
Get statistics about insights:
```bash
curl -X GET "http://localhost:8000/api/v1/insights/analytics" \
  -H "Authorization: Bearer $TOKEN" \
  | python3 -m json.tool
```

Expected response:
```json
{
  "total_insights": 25,
  "total_read": 18,
  "total_dismissed": 3,
  "read_rate": 72.0,
  "dismiss_rate": 12.0,
  "insights_by_type": {
    "spending_alert": 8,
    "savings_opportunity": 6,
    "goal_progress": 4,
    "celebration": 3,
    "tip": 4
  },
  "insights_by_priority": {
    "high": 5,
    "normal": 15,
    "low": 5
  },
  "recent_insights_count": 8,
  "avg_insights_per_week": 3.5
}
```

### 7.8 Detect Anomalies
Run anomaly detection on transactions:
```bash
curl -X POST "http://localhost:8000/api/v1/insights/detect-anomalies" \
  -H "Authorization: Bearer $TOKEN" \
  | python3 -m json.tool
```

Expected response:
```json
{
  "anomalies_found": 2,
  "insights_created": 2,
  "insights": [
    {
      "id": "uuid",
      "type": "anomaly",
      "priority": "high",
      "title": "Unusual Transaction Detected",
      "message": "Transaction of $1,250 is significantly higher than your average"
    }
  ]
}
```

---

## Phase 8: Testing Analytics

### 8.1 Dashboard Summary
Get comprehensive dashboard overview:
```bash
curl -X GET "http://localhost:8000/api/v1/analytics/dashboard" \
  -H "Authorization: Bearer $TOKEN" \
  | python3 -m json.tool
```

Expected response:
```json
{
  "current_balance": 5432.50,
  "total_income_this_month": 4500.00,
  "total_spending_this_month": 2345.67,
  "net_cash_flow_this_month": 2154.33,
  "savings_rate": 47.87,
  "active_budgets_count": 5,
  "over_budget_count": 1,
  "active_goals_count": 3,
  "goals_on_track": 2,
  "net_worth": 45678.90,
  "net_worth_change": 1234.56,
  "top_spending_categories": [
    {
      "category": "Food & Dining",
      "amount": 450.00,
      "transaction_count": 23,
      "percentage": 19.18,
      "average_transaction": 19.57
    }
  ],
  "upcoming_bills_count": 4,
  "upcoming_bills_amount": 875.00,
  "active_subscriptions_count": 6,
  "monthly_subscription_cost": 89.94,
  "recent_insights_count": 8,
  "unread_insights_count": 3
}
```

### 8.2 Spending Analytics
Get detailed spending analysis:

**Current Month** (default):
```bash
curl -X GET "http://localhost:8000/api/v1/analytics/spending" \
  -H "Authorization: Bearer $TOKEN" \
  | python3 -m json.tool
```

**Custom Date Range**:
```bash
curl -X GET "http://localhost:8000/api/v1/analytics/spending?start_date=2026-01-01&end_date=2026-01-31" \
  -H "Authorization: Bearer $TOKEN" \
  | python3 -m json.tool
```

**With Comparison to Previous Period**:
```bash
curl -X GET "http://localhost:8000/api/v1/analytics/spending?compare=true" \
  -H "Authorization: Bearer $TOKEN" \
  | python3 -m json.tool
```

Expected response:
```json
{
  "total_spending": 2345.67,
  "period_start": "2026-01-01",
  "period_end": "2026-01-31",
  "by_category": [
    {
      "category": "Food & Dining",
      "amount": 450.00,
      "transaction_count": 23,
      "percentage": 19.18,
      "average_transaction": 19.57
    },
    {
      "category": "Transportation",
      "amount": 320.50,
      "transaction_count": 15,
      "percentage": 13.66,
      "average_transaction": 21.37
    }
  ],
  "trend_data": [
    {
      "date": "2026-01-01",
      "amount": 75.23,
      "transaction_count": 4
    }
  ],
  "top_merchants": [
    {
      "merchant": "Whole Foods",
      "amount": 234.56,
      "count": 8
    }
  ],
  "daily_average": 75.67,
  "comparison_to_previous_period": 15.5
}
```

### 8.3 Income Analytics
Get income analysis:
```bash
curl -X GET "http://localhost:8000/api/v1/analytics/income" \
  -H "Authorization: Bearer $TOKEN" \
  | python3 -m json.tool
```

With parameters:
```bash
curl -X GET "http://localhost:8000/api/v1/analytics/income?start_date=2026-01-01&end_date=2026-01-31&compare=true" \
  -H "Authorization: Bearer $TOKEN" \
  | python3 -m json.tool
```

Expected response:
```json
{
  "total_income": 4500.00,
  "period_start": "2026-01-01",
  "period_end": "2026-01-31",
  "by_source": [
    {
      "source": "Salary",
      "amount": 4000.00,
      "transaction_count": 2,
      "percentage": 88.89
    },
    {
      "source": "Freelance",
      "amount": 500.00,
      "transaction_count": 3,
      "percentage": 11.11
    }
  ],
  "trend_data": [
    {
      "date": "2026-01-15",
      "amount": 2000.00
    }
  ],
  "monthly_average": 4500.00,
  "comparison_to_previous_period": 5.2
}
```

### 8.4 Cash Flow Analytics
Get income vs expenses:
```bash
curl -X GET "http://localhost:8000/api/v1/analytics/cash-flow" \
  -H "Authorization: Bearer $TOKEN" \
  | python3 -m json.tool
```

Expected response:
```json
{
  "period_start": "2026-01-01",
  "period_end": "2026-01-31",
  "total_income": 4500.00,
  "total_expenses": 2345.67,
  "net_cash_flow": 2154.33,
  "periods": [
    {
      "date": "2026-01-01",
      "income": 0,
      "expenses": 75.23,
      "net_cash_flow": -75.23
    },
    {
      "date": "2026-01-15",
      "income": 2000.00,
      "expenses": 120.45,
      "net_cash_flow": 1879.55
    }
  ],
  "average_monthly_income": 4500.00,
  "average_monthly_expenses": 2345.67,
  "savings_rate": 47.87
}
```

### 8.5 Net Worth History
Get historical net worth data:
```bash
curl -X GET "http://localhost:8000/api/v1/analytics/net-worth" \
  -H "Authorization: Bearer $TOKEN" \
  | python3 -m json.tool
```

With filters:
```bash
curl -X GET "http://localhost:8000/api/v1/analytics/net-worth?start_date=2025-01-01&limit=50" \
  -H "Authorization: Bearer $TOKEN" \
  | python3 -m json.tool
```

Expected response:
```json
{
  "snapshots": [
    {
      "id": "uuid",
      "user_id": "uuid",
      "total_assets": 75000.00,
      "total_liabilities": 29321.10,
      "net_worth": 45678.90,
      "liquid_assets": 15000.00,
      "investment_assets": 50000.00,
      "fixed_assets": 10000.00,
      "credit_card_debt": 2500.00,
      "student_loans": 15000.00,
      "mortgage_debt": 10000.00,
      "auto_loans": 1821.10,
      "snapshot_date": "2026-01-31T00:00:00Z",
      "debt_to_asset_ratio": 0.39,
      "liquid_ratio": 0.20,
      "created_at": "2026-01-31T10:00:00Z"
    }
  ],
  "total_count": 12,
  "period_start": "2025-01-01",
  "period_end": "2026-01-31",
  "net_worth_change": 5678.90,
  "percentage_change": 14.2
}
```

### 8.6 Create Net Worth Snapshot
Manually record net worth:
```bash
curl -X POST "http://localhost:8000/api/v1/analytics/net-worth" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "total_assets": 75000.00,
    "total_liabilities": 29321.10,
    "liquid_assets": 15000.00,
    "investment_assets": 50000.00,
    "fixed_assets": 10000.00,
    "credit_card_debt": 2500.00,
    "student_loans": 15000.00,
    "mortgage_debt": 10000.00,
    "auto_loans": 1821.10,
    "notes": "January 2026 snapshot"
  }' \
  | python3 -m json.tool
```

Expected response:
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "total_assets": 75000.00,
  "total_liabilities": 29321.10,
  "net_worth": 45678.90,
  "debt_to_asset_ratio": 0.39,
  "liquid_ratio": 0.20,
  "snapshot_date": "2026-01-31T10:30:00Z",
  "notes": "January 2026 snapshot",
  "created_at": "2026-01-31T10:30:00Z"
}
```

### 8.7 Get Latest Net Worth
```bash
curl -X GET "http://localhost:8000/api/v1/analytics/net-worth/latest" \
  -H "Authorization: Bearer $TOKEN" \
  | python3 -m json.tool
```

### 8.8 Spending Trends (Multi-Month)
Get spending trends over multiple months:
```bash
curl -X GET "http://localhost:8000/api/v1/analytics/trends/spending?months=6" \
  -H "Authorization: Bearer $TOKEN" \
  | python3 -m json.tool
```

Expected response:
```json
{
  "trends": [
    {
      "month": "2026-01",
      "total": 2345.67,
      "by_category": [
        {
          "category": "Food & Dining",
          "amount": 450.00
        }
      ]
    },
    {
      "month": "2025-12",
      "total": 2100.45,
      "by_category": [...]
    }
  ]
}
```

### 8.9 Period Comparison
Compare current period with previous:
```bash
curl -X GET "http://localhost:8000/api/v1/analytics/comparison?period_type=month" \
  -H "Authorization: Bearer $TOKEN" \
  | python3 -m json.tool
```

Period types: `week`, `month`, `quarter`, `year`

Expected response:
```json
{
  "period_type": "month",
  "current": {
    "start": "2026-01-01",
    "end": "2026-01-31",
    "spending": 2345.67,
    "income": 4500.00,
    "net": 2154.33
  },
  "previous": {
    "start": "2025-12-01",
    "end": "2025-12-31",
    "spending": 2100.45,
    "income": 4300.00,
    "net": 2199.55
  },
  "changes": {
    "spending": 245.22,
    "income": 200.00,
    "net": -45.22
  }
}
```

---

## Integration Testing Scenarios

### Scenario 1: Complete User Journey

```bash
# 1. Register user
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"journey@test.com","password":"Test123!","first_name":"Journey","last_name":"Test"}'

# 2. Login and get token
export TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"journey@test.com","password":"Test123!"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# 3. Get dashboard (should be mostly empty)
curl -X GET "http://localhost:8000/api/v1/analytics/dashboard" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

# 4. Generate insights
curl -X POST "http://localhost:8000/api/v1/insights/generate" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

# 5. Check daily nudge
curl -X GET "http://localhost:8000/api/v1/insights/daily" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

# 6. Create net worth snapshot
curl -X POST "http://localhost:8000/api/v1/analytics/net-worth" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"total_assets":50000,"total_liabilities":20000}' \
  | python3 -m json.tool
```

### Scenario 2: Insight Lifecycle

```bash
# 1. Generate insights
INSIGHTS=$(curl -s -X POST "http://localhost:8000/api/v1/insights/generate" \
  -H "Authorization: Bearer $TOKEN")

# 2. Get first insight ID
INSIGHT_ID=$(echo $INSIGHTS | python3 -c "import sys,json; data=json.load(sys.stdin); print(data['insights'][0]['id']) if data['insights'] else print('none')")

# 3. Mark as read
curl -X POST "http://localhost:8000/api/v1/insights/$INSIGHT_ID/read" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

# 4. Get insight analytics
curl -X GET "http://localhost:8000/api/v1/insights/analytics" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

### Scenario 3: Analytics Deep Dive

```bash
# 1. Get spending analytics with comparison
curl -X GET "http://localhost:8000/api/v1/analytics/spending?compare=true" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

# 2. Get income analytics
curl -X GET "http://localhost:8000/api/v1/analytics/income?compare=true" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

# 3. Get cash flow
curl -X GET "http://localhost:8000/api/v1/analytics/cash-flow" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

# 4. Compare periods
curl -X GET "http://localhost:8000/api/v1/analytics/comparison?period_type=month" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

# 5. Get 6-month trends
curl -X GET "http://localhost:8000/api/v1/analytics/trends/spending?months=6" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

---

## Troubleshooting

### Issue: 401 Unauthorized
**Problem**: Token expired or invalid  
**Solution**: 
```bash
# Login again to get new token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"your-email@test.com","password":"your-password"}'

# Set new token
export TOKEN="new-token-here"
```

### Issue: 404 Not Found
**Problem**: Endpoint doesn't exist or wrong URL  
**Solution**: 
- Check API docs: http://localhost:8000/docs
- Verify endpoint path
- Ensure server is running on correct port

### Issue: No Insights Generated
**Problem**: Insufficient transaction data  
**Solution**:
1. Add sample transactions first
2. Insights require transaction history to analyze
3. Check that transactions have categories

### Issue: Empty Analytics
**Problem**: No transaction or financial data  
**Solution**:
1. Create transactions first
2. Add net worth snapshots for net worth analytics
3. Ensure date ranges include existing data

### Issue: Server Not Starting
**Problem**: Port in use or configuration error  
**Solution**:
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Check database connection
docker ps  # Ensure postgres is running

# Check logs
cd /Users/pulkithooda/smart-fin-coach/backend
tail -f logs/app.log  # if logging is configured
```

### Issue: Database Migration Errors
**Problem**: Migration not applied  
**Solution**:
```bash
cd /Users/pulkithooda/smart-fin-coach/backend
source venv/bin/activate

# Check current version
alembic current

# Upgrade to latest
alembic upgrade head

# If issues, check migration history
alembic history
```

---

## Testing Checklist

### Phase 7: AI Insights
- [ ] List insights with filters
- [ ] Get daily nudge
- [ ] Get specific insight
- [ ] Mark insight as read
- [ ] Dismiss insight
- [ ] Generate insights manually
- [ ] Get insight analytics
- [ ] Detect anomalies

### Phase 8: Analytics
- [ ] Get dashboard summary
- [ ] Get spending analytics (current month)
- [ ] Get spending analytics (custom range)
- [ ] Get spending analytics (with comparison)
- [ ] Get income analytics
- [ ] Get cash flow analytics
- [ ] Create net worth snapshot
- [ ] Get net worth history
- [ ] Get latest net worth
- [ ] Get spending trends
- [ ] Compare periods (week/month/quarter/year)

### Integration Tests
- [ ] Complete user journey
- [ ] Insight lifecycle
- [ ] Analytics deep dive
- [ ] Period comparisons work correctly
- [ ] All filters and query parameters work
- [ ] Authentication works across all endpoints
- [ ] Error handling works properly

---

## Performance Testing

### Load Testing
Test with multiple concurrent requests:
```bash
# Install Apache Bench
brew install httpd  # macOS

# Test dashboard endpoint
ab -n 100 -c 10 -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/analytics/dashboard

# Test insights list
ab -n 100 -c 10 -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/insights/
```

### Response Time Benchmarks
Expected response times:
- Dashboard: < 500ms
- Spending Analytics: < 300ms
- Income Analytics: < 300ms
- Cash Flow: < 400ms
- Net Worth History: < 200ms
- Insights List: < 200ms
- Generate Insights: < 2000ms (includes LLM call)

---

## Next Steps

After completing Phase 7 & 8 testing:
1. Document any bugs or issues found
2. Test edge cases (empty data, large datasets, invalid inputs)
3. Performance optimization if needed
4. Prepare for Phase 9: Gamification testing
5. Consider adding automated tests (pytest)

---

**Testing Guide Version**: 1.0  
**Last Updated**: January 31, 2026  
**Maintainer**: Smart Financial Coach Team