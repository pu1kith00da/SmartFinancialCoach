"""
Seed realistic demo transaction data for the past 6 months.
"""
import asyncio
import random
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.models.user import User
from app.models.plaid import Account, Institution
from app.models.transaction import Transaction, TransactionType, TransactionStatus
from app.models.insight import Insight
from app.models.goal import Goal
from app.models.subscription import Subscription
from app.models.bill import Bill
from app.models.analytics import NetWorthSnapshot
from app.models.gamification import Achievement, Streak


# Realistic transaction templates
INCOME_SOURCES = [
    {"name": "Paycheck - Acme Corp", "merchant": "Acme Corporation", "amount": 3500.00, "category": "Income"},
    {"name": "Freelance Payment", "merchant": "Upwork", "amount": 1200.00, "category": "Income"},
]

FIXED_EXPENSES = [
    {"name": "Rent Payment", "merchant": "Property Management Co", "amount": 1850.00, "category": "Housing", "day": 1},
    {"name": "Car Insurance", "merchant": "State Farm", "amount": 145.00, "category": "Bills & Utilities", "day": 5},
    {"name": "Internet Service", "merchant": "Comcast", "amount": 79.99, "category": "Bills & Utilities", "day": 10},
    {"name": "Cell Phone Bill", "merchant": "Verizon", "amount": 85.00, "category": "Bills & Utilities", "day": 15},
    {"name": "Electric Bill", "merchant": "PG&E", "amount": 120.00, "category": "Bills & Utilities", "day": 20, "variance": 30},
    {"name": "Gym Membership", "merchant": "24 Hour Fitness", "amount": 49.99, "category": "Healthcare", "day": 1},
    {"name": "Streaming Services", "merchant": "Netflix", "amount": 15.99, "category": "Entertainment", "day": 12},
    {"name": "Music Subscription", "merchant": "Spotify", "amount": 10.99, "category": "Entertainment", "day": 5},
]

WEEKLY_EXPENSES = [
    {"name": "Grocery Shopping", "merchant": "Safeway", "amount": 120.00, "category": "Groceries", "variance": 40},
    {"name": "Gas Station", "merchant": "Shell", "amount": 55.00, "category": "Transportation", "variance": 15},
]

RANDOM_EXPENSES = [
    {"name": "Restaurant", "merchant": "Chipotle", "amount": 15.00, "category": "Food & Dining", "variance": 10, "frequency": 0.3},
    {"name": "Coffee Shop", "merchant": "Starbucks", "amount": 6.50, "category": "Food & Dining", "variance": 3, "frequency": 0.4},
    {"name": "Fast Food", "merchant": "McDonald's", "amount": 12.00, "category": "Food & Dining", "variance": 5, "frequency": 0.2},
    {"name": "Online Shopping", "merchant": "Amazon", "amount": 45.00, "category": "Shopping", "variance": 35, "frequency": 0.15},
    {"name": "Pharmacy", "merchant": "CVS", "amount": 25.00, "category": "Healthcare", "variance": 15, "frequency": 0.1},
    {"name": "Movie Theater", "merchant": "AMC Theaters", "amount": 28.00, "category": "Entertainment", "variance": 10, "frequency": 0.05},
    {"name": "Uber Ride", "merchant": "Uber", "amount": 18.00, "category": "Transportation", "variance": 12, "frequency": 0.15},
    {"name": "Clothing Store", "merchant": "Target", "amount": 75.00, "category": "Shopping", "variance": 50, "frequency": 0.08},
    {"name": "Home Improvement", "merchant": "Home Depot", "amount": 95.00, "category": "Shopping", "variance": 70, "frequency": 0.05},
    {"name": "Bar/Pub", "merchant": "Local Tavern", "amount": 35.00, "category": "Food & Dining", "variance": 20, "frequency": 0.1},
]


