"""
Apply database indexes for performance optimization.
This script creates indexes on commonly queried columns to improve query performance.
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.core.database import get_db_engine
from app.core.logging import get_logger

logger = get_logger(__name__)

# Database indexes from performance.py
DATABASE_INDEXES = """
-- User table indexes
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);

-- Transaction indexes
CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_transactions_account_id ON transactions(account_id);
CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(date);
CREATE INDEX IF NOT EXISTS idx_transactions_category ON transactions(category);
CREATE INDEX IF NOT EXISTS idx_transactions_user_date ON transactions(user_id, date DESC);
CREATE INDEX IF NOT EXISTS idx_transactions_user_category ON transactions(user_id, category);

-- Account indexes
CREATE INDEX IF NOT EXISTS idx_accounts_user_id ON accounts(user_id);
CREATE INDEX IF NOT EXISTS idx_accounts_institution_id ON accounts(institution_id);
CREATE INDEX IF NOT EXISTS idx_accounts_type ON accounts(type);
CREATE INDEX IF NOT EXISTS idx_accounts_user_active ON accounts(user_id, is_active);

-- Goal indexes
CREATE INDEX IF NOT EXISTS idx_goals_user_id ON goals(user_id);
CREATE INDEX IF NOT EXISTS idx_goals_target_date ON goals(target_date);
CREATE INDEX IF NOT EXISTS idx_goals_user_status ON goals(user_id, is_completed);

-- Subscription indexes
CREATE INDEX IF NOT EXISTS idx_subscriptions_user_id ON subscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_next_billing ON subscriptions(next_billing_date);
CREATE INDEX IF NOT EXISTS idx_subscriptions_user_active ON subscriptions(user_id, is_active);

-- Bill indexes
CREATE INDEX IF NOT EXISTS idx_bills_user_id ON bills(user_id);
CREATE INDEX IF NOT EXISTS idx_bills_due_date ON bills(due_date);
CREATE INDEX IF NOT EXISTS idx_bills_user_status ON bills(user_id, is_paid);

-- Insight indexes
CREATE INDEX IF NOT EXISTS idx_insights_user_id ON insights(user_id);
CREATE INDEX IF NOT EXISTS idx_insights_type ON insights(insight_type);
CREATE INDEX IF NOT EXISTS idx_insights_created ON insights(created_at);
CREATE INDEX IF NOT EXISTS idx_insights_user_type_created ON insights(user_id, insight_type, created_at DESC);

-- Institution indexes
CREATE INDEX IF NOT EXISTS idx_institutions_name ON institutions(name);

-- Gamification indexes
CREATE INDEX IF NOT EXISTS idx_user_achievements_user_id ON user_achievements(user_id);
CREATE INDEX IF NOT EXISTS idx_user_achievements_achievement_id ON user_achievements(achievement_id);
CREATE INDEX IF NOT EXISTS idx_user_achievements_earned ON user_achievements(earned_at);

CREATE INDEX IF NOT EXISTS idx_user_challenges_user_id ON user_challenges(user_id);
CREATE INDEX IF NOT EXISTS idx_user_challenges_challenge_id ON user_challenges(challenge_id);
CREATE INDEX IF NOT EXISTS idx_user_challenges_status ON user_challenges(status);
CREATE INDEX IF NOT EXISTS idx_user_challenges_deadline ON user_challenges(deadline);

CREATE INDEX IF NOT EXISTS idx_user_badges_user_id ON user_badges(user_id);
CREATE INDEX IF NOT EXISTS idx_user_badges_badge_id ON user_badges(badge_id);

CREATE INDEX IF NOT EXISTS idx_user_streaks_user_id ON user_streaks(user_id);
CREATE INDEX IF NOT EXISTS idx_user_streaks_type ON user_streaks(streak_type);
"""


async def apply_indexes():
    """Apply all database indexes."""
    engine = get_db_engine()
    
    try:
        async with engine.begin() as conn:
            logger.info("Starting database index creation...")
            
            # Split by semicolon and execute each statement
            statements = [stmt.strip() for stmt in DATABASE_INDEXES.split(';') if stmt.strip()]
            
            for i, statement in enumerate(statements, 1):
                if statement:
                    try:
                        await conn.execute(text(statement))
                        # Extract index name from statement
                        index_name = statement.split('idx_')[1].split(' ')[0] if 'idx_' in statement else f"statement_{i}"
                        logger.info(f"✓ Created index: idx_{index_name}")
                    except Exception as e:
                        logger.error(f"✗ Failed to create index {i}: {str(e)}")
            
            logger.info(f"✓ Successfully applied {len(statements)} database indexes")
            
    except Exception as e:
        logger.error(f"✗ Failed to apply indexes: {str(e)}")
        raise
    finally:
        await engine.dispose()


if __name__ == "__main__":
    print("=" * 60)
    print("Database Index Application Script")
    print("=" * 60)
    print("\nThis script will create indexes on the following tables:")
    print("  - users")
    print("  - transactions")
    print("  - accounts")
    print("  - goals")
    print("  - subscriptions")
    print("  - bills")
    print("  - insights")
    print("  - institutions")
    print("  - user_achievements")
    print("  - user_challenges")
    print("  - user_badges")
    print("  - user_streaks")
    print("\nIndexes improve query performance on commonly queried columns.")
    print("=" * 60)
    
    response = input("\nProceed with index creation? (y/n): ")
    if response.lower() == 'y':
        asyncio.run(apply_indexes())
        print("\n✓ Index creation complete!")
    else:
        print("\n✗ Index creation cancelled.")
