# Goals & Savings Testing Guide

## Phase 5: Goals & Savings System

This guide covers testing the complete Goals & Savings functionality including goal creation, contribution tracking, progress monitoring, and feasibility analysis.

## Prerequisites

1. Server running on port 8000
2. User registered and logged in
3. Test credentials: `testuser4@fincoach.com` / `SecurePass123!`

## Quick Start

### 1. Get Authentication Token

```bash
# Login and get token
TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login/" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser4@fincoach.com" \
  -d "password=SecurePass123!" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

echo "Token: ${TOKEN:0:20}..."
```

### 2. Create an Emergency Fund Goal

```bash
curl -X POST "http://localhost:8000/api/v1/goals/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Emergency Fund",
    "description": "Build 6 months of expenses",
    "type": "emergency_fund",
    "priority": "high",
    "target_amount": 15000,
    "target_date": "2024-12-31",
    "monthly_target": 1250,
    "auto_contribute": true,
    "auto_contribute_amount": 500,
    "auto_contribute_day": 1,
    "enable_roundup": true,
    "current_amount": 2000
  }' | python3 -m json.tool
```

**Expected Response:**
- Goal ID (UUID)
- All goal details
- `status`: "active"
- `progress_percentage`: 13.33 (2000/15000)
- `remaining_amount`: 13000
- `is_on_track`: true/false based on projection

### 3. List All Goals

```bash
curl -s "http://localhost:8000/api/v1/goals/" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

**Expected Response:**
```json
{
  "goals": [...],
  "total": 1,
  "active_count": 1,
  "completed_count": 0
}
```

### 4. Get Goal Details

```bash
# Save goal ID from creation response
GOAL_ID="<your-goal-id>"

curl -s "http://localhost:8000/api/v1/goals/$GOAL_ID/" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

### 5. Add a Contribution

```bash
curl -X POST "http://localhost:8000/api/v1/goals/$GOAL_ID/contributions/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 500,
    "notes": "Monthly automatic transfer",
    "source": "auto"
  }' | python3 -m json.tool
```

**Expected Response:**
- Contribution ID
- Updated goal's `current_amount` increases by 500
- If goal reaches target, `status` changes to "completed"

### 6. List Contributions

```bash
curl -s "http://localhost:8000/api/v1/goals/$GOAL_ID/contributions/" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

### 7. Get Progress Details

```bash
curl -s "http://localhost:8000/api/v1/goals/$GOAL_ID/progress/" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

**Expected Response:**
```json
{
  "goal": {...},
  "progress_percentage": 16.67,
  "remaining_amount": 12500,
  "days_remaining": 350,
  "months_remaining": 11.67,
  "projected_completion_date": "2024-12-15",
  "is_on_track": true,
  "required_monthly_contribution": 1071.43,
  "recent_contributions": [...],
  "total_contributed": 2500
}
```

### 8. Analyze Feasibility

```bash
curl -s "http://localhost:8000/api/v1/goals/$GOAL_ID/feasibility/" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

**Expected Response:**
```json
{
  "is_achievable": true,
  "confidence_level": "high",
  "estimated_completion_date": "2024-12-31",
  "required_monthly_savings": 1250,
  "current_savings_rate": 500,
  "shortfall_per_month": 750,
  "recommendations": [
    "Increase contributions by $750/month to stay on track",
    "Consider extending your target date for a more achievable pace",
    "Look for areas to reduce spending and redirect to this goal"
  ],
  "scenario_if_increase_10_percent": {
    "new_monthly_rate": 550,
    "estimated_completion": "2025-02-15"
  },
  "scenario_if_reduce_spending": {
    "monthly_savings_increase": 200,
    "new_monthly_rate": 700,
    "estimated_completion": "2024-11-20"
  }
}
```

### 9. Update Goal

```bash
curl -X PUT "http://localhost:8000/api/v1/goals/$GOAL_ID/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "target_amount": 18000,
    "monthly_target": 1500
  }' | python3 -m json.tool
```

### 10. Pause/Resume Goal

```bash
# Pause a goal
curl -X POST "http://localhost:8000/api/v1/goals/$GOAL_ID/pause/" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

# Resume a goal
curl -X POST "http://localhost:8000/api/v1/goals/$GOAL_ID/resume/" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

### 11. Complete Goal Manually

```bash
curl -X POST "http://localhost:8000/api/v1/goals/$GOAL_ID/complete/" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

### 12. Estimate Round-Up Savings

```bash
# Estimate savings from round-up feature over last 30 days
curl -s "http://localhost:8000/api/v1/goals/roundup-estimate/?days=30" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

**Expected Response:**
```json
{
  "period_days": 30,
  "total_roundup": 15.50,
  "monthly_estimate": 15.50,
  "yearly_estimate": 189.08,
  "message": "You could save $15.50 over 30 days with round-up savings"
}
```

## Complete Testing Workflow

### Create Multiple Goals

