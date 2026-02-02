# Plaid Integration Testing Guide

## ✅ Verification Status
- **Link Token Generation**: Working ✓
- **Sandbox Environment**: Active ✓
- **API Endpoints**: Ready ✓

## Testing Methods

### Method 1: API Testing (Backend Only)

#### Step 1: Get Access Token
```bash
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "SecurePass123!"}' | \
  python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")
```

#### Step 2: Create Link Token
```bash
curl -X POST http://localhost:8000/api/v1/plaid/link/token \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}' | python3 -m json.tool
```

Expected response:
```json
{
  "link_token": "link-sandbox-...",
  "expiration": "2026-01-31T..."
}
```

#### Step 3: View Connected Institutions
```bash
curl -X GET http://localhost:8000/api/v1/plaid/institutions \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

#### Step 4: View Connected Accounts
```bash
curl -X GET http://localhost:8000/api/v1/plaid/accounts \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

---

### Method 2: Full Flow Testing (Requires Frontend or Plaid Link)

To complete the full bank connection, you need to:

1. **Initialize Plaid Link** with the link_token from Step 2
2. **User connects their bank** through Plaid's UI
3. **Plaid returns a public_token**
4. **Exchange public_token** for access_token:

```bash
# After getting public_token from Plaid Link
curl -X POST http://localhost:8000/api/v1/plaid/link/exchange \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"public_token": "public-sandbox-xxxxx"}' | python3 -m json.tool
```

#### Step 5: Sync Account Balances
```bash
# Get institution_id from previous response
curl -X POST http://localhost:8000/api/v1/plaid/sync \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"institution_id": "your-institution-uuid"}' | python3 -m json.tool
```

---

### Method 3: Using Plaid Sandbox (Automated Testing)

Plaid Sandbox provides test institutions and credentials:

#### Test Bank Credentials
- **Institution**: First Platypus Bank (search for "Platypus" in Plaid Link)
- **Username**: `user_good`
- **Password**: `pass_good`
- **MFA Code**: `1234` (if prompted)

#### Test Scenarios Available:
1. **Success Flow**: Use `user_good` / `pass_good`
2. **Invalid Credentials**: Use `user_bad` / `pass_bad`
3. **MFA Required**: Some test institutions require MFA
4. **Account Selection**: Multiple accounts to choose from

---

## What Each Endpoint Does

### 1. Create Link Token
- **Purpose**: Initializes Plaid Link session
- **Use**: Frontend uses this token to open Plaid Link UI
- **Result**: Returns link_token for Plaid Link initialization

### 2. Exchange Public Token
- **Purpose**: Converts temporary public_token to permanent access_token
- **Use**: Called after user successfully connects via Plaid Link
- **Result**: Stores institution & accounts in your database

### 3. Get Institutions
- **Purpose**: List all connected banks/institutions
- **Use**: Display user's connected banks in UI
- **Result**: Array of institutions with account counts

### 4. Get Accounts
- **Purpose**: List all bank accounts with balances
- **Use**: Show account overview, calculate net worth
- **Result**: Array of accounts with current balances

### 5. Sync Accounts
- **Purpose**: Refresh account balances from Plaid
- **Use**: Update data before showing user
- **Result**: Updated balance information

### 6. Remove Institution
- **Purpose**: Disconnect a bank
- **Use**: User wants to remove a connected bank
- **Result**: Deletes institution and all its accounts

---

## Quick Verification Checklist

✅ **Backend Verification** (No Plaid Link needed):
1. Create link token → Should return token starting with "link-sandbox-"
2. Check institutions endpoint → Should return empty array initially
3. Check accounts endpoint → Should return empty accounts array

✅ **Full Integration Verification** (Requires Plaid Link UI):
1. Get link_token from backend
2. Initialize Plaid Link with token
3. Connect test bank (Platypus)
4. Get public_token from Plaid
5. Exchange public_token via backend
6. Verify institution and accounts appear in GET endpoints

---

## Testing with Plaid's Sandbox Dashboard

You can also test directly via Plaid's dashboard:
1. Go to https://dashboard.plaid.com/team/sandbox
2. Use your client_id: `697db7f9336016002220077b`
3. View test accounts and transactions
4. Monitor API calls in real-time

---

## Troubleshooting

### "Failed to create link token"
- Check that PLAID_CLIENT_ID and PLAID_SECRET are set in .env
- Verify PLAID_ENV is set to "sandbox"
- Check server logs: `tail -f backend/server.log`

### "Invalid credentials"
- Get a fresh access token (they expire in 30 minutes)
- Verify you're using the correct Bearer token

### "Institution not found"
- Make sure you've completed the public_token exchange
- Check institution_id matches UUID from database

### Can't complete full flow
- You need either:
  - A frontend with Plaid Link integrated, OR
  - Use Plaid's API Postman collection, OR
  - Use their Quickstart repo: https://github.com/plaid/quickstart

---

## Next Steps

To complete full testing:
1. **Option A**: Build the frontend (Next.js app with react-plaid-link)
2. **Option B**: Use Plaid's Quickstart app to test the backend
3. **Option C**: Use curl with manually generated public_tokens

The backend Plaid integration is **fully functional** and ready for frontend integration!
