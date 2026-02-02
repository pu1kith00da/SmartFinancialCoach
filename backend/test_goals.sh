#!/bin/bash

# Test Goals API

echo "=== Phase 5: Goals & Savings Testing ==="
echo ""

# 1. Login
echo "1. Logging in..."
TOKEN=$(curl -s -L -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"testuser4@fincoach.com","password":"SecurePass123!"}' | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

if [ -z "$TOKEN" ]; then
  echo "❌ Failed to get token"
  exit 1
fi

echo "✅ Token obtained"
echo ""

# 2. Create Emergency Fund Goal
echo "2. Creating Emergency Fund goal..."
GOAL_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/goals" \
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
  }')

GOAL_ID=$(echo $GOAL_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null)

if [ -z "$GOAL_ID" ]; then
  echo "❌ Failed to create goal"
  echo "Response: $GOAL_RESPONSE"
  exit 1
fi

echo "✅ Goal created: $GOAL_ID"
echo "Response:"
echo $GOAL_RESPONSE | python3 -m json.tool
echo ""

# 3. List Goals
echo "3. Listing all goals..."
curl -s "http://localhost:8000/api/v1/goals" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""

# 4. Add Contribution
echo "4. Adding contribution of \$500..."
curl -s -X POST "http://localhost:8000/api/v1/goals/$GOAL_ID/contributions" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 500,
    "notes": "First automatic transfer",
    "source": "auto"
  }' | python3 -m json.tool
echo ""

# 5. Get Progress
echo "5. Getting goal progress..."
curl -s "http://localhost:8000/api/v1/goals/$GOAL_ID/progress" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""

# 6. Feasibility Analysis
echo "6. Analyzing feasibility..."
curl -s "http://localhost:8000/api/v1/goals/$GOAL_ID/feasibility" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""

# 7. Round-up Estimate
echo "7. Estimating round-up savings..."
curl -s "http://localhost:8000/api/v1/goals/roundup-estimate?days=30" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""

echo "=== All tests completed! ==="