```bash
# 1. Emergency Fund
curl -X POST "http://localhost:8000/api/v1/goals/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Emergency Fund",
    "type": "emergency_fund",
    "priority": "critical",
    "target_amount": 15000,
    "target_date": "2024-12-31",
    "current_amount": 2000
  }' | python3 -m json.tool

# 2. Debt Payoff (Credit Card)
curl -X POST "http://localhost:8000/api/v1/goals/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Pay Off Credit Card",
    "type": "debt_payoff",
    "priority": "high",
    "target_amount": 5000,
    "target_date": "2024-09-01",
    "interest_rate": 18.99,
    "current_amount": 1200
  }' | python3 -m json.tool

# 3. Vacation Savings
curl -X POST "http://localhost:8000/api/v1/goals/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Europe Vacation",
    "type": "savings",
    "priority": "medium",
    "target_amount": 8000,
    "target_date": "2024-07-01",
    "icon": "✈️",
    "color": "#4A90E2",
    "enable_roundup": true
  }' | python3 -m json.tool

# 4. Retirement Savings
curl -X POST "http://localhost:8000/api/v1/goals/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Retirement Fund",
    "type": "retirement",
    "priority": "high",
    "target_amount": 1000000,
    "auto_contribute": true,
    "auto_contribute_amount": 500,
    "auto_contribute_day": 15
  }' | python3 -m json.tool

# 5. Car Repair Fund
curl -X POST "http://localhost:8000/api/v1/goals/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Car Repairs",
    "type": "irregular_expense",
    "priority": "medium",
    "target_amount": 2000,
    "current_amount": 500
  }' | python3 -m json.tool
```

### Filter Goals

```bash
# Get only active goals
curl -s "http://localhost:8000/api/v1/goals/?status=active" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

# Get only emergency fund goals
curl -s "http://localhost:8000/api/v1/goals/?goal_type=emergency_fund" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

# Get high priority goals
curl -s "http://localhost:8000/api/v1/goals/?priority=high" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

## Goal Types

### 1. Emergency Fund (`emergency_fund`)
- Recommended: 3-6 months of expenses
- Highest priority
- Should be liquid savings

### 2. Debt Payoff (`debt_payoff`)
- Track debt paydown
- Include interest rate for projection
- Can link to specific account

### 3. Savings (`savings`)
- General savings goals
- Vacation, down payment, etc.
- Can add images/icons

### 4. Retirement (`retirement`)
- Long-term retirement savings
- Automatic contributions
- Track progress over years

### 5. Irregular Expense (`irregular_expense`)
- Car repairs, medical expenses
- Seasonal expenses (holidays, back-to-school)
- One-time purchases

## Contribution Sources

- `manual`: Manually added by user
- `auto`: Automatic transfer from linked account
- `roundup`: Round-up savings from transactions
- `windfall`: One-time windfall (bonus, tax refund, gift)

## Status Workflow

```
                 ┌─────────┐
                 │ ACTIVE  │ ◄─┐
                 └────┬────┘   │
                      │        │ resume
              pause   │        │
                      ▼        │
                 ┌─────────┐   │
                 │ PAUSED  │───┘
                 └─────────┘

                 ┌─────────┐
  reach target   │         │  manual
  or manual ───► │COMPLETED│ ◄────
                 │         │
                 └─────────┘

                 ┌─────────┐
      manual ───►│CANCELLED│
                 └─────────┘
```

## API Endpoints Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/goals/` | Create goal |
| GET | `/api/v1/goals/` | List goals (with filters) |
| GET | `/api/v1/goals/{id}/` | Get goal details |
| PUT | `/api/v1/goals/{id}/` | Update goal |
| DELETE | `/api/v1/goals/{id}/` | Delete goal |
| POST | `/api/v1/goals/{id}/contributions/` | Add contribution |
| GET | `/api/v1/goals/{id}/contributions/` | List contributions |
| GET | `/api/v1/goals/{id}/progress/` | Get progress details |
| GET | `/api/v1/goals/{id}/feasibility/` | Analyze feasibility |
| POST | `/api/v1/goals/{id}/pause/` | Pause goal |
| POST | `/api/v1/goals/{id}/resume/` | Resume goal |
| POST | `/api/v1/goals/{id}/complete/` | Complete goal |
| GET | `/api/v1/goals/roundup-estimate/` | Estimate round-up savings |

## Troubleshooting

### Issue: 401 Unauthorized
**Solution**: Token may have expired (30-minute lifetime). Re-authenticate.

### Issue: 404 Goal not found
**Solution**: Verify goal ID and that goal belongs to current user.

### Issue: 400 Cannot be paused/resumed
**Solution**: Check current goal status. Can only pause ACTIVE goals and resume PAUSED goals.

### Issue: Progress not updating
**Solution**: Add contributions to update progress. System recalculates projection after each contribution.

## Next Steps

After testing Goals & Savings:
1. Phase 6: Subscriptions & Bills
2. Phase 7: Analytics & Reports
3. Phase 8: Frontend Development

---

**Note**: All endpoints require trailing slashes for consistency with the rest of the API.

**Tip**: Use `python3 -m json.tool` to pretty-print JSON responses for easier reading.
