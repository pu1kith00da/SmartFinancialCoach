"""
Seed script to add sample transactions for testing AI insights.
Run with: python -m scripts.seed_transactions
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from datetime import datetime, timedelta
from uuid import uuid4
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.user import User
from app.models.plaid import Account
from app.models.transaction import Transaction, TransactionType, TransactionStatus


async def seed_transactions():
    """Add sample transactions for testing."""
    async with AsyncSessionLocal() as db:
        # Get first user
        user_query = select(User).limit(1)
        result = await db.execute(user_query)
        user = result.scalar_one_or_none()
        
        if not user:
            print("No users found. Please create a user first.")
            return
        
        print(f"Found user: {user.email}")
        
        # Get or create an account for this user
        account_query = select(Account).where(Account.user_id == user.id).limit(1)
        result = await db.execute(account_query)
        account = result.scalar_one_or_none()
        
        if not account:
            # Create a mock checking account
            account = Account(
                id=uuid4(),
                user_id=user.id,
                plaid_account_id=f"mock_account_{uuid4().hex[:8]}",
                plaid_institution_id=f"mock_inst_{uuid4().hex[:8]}",
                name="Mock Checking Account",
                official_name="Mock Checking Account",
                type="depository",
                subtype="checking",
                mask="1234",
                current_balance=5000.00,
                available_balance=4800.00,
                currency_code="USD",
                is_active=True
            )
            db.add(account)
            await db.commit()
            print(f"Created mock account: {account.name}")
        else:
            print(f"Using existing account: {account.name}")
        
        # Sample transactions for last 30 days
        today = datetime.now().date()
        
        sample_transactions = [
            # High spending in dining
            {"days_ago": 1, "name": "Starbucks Coffee", "merchant": "Starbucks", "amount": -6.50, "category": "Dining"},
            {"days_ago": 2, "name": "McDonald's", "merchant": "McDonald's", "amount": -12.75, "category": "Dining"},
            {"days_ago": 3, "name": "Chipotle", "merchant": "Chipotle", "amount": -15.30, "category": "Dining"},
            {"days_ago": 4, "name": "Panera Bread", "merchant": "Panera Bread", "amount": -18.50, "category": "Dining"},
            {"days_ago": 5, "name": "Thai Restaurant", "merchant": "Thai Basil", "amount": -45.00, "category": "Dining"},
            {"days_ago": 8, "name": "Pizza Hut", "merchant": "Pizza Hut", "amount": -28.50, "category": "Dining"},
            {"days_ago": 10, "name": "Sushi Place", "merchant": "Sushi Bar", "amount": -67.00, "category": "Dining"},
            {"days_ago": 12, "name": "Starbucks", "merchant": "Starbucks", "amount": -5.75, "category": "Dining"},
            {"days_ago": 15, "name": "Burger Joint", "merchant": "Five Guys", "amount": -22.00, "category": "Dining"},
            {"days_ago": 18, "name": "Coffee Shop", "merchant": "Local Cafe", "amount": -8.50, "category": "Dining"},
            {"days_ago": 20, "name": "Italian Restaurant", "merchant": "Olive Garden", "amount": -55.00, "category": "Dining"},
            {"days_ago": 25, "name": "Dunkin Donuts", "merchant": "Dunkin", "amount": -4.25, "category": "Dining"},
            
            # Entertainment - over budget
            {"days_ago": 2, "name": "Movie Tickets", "merchant": "AMC Theaters", "amount": -35.00, "category": "Entertainment"},
            {"days_ago": 7, "name": "Concert Tickets", "merchant": "Ticketmaster", "amount": -150.00, "category": "Entertainment"},
            {"days_ago": 14, "name": "Spotify", "merchant": "Spotify", "amount": -9.99, "category": "Entertainment"},
            {"days_ago": 21, "name": "Netflix", "merchant": "Netflix", "amount": -15.99, "category": "Entertainment"},
            
            # Groceries - under budget
            {"days_ago": 3, "name": "Whole Foods", "merchant": "Whole Foods", "amount": -85.50, "category": "Groceries"},
            {"days_ago": 9, "name": "Trader Joe's", "merchant": "Trader Joe's", "amount": -62.30, "category": "Groceries"},
            {"days_ago": 16, "name": "Safeway", "merchant": "Safeway", "amount": -48.75, "category": "Groceries"},
            {"days_ago": 23, "name": "Costco", "merchant": "Costco", "amount": -124.50, "category": "Groceries"},
            
            # Shopping
            {"days_ago": 4, "name": "Amazon Purchase", "merchant": "Amazon", "amount": -45.99, "category": "Shopping"},
            {"days_ago": 11, "name": "Target", "merchant": "Target", "amount": -78.25, "category": "Shopping"},
            {"days_ago": 19, "name": "Nike Store", "merchant": "Nike", "amount": -95.00, "category": "Shopping"},
            
            # Transportation
            {"days_ago": 1, "name": "Uber Ride", "merchant": "Uber", "amount": -18.50, "category": "Transportation"},
            {"days_ago": 6, "name": "Gas Station", "merchant": "Shell", "amount": -52.00, "category": "Transportation"},
            {"days_ago": 13, "name": "Lyft Ride", "merchant": "Lyft", "amount": -22.75, "category": "Transportation"},
            {"days_ago": 20, "name": "Gas Station", "merchant": "Chevron", "amount": -48.50, "category": "Transportation"},
            
            # Utilities
            {"days_ago": 5, "name": "Electric Bill", "merchant": "PG&E", "amount": -125.00, "category": "Utilities"},
            {"days_ago": 15, "name": "Internet Service", "merchant": "Comcast", "amount": -79.99, "category": "Utilities"},
            
            # Income
            {"days_ago": 1, "name": "Paycheck Deposit", "merchant": "Employer Direct Deposit", "amount": 3500.00, "category": "Income"},
            {"days_ago": 15, "name": "Paycheck Deposit", "merchant": "Employer Direct Deposit", "amount": 3500.00, "category": "Income"},
            
            # Anomaly - large purchase
            {"days_ago": 7, "name": "Electronics Store", "merchant": "Best Buy", "amount": -1299.99, "category": "Shopping"},
        ]
        
        # Create transactions
        created_count = 0
        for tx_data in sample_transactions:
            tx_date = today - timedelta(days=tx_data["days_ago"])
            
            transaction = Transaction(
                id=uuid4(),
                user_id=user.id,
                account_id=account.id,
                plaid_transaction_id=f"mock_tx_{uuid4().hex[:12]}",
                name=tx_data["name"],
                merchant_name=tx_data["merchant"],
                amount=tx_data["amount"],
                type=TransactionType.CREDIT if tx_data["amount"] > 0 else TransactionType.DEBIT,
                category=tx_data["category"],
                date=tx_date,
                status=TransactionStatus.POSTED,
                pending=False,
                is_excluded=False,
                currency_code="USD"
            )
            db.add(transaction)
            created_count += 1
        
        await db.commit()
        print(f"✅ Successfully created {created_count} sample transactions for user {user.email}")
        print("\nSummary:")
        print(f"  - Dining: 12 transactions (~$294)")
        print(f"  - Entertainment: 4 transactions (~$211)")
        print(f"  - Groceries: 4 transactions (~$321)")
        print(f"  - Shopping: 4 transactions (~$1,519 including anomaly)")
        print(f"  - Transportation: 4 transactions (~$142)")
        print(f"  - Utilities: 2 transactions (~$205)")
        print(f"  - Income: 2 transactions ($7,000)")
        print("\nYou can now test AI insights generation!")


if __name__ == "__main__":
    asyncio.run(seed_transactions())
