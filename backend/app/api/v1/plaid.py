from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID
import logging

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.services.plaid_service import PlaidService
from app.schemas.plaid import (
    LinkTokenRequest,
    LinkTokenResponse,
    PublicTokenExchangeRequest,
    PublicTokenExchangeResponse,
    InstitutionResponse,
    AccountResponse,
    AccountBalance,
    AccountListResponse,
    SyncRequest,
    SyncResponse,
    RemoveInstitutionRequest
)
from app.models.user import User

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/link/token", response_model=LinkTokenResponse)
async def create_link_token(
    request: LinkTokenRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a Plaid Link token for connecting a bank account.
    
    This token is used to initialize Plaid Link in the frontend.
    """
    try:
        plaid_service = PlaidService(db)
        result = await plaid_service.create_link_token(
            user_id=current_user.id,
            redirect_uri=request.redirect_uri,
            webhook_url=request.webhook_url
        )
        
        return LinkTokenResponse(**result)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create link token: {str(e)}"
        )


@router.post("/link/exchange", response_model=PublicTokenExchangeResponse)
async def exchange_public_token(
    request: PublicTokenExchangeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Exchange a public token for an access token and link the institution.
    
    This is called after the user successfully connects their bank via Plaid Link.
    """
    try:
        plaid_service = PlaidService(db)
        institution = await plaid_service.exchange_public_token(
            user_id=current_user.id,
            public_token=request.public_token
        )
        
        # Count accounts
        accounts = await plaid_service.get_user_accounts(current_user.id)
        accounts_count = len([a for a in accounts if a.institution_id == institution.id])
        
        return PublicTokenExchangeResponse(
            institution_id=institution.id,
            accounts_added=accounts_count
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to exchange token: {str(e)}"
        )


@router.get("/institutions", response_model=List[InstitutionResponse])
async def get_institutions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all connected institutions for the current user."""
    try:
        plaid_service = PlaidService(db)
        institutions = await plaid_service.get_user_institutions(current_user.id)
        
        # Get account counts
        accounts = await plaid_service.get_user_accounts(current_user.id)
        
        result = []
        for inst in institutions:
            accounts_count = len([a for a in accounts if a.institution_id == inst.id])
            result.append(
                InstitutionResponse(
                    id=inst.id,
                    name=inst.name,
                    logo=inst.logo,
                    primary_color=inst.primary_color,
                    is_active=inst.is_active,
                    last_synced_at=inst.last_synced_at,
                    accounts_count=accounts_count,
                    error_code=inst.error_code,
                    error_message=inst.error_message,
                    created_at=inst.created_at,
                    updated_at=inst.updated_at
                )
            )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch institutions: {str(e)}"
        )


@router.get("/accounts", response_model=AccountListResponse)
async def get_accounts(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all bank accounts for the current user."""
    try:
        plaid_service = PlaidService(db)
        accounts = await plaid_service.get_user_accounts(current_user.id)
        
        account_responses = []
        for acc in accounts:
            try:
                account_responses.append(AccountResponse.from_account(acc))
            except Exception as e:
                logger.error(f"Error converting account {acc.id}: {str(e)}")
                # Skip this account and continue with others
                continue
        
        return AccountListResponse(
            accounts=account_responses,
            total=len(account_responses)
        )
        
    except Exception as e:
        logger.error(f"Error fetching accounts for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch accounts: {str(e)}"
        )


@router.post("/sync", response_model=SyncResponse)
async def sync_institution(
    request: SyncRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Sync account balances and transactions for an institution.
    
    This fetches the latest data from Plaid and updates the database.
    """
    try:
        plaid_service = PlaidService(db)
        result = await plaid_service.sync_accounts(
            institution_id=request.institution_id,
            user_id=current_user.id
        )
        
        return SyncResponse(**result)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sync institution: {str(e)}"
        )


@router.delete("/institutions/{institution_id}")
async def remove_institution(
    institution_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Remove an institution and all its associated accounts."""
    try:
        plaid_service = PlaidService(db)
        success = await plaid_service.remove_institution(
            institution_id=institution_id,
            user_id=current_user.id
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Institution not found"
            )
        
        return {"message": "Institution removed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove institution: {str(e)}"
        )


@router.post("/sandbox/load-sample-data")
async def load_sample_data(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    [SANDBOX ONLY] Load complete sample data for demo purposes.
    
    This endpoint:
    1. Syncs transactions from Plaid sandbox
    2. Generates 6 months of realistic demo transactions
    3. Creates sample budgets for all 7 categories
    4. Creates sample financial goals
    5. Creates placeholder insights
    6. Creates sample subscriptions
    7. Detects additional subscriptions from transaction patterns
    
    Only works in sandbox/development environments.
    """
    try:
        from app.config import get_settings
        from app.services.budget_service import BudgetService
        from app.services.goal_service import GoalService
        from app.services.insight_service import InsightService
        from app.services.subscription_service import SubscriptionService
        from app.models.budget import Budget
        from app.models.goal import Goal
        from app.models.insight import Insight
        from app.models.subscription import Subscription
        from app.models.plaid import Account
        from app.models.transaction import Transaction, TransactionType, TransactionStatus
        from datetime import datetime, timedelta, date
        from decimal import Decimal
        from sqlalchemy import select
        import random
        
        settings = get_settings()
        
        # Only allow in sandbox/development
        if settings.PLAID_ENV not in ['sandbox', 'development']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This endpoint is only available in sandbox/development mode"
            )
        
        # Get user_id upfront to avoid lazy loading issues
        user_id = current_user.id
        
        plaid_service = PlaidService(db)
        
        # Get all user institutions
        institutions = await plaid_service.get_user_institutions(user_id)
        
        if not institutions:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No institutions found. Please connect a bank account first."
            )
        
        # STEP 1: Sync transactions from Plaid
        total_transactions = 0
        transaction_results = []
        
        for institution in institutions:
            try:
                result = await plaid_service.sync_accounts(
                    institution_id=institution.id,
                    user_id=user_id
                )
                total_transactions += result.get('transactions_added', 0)
                transaction_results.append({
                    'institution_id': str(institution.id),
                    'institution_name': institution.name,
                    'transactions_added': result.get('transactions_added', 0),
                    'accounts_updated': result.get('accounts_updated', 0),
                    'success': True
                })
            except Exception as e:
                logger.error(f"Error syncing institution {institution.id}: {e}")
                transaction_results.append({
                    'institution_id': str(institution.id),
                    'institution_name': institution.name,
                    'success': False,
                    'error': str(e)
                })
        
        # STEP 1.5: Generate 6 months of demo transactions
        demo_transactions_count = 0
        # Get user's first account
        result = await db.execute(
            select(Account).where(Account.user_id == user_id).limit(1)
        )
        account = result.scalar_one_or_none()
        
        if account:
            try:
                logger.info(f"Generating 6 months of demo transactions for account {account.name}...")
                
                # Transaction templates
                INCOME_SOURCES = [
                    {"name": "Paycheck - Acme Corp", "merchant": "Acme Corporation", "amount": 3500.00, "category": "Income"},
                ]
                
                FIXED_EXPENSES = [
                    {"name": "Rent Payment", "merchant": "Property Management Co", "amount": 1850.00, "category": "Bills", "day": 1},
                    {"name": "Car Insurance", "merchant": "State Farm", "amount": 145.00, "category": "Bills", "day": 5},
                    {"name": "Internet Service", "merchant": "Comcast", "amount": 79.99, "category": "Bills", "day": 10},
                    {"name": "Cell Phone Bill", "merchant": "Verizon", "amount": 85.00, "category": "Bills", "day": 15},
                    {"name": "Electric Bill", "merchant": "PG&E", "amount": 120.00, "category": "Bills", "day": 20, "variance": 30},
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
                    {"name": "Uber Ride", "merchant": "Uber", "amount": 18.00, "category": "Transportation", "variance": 12, "frequency": 0.15},
                    {"name": "Clothing Store", "merchant": "Target", "amount": 75.00, "category": "Shopping", "variance": 50, "frequency": 0.08},
                ]
                
                # Generate transactions for 6 months
                end_date = datetime.now().date()
                start_date = end_date - timedelta(days=180)  # 6 months
                current_date = start_date
                demo_transactions = []
                
                while current_date <= end_date:
                    # Income (twice per month - 1st and 15th)
                    if current_date.day == 1 or current_date.day == 15:
                        income = random.choice(INCOME_SOURCES)
                        demo_transactions.append(Transaction(
                            user_id=user_id,
                            account_id=account.id,
                            date=current_date,
                            name=income["name"],
                            merchant_name=income["merchant"],
                            amount=Decimal(str(income["amount"])),
                            type=TransactionType.CREDIT,
                            status=TransactionStatus.POSTED,
                            category=income["category"],
                        ))
                    
                    # Fixed monthly expenses
                    for expense in FIXED_EXPENSES:
                        if current_date.day == expense["day"]:
                            variance = expense.get("variance", 0)
                            amount = expense["amount"]
                            if variance > 0:
                                amount += random.uniform(-variance, variance)
                            
                            demo_transactions.append(Transaction(
                                user_id=user_id,
                                account_id=account.id,
                                date=current_date,
                                name=expense["name"],
                                merchant_name=expense["merchant"],
                                amount=Decimal(str(round(amount, 2))),
                                type=TransactionType.DEBIT,
                                status=TransactionStatus.POSTED,
                                category=expense["category"],
                            ))
                    
                    # Weekly expenses (every 7 days)
                    if current_date.weekday() == 6:  # Sunday
                        for expense in WEEKLY_EXPENSES:
                            variance = expense.get("variance", 0)
                            amount = expense["amount"] + random.uniform(-variance, variance)
                            
                            demo_transactions.append(Transaction(
                                user_id=user_id,
                                account_id=account.id,
                                date=current_date,
                                name=expense["name"],
                                merchant_name=expense["merchant"],
                                amount=Decimal(str(round(amount, 2))),
                                type=TransactionType.DEBIT,
                                status=TransactionStatus.POSTED,
                                category=expense["category"],
                            ))
                    
                    # Random daily expenses
                    for expense in RANDOM_EXPENSES:
                        if random.random() < expense["frequency"]:
                            variance = expense.get("variance", 0)
                            amount = expense["amount"] + random.uniform(-variance, variance)
                            
                            demo_transactions.append(Transaction(
                                user_id=user_id,
                                account_id=account.id,
                                date=current_date,
                                name=expense["name"],
                                merchant_name=expense["merchant"],
                                amount=Decimal(str(round(amount, 2))),
                                type=TransactionType.DEBIT,
                                status=TransactionStatus.POSTED,
                                category=expense["category"],
                            ))
                    
                    current_date += timedelta(days=1)
                
                # Add demo transactions to database
                db.add_all(demo_transactions)
                await db.commit()
                demo_transactions_count = len(demo_transactions)
                logger.info(f"Created {demo_transactions_count} demo transactions")
            except Exception as e:
                await db.rollback()
                logger.error(f"Error generating demo transactions: {e}")
        
        # STEP 2: Create sample budgets (7 categories)
        budgets_created = 0
        sample_budgets = [
            {"category": "Groceries", "amount": 600.00},
            {"category": "Shopping", "amount": 200.00},
            {"category": "Food & Dining", "amount": 300.00},
            {"category": "Bills", "amount": 1200.00},
            {"category": "Transportation", "amount": 400.00},
            {"category": "Other", "amount": 150.00},
            {"category": "Savings", "amount": 500.00}
        ]
        
        for budget_data in sample_budgets:
            try:
                # Check if budget already exists for this category
                existing = await db.execute(
                    select(Budget).where(
                        Budget.user_id == user_id,
                        Budget.category == budget_data["category"]
                    )
                )
                if existing.scalar_one_or_none() is None:
                    new_budget = Budget(
                        user_id=user_id,
                        category=budget_data["category"],
                        amount=Decimal(str(budget_data["amount"])),
                        period="monthly",
                        notes=f"Sample budget for demo purposes"
                    )
                    db.add(new_budget)
                    budgets_created += 1
            except Exception as e:
                logger.warning(f"Error creating budget for {budget_data['category']}: {e}")
        
        try:
            await db.commit()
            logger.info(f"Created {budgets_created} budgets")
        except Exception as e:
            await db.rollback()
            logger.error(f"Error committing budgets: {e}")
        
        # STEP 3: Create sample goals
        goals_created = 0
        sample_goals = [
            {
                "name": "Emergency Fund",
                "description": "Build 6 months of expenses for emergencies",
                "target_amount": 15000.00,
                "current_amount": 5000.00,
                "type": "SAVINGS",
                "status": "ACTIVE",
                "priority": "HIGH",
                "target_date": (datetime.utcnow() + timedelta(days=365)).date()
            },
            {
                "name": "Vacation to Europe",
                "description": "Save for 2-week European vacation",
                "target_amount": 5000.00,
                "current_amount": 1200.00,
                "type": "SAVINGS",
                "status": "ACTIVE",
                "priority": "MEDIUM",
                "target_date": (datetime.utcnow() + timedelta(days=180)).date()
            },
            {
                "name": "Pay Off Credit Card",
                "description": "Eliminate credit card debt",
                "target_amount": 3500.00,
                "current_amount": 2800.00,
                "type": "DEBT_PAYOFF",
                "status": "ACTIVE",
                "priority": "HIGH",
                "target_date": (datetime.utcnow() + timedelta(days=120)).date()
            }
        ]
        
        for goal_data in sample_goals:
            try:
                # Check if goal already exists
                existing = await db.execute(
                    select(Goal).where(
                        Goal.user_id == user_id,
                        Goal.name == goal_data["name"]
                    )
                )
                if existing.scalar_one_or_none() is None:
                    new_goal = Goal(
                        user_id=user_id,
                        name=goal_data["name"],
                        description=goal_data["description"],
                        target_amount=Decimal(str(goal_data["target_amount"])),
                        current_amount=Decimal(str(goal_data["current_amount"])),
                        type=goal_data["type"],
                        status=goal_data["status"],
                        priority=goal_data["priority"],
                        target_date=goal_data["target_date"]
                    )
                    db.add(new_goal)
                    goals_created += 1
            except Exception as e:
                logger.warning(f"Error creating goal {goal_data['name']}: {e}")
        
        try:
            await db.commit()
            logger.info(f"Created {goals_created} goals")
        except Exception as e:
            await db.rollback()
            logger.error(f"Error committing goals: {e}")
        
        # STEP 4: Create sample insights
        insights_created = 0
        sample_insights = [
            {
                "type": "savings_opportunity",
                "priority": "high",
                "title": "High Dining Out Spending",
                "message": "You spent significantly on dining out. Consider cooking at home more often to save money. Even reducing dining out by 30% could save you around $150/month.",
                "category": "Food & Dining",
                "amount": 150.00
            },
            {
                "type": "savings_opportunity",
                "priority": "normal",
                "title": "Coffee Shop Spending Pattern",
                "message": "You visit coffee shops frequently. Brewing coffee at home could save you approximately $80 per month.",
                "category": "Food & Dining",
                "amount": 80.00
            },
            {
                "type": "savings_opportunity",
                "priority": "high",
                "title": "Multiple Streaming Subscriptions",
                "message": "You have multiple active streaming subscriptions. Consider consolidating or rotating subscriptions to save around $25/month.",
                "category": "Bills",
                "amount": 25.00
            }
        ]
        
        for insight_data in sample_insights:
            try:
                # Check if insight already exists
                existing = await db.execute(
                    select(Insight).where(
                        Insight.user_id == user_id,
                        Insight.title == insight_data["title"]
                    )
                )
                if existing.scalar_one_or_none() is None:
                    new_insight = Insight(
                        user_id=user_id,
                        type=insight_data["type"],
                        priority=insight_data["priority"],
                        title=insight_data["title"],
                        message=insight_data["message"],
                        category=insight_data["category"],
                        amount=Decimal(str(insight_data["amount"])) if insight_data.get("amount") else None,
                        is_read=False,
                        is_dismissed=False
                    )
                    db.add(new_insight)
                    insights_created += 1
            except Exception as e:
                logger.warning(f"Error creating insight: {e}")
        
        try:
            await db.commit()
            logger.info(f"Created {insights_created} insights")
        except Exception as e:
            await db.rollback()
            logger.error(f"Error committing insights: {e}")
        
        # STEP 5: Create sample subscriptions
        subscriptions_created = 0
        sample_subscriptions = [
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
        ]
        
        for sub_data in sample_subscriptions:
            try:
                # Check if subscription already exists
                existing = await db.execute(
                    select(Subscription).where(
                        Subscription.user_id == user_id,
                        Subscription.name == sub_data["name"]
                    )
                )
                if existing.scalar_one_or_none() is None:
                    new_subscription = Subscription(
                        user_id=user_id,
                        name=sub_data["name"],
                        service_provider=sub_data["service_provider"],
                        category=sub_data["category"],
                        amount=Decimal(str(sub_data["amount"])),
                        billing_cycle=sub_data["billing_cycle"],
                        first_charge_date=sub_data["first_charge_date"],
                        next_billing_date=sub_data["next_billing_date"],
                        status=sub_data["status"],
                        detection_confidence=sub_data["detection_confidence"],
                        confirmed_by_user=sub_data["confirmed_by_user"],
                        website_url=sub_data.get("website_url")
                    )
                    db.add(new_subscription)
                    subscriptions_created += 1
            except Exception as e:
                logger.warning(f"Error creating subscription {sub_data['name']}: {e}")
        
        try:
            await db.commit()
            logger.info(f"Created {subscriptions_created} sample subscriptions")
        except Exception as e:
            await db.rollback()
            logger.error(f"Error committing subscriptions: {e}")
        
        # STEP 6: Detect additional subscriptions from transactions (skipped - feature not implemented)
        subscriptions_detected = 0
        # subscription_service = SubscriptionService(db)
        # try:
        #     detected = await subscription_service.detect_subscriptions_from_transactions(current_user.id)
        #     subscriptions_detected = len(detected)
        # except Exception as e:
        #     logger.warning(f"Error detecting subscriptions: {e}")
        
        return {
            'message': f'Successfully loaded sample data with {total_transactions + demo_transactions_count} transactions, {budgets_created} budgets, {goals_created} goals, {insights_created} insights, and {subscriptions_created + subscriptions_detected} subscriptions',
            'plaid_transactions': total_transactions,
            'demo_transactions': demo_transactions_count,
            'total_transactions': total_transactions + demo_transactions_count,
            'budgets_created': budgets_created,
            'goals_created': goals_created,
            'insights_created': insights_created,
            'subscriptions_created': subscriptions_created,
            'subscriptions_detected': subscriptions_detected,
            'total_subscriptions': subscriptions_created + subscriptions_detected,
            'institutions_processed': len(transaction_results),
            'transaction_results': transaction_results
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error loading sample data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load sample data: {str(e)}"
        )
