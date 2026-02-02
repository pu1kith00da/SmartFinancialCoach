"""
Seed data for achievements and challenges
"""
from typing import List, Dict, Any


# Achievement definitions
ACHIEVEMENTS: List[Dict[str, Any]] = [
    # Savings Achievements
    {
        "code": "first_savings",
        "name": "First Steps",
        "description": "Save your first $100",
        "category": "savings",
        "tier": "bronze",
        "xp_reward": 50,
        "icon": "💰",
        "criteria": {"savings_amount": 100},
        "is_secret": False,
        "is_repeatable": False,
        "sort_order": 1
    },
    {
        "code": "savings_milestone_1k",
        "name": "Savings Champion",
        "description": "Reach $1,000 in savings",
        "category": "savings",
        "tier": "silver",
        "xp_reward": 150,
        "icon": "💎",
        "criteria": {"savings_amount": 1000},
        "is_secret": False,
        "is_repeatable": False,
        "sort_order": 2
    },
    {
        "code": "savings_milestone_10k",
        "name": "Savings Master",
        "description": "Reach $10,000 in savings",
        "category": "savings",
        "tier": "gold",
        "xp_reward": 500,
        "icon": "🏆",
        "criteria": {"savings_amount": 10000},
        "is_secret": False,
        "is_repeatable": False,
        "sort_order": 3
    },
    {
        "code": "emergency_fund",
        "name": "Safety Net",
        "description": "Build a 3-month emergency fund",
        "category": "savings",
        "tier": "gold",
        "xp_reward": 300,
        "icon": "🛡️",
        "criteria": {"emergency_fund_months": 3},
        "is_secret": False,
        "is_repeatable": False,
        "sort_order": 4
    },
    
    # Spending Achievements
    {
        "code": "first_transaction",
        "name": "Getting Started",
        "description": "Log your first transaction",
        "category": "spending",
        "tier": "bronze",
        "xp_reward": 25,
        "icon": "📝",
        "criteria": {"transaction_count": 1},
        "is_secret": False,
        "is_repeatable": False,
        "sort_order": 10
    },
    {
        "code": "transaction_tracker",
        "name": "Transaction Tracker",
        "description": "Log 100 transactions",
        "category": "spending",
        "tier": "silver",
        "xp_reward": 100,
        "icon": "📊",
        "criteria": {"transaction_count": 100},
        "is_secret": False,
        "is_repeatable": False,
        "sort_order": 11
    },
    {
        "code": "spending_reduced",
        "name": "Spending Cutter",
        "description": "Reduce spending by 20% month-over-month",
        "category": "spending",
        "tier": "gold",
        "xp_reward": 200,
        "icon": "✂️",
        "criteria": {"spending_reduction_percent": 20},
        "is_secret": False,
        "is_repeatable": True,
        "sort_order": 12
    },
    
    # Budgeting Achievements
    {
        "code": "first_budget",
        "name": "Budget Builder",
        "description": "Create your first budget",
        "category": "budgeting",
        "tier": "bronze",
        "xp_reward": 50,
        "icon": "📋",
        "criteria": {"budget_count": 1},
        "is_secret": False,
        "is_repeatable": False,
        "sort_order": 20
    },
    {
        "code": "budget_keeper",
        "name": "Budget Keeper",
        "description": "Stay within budget for 1 month",
        "category": "budgeting",
        "tier": "silver",
        "xp_reward": 150,
        "icon": "🎯",
        "criteria": {"months_on_budget": 1},
        "is_secret": False,
        "is_repeatable": True,
        "sort_order": 21
    },
    {
        "code": "budget_master",
        "name": "Budget Master",
        "description": "Stay within budget for 6 consecutive months",
        "category": "budgeting",
        "tier": "gold",
        "xp_reward": 500,
        "icon": "👑",
        "criteria": {"months_on_budget": 6},
        "is_secret": False,
        "is_repeatable": False,
        "sort_order": 22
    },
    
    # Goals Achievements
    {
        "code": "first_goal",
        "name": "Goal Setter",
        "description": "Create your first financial goal",
        "category": "goals",
        "tier": "bronze",
        "xp_reward": 50,
        "icon": "🎯",
        "criteria": {"goal_count": 1},
        "is_secret": False,
        "is_repeatable": False,
        "sort_order": 30
    },
    {
        "code": "goal_achieved",
        "name": "Goal Crusher",
        "description": "Complete your first goal",
        "category": "goals",
        "tier": "silver",
        "xp_reward": 200,
        "icon": "🏅",
        "criteria": {"goals_completed": 1},
        "is_secret": False,
        "is_repeatable": True,
        "sort_order": 31
    },
    {
        "code": "goal_overachiever",
        "name": "Overachiever",
        "description": "Complete 10 goals",
        "category": "goals",
        "tier": "gold",
        "xp_reward": 1000,
        "icon": "⭐",
        "criteria": {"goals_completed": 10},
        "is_secret": False,
        "is_repeatable": False,
        "sort_order": 32
    },
    
    # Streak Achievements
    {
        "code": "streak_7",
        "name": "Week Warrior",
        "description": "Maintain a 7-day streak",
        "category": "streaks",
        "tier": "bronze",
        "xp_reward": 75,
        "icon": "🔥",
        "criteria": {"streak_days": 7},
        "is_secret": False,
        "is_repeatable": False,
        "sort_order": 40
    },
    {
        "code": "streak_30",
        "name": "Monthly Master",
        "description": "Maintain a 30-day streak",
        "category": "streaks",
        "tier": "silver",
        "xp_reward": 250,
        "icon": "🔥🔥",
        "criteria": {"streak_days": 30},
        "is_secret": False,
        "is_repeatable": False,
        "sort_order": 41
    },
    {
        "code": "streak_100",
        "name": "Streak Legend",
        "description": "Maintain a 100-day streak",
        "category": "streaks",
        "tier": "gold",
        "xp_reward": 1000,
        "icon": "🔥🔥🔥",
        "criteria": {"streak_days": 100},
        "is_secret": False,
        "is_repeatable": False,
        "sort_order": 42
    },
    {
        "code": "streak_365",
        "name": "Year-Round Champion",
        "description": "Maintain a 365-day streak",
        "category": "streaks",
        "tier": "diamond",
        "xp_reward": 5000,
        "icon": "💥",
        "criteria": {"streak_days": 365},
        "is_secret": False,
        "is_repeatable": False,
        "sort_order": 43
    },
    
    # Consistency Achievements
    {
        "code": "early_bird",
        "name": "Early Bird",
        "description": "Log transactions before 9 AM for 7 days",
        "category": "consistency",
        "tier": "bronze",
        "xp_reward": 100,
        "icon": "🌅",
        "criteria": {"morning_logs": 7},
        "is_secret": False,
        "is_repeatable": False,
        "sort_order": 50
    },
    {
        "code": "weekend_warrior",
        "name": "Weekend Warrior",
        "description": "Stay on track during 4 consecutive weekends",
        "category": "consistency",
        "tier": "silver",
        "xp_reward": 150,
        "icon": "🏖️",
        "criteria": {"weekend_tracking": 4},
        "is_secret": False,
        "is_repeatable": False,
        "sort_order": 51
    },
    
    # Milestone Achievements
    {
        "code": "level_10",
        "name": "Rising Star",
        "description": "Reach level 10",
        "category": "milestones",
        "tier": "silver",
        "xp_reward": 500,
        "icon": "⭐",
        "criteria": {"level": 10},
        "is_secret": False,
        "is_repeatable": False,
        "sort_order": 60
    },
    {
        "code": "level_25",
        "name": "Financial Guru",
        "description": "Reach level 25",
        "category": "milestones",
        "tier": "gold",
        "xp_reward": 1500,
        "icon": "🌟",
        "criteria": {"level": 25},
        "is_secret": False,
        "is_repeatable": False,
        "sort_order": 61
    },
    {
        "code": "level_50",
        "name": "Finance Master",
        "description": "Reach level 50",
        "category": "milestones",
        "tier": "platinum",
        "xp_reward": 5000,
        "icon": "💫",
        "criteria": {"level": 50},
        "is_secret": False,
        "is_repeatable": False,
        "sort_order": 62
    },
    {
        "code": "secret_saver",
        "name": "Secret Saver",
        "description": "Discover a hidden savings opportunity",
        "category": "savings",
        "tier": "platinum",
        "xp_reward": 1000,
        "icon": "🔐",
        "criteria": {"hidden_savings": True},
        "is_secret": True,
        "is_repeatable": False,
        "sort_order": 100
    },
]