async def seed_demo_transactions(user_id: str, months: int = 6):
    """
    Generate realistic demo transactions for the specified user.
    
    Args:
        user_id: UUID of the user
        months: Number of months of history to generate (default 6)
    """
    async with AsyncSessionLocal() as db:
        # Get user's first account
        result = await db.execute(
            select(Account).where(Account.user_id == user_id).limit(1)
        )
        account = result.scalar_one_or_none()
        
        if not account:
            print(f"No account found for user {user_id}")
            return
        
        print(f"Generating {months} months of transactions for account {account.name}...")
        
        transactions = []
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=months * 30)
        
        current_date = start_date
        
        while current_date <= end_date:
            # Income (twice per month - 1st and 15th)
            if current_date.day == 1 or current_date.day == 15:
                income = random.choice(INCOME_SOURCES)
                transactions.append(Transaction(
                    user_id=user_id,
                    account_id=account.id,
                    date=current_date,
                    name=income["name"],
                    merchant_name=income["merchant"],
                    amount=Decimal(str(income["amount"])),
                    currency="USD",
                    type=TransactionType.CREDIT,
                    status=TransactionStatus.POSTED,
                    category=income["category"],
                    payment_channel="other"
                ))
            
            # Fixed monthly expenses
            for expense in FIXED_EXPENSES:
                if current_date.day == expense["day"]:
                    variance = expense.get("variance", 0)
                    amount = expense["amount"]
                    if variance > 0:
                        amount += random.uniform(-variance, variance)
                    
                    transactions.append(Transaction(
                        user_id=user_id,
                        account_id=account.id,
                        date=current_date,
                        name=expense["name"],
                        merchant_name=expense["merchant"],
                        amount=Decimal(str(round(amount, 2))),
                        currency="USD",
                        type=TransactionType.DEBIT,
                        status=TransactionStatus.POSTED,
                        category=expense["category"],
                        payment_channel="other"
                    ))
            
            # Weekly expenses (every 7 days)
            if current_date.weekday() == 6:  # Sunday
                for expense in WEEKLY_EXPENSES:
                    variance = expense.get("variance", 0)
                    amount = expense["amount"] + random.uniform(-variance, variance)
                    
                    transactions.append(Transaction(
                        user_id=user_id,
                        account_id=account.id,
                        date=current_date,
                        name=expense["name"],
                        merchant_name=expense["merchant"],
                        amount=Decimal(str(round(amount, 2))),
                        currency="USD",
                        type=TransactionType.DEBIT,
                        status=TransactionStatus.POSTED,
                        category=expense["category"],
                        payment_channel="in store"
                    ))
            
            # Random daily expenses
            for expense in RANDOM_EXPENSES:
                if random.random() < expense["frequency"]:
                    variance = expense.get("variance", 0)
                    amount = expense["amount"] + random.uniform(-variance, variance)
                    
                    transactions.append(Transaction(
                        user_id=user_id,
                        account_id=account.id,
                        date=current_date,
                        name=expense["name"],
                        merchant_name=expense["merchant"],
                        amount=Decimal(str(round(amount, 2))),
                        currency="USD",
                        type=TransactionType.DEBIT,
                        status=TransactionStatus.POSTED,
                        category=expense["category"],
                        payment_channel="online" if "Online" in expense["name"] else "in store"
                    ))
            
            current_date += timedelta(days=1)
        
        # Add all transactions to database
        db.add_all(transactions)
        await db.commit()
        
        print(f"✅ Successfully created {len(transactions)} demo transactions")
        print(f"   Date range: {start_date} to {end_date}")
        
        # Show summary
        income_total = sum(t.amount for t in transactions if t.type == TransactionType.CREDIT)
        expense_total = sum(t.amount for t in transactions if t.type == TransactionType.DEBIT)
        
        print(f"   Total income: ${income_total:,.2f}")
        print(f"   Total expenses: ${expense_total:,.2f}")
        print(f"   Net: ${income_total - expense_total:,.2f}")


async def main():
    """Run the seeding script for the first user in the database."""
    async with AsyncSessionLocal() as db:
        # Use the specific user with email test@example.com
        result = await db.execute(select(User).where(User.email == "test@example.com"))
        user = result.scalar_one_or_none()
        
        if not user:
            print("User test@example.com not found in database")
            return
        
        print(f"Seeding transactions for user: {user.email}")
        await seed_demo_transactions(str(user.id), months=6)


if __name__ == "__main__":
    asyncio.run(main())
