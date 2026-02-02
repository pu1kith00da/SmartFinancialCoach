"""Seed budget data for testing."""
import asyncio
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.user import User
from app.models.budget import Budget
# Import all models to ensure relationships are configured
from app.models import insight, goal, subscription, bill


async def seed_budgets():
    """Seed budget data for the test user."""
    async with AsyncSessionLocal() as session:
        # Get test user
        result = await session.execute(
            select(User).where(User.email == "test@example.com")
        )
        user = result.scalar_one_or_none()
        
        if not user:
            print("❌ Test user not found. Please run seed_users.py first.")
            return
        
        # Sample budget categories with reasonable amounts
        budget_data = [
            {"category": "Groceries", "amount": 600.00},
            {"category": "Food & Dining", "amount": 300.00},
            {"category": "Transportation", "amount": 400.00},
            {"category": "Bills", "amount": 1200.00},
            {"category": "Shopping", "amount": 200.00},
            {"category": "Other", "amount": 150.00},
            {"category": "Savings", "amount": 500.00},
        ]
        
        # Check existing budgets
        existing_result = await session.execute(
            select(Budget).where(Budget.user_id == user.id)
        )
        existing_budgets = list(existing_result.scalars().all())
        
        if existing_budgets:
            print(f"⚠️  Found {len(existing_budgets)} existing budgets for {user.email}")
            # Deactivate old budgets
            for budget in existing_budgets:
                budget.is_active = False
        
        # Create new budgets
        budgets_created = 0
        for data in budget_data:
            budget = Budget(
                user_id=user.id,
                category=data["category"],
                amount=data["amount"],
                period="monthly",
                is_active=True,
                notes=f"Monthly budget for {data['category']}"
            )
            session.add(budget)
            budgets_created += 1
        
        await session.commit()
        
        print(f"✅ Created {budgets_created} budgets for {user.email}")
        print(f"   Total monthly budget: ${sum(b['amount'] for b in budget_data):.2f}")
        print("\n📊 Budget breakdown:")
        for data in budget_data:
            print(f"   {data['category']}: ${data['amount']:.2f}")


if __name__ == "__main__":
    print("🌱 Seeding budget data...")
    asyncio.run(seed_budgets())
    print("\n✨ Done!")