# Challenge definitions
CHALLENGES: List[Dict[str, Any]] = [
    # Daily Challenges
    {
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
        "is_active": True,
        "difficulty_level": 1,
        "sort_order": 1
    },
    {
        "code": "daily_no_spend",
        "name": "No-Spend Day",
        "description": "Don't spend any money today (except bills)",
        "challenge_type": "no_spend",
        "frequency": "daily",
        "xp_reward": 50,
        "icon": "🚫",
        "target_value": 1,
        "duration_days": 1,
        "criteria": {"max_spending": 0, "exclude_bills": True},
        "is_active": True,
        "difficulty_level": 2,
        "sort_order": 2
    },
    
    # Weekly Challenges
    {
        "code": "weekly_budget_check",
        "name": "Budget Check-In",
        "description": "Stay within all budgets this week",
        "challenge_type": "budget_adherence",
        "frequency": "weekly",
        "xp_reward": 100,
        "icon": "✅",
        "target_value": 100,
        "duration_days": 7,
        "criteria": {"budget_compliance": 100},
        "is_active": True,
        "difficulty_level": 2,
        "sort_order": 10
    },
    {
        "code": "weekly_savings",
        "name": "Save $50 This Week",
        "description": "Save at least $50 this week",
        "challenge_type": "savings",
        "frequency": "weekly",
        "xp_reward": 75,
        "icon": "💰",
        "target_value": 50,
        "duration_days": 7,
        "criteria": {"savings_target": 50},
        "is_active": True,
        "difficulty_level": 2,
        "sort_order": 11
    },
    {
        "code": "weekly_spending_limit",
        "name": "Dining Out Limit",
        "description": "Spend less than $100 on dining out this week",
        "challenge_type": "spending_limit",
        "frequency": "weekly",
        "xp_reward": 75,
        "icon": "🍽️",
        "target_value": 100,
        "duration_days": 7,
        "criteria": {"category": "Food & Dining", "max_spending": 100},
        "is_active": True,
        "difficulty_level": 2,
        "sort_order": 12
    },
    
    # Monthly Challenges
    {
        "code": "monthly_savings_200",
        "name": "Monthly Savings Goal",
        "description": "Save $200 this month",
        "challenge_type": "savings",
        "frequency": "monthly",
        "xp_reward": 250,
        "icon": "💎",
        "target_value": 200,
        "duration_days": 30,
        "criteria": {"savings_target": 200},
        "is_active": True,
        "difficulty_level": 3,
        "sort_order": 20
    },
    {
        "code": "monthly_all_budgets",
        "name": "Budget Perfectionist",
        "description": "Stay within all budgets for the entire month",
        "challenge_type": "budget_adherence",
        "frequency": "monthly",
        "xp_reward": 500,
        "icon": "🎯",
        "target_value": 100,
        "duration_days": 30,
        "criteria": {"budget_compliance": 100, "all_categories": True},
        "is_active": True,
        "difficulty_level": 4,
        "sort_order": 21
    },
    {
        "code": "monthly_goal_progress",
        "name": "Goal Progress Pusher",
        "description": "Make progress on at least one goal every week this month",
        "challenge_type": "goal_progress",
        "frequency": "monthly",
        "xp_reward": 300,
        "icon": "📈",
        "target_value": 4,
        "duration_days": 30,
        "criteria": {"min_weekly_contributions": 1},
        "is_active": True,
        "difficulty_level": 3,
        "sort_order": 22
    },
    {
        "code": "monthly_no_impulse",
        "name": "Impulse Control Master",
        "description": "No impulse purchases over $50 this month",
        "challenge_type": "spending_limit",
        "frequency": "monthly",
        "xp_reward": 400,
        "icon": "🧘",
        "target_value": 0,
        "duration_days": 30,
        "criteria": {"max_impulse_purchase": 50},
        "is_active": True,
        "difficulty_level": 4,
        "sort_order": 23
    },
    
    # Special One-Time Challenges
    {
        "code": "winter_savings_2026",
        "name": "Winter Savings Challenge 2026",
        "description": "Save an extra $500 this winter",
        "challenge_type": "savings",
        "frequency": "one_time",
        "xp_reward": 1000,
        "icon": "❄️",
        "target_value": 500,
        "duration_days": 90,
        "criteria": {"savings_target": 500},
        "is_active": True,
        "difficulty_level": 4,
        "start_date": "2026-01-01",
        "end_date": "2026-03-31",
        "sort_order": 30
    },
]


