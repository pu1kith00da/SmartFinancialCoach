# Phase 9 Gamification Testing Guide

## Overview
This guide provides comprehensive instructions for testing the Phase 9 Gamification features of the Smart Financial Coach API. Phase 9 introduces achievements, challenges, streaks, XP/leveling, and leaderboards to enhance user engagement.

**API Base URL**: `http://localhost:8000`  
**Documentation**: `http://localhost:8000/docs`

---

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Authentication Setup](#authentication-setup)
3. [Testing Gamification Dashboard](#testing-gamification-dashboard)
4. [Testing Achievements](#testing-achievements)
5. [Testing Challenges](#testing-challenges)
6. [Testing Streaks](#testing-streaks)
7. [Testing XP and Leveling](#testing-xp-and-leveling)
8. [Testing Leaderboard](#testing-leaderboard)
9. [Error Handling Tests](#error-handling-tests)
10. [Integration Testing Scenarios](#integration-testing-scenarios)

---

## Prerequisites

### 1. Start the Server
```bash
cd /Users/pulkithooda/smart-fin-coach/backend
/Users/pulkithooda/smart-fin-coach/backend/venv/bin/python run.py
```

### 2. Verify Server is Running
```bash
curl http://localhost:8000/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "service": "Smart Financial Coach API",
  "version": "1.0.0"
}
```

### 3. Verify Database Migration
```bash
cd /Users/pulkithooda/smart-fin-coach/backend
venv/bin/alembic current
```

Should show: `008 (head)`

---

## Authentication Setup

### Register a Test User
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "gamification_test@example.com",
    "password": "TestPassword123!",
    "first_name": "Gamification",
    "last_name": "Tester"
  }'
```

**Expected Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "uuid-here",
    "email": "gamification_test@example.com",
    "first_name": "Gamification",
    "last_name": "Tester"
  }
}
```

### Set Token Environment Variable
```bash
export TOKEN="your-access-token-here"
```

### Verify Authentication
```bash
curl http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer $TOKEN"
```

---

## Testing Gamification Dashboard

The dashboard provides a complete overview of the user's gamification status.

### Get Dashboard
```bash
curl -X GET http://localhost:8000/api/v1/gamification/dashboard \
  -H "Authorization: Bearer $TOKEN" \
  | python3 -m json.tool
```

**Expected Response Structure:**
```json
{
  "user_level": {
    "user_id": "uuid",
    "level": 1,
    "current_xp": 0,
    "xp_for_next_level": 150,
    "xp_progress_percentage": 0.0,
    "total_xp_earned": 0
  },
  "streak": {
    "id": "uuid",
    "user_id": "uuid",
    "current_streak": 0,
    "longest_streak": 0,
    "last_activity_date": null,
    "total_activity_days": 0
  },
  "active_challenges": [],
  "recent_achievements": [],
  "total_achievements": 25,
  "unlocked_achievements": 0,
  "achievement_completion_rate": 0.0,
  "total_xp_earned": 0,
  "level_progress": 0.0
}
```

**What to Check:**
- ✅ User starts at level 1 with 0 XP
- ✅ Streak data is initialized
- ✅ Total achievements count matches seeded data
- ✅ All fields are present and correctly typed

---

## Testing Achievements

### 1. List All Achievements
```bash
curl -X GET http://localhost:8000/api/v1/gamification/achievements \
  -H "Authorization: Bearer $TOKEN" \
  | python3 -m json.tool
```

**Expected Response:**
```json
{
  "achievements": [
    {
      "id": "uuid",
      "code": "first_savings",
      "name": "First Steps",
      "description": "Save your first $100",
      "category": "savings",
      "tier": "bronze",
      "xp_reward": 50,
      "icon": "💰",
      "criteria": {"savings_amount": 100},
      "is_secret": false,
      "is_repeatable": false,
      "sort_order": 1,
      "created_at": "2026-01-31T10:00:00Z",
      "updated_at": "2026-01-31T10:00:00Z"
    }
  ],
  "total": 25
}
```

**What to Check:**
- ✅ All 25+ achievements are returned
- ✅ Achievement categories: savings, spending, budgeting, goals, streaks, consistency, milestones
- ✅ Achievement tiers: bronze, silver, gold, platinum, diamond
- ✅ Each achievement has proper icon and criteria

### 2. Filter Achievements by Category
```bash
curl -X GET "http://localhost:8000/api/v1/gamification/achievements?category=savings" \
  -H "Authorization: Bearer $TOKEN" \
  | python3 -m json.tool
```

**Test All Categories:**
- `category=savings` - Should return savings achievements
- `category=spending` - Should return spending achievements
- `category=budgeting` - Should return budgeting achievements
- `category=goals` - Should return goal achievements
- `category=streaks` - Should return streak achievements
- `category=consistency` - Should return consistency achievements
- `category=milestones` - Should return milestone achievements

### 3. List User's Achievements
```bash
curl -X GET http://localhost:8000/api/v1/gamification/achievements/mine \
  -H "Authorization: Bearer $TOKEN" \
  | python3 -m json.tool
```

**Expected Response (New User):**
```json
{
  "achievements": [],
  "total": 0,
  "total_xp_earned": 0,
  "completion_rate": 0.0
}
```

**What to Check:**
- ✅ New users start with no achievements
- ✅ Completion rate is 0%
- ✅ Total XP from achievements is 0

### 4. Manually Test Achievement Unlocking

Achievements are unlocked automatically by the system based on user actions. To test:

**Scenario: First Transaction Achievement**
1. Create a transaction (using Phase 3 endpoints)
2. Check if "Getting Started" achievement is unlocked
3. Verify XP was awarded

**Scenario: Streak Achievement**
1. Update streak for 7 consecutive days
2. Check if "Week Warrior" achievement is unlocked

---

## Testing Challenges

### 1. List Available Challenges
```bash
curl -X GET http://localhost:8000/api/v1/gamification/challenges \
  -H "Authorization: Bearer $TOKEN" \
  | python3 -m json.tool
```

**Expected Response:**
```json
{
  "challenges": [
    {
      "id": "uuid",
      "code": "daily_log",
      "name": "Daily Logger",
      "description": "Log at least 3 transactions today",
      "challenge_type": "transaction_tracking",
      "frequency": "daily",
      "xp_reward": 25,
      "icon": "📝",
      "target_value": 3,
      "duration_days": 1,
      "criteria": {"min_transactions": 3},
      "is_active": true,
      "difficulty_level": 1,
      "start_date": null,
      "end_date": null,
      "sort_order": 1,
      "created_at": "2026-01-31T10:00:00Z",
      "updated_at": "2026-01-31T10:00:00Z"
    }
  ],
  "total": 10
}
```

**What to Check:**
- ✅ Multiple challenges are available
- ✅ Challenge types: savings, spending_limit, no_spend, budget_adherence, goal_progress, transaction_tracking
- ✅ Challenge frequencies: daily, weekly, monthly, one_time
- ✅ Each challenge has clear criteria and rewards

### 2. Filter Challenges by Type
```bash
curl -X GET "http://localhost:8000/api/v1/gamification/challenges?challenge_type=savings" \
  -H "Authorization: Bearer $TOKEN" \
  | python3 -m json.tool
```

**Test All Types:**
- `challenge_type=savings`
- `challenge_type=spending_limit`
- `challenge_type=no_spend`
- `challenge_type=budget_adherence`
- `challenge_type=goal_progress`
- `challenge_type=transaction_tracking`

### 3. Accept a Challenge

First, get a challenge ID from the list, then:

```bash
# Replace CHALLENGE_ID with actual UUID
curl -X POST http://localhost:8000/api/v1/gamification/challenges/accept \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "challenge_id": "CHALLENGE_ID"
  }' \
  | python3 -m json.tool
```

**Expected Response:**
```json
{
  "id": "user_challenge_uuid",
  "user_id": "user_uuid",
  "challenge_id": "challenge_uuid",
  "status": "active",
  "progress": 0,
  "target_progress": 3,
  "started_at": "2026-01-31T10:00:00Z",
  "completed_at": null,
  "expires_at": "2026-02-01T00:00:00Z",
  "extra_data": null,
  "challenge": {
    "id": "uuid",
    "name": "Daily Logger",
    ...
  }
}
```

**What to Check:**
- ✅ Challenge status is "active"
- ✅ Progress starts at 0
- ✅ Expiration date is set based on duration
- ✅ Full challenge details are included

### 4. Update Challenge Progress

```bash
# Replace USER_CHALLENGE_ID with actual UUID
curl -X PUT http://localhost:8000/api/v1/gamification/challenges/USER_CHALLENGE_ID/progress \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "progress": 50,
    "extra_data": {
      "note": "Halfway done!",
      "transactions_logged": 2
    }
  }' \
  | python3 -m json.tool
```

**Expected Response:**
```json
{
  "id": "user_challenge_uuid",
  "status": "active",
  "progress": 50,
  "target_progress": 100,
  "extra_data": {
    "note": "Halfway done!",
    "transactions_logged": 2
  },
  ...
}
```

**Test Progress Values:**
- `progress: 25` - Should remain active
- `progress: 75` - Should remain active
- `progress: 100` - Should complete challenge, status becomes "completed"
- `progress: 150` - Should complete challenge (capped at 100%)

### 5. List User's Challenges
```bash
curl -X GET http://localhost:8000/api/v1/gamification/challenges/mine \
  -H "Authorization: Bearer $TOKEN" \
  | python3 -m json.tool
```

**Expected Response:**
```json
{
  "challenges": [
    {
      "id": "uuid",
      "status": "active",
      "progress": 50,
      "challenge": {...}
    }
  ],
  "total": 1,
  "active_count": 1,
  "completed_count": 0
}
```

### 6. Filter User's Challenges by Status
```bash
# Active challenges
curl -X GET "http://localhost:8000/api/v1/gamification/challenges/mine?status=active" \
  -H "Authorization: Bearer $TOKEN"

# Completed challenges
curl -X GET "http://localhost:8000/api/v1/gamification/challenges/mine?status=completed" \
  -H "Authorization: Bearer $TOKEN"

# Failed challenges
curl -X GET "http://localhost:8000/api/v1/gamification/challenges/mine?status=failed" \
  -H "Authorization: Bearer $TOKEN"
```

---

## Testing Streaks

### 1. Get Current Streak
```bash
curl -X GET http://localhost:8000/api/v1/gamification/streak \
  -H "Authorization: Bearer $TOKEN" \
  | python3 -m json.tool
```

**Expected Response (New User):**
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "current_streak": 0,
  "longest_streak": 0,
  "last_activity_date": null,
  "streak_start_date": null,
  "total_activity_days": 0,
  "streak_history": null,
  "created_at": "2026-01-31T10:00:00Z",
  "updated_at": "2026-01-31T10:00:00Z"
}
```

### 2. Update Streak (Log Activity)
```bash
curl -X POST http://localhost:8000/api/v1/gamification/streak/update \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "activity_type": "login"
  }' \
  | python3 -m json.tool
```

**Expected Response (First Activity):**
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "current_streak": 1,
  "longest_streak": 1,
  "last_activity_date": "2026-01-31",
  "streak_start_date": "2026-01-31",
  "total_activity_days": 1,
  ...
}
```

**What to Check:**
- ✅ First activity sets streak to 1
- ✅ Consecutive day activities increment streak
- ✅ Missing a day resets current_streak to 1
- ✅ longest_streak is preserved
- ✅ Every 7-day milestone awards 50 XP

### 3. Test Streak Behavior

**Day 1 (Today):**
```bash
curl -X POST http://localhost:8000/api/v1/gamification/streak/update \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"activity_type": "login"}'
```
Expected: `current_streak: 1`, `longest_streak: 1`

**Day 1 (Second Call - Same Day):**
```bash
# Call again immediately
```
Expected: No change (already logged today)

**Simulating Day 2:**
Note: You can't actually test this without changing dates or modifying the database. Document the expected behavior:
- If user logs activity tomorrow → `current_streak: 2`
- If user skips tomorrow and logs day after → `current_streak: 1` (reset)

---

## Testing XP and Leveling

### 1. Get User Level Information
```bash
curl -X GET http://localhost:8000/api/v1/gamification/level \
  -H "Authorization: Bearer $TOKEN" \
  | python3 -m json.tool
```

**Expected Response:**
```json
{
  "user_id": "uuid",
  "level": 1,
  "current_xp": 0,
  "xp_for_next_level": 150,
  "xp_progress_percentage": 0.0,
  "total_xp_earned": 0
}
```

**Level Progression Formula:**
- Level 1→2: 100 XP (base × 1.5^0)
- Level 2→3: 150 XP (base × 1.5^1)
- Level 3→4: 225 XP (base × 1.5^2)
- Level 4→5: 337 XP (base × 1.5^3)

**What to Check:**
- ✅ New users start at level 1
- ✅ XP required increases exponentially
- ✅ Progress percentage is calculated correctly

### 2. Get XP History
```bash
curl -X GET "http://localhost:8000/api/v1/gamification/xp/history?limit=20&offset=0" \
  -H "Authorization: Bearer $TOKEN" \
  | python3 -m json.tool
```

**Expected Response:**
```json
{
  "history": [
    {
      "id": "uuid",
      "user_id": "uuid",
      "xp_amount": 50,
      "source": "streak_milestone",
      "source_id": null,
      "description": "7 day streak!",
      "created_at": "2026-01-31T10:00:00Z"
    }
  ],
  "total": 1,
  "total_xp": 50
}
```

**XP Sources to Test:**
- `achievement` - From unlocking achievements
- `challenge` - From completing challenges
- `streak_milestone` - From streak milestones (every 7 days)
- `daily_login` - Could be implemented

### 3. Test XP Accumulation

**Scenario 1: Complete a Challenge**
1. Accept a challenge
2. Update progress to 100
3. Check XP history - should show new entry
4. Check level - XP should increase

**Scenario 2: Unlock an Achievement**
1. Perform action that unlocks achievement
2. Check XP history
3. Verify XP amount matches achievement reward

**Scenario 3: Level Up**
1. Accumulate enough XP (e.g., 100 XP for level 2)
2. Check level info
3. Verify level increased
4. Check XP progress resets for new level

---

## Testing Leaderboard

### 1. Get Global Leaderboard
```bash
curl -X GET "http://localhost:8000/api/v1/gamification/leaderboard?limit=10&offset=0" \
  -H "Authorization: Bearer $TOKEN" \
  | python3 -m json.tool
```

**Expected Response:**
```json
{
  "entries": [
    {
      "rank": 1,
      "user_id": "uuid",
      "display_name": "John Doe",
      "level": 5,
      "xp": 500,
      "achievements_count": 10,
      "current_streak": 15,
      "profile_picture_url": null
    },
    {
      "rank": 2,
      "user_id": "uuid",
      "display_name": "Jane Smith",
      "level": 4,
      "xp": 350,
      "achievements_count": 8,
      "current_streak": 10,
      "profile_picture_url": null
    }
  ],
  "user_rank": 5,
  "total_users": 20,
  "leaderboard_type": "global"
}
```

**What to Check:**
- ✅ Users are ranked by XP (highest first)
- ✅ Current user's rank is shown
- ✅ Display name is first_name + last_name
- ✅ Achievement count is accurate
- ✅ Current streak is included

### 2. Test Leaderboard Pagination
```bash
# First page
curl -X GET "http://localhost:8000/api/v1/gamification/leaderboard?limit=5&offset=0" \
  -H "Authorization: Bearer $TOKEN"

# Second page
curl -X GET "http://localhost:8000/api/v1/gamification/leaderboard?limit=5&offset=5" \
  -H "Authorization: Bearer $TOKEN"

# Third page
curl -X GET "http://localhost:8000/api/v1/gamification/leaderboard?limit=5&offset=10" \
  -H "Authorization: Bearer $TOKEN"
```

**What to Check:**
- ✅ Ranks continue sequentially (1-5, 6-10, 11-15)
- ✅ No duplicate entries
- ✅ Total users count is consistent

### 3. Verify User Rank Calculation

After gaining XP:
1. Check leaderboard position
2. Gain more XP
3. Check leaderboard again
4. Verify rank improved

---

## Error Handling Tests

### 1. Invalid Authentication
```bash
curl -X GET http://localhost:8000/api/v1/gamification/dashboard \
  -H "Authorization: Bearer invalid_token"
```

**Expected:** HTTP 401 Unauthorized

### 2. Missing Authentication
```bash
curl -X GET http://localhost:8000/api/v1/gamification/dashboard
```

**Expected:** HTTP 401 or 403

### 3. Invalid Challenge ID
```bash
curl -X POST http://localhost:8000/api/v1/gamification/challenges/accept \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "challenge_id": "00000000-0000-0000-0000-000000000000"
  }'
```

**Expected:** HTTP 400 Bad Request

### 4. Challenge Already Accepted
```bash
# Accept same challenge twice
curl -X POST http://localhost:8000/api/v1/gamification/challenges/accept \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "challenge_id": "SAME_CHALLENGE_ID"
  }'
```

**Expected:** HTTP 400 with message "Challenge already accepted"

### 5. Invalid Progress Value
```bash
curl -X PUT http://localhost:8000/api/v1/gamification/challenges/USER_CHALLENGE_ID/progress \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "progress": -10
  }'
```

**Expected:** HTTP 422 Validation Error

### 6. Update Non-Existent Challenge
```bash
curl -X PUT http://localhost:8000/api/v1/gamification/challenges/00000000-0000-0000-0000-000000000000/progress \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "progress": 50
  }'
```

**Expected:** HTTP 400 or 404

### 7. Invalid Category Filter
```bash
curl -X GET "http://localhost:8000/api/v1/gamification/achievements?category=invalid_category" \
  -H "Authorization: Bearer $TOKEN"
```

**Expected:** HTTP 422 Validation Error

---

## Integration Testing Scenarios

### Scenario 1: New User Journey
**Goal:** Test complete onboarding flow

1. **Register & Authenticate**
   - Register new user
   - Verify initial gamification state (level 1, 0 XP)

2. **Check Dashboard**
   - View empty dashboard
   - Verify 0 achievements, 0 active challenges

3. **Log First Activity**
   - Update streak
   - Verify streak = 1

4. **Accept First Challenge**
   - Browse available challenges
   - Accept a daily challenge

5. **Check Progress**
   - View updated dashboard
   - Verify active challenge appears

### Scenario 2: Challenge Completion Flow
**Goal:** Complete a challenge and verify XP award

1. **Accept Challenge**
   - Choose "Daily Logger" challenge

2. **Update Progress**
   - Update to 33% progress
   - Update to 66% progress
   - Update to 100% progress

3. **Verify Completion**
   - Check challenge status = "completed"
   - Verify XP was awarded (check level endpoint)
   - Check XP history for new entry

4. **Check Leaderboard**
   - Verify rank updated (if applicable)

### Scenario 3: Achievement Unlocking
**Goal:** Unlock an achievement through actions

1. **Identify Achievement Criteria**
   - Look at "First Steps" achievement (save $100)

2. **Perform Required Action**
   - Create transactions totaling savings

3. **Verify Achievement**
   - Check achievements/mine endpoint
   - Verify achievement appears

4. **Verify XP Award**
   - Check XP history
   - Check level progress

### Scenario 4: Streak Building
**Goal:** Build and maintain a streak

1. **Day 1: Initial Activity**
   - Update streak
   - Verify streak = 1

2. **Day 1: Duplicate Activity**
   - Update streak again
   - Verify streak still = 1 (no change)

3. **Simulate Day 2** (requires manual intervention or waiting)
   - Update streak
   - Verify streak = 2

4. **Week Milestone**
   - Reach 7-day streak
   - Verify XP bonus (50 XP)
   - Check for "Week Warrior" achievement

### Scenario 5: Multi-User Leaderboard
**Goal:** Test competitive features

1. **Create Multiple Users**
   - Register 3-5 test users

2. **Generate Different XP Amounts**
   - User A: 500 XP (complete challenges, unlock achievements)
   - User B: 300 XP
   - User C: 150 XP

3. **Check Leaderboard**
   - Verify correct ranking
   - Verify each user sees their own rank

4. **Update Rankings**
   - User C gains 400 XP
   - Verify leaderboard updates correctly

---

## Performance Testing

### Load Testing Endpoints

Test with multiple concurrent requests:

```bash
# Test dashboard performance
for i in {1..10}; do
  curl -X GET http://localhost:8000/api/v1/gamification/dashboard \
    -H "Authorization: Bearer $TOKEN" &
done
wait
```

**Expected Response Times:**
- Dashboard: < 500ms
- Achievements list: < 300ms
- Challenges list: < 300ms
- Leaderboard: < 400ms
- XP history: < 200ms

### Database Query Optimization

Check for N+1 queries:
- List achievements (should use eager loading)
- List challenges with user's status
- Leaderboard with achievement counts

---

## Troubleshooting

### Issue: No Achievements Showing
**Possible Causes:**
1. Achievements not seeded in database
2. Database migration not applied

**Solution:**
```bash
# Check migration
cd /Users/pulkithooda/smart-fin-coach/backend
venv/bin/alembic current

# Should show 008 (head)
# If not, run: venv/bin/alembic upgrade head
```

### Issue: Challenges Not Available
**Possible Causes:**
1. Challenges not seeded
2. Date filters excluding all challenges

**Solution:**
Check that challenges exist in database and are marked as `is_active=true`

### Issue: XP Not Updating
**Possible Causes:**
1. Challenge not marked as completed
2. Achievement not properly unlocked
3. Service layer error

**Solution:**
- Check server logs for errors
- Verify challenge status changed to "completed"
- Check XP history for missing entries

### Issue: Leaderboard Shows Wrong Rank
**Possible Causes:**
1. XP not properly synced
2. Multiple users with same XP

**Solution:**
- Verify user's actual XP value
- Check if rank calculation includes tie-breaking

---

## Testing Checklist

### Phase 9 Core Features
- [ ] Dashboard displays complete gamification overview
- [ ] All 25+ achievements are accessible
- [ ] Achievement filtering by category works
- [ ] Challenges can be browsed and filtered
- [ ] Users can accept challenges
- [ ] Challenge progress updates correctly
- [ ] Challenges complete when reaching 100%
- [ ] Streak tracking works for consecutive days
- [ ] Streak resets correctly when day is missed
- [ ] XP is awarded for achievements
- [ ] XP is awarded for challenge completion
- [ ] XP is awarded for streak milestones
- [ ] Level calculation is correct
- [ ] Leveling up works properly
- [ ] XP history tracks all sources
- [ ] Leaderboard ranks by XP correctly
- [ ] User's rank is displayed accurately
- [ ] Leaderboard pagination works

### Edge Cases
- [ ] Same-day streak updates don't duplicate
- [ ] Negative progress values are rejected
- [ ] Invalid UUIDs return proper errors
- [ ] Unauthorized access is blocked
- [ ] Duplicate challenge acceptance is prevented
- [ ] Secret achievements remain hidden until unlocked
- [ ] Repeatable achievements can be completed multiple times

### Performance
- [ ] Dashboard loads within 500ms
- [ ] Leaderboard loads within 400ms
- [ ] Achievement list loads within 300ms
- [ ] No N+1 query problems
- [ ] Proper indexing on frequently queried fields

---

## Next Steps

After completing Phase 9 testing:

1. **Document Bugs**: Create tickets for any issues found
2. **Seed Data**: Run seeders to populate achievements and challenges
3. **Integration**: Test with existing Phases 1-8 features
4. **User Acceptance**: Get feedback on gamification mechanics
5. **Phase 10**: Proceed to polish and security hardening

---

**Testing Guide Version**: 1.0  
**Last Updated**: January 31, 2026  
**Phase**: 9 - Gamification & Engagement  
**Total Endpoints Tested**: 12
