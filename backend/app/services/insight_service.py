"""
Service for generating and managing AI-powered financial insights.
"""
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy import select, and_, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.insight import Insight, InsightType, InsightPriority
from app.models.transaction import Transaction, TransactionType
from app.models.user import User
from app.schemas.insight import InsightCreate
from app.core.llm_client import get_llm_client

logger = logging.getLogger(__name__)


class InsightService:
    """Service for generating and managing financial insights."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.llm_client = get_llm_client()
    
    async def generate_daily_insights(self, user_id: UUID) -> List[Insight]:
        """
        Generate daily insights for a user.
        Creates 1-2 high-priority, actionable insights.
        
        Args:
            user_id: User ID to generate insights for
        
        Returns:
            List of generated insights
        """
        logger.info(f"Generating daily insights for user {user_id}")
        
        # Gather user context
        context = await self._gather_user_context(user_id)
        
        # Identify insight opportunities
        opportunities = await self._identify_opportunities(context)
        
        # Prioritize and select top 2
        selected = self._prioritize_opportunities(opportunities)[:2]
        
        # Generate insights using LLM
        insights = []
        for opp in selected:
            try:
                insight = await self._generate_insight_from_opportunity(user_id, opp, context)
                if insight:
                    insights.append(insight)
            except Exception as e:
                logger.error(f"Failed to generate insight: {e}")
        
        return insights
    
    async def _gather_user_context(self, user_id: UUID) -> Dict[str, Any]:
        """Gather relevant user data for insight generation."""
        now = datetime.utcnow()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        last_month_start = (month_start - timedelta(days=1)).replace(day=1)
        
        # Get user info
        user_result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = user_result.scalar_one_or_none()
        
        if not user:
            return {}
        
        # Current month transactions
        current_month_query = select(Transaction).where(
            and_(
                Transaction.user_id == user_id,
                Transaction.date >= month_start
            )
        )
        current_month_result = await self.db.execute(current_month_query)
        current_month_transactions = current_month_result.scalars().all()
        
        # Last month transactions
        last_month_query = select(Transaction).where(
            and_(
                Transaction.user_id == user_id,
                Transaction.date >= last_month_start,
                Transaction.date < month_start
            )
        )
        last_month_result = await self.db.execute(last_month_query)
        last_month_transactions = last_month_result.scalars().all()
        
        # Calculate spending by category
        current_spending = self._calculate_spending_by_category(current_month_transactions)
        last_spending = self._calculate_spending_by_category(last_month_transactions)
        
        # Total spending
        current_total = sum(t.amount for t in current_month_transactions if t.type == TransactionType.DEBIT)
        last_total = sum(t.amount for t in last_month_transactions if t.type == TransactionType.DEBIT)
        
        # Income
        current_income = sum(t.amount for t in current_month_transactions if t.type == TransactionType.CREDIT)
        
        return {
            "user_id": user_id,
            "user_name": user.first_name,
            "current_month_transactions": current_month_transactions,
            "last_month_transactions": last_month_transactions,
            "current_spending": current_spending,
            "last_spending": last_spending,
            "current_total_spending": current_total,
            "last_total_spending": last_total,
            "current_income": current_income,
            "days_into_month": (now - month_start).days + 1,
            "month_name": now.strftime("%B")
        }
    
    def _calculate_spending_by_category(self, transactions: List[Transaction]) -> Dict[str, float]:
        """Calculate total spending per category."""
        spending = {}
        for t in transactions:
            if t.type == TransactionType.DEBIT and t.category:
                spending[t.category] = spending.get(t.category, 0) + t.amount
        return spending
    
    async def _identify_opportunities(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify potential insight opportunities from context."""
        opportunities = []
        
        if not context:
            return opportunities
        
        # Check for high spending categories
        current = context.get("current_spending", {})
        last = context.get("last_spending", {})
        
        for category, amount in current.items():
            last_amount = last.get(category, 0)
            if last_amount > 0:
                percent_change = ((amount - last_amount) / last_amount) * 100
                if percent_change > 50:  # 50% increase
                    opportunities.append({
                        "type": "high_category_spending",
                        "insight_type": InsightType.SPENDING_ALERT,
                        "priority": InsightPriority.NORMAL if percent_change < 100 else InsightPriority.HIGH,
                        "category": category,
                        "current_amount": amount,
                        "last_amount": last_amount,
                        "percent_change": percent_change
                    })
        
        # Check for overall spending trends
        current_total = context.get("current_total_spending", 0)
        last_total = context.get("last_total_spending", 0)
        
        if last_total > 0:
            overall_change = ((current_total - last_total) / last_total) * 100
            if overall_change > 20:
                opportunities.append({
                    "type": "overall_spending_increase",
                    "insight_type": InsightType.SPENDING_ALERT,
                    "priority": InsightPriority.NORMAL,
                    "current_total": current_total,
                    "last_total": last_total,
                    "percent_change": overall_change
                })
            elif overall_change < -20:
                opportunities.append({
                    "type": "spending_reduction",
                    "insight_type": InsightType.CELEBRATION,
                    "priority": InsightPriority.NORMAL,
                    "current_total": current_total,
                    "last_total": last_total,
                    "savings": last_total - current_total
                })
        
        # Check for savings opportunities
        if current.get("Food & Dining", 0) > 300:
            opportunities.append({
                "type": "dining_savings",
                "insight_type": InsightType.SAVINGS_OPPORTUNITY,
                "priority": InsightPriority.LOW,
                "category": "Food & Dining",
                "amount": current.get("Food & Dining", 0)
            })
        
        # General financial tip if no specific opportunities
        if not opportunities:
            opportunities.append({
                "type": "general_tip",
                "insight_type": InsightType.TIP,
                "priority": InsightPriority.LOW
            })
        
        return opportunities
    
    def _prioritize_opportunities(self, opportunities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prioritize insights by importance and actionability."""
        priority_order = {
            InsightPriority.URGENT: 4,
            InsightPriority.HIGH: 3,
            InsightPriority.NORMAL: 2,
            InsightPriority.LOW: 1
        }
        
        return sorted(
            opportunities,
            key=lambda x: priority_order.get(x.get("priority", InsightPriority.LOW), 0),
            reverse=True
        )
    
    async def _generate_insight_from_opportunity(
        self,
        user_id: UUID,
        opportunity: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Optional[Insight]:
        """Generate a specific insight from an opportunity."""
        opp_type = opportunity.get("type")
        insight_type = opportunity.get("insight_type")
        priority = opportunity.get("priority", InsightPriority.NORMAL)
        
        # Build LLM context
        llm_context = {}
        if opp_type == "high_category_spending":
            llm_context = {
                "category": opportunity.get("category"),
                "current_amount": f"${opportunity.get('current_amount', 0):.2f}",
                "last_amount": f"${opportunity.get('last_amount', 0):.2f}",
                "percent_change": f"{opportunity.get('percent_change', 0):.0f}%",
                "month": context.get("month_name", "this month")
            }
        elif opp_type == "overall_spending_increase":
            llm_context = {
                "current_total": f"${opportunity.get('current_total', 0):.2f}",
                "last_total": f"${opportunity.get('last_total', 0):.2f}",
                "percent_change": f"{opportunity.get('percent_change', 0):.0f}%"
            }
        elif opp_type == "spending_reduction":
            llm_context = {
                "savings": f"${opportunity.get('savings', 0):.2f}",
                "percent_change": f"{abs(opportunity.get('percent_change', 0)):.0f}%"
            }
        elif opp_type == "dining_savings":
            llm_context = {
                "category": opportunity.get("category"),
                "amount": f"${opportunity.get('amount', 0):.2f}",
                "potential_savings": f"${opportunity.get('amount', 0) * 0.3:.2f}"
            }
        
        # Generate insight text using LLM
        result = await self.llm_client.generate_insight(
            insight_type=opp_type,
            context=llm_context,
            user_name=context.get("user_name")
        )
        
        # Create insight
        insight_data = InsightCreate(
            user_id=user_id,
            type=insight_type,
            priority=priority,
            title=result.get("title", "Financial Insight"),
            message=result.get("message", "Review your spending patterns."),
            category=opportunity.get("category"),
            amount=opportunity.get("current_amount") or opportunity.get("amount"),
            context_data=llm_context,
            expires_at=datetime.utcnow() + timedelta(days=7)  # Insights expire after 7 days
        )
        
        insight = Insight(**insight_data.model_dump())
        self.db.add(insight)
        await self.db.commit()
        await self.db.refresh(insight)
        
        logger.info(f"Generated insight: {insight.type} for user {user_id}")
        return insight
    
    async def get_insights(
        self,
        user_id: UUID,
        filters: Optional[Dict[str, Any]] = None
    ) -> tuple[List[Insight], int]:
        """
        Get insights for a user with optional filters.
        
        Returns:
            Tuple of (insights list, total count)
        """
        query = select(Insight).where(Insight.user_id == user_id)
        
        # Apply filters
        if filters:
            if filters.get("type"):
                query = query.where(Insight.type == filters["type"])
            if filters.get("priority"):
                query = query.where(Insight.priority == filters["priority"])
            if filters.get("is_read") is not None:
                query = query.where(Insight.is_read == filters["is_read"])
            if filters.get("is_dismissed") is not None:
                query = query.where(Insight.is_dismissed == filters["is_dismissed"])
            if filters.get("category"):
                query = query.where(Insight.category == filters["category"])
            if filters.get("since"):
                query = query.where(Insight.created_at >= filters["since"])
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0
        
        # Apply pagination and ordering
        limit = filters.get("limit", 20) if filters else 20
        offset = filters.get("offset", 0) if filters else 0
        
        query = query.order_by(desc(Insight.created_at)).limit(limit).offset(offset)
        
        result = await self.db.execute(query)
        insights = result.scalars().all()
        
        return list(insights), total
    
    async def get_daily_nudge(self, user_id: UUID) -> Optional[Insight]:
        """Get today's most important unread insight."""
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        query = select(Insight).where(
            and_(
                Insight.user_id == user_id,
                Insight.is_read == False,
                Insight.is_dismissed == False,
                Insight.created_at >= today
            )
        ).order_by(
            desc(Insight.priority),
            desc(Insight.created_at)
        ).limit(1)
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def mark_as_read(self, insight_id: UUID, user_id: UUID) -> Optional[Insight]:
        """Mark an insight as read."""
        query = select(Insight).where(
            and_(
                Insight.id == insight_id,
                Insight.user_id == user_id
            )
        )
        result = await self.db.execute(query)
        insight = result.scalar_one_or_none()
        
        if insight and not insight.is_read:
            insight.is_read = True
            insight.read_at = datetime.utcnow()
            await self.db.commit()
            await self.db.refresh(insight)
        
        return insight
    
    async def dismiss(self, insight_id: UUID, user_id: UUID) -> Optional[Insight]:
        """Dismiss an insight."""
        query = select(Insight).where(
            and_(
                Insight.id == insight_id,
                Insight.user_id == user_id
            )
        )
        result = await self.db.execute(query)
        insight = result.scalar_one_or_none()
        
        if insight:
            insight.is_dismissed = True
            insight.dismissed_at = datetime.utcnow()
            await self.db.commit()
            await self.db.refresh(insight)
        
        return insight
    
    async def detect_anomalies(self, user_id: UUID) -> List[Dict[str, Any]]:
        """
        Detect spending anomalies using statistical analysis.
        
        Returns list of anomaly insights with:
        - Unusually large transactions
        - Spending at unusual times
        - New merchants with significant amounts
        - Duplicate/suspicious transactions
        """
        anomalies = []
        
        # Get last 90 days of transactions
        ninety_days_ago = datetime.utcnow() - timedelta(days=90)
        query = select(Transaction).where(
            and_(
                Transaction.user_id == user_id,
                Transaction.date >= ninety_days_ago,
                Transaction.type == TransactionType.DEBIT
            )
        )
        result = await self.db.execute(query)
        transactions = result.scalars().all()
        
        if not transactions:
            return anomalies
        
        # Calculate statistical thresholds
        amounts = [t.amount for t in transactions]
        avg_amount = sum(amounts) / len(amounts)
        
        # Calculate standard deviation
        variance = sum((x - avg_amount) ** 2 for x in amounts) / len(amounts)
        std_dev = variance ** 0.5
        
        # Detect unusually large transactions (> 3 standard deviations)
        threshold = avg_amount + (3 * std_dev)
        recent_transactions = [t for t in transactions if t.date >= datetime.utcnow() - timedelta(days=7)]
        
        for transaction in recent_transactions:
            if transaction.amount > threshold and transaction.amount > 100:  # At least $100
                anomalies.append({
                    "type": "unusual_large_transaction",
                    "transaction": transaction,
                    "amount": transaction.amount,
                    "threshold": threshold,
                    "avg_amount": avg_amount,
                    "std_dev": std_dev,
                    "severity": "high" if transaction.amount > threshold * 1.5 else "medium"
                })
        
        # Detect duplicate transactions (same merchant and amount within 24 hours)
        for i, t1 in enumerate(recent_transactions):
            for t2 in recent_transactions[i+1:]:
                time_diff = abs((t1.date - t2.date).total_seconds()) / 3600
                if (time_diff < 24 and 
                    t1.merchant == t2.merchant and 
                    abs(t1.amount - t2.amount) < 0.01):
                    anomalies.append({
                        "type": "duplicate_transaction",
                        "transaction": t1,
                        "duplicate_of": t2,
                        "severity": "medium"
                    })
                    break
        
        # Detect spending at unusual hours (between 2 AM and 5 AM)
        for transaction in recent_transactions:
            hour = transaction.date.hour
            if 2 <= hour < 5 and transaction.amount > 50:
                anomalies.append({
                    "type": "unusual_time",
                    "transaction": transaction,
                    "hour": hour,
                    "severity": "low"
                })
        
        # Detect new merchants with large amounts
        merchant_history = {}
        for t in transactions[:-7]:  # All except last 7 days
            merchant_history[t.merchant] = merchant_history.get(t.merchant, 0) + 1
        
        for transaction in recent_transactions:
            if (transaction.merchant not in merchant_history and 
                transaction.amount > avg_amount * 2):
                anomalies.append({
                    "type": "new_merchant_large_amount",
                    "transaction": transaction,
                    "merchant": transaction.merchant,
                    "severity": "medium"
                })
        
        return anomalies
    
    async def create_anomaly_insights(self, user_id: UUID) -> List[Insight]:
        """Generate insights from detected anomalies."""
        anomalies = await self.detect_anomalies(user_id)
        insights = []
        
        for anomaly in anomalies[:3]:  # Limit to top 3 anomalies
            anomaly_type = anomaly.get("type")
            transaction = anomaly.get("transaction")
            severity = anomaly.get("severity", "low")
            
            # Determine priority based on severity
            priority_map = {
                "high": InsightPriority.URGENT,
                "medium": InsightPriority.HIGH,
                "low": InsightPriority.NORMAL
            }
            priority = priority_map.get(severity, InsightPriority.NORMAL)
            
            # Generate appropriate message
            if anomaly_type == "unusual_large_transaction":
                title = f"Unusual Large Transaction Detected"
                message = (
                    f"You spent ${transaction.amount:.2f} at {transaction.merchant}, "
                    f"which is significantly higher than your typical transaction of "
                    f"${anomaly.get('avg_amount', 0):.2f}. "
                    "Please verify this transaction is correct."
                )
            elif anomaly_type == "duplicate_transaction":
                title = "Possible Duplicate Transaction"
                message = (
                    f"Two similar transactions detected at {transaction.merchant} "
                    f"for ${transaction.amount:.2f}. You may want to check if this "
                    "was charged twice."
                )
            elif anomaly_type == "unusual_time":
                title = "Unusual Transaction Time"
                message = (
                    f"Transaction of ${transaction.amount:.2f} at {transaction.merchant} "
                    f"occurred at {anomaly.get('hour')}:00 AM. "
                    "If this wasn't you, please review your account security."
                )
            elif anomaly_type == "new_merchant_large_amount":
                title = "Large Transaction at New Merchant"
                message = (
                    f"First time transaction of ${transaction.amount:.2f} at "
                    f"{transaction.merchant}. Please verify this purchase."
                )
            else:
                continue
            
            # Create insight
            insight = Insight(
                user_id=user_id,
                type=InsightType.ANOMALY,
                priority=priority,
                title=title,
                message=message,
                category=transaction.category if transaction else None,
                amount=transaction.amount if transaction else None,
                context_data={
                    "anomaly_type": anomaly_type,
                    "transaction_id": str(transaction.id) if transaction else None,
                    "severity": severity
                },
                expires_at=datetime.utcnow() + timedelta(days=30)
            )
            
            self.db.add(insight)
            insights.append(insight)
        
        if insights:
            await self.db.commit()
            for insight in insights:
                await self.db.refresh(insight)
        
        return insights
    
    async def get_analytics(self, user_id: UUID) -> Dict[str, Any]:
        """
        Get analytics and statistics about user's insights.
        
        Returns engagement metrics and distribution data.
        """
        # Get all insights for user
        all_insights_query = select(Insight).where(Insight.user_id == user_id)
        all_result = await self.db.execute(all_insights_query)
        all_insights = all_result.scalars().all()
        
        total = len(all_insights)
        if total == 0:
            return {
                "total_insights": 0,
                "total_read": 0,
                "total_dismissed": 0,
                "read_rate": 0.0,
                "dismiss_rate": 0.0,
                "insights_by_type": {},
                "insights_by_priority": {},
                "recent_insights_count": 0,
                "avg_insights_per_week": 0.0
            }
        
        # Calculate metrics
        total_read = sum(1 for i in all_insights if i.is_read)
        total_dismissed = sum(1 for i in all_insights if i.is_dismissed)
        read_rate = (total_read / total) * 100
        dismiss_rate = (total_dismissed / total) * 100
        
        # Distribution by type
        insights_by_type = {}
        for insight in all_insights:
            type_name = insight.type.value if hasattr(insight.type, 'value') else str(insight.type)
            insights_by_type[type_name] = insights_by_type.get(type_name, 0) + 1
        
        # Distribution by priority
        insights_by_priority = {}
        for insight in all_insights:
            priority_name = insight.priority.value if hasattr(insight.priority, 'value') else str(insight.priority)
            insights_by_priority[priority_name] = insights_by_priority.get(priority_name, 0) + 1
        
        # Recent insights (last 7 days)
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        recent_insights_count = sum(1 for i in all_insights if i.created_at >= seven_days_ago)
        
        # Average per week
        if all_insights:
            oldest_insight = min(i.created_at for i in all_insights)
            weeks_elapsed = max(1, (datetime.utcnow() - oldest_insight).days / 7)
            avg_insights_per_week = total / weeks_elapsed
        else:
            avg_insights_per_week = 0.0
        
        return {
            "total_insights": total,
            "total_read": total_read,
            "total_dismissed": total_dismissed,
            "read_rate": round(read_rate, 2),
            "dismiss_rate": round(dismiss_rate, 2),
            "insights_by_type": insights_by_type,
            "insights_by_priority": insights_by_priority,
            "recent_insights_count": recent_insights_count,
            "avg_insights_per_week": round(avg_insights_per_week, 2)
        }