async def seed_achievements(db):
    """Seed achievements into database"""
    from app.models.gamification import Achievement
    from sqlalchemy import select
    
    for ach_data in ACHIEVEMENTS:
        # Check if already exists
        result = await db.execute(
            select(Achievement).where(Achievement.code == ach_data["code"])
        )
        existing = result.scalar_one_or_none()
        
        if not existing:
            achievement = Achievement(**ach_data)
            db.add(achievement)
    
    await db.commit()
    print(f"Seeded {len(ACHIEVEMENTS)} achievements")


async def seed_challenges(db):
    """Seed challenges into database"""
    from app.models.gamification import Challenge
    from sqlalchemy import select
    from datetime import date
    
    for chal_data in CHALLENGES:
        # Check if already exists
        result = await db.execute(
            select(Challenge).where(Challenge.code == chal_data["code"])
        )
        existing = result.scalar_one_or_none()
        
        if not existing:
            # Convert date strings to date objects
            if "start_date" in chal_data and isinstance(chal_data["start_date"], str):
                chal_data["start_date"] = date.fromisoformat(chal_data["start_date"])
            if "end_date" in chal_data and isinstance(chal_data["end_date"], str):
                chal_data["end_date"] = date.fromisoformat(chal_data["end_date"])
            
            challenge = Challenge(**chal_data)
            db.add(challenge)
    
    await db.commit()
    print(f"Seeded {len(CHALLENGES)} challenges")


async def seed_gamification_data(db):
    """Seed all gamification data"""
    await seed_achievements(db)
    await seed_challenges(db)
