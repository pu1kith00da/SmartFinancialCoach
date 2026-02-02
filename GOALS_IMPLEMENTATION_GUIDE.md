# Financial Goals Feature - Implementation Guide

## Summary
This document outlines the complete implementation of the robust financial goals feature including:
- Goal CRUD operations
- Monthly contribution calculation
- On-track status monitoring
- Fund reservation from cash management
- AI chatbot integration for goal insights

## Backend Implementation

### 1. Database Schema ✅
- Added `reserved_amount` column to goals table

### 2. Goal Service Enhancements Needed
Add these methods to `/backend/app/services/goal_service.py`:

```python
async def reserve_funds(self, db: AsyncSession, goal_id: UUID, user_id: UUID, amount: float) -> Optional[Goal]:
    """Reserve funds from cash management for a goal."""
    goal = await self.get_goal(db, goal_id, user_id)
    if not goal:
        return None
    
    goal.reserved_amount = Decimal(str(goal.reserved_amount)) + Decimal(str(amount))
    await db.commit()
    await db.refresh(goal)
    return goal

async def calculate_monthly_contribution_needed(self, goal: Goal) -> float:
    """Calculate monthly contribution needed to reach goal by target date."""
    if not goal.target_date or goal.target_date <= date.today():
        return 0.0
    
    remaining = float(goal.target_amount) - float(goal.current_amount) - float(goal.reserved_amount)
    if remaining <= 0:
        return 0.0
    
    months_remaining = (goal.target_date.year - date.today().year) * 12 + (goal.target_date.month - date.today().month)
    if months_remaining <= 0:
        return remaining  # Need all remaining amount immediately
    
    return remaining / months_remaining

async def check_goal_on_track(self, goal: Goal) -> dict:
    """Check if goal is on track to meet target date."""
    if not goal.target_date:
        return {"on_track": True, "message": "No deadline set"}
    
    total_saved = float(goal.current_amount) + float(goal.reserved_amount)
    progress = (total_saved / float(goal.target_amount)) * 100
    
    days_elapsed = (date.today() - goal.started_at).days
    days_total = (goal.target_date - goal.started_at).days
    
    if days_total <= 0:
        return {"on_track": False, "message": "Target date has passed"}
    
    expected_progress = (days_elapsed / days_total) * 100
    on_track = progress >= expected_progress - 10  # 10% tolerance
    
    return {
        "on_track": on_track,
        "progress": progress,
        "expected_progress": expected_progress,
        "monthly_needed": await self.calculate_monthly_contribution_needed(goal)
    }
```

### 3. MCP Tool for Chatbot Integration
Add to `/backend/app/services/mcp_server.py`:

```python
{
    "name": "get_financial_goals",
    "description": "Get user's financial goals with progress, on-track status, and recommendations",
    "inputSchema": {
        "type": "object",
        "properties": {
            "include_completed": {
                "type": "boolean",
                "description": "Whether to include completed goals",
                "default": False
            }
        }
    }
},

# In handle_tool_call method:
async def _handle_get_financial_goals(self, arguments: dict, db: AsyncSession, user_id: str) -> dict:
    """Handle get_financial_goals tool call."""
    try:
        include_completed = arguments.get("include_completed", False)
        
        # Get goals
        status_filter = None if include_completed else GoalStatus.ACTIVE
        goals, total, active, completed = await goal_service.list_goals(
            db, UUID(user_id), status=status_filter
        )
        
        result_goals = []
        for goal in goals:
            on_track_info = await goal_service.check_goal_on_track(goal)
            monthly_needed = await goal_service.calculate_monthly_contribution_needed(goal)
            
            result_goals.append({
                "name": goal.name,
                "type": goal.type,
                "target_amount": float(goal.target_amount),
                "current_amount": float(goal.current_amount),
                "reserved_amount": float(goal.reserved_amount),
                "progress_percentage": goal.progress_percentage,
                "target_date": goal.target_date.isoformat() if goal.target_date else None,
                "monthly_contribution_needed": monthly_needed,
                "on_track": on_track_info["on_track"],
                "status": goal.status
            })
        
        return {
            "goals": result_goals,
            "total_goals": total,
            "active_goals": active,
            "recommendations": self._generate_goal_recommendations(result_goals)
        }
    except Exception as e:
        return {"error": str(e), "goals": []}

def _generate_goal_recommendations(self, goals: list) -> list:
    """Generate recommendations based on goals."""
    recommendations = []
    
    off_track_goals = [g for g in goals if not g.get("on_track", True)]
    if off_track_goals:
        recommendations.append(f"You have {len(off_track_goals)} goal(s) that are off track. Consider increasing monthly contributions.")
    
    high_monthly_goals = [g for g in goals if g.get("monthly_contribution_needed", 0) > 500]
    if high_monthly_goals:
        recommendations.append(f"{len(high_monthly_goals)} goal(s) require over $500/month. You may want to adjust target dates.")
    
    return recommendations
```

## Frontend Implementation

### 1. API Client Updates
Add to `/frontend/lib/api.ts`:

```typescript
goals: {
  list: () => api.get('/goals'),
  get: (id: string) => api.get(`/goals/${id}`),
  create: (data: any) => api.post('/goals', data),
  update: (id: string, data: any) => api.put(`/goals/${id}`, data),
  delete: (id: string) => api.delete(`/goals/${id}`),
  contribute: (id: string, amount: number, notes?: string) => 
    api.post(`/goals/${id}/contributions`, { amount, notes }),
  reserve: (id: string, amount: number) => 
    api.post(`/goals/${id}/reserve`, { amount }),
}
```

### 2. Goals List Page
Create `/frontend/app/goals/page.tsx` with:
- List of all goals with progress bars
- Add Goal button
- Edit/Delete actions
- Monthly contribution display

### 3. Create Goal Page
Create `/frontend/app/goals/new/page.tsx` with form for:
- Goal name
- Target amount
- Target date
- Description (optional)
- Goal type selection

### 4. Goal Card Component
Create `/frontend/components/goals/GoalCard.tsx` showing:
- Progress bar
- Current vs target amount
- Monthly contribution needed
- Reserve funds button
- Edit/Delete buttons

## Testing Steps

1. **Create a Goal via API:**
```bash
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login -H "Content-Type: application/json" -d '{"email":"test@example.com","password":"SecurePass123!"}' | jq -r '.access_token')

curl -X POST http://localhost:8000/api/v1/goals -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{
  "name": "Emergency Fund",
  "description": "Build 6 months expenses",
  "type": "savings",
  "priority": "high",
  "target_amount": 10000,
  "target_date": "2026-12-31",
  "current_amount": 2000
}'
```

2. **Test Chatbot Integration:**
Ask: "What are my financial goals?" or "Am I on track with my goals?"

3. **Frontend Testing:**
- Navigate to /goals
- Click "Add Goal"
- Fill form and submit
- View goal progress
- Reserve funds from cash management
- Edit/Delete goal

## Status
- ✅ Database schema updated
- ✅ Model updated with reserved_amount
- 🔄 Service enhancements needed
- 🔄 MCP tool integration needed
- 🔄 Frontend pages needed
- 🔄 Testing needed
