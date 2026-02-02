"""
Script to add test subscriptions for testing.
"""
import asyncio
import sys
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path
from uuid import UUID, uuid4

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import text
from app.config import get_settings


async def add_test_subscriptions():
    """Add test subscriptions for a user."""
    settings = get_settings()
    
    # Create async engine
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    # Use the test@example.com user
    user_id = "4db3641b-7fb5-439f-b682-4e212bcbd37e"
    
    test_subscriptions = [
        {
            "name": "Netflix",
            "service_provider": "Netflix Inc.",
            "category": "Entertainment",
            "amount": 15.99,
            "billing_cycle": "monthly",
            "first_charge_date": date.today() - timedelta(days=15),
            "next_billing_date": date.today() + timedelta(days=15),
            "status": "active",
            "detection_confidence": "high",
            "confirmed_by_user": True,
            "website_url": "https://netflix.com",
        },
        {
            "name": "Spotify Premium",
            "service_provider": "Spotify AB",
            "category": "Music",
            "amount": 9.99,
            "billing_cycle": "monthly",
            "first_charge_date": date.today() - timedelta(days=20),
            "next_billing_date": date.today() + timedelta(days=10),
            "status": "active",
            "detection_confidence": "high",
            "confirmed_by_user": True,
            "website_url": "https://spotify.com",
        },
        {
            "name": "Apple Music",
            "service_provider": "Apple Inc.",
            "category": "Music",
            "amount": 10.99,
            "billing_cycle": "monthly",
            "first_charge_date": date.today() - timedelta(days=25),
            "next_billing_date": date.today() + timedelta(days=5),
            "status": "active",
            "detection_confidence": "high",
            "confirmed_by_user": True,
            "website_url": "https://music.apple.com",
        },
        {
            "name": "Amazon Prime",
            "service_provider": "Amazon.com",
            "category": "Shopping",
            "amount": 139.00,
            "billing_cycle": "yearly",
            "first_charge_date": date.today() - timedelta(days=180),
            "next_billing_date": date.today() + timedelta(days=185),
            "status": "active",
            "detection_confidence": "medium",
            "confirmed_by_user": True,
            "website_url": "https://amazon.com/prime",
        },
        {
            "name": "Adobe Creative Cloud",
            "service_provider": "Adobe Inc.",
            "category": "Software",
            "amount": 54.99,
            "billing_cycle": "monthly",
            "first_charge_date": date.today() - timedelta(days=5),
            "next_billing_date": date.today() + timedelta(days=25),
            "status": "active",
            "detection_confidence": "high",
            "confirmed_by_user": True,
            "website_url": "https://adobe.com",
        },
    ]
    
    async with async_session() as session:
        try:
            for sub_data in test_subscriptions:
                query = text("""
                    INSERT INTO subscriptions (
                        id, user_id, name, service_provider, category, amount,
                        billing_cycle, first_charge_date, next_billing_date,
                        status, detection_confidence, confirmed_by_user, website_url
                    ) VALUES (
                        :id, :user_id, :name, :service_provider, :category, :amount,
                        :billing_cycle, :first_charge_date, :next_billing_date,
                        :status, :detection_confidence, :confirmed_by_user, :website_url
                    )
                """)
                await session.execute(query, {
                    "id": str(uuid4()),
                    "user_id": user_id,
                    **sub_data
                })
            
            await session.commit()
            print(f"✅ Added {len(test_subscriptions)} test subscriptions for user {user_id}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            await session.rollback()
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(add_test_subscriptions())
