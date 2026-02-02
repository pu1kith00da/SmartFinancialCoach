"""
Enhanced AI Insight Generator for personalized financial advice.
Analyzes transactions, budgets, goals, and spending patterns to generate actionable insights.
"""
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from uuid import UUID
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.transaction import Transaction, TransactionType
from app.models.goal import Goal, GoalStatus
from app.models.user import User
from app.models.insight import Insight, InsightType, InsightPriority
from app.schemas.insight import InsightCreate
from app.core.llm_client import get_llm_client

# Map insight types for AI generation
INSIGHT_TYPE_MAP = {
    'spending_alert': InsightType.SPENDING_ALERT,
    'budget_alert': InsightType.BUDGET_ALERT,
    'goal_progress': InsightType.GOAL_PROGRESS,
    'goal_behind': InsightType.GOAL_BEHIND,
    'savings_opportunity': InsightType.SAVINGS_OPPORTUNITY,
    'anomaly': InsightType.ANOMALY
}

PRIORITY_MAP = {
    'low': InsightPriority.LOW,
    'normal': InsightPriority.NORMAL,
    'high': InsightPriority.HIGH,
    'urgent': InsightPriority.URGENT
}

logger = logging.getLogger(__name__)


class AIInsightGenerator:
    """Enhanced AI-powered insight generator."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.llm_client = get_llm_client()

    async def generate_comprehensive_insights(self, user_id: UUID) -> List[Dict[str, Any]]:
        """
        Generate comprehensive financial insights by analyzing all user data.
        
        Returns list of insight dictionaries ready to be saved to database.
        """
        logger.info(f"Generating comprehensive insights for user {user_id}")
        
        # Check if we already have stored AI recommendations to rotate
        existing_ai_recommendations = await self._get_stored_ai_recommendations(user_id)
        
        if len(existing_ai_recommendations) >= 7:
            # We have enough recommendations - just rotate which ones are visible
            logger.info(f"Rotating existing {len(existing_ai_recommendations)} AI recommendations")
            await self._rotate_visible_recommendations(user_id, existing_ai_recommendations)
            return []  # No new insights to create, just rotated visibility
        
        # Not enough stored recommendations - generate fresh ones from AI
        logger.info(f"Generating fresh AI recommendations (only {len(existing_ai_recommendations)} stored)")
        await self._clear_ai_recommendations(user_id)
        
        # Gather all relevant data
        analysis = await self._analyze_user_finances(user_id)
        
        # Get existing recent insights to avoid duplicates (for non-AI insights)
        existing_insights = await self._get_recent_insights(user_id, hours=24)
        
        # Generate insights using AI
        insights = []
        
        # 1. Spending pattern insights
        if analysis['spending_patterns']:
            spending_insights = await self._generate_spending_insights(
                user_id, analysis['spending_patterns'], analysis['user_info']
            )
            insights.extend(spending_insights)
        
        # 2. AI-generated money-saving recommendations
        if analysis['transactions']:
            ai_recommendations = await self._generate_ai_recommendations(
                user_id, analysis['transactions'], analysis['user_info']
            )
            insights.extend(ai_recommendations)
        
        # 3. Goal progress insights
        if analysis['goal_progress']:
            goal_insights = await self._generate_goal_insights(
                user_id, analysis['goal_progress'], analysis['user_info']
            )
            insights.extend(goal_insights)
        
        # Note: Disabled generic savings and anomaly insights since AI recommendations are more comprehensive
        # 4. Savings opportunities (DISABLED - AI recommendations are better)
        # savings_insights = await self._generate_savings_insights(
        #     user_id, analysis, analysis['user_info']
        # )
        # insights.extend(savings_insights)
        
        # 5. Anomaly alerts (DISABLED - AI recommendations cover unusual spending patterns)
        # if analysis['anomalies']:
        #     anomaly_insights = await self._generate_anomaly_insights(
        #         user_id, analysis['anomalies'], analysis['user_info']
        #     )
        #     insights.extend(anomaly_insights)
        
        # Deduplicate insights
        insights = self._deduplicate_insights(insights, existing_insights)
        
        logger.info(f"Generated {len(insights)} insights for user {user_id}")
        return insights
    
    async def _get_stored_ai_recommendations(self, user_id: UUID) -> List[Insight]:
        """Get all stored AI recommendations for rotation."""
        query = select(Insight).where(
            and_(
                Insight.user_id == user_id,
                Insight.type == InsightType.SAVINGS_OPPORTUNITY
            )
        )
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def _rotate_visible_recommendations(self, user_id: UUID, all_recommendations: List[Insight]) -> None:
        """Hide currently visible recommendations and show 3 different ones."""
        import random
        
        # Find currently visible (not dismissed) recommendations
        visible = [r for r in all_recommendations if not r.is_dismissed]
        hidden = [r for r in all_recommendations if r.is_dismissed]
        
        logger.info(f"Current state: {len(visible)} visible, {len(hidden)} hidden")
        
        # If we have hidden recommendations, rotate
        if hidden:
            # Hide current visible ones
            for rec in visible:
                rec.is_dismissed = True
                rec.dismissed_at = datetime.utcnow()
            
            # Show 3 random hidden ones
            num_to_show = min(3, len(hidden))
            newly_visible = random.sample(hidden, num_to_show)
            
            for rec in newly_visible:
                rec.is_dismissed = False
                rec.dismissed_at = None
                rec.created_at = datetime.utcnow()  # Update timestamp so they appear as "new"
            
            await self.db.commit()
            logger.info(f"Rotated: hid {len(visible)}, showed {num_to_show} different recommendations")
        else:
            # All recommendations are already visible, just refresh timestamps
            for rec in visible:
                rec.created_at = datetime.utcnow()
            await self.db.commit()
            logger.info("All recommendations already visible, refreshed timestamps")
    
    async def _clear_ai_recommendations(self, user_id: UUID) -> None:
        """Clear old AI-generated savings recommendations to ensure fresh insights."""
        from sqlalchemy import delete
        
        delete_query = delete(Insight).where(
            and_(
                Insight.user_id == user_id,
                Insight.type == InsightType.SAVINGS_OPPORTUNITY
            )
        )
        await self.db.execute(delete_query)
        await self.db.commit()
        logger.info(f"Cleared old AI recommendations for user {user_id}")
    
    async def _get_recent_insights(self, user_id: UUID, hours: int = 24) -> List[Insight]:
        """Get insights created in the last N hours."""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        query = select(Insight).where(
            and_(
                Insight.user_id == user_id,
                Insight.created_at >= cutoff_time
            )
        )
        result = await self.db.execute(query)
        return result.scalars().all()
    
    def _deduplicate_insights(
        self, 
        new_insights: List[Dict[str, Any]], 
        existing_insights: List[Insight]
    ) -> List[Dict[str, Any]]:
        """Remove insights that are duplicates of recent ones."""
        # Create signature set from existing insights
        existing_signatures = set()
        for insight in existing_insights:
            # Signature: type + category (if present)
            signature = f"{insight.type}:{insight.category or 'none'}"
            existing_signatures.add(signature)
        
        # Filter new insights
        deduplicated = []
        for insight in new_insights:
            # Skip deduplication for AI recommendations since we clear and regenerate them fresh
            if insight['type'] == InsightType.SAVINGS_OPPORTUNITY.value:
                deduplicated.append(insight)
                continue
                
            signature = f"{insight['type']}:{insight.get('category', 'none')}"
            if signature not in existing_signatures:
                deduplicated.append(insight)
                existing_signatures.add(signature)  # Prevent duplicates within new batch
        
        if len(deduplicated) < len(new_insights):
            logger.info(f"Deduplicated {len(new_insights) - len(deduplicated)} duplicate insights")
        
        return deduplicated

    async def _analyze_user_finances(self, user_id: UUID) -> Dict[str, Any]:
        """Analyze user's complete financial picture."""
        
        # Get user info
        user_query = select(User).where(User.id == user_id)
        user_result = await self.db.execute(user_query)
        user = user_result.scalar_one_or_none()
        
        user_info = {
            'name': user.first_name if user else "there",
            'email': user.email if user else None
        }
        
        # Get transactions from last 180 days (6 months of demo data)
        six_months_ago = datetime.utcnow() - timedelta(days=180)
        tx_query = select(Transaction).where(
            and_(
                Transaction.user_id == user_id,
                Transaction.date >= six_months_ago,
                Transaction.is_excluded == False
            )
        ).order_by(Transaction.date.desc())
        
        tx_result = await self.db.execute(tx_query)
        transactions = tx_result.scalars().all()
        
        # Analyze spending patterns
        spending_patterns = self._analyze_spending_patterns(transactions)
        
        # Get goal progress
        goal_query = select(Goal).where(
            and_(
                Goal.user_id == user_id,
                Goal.status == GoalStatus.ACTIVE
            )
        )
        goal_result = await self.db.execute(goal_query)
        goals = goal_result.scalars().all()
        goal_progress = self._analyze_goal_progress(goals)
        
        # Detect anomalies
        anomalies = self._detect_anomalies(transactions)
        
        return {
            'user_info': user_info,
            'transactions': transactions,
            'spending_patterns': spending_patterns,
            'goal_progress': goal_progress,
            'anomalies': anomalies
        }

    def _analyze_spending_patterns(self, transactions: List[Transaction]) -> Dict[str, Any]:
        """Analyze spending patterns from transactions."""
        if not transactions:
            return {}
        
        # Calculate spending by category
        category_spending = {}
        total_spending = 0.0
        
        for tx in transactions:
            if tx.type == TransactionType.DEBIT:
                category = tx.category or "Uncategorized"
                amount = float(abs(tx.amount))
                category_spending[category] = category_spending.get(category, 0) + amount
                total_spending += amount
        
        # Find top spending categories
        sorted_categories = sorted(
            category_spending.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        # Calculate averages
        num_days = 30
        daily_avg = total_spending / num_days if num_days > 0 else 0
        
        return {
            'total_spending': total_spending,
            'daily_average': daily_avg,
            'top_categories': sorted_categories,
            'transaction_count': len([t for t in transactions if t.type == TransactionType.DEBIT]),
            'category_breakdown': category_spending
        }

    async def _generate_ai_recommendations(
        self,
        user_id: UUID,
        transactions: List[Transaction],
        user_info: Dict[str, str]
    ) -> List[Dict[str, Any]]:
        """Generate AI-powered money-saving recommendations from actual transactions."""
        insights = []
        
        if not transactions:
            return insights
        
        # Calculate financial summary
        total_income = sum(float(tx.amount) for tx in transactions if tx.type == TransactionType.CREDIT)
        total_expenses = sum(float(abs(tx.amount)) for tx in transactions if tx.type == TransactionType.DEBIT)
        savings_rate = ((total_income - total_expenses) / total_income * 100) if total_income > 0 else 0
        
        # Format transactions for AI analysis
        transaction_summary = self._format_transactions_for_ai(transactions)
        
        # Build comprehensive financial context
        financial_context = f"""Financial Summary (Last 6 Months):
- Total Income: ${total_income:.2f}
- Total Expenses: ${total_expenses:.2f}
- Savings Rate: {savings_rate:.1f}%
- Transaction Count: {len([t for t in transactions if t.type == TransactionType.DEBIT])} expenses

{transaction_summary}"""
        
        try:
            # Use AI to generate recommendations
            ai_result = await self.llm_client.generate_savings_recommendations(
                transactions=financial_context,
                user_name=user_info['name']
            )
            
            # Parse AI response to create insights
            recommendations = ai_result.get('recommendations', [])
            
            # Store ALL recommendations (don't randomly select, store all 10)
            for i, recommendation in enumerate(recommendations):
                # Mark first 3 as visible (not dismissed), rest as dismissed (hidden)
                is_dismissed = i >= 3
                
                insights.append({
                    'user_id': str(user_id),
                    'type': InsightType.SAVINGS_OPPORTUNITY.value,
                    'priority': InsightPriority.NORMAL.value,
                    'title': recommendation.get('title', f'Savings Recommendation {i+1}'),
                    'message': recommendation.get('message', ''),
                    'category': recommendation.get('category'),
                    'amount': recommendation.get('potential_savings'),
                    'is_dismissed': is_dismissed,  # Hide recommendations 4-10 initially
                    'context_data': {
                        'recommendation_type': recommendation.get('type'),
                        'actionable_steps': recommendation.get('action_items', []),
                        'pool_index': i  # Track which recommendation this is
                    }
                })
            
            logger.info(f"Generated {len(insights)} AI recommendations (3 visible, {len(insights)-3} in reserve pool) for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error generating AI recommendations: {str(e)}")
            # Fallback to basic recommendation
            insights.append({
                'user_id': str(user_id),
                'type': InsightType.SAVINGS_OPPORTUNITY.value,
                'priority': InsightPriority.NORMAL.value,
                'title': 'Review Your Spending',
                'message': f'Based on your {len(transactions)} recent transactions, consider reviewing your top spending categories to identify savings opportunities.',
                'context_data': {'fallback': True}
            })
        
        return insights
    
    def _format_transactions_for_ai(self, transactions: List[Transaction]) -> str:
        """Format transactions into a detailed summary for AI analysis."""
        # Group transactions by category and merchant
        category_data = {}
        merchant_spending = {}
        
        for tx in transactions:
            if tx.type == TransactionType.DEBIT:
                category = tx.category or 'Uncategorized'
                merchant = tx.merchant_name or tx.name or 'Unknown'
                
                # Track by category
                if category not in category_data:
                    category_data[category] = {
                        'total': 0,
                        'count': 0,
                        'merchants': {},
                        'transactions': []
                    }
                
                category_data[category]['total'] += abs(float(tx.amount))
                category_data[category]['count'] += 1
                
                # Track merchants within category
                if merchant not in category_data[category]['merchants']:
                    category_data[category]['merchants'][merchant] = {'total': 0, 'count': 0}
                category_data[category]['merchants'][merchant]['total'] += abs(float(tx.amount))
                category_data[category]['merchants'][merchant]['count'] += 1
                
                # Track overall merchant spending
                if merchant not in merchant_spending:
                    merchant_spending[merchant] = 0
                merchant_spending[merchant] += abs(float(tx.amount))
                
                # Keep top transactions
                category_data[category]['transactions'].append({
                    'merchant': merchant,
                    'amount': abs(float(tx.amount)),
                    'date': tx.date.strftime('%Y-%m-%d')
                })
        
        # Format as detailed text
        summary_parts = ["Spending Breakdown by Category:\n"]
        
        for category, data in sorted(category_data.items(), key=lambda x: x[1]['total'], reverse=True)[:6]:
            avg_transaction = data['total'] / data['count'] if data['count'] > 0 else 0
            summary_parts.append(
                f"{category}: ${data['total']:.2f} ({data['count']} transactions, avg ${avg_transaction:.2f})"
            )
            
            # Show top 2 merchants in this category
            top_merchants = sorted(data['merchants'].items(), key=lambda x: x[1]['total'], reverse=True)[:2]
            for merchant, merchant_data in top_merchants:
                summary_parts.append(
                    f"  → {merchant}: ${merchant_data['total']:.2f} ({merchant_data['count']}x)"
                )
        
        # Add top overall merchants
        summary_parts.append("\nTop Merchants Overall:")
        top_merchants = sorted(merchant_spending.items(), key=lambda x: x[1], reverse=True)[:5]
        for merchant, total in top_merchants:
            summary_parts.append(f"  • {merchant}: ${total:.2f}")
        
        return '\n'.join(summary_parts)

    def _analyze_goal_progress(self, goals: List[Goal]) -> List[Dict[str, Any]]:
        """Analyze progress on financial goals."""
        goal_data = []
        
        for goal in goals:
            if goal.target_amount and goal.target_amount > 0:
                progress_pct = (goal.current_amount / goal.target_amount) * 100
                
                # Calculate if on track
                if goal.target_date:
                    days_elapsed = (datetime.utcnow().date() - goal.started_at).days
                    days_total = (goal.target_date - goal.started_at).days
                    expected_progress = (days_elapsed / days_total) * 100 if days_total > 0 else 0
                    is_on_track = progress_pct >= (expected_progress * 0.9)  # 90% threshold
                else:
                    is_on_track = True
                
                goal_data.append({
                    'name': goal.name,
                    'type': goal.type.value if hasattr(goal.type, 'value') else str(goal.type),
                    'target_amount': goal.target_amount,
                    'current_amount': goal.current_amount,
                    'progress_percentage': progress_pct,
                    'is_on_track': is_on_track,
                    'target_date': goal.target_date.isoformat() if goal.target_date else None
                })
        
        return goal_data

    def _detect_anomalies(self, transactions: List[Transaction]) -> List[Dict[str, Any]]:
        """Detect unusual transactions."""
        anomalies = []
        
        if not transactions:
            return anomalies
        
        # Calculate mean and std dev for spending (convert to float)
        spending_amounts = [float(abs(tx.amount)) for tx in transactions if tx.type == TransactionType.DEBIT]
        
        if len(spending_amounts) < 3:
            return anomalies
        
        mean = sum(spending_amounts) / len(spending_amounts)
        variance = sum((x - mean) ** 2 for x in spending_amounts) / len(spending_amounts)
        std_dev = variance ** 0.5
        
        # Find transactions > 2 standard deviations above mean
        threshold = mean + (2 * std_dev)
        
        for tx in transactions:
            if tx.type == TransactionType.DEBIT and float(abs(tx.amount)) > threshold:
                anomalies.append({
                    'transaction': tx,
                    'amount': float(abs(tx.amount)),
                    'merchant': tx.merchant_name or tx.name,
                    'category': tx.category,
                    'date': tx.date.isoformat(),
                    'type': 'large_transaction'
                })
        
        return anomalies

    async def _generate_spending_insights(
        self,
        user_id: UUID,
        patterns: Dict[str, Any],
        user_info: Dict[str, str]
    ) -> List[Dict[str, Any]]:
        """Generate insights about spending patterns."""
        insights = []
        
        if not patterns or not patterns.get('top_categories'):
            return insights
        
        # High spending category insight
        top_category = patterns['top_categories'][0]
        category_name = top_category[0]
        amount = top_category[1]
        
        context = {
            'category': category_name,
            'amount': amount,
            'total_spending': patterns['total_spending'],
            'percentage': (amount / patterns['total_spending'] * 100) if patterns['total_spending'] > 0 else 0,
            'daily_average': patterns['daily_average']
        }
        
        # Use AI to generate insight
        ai_result = await self.llm_client.generate_insight(
            insight_type='spending_alert',
            context=context,
            user_name=user_info['name']
        )
        
        insights.append({
            'user_id': str(user_id),
            'type': InsightType.SPENDING_ALERT.value,
            'priority': InsightPriority.NORMAL.value,
            'title': ai_result.get('title', f'High {category_name} Spending'),
            'message': ai_result.get('message', f'You spent ${amount:.2f} on {category_name} this month.'),
            'category': category_name,
            'amount': amount,
            'context_data': context
        })
        
        return insights

    async def _generate_budget_insights(
        self,
        user_id: UUID,
        budget_status: List[Dict[str, Any]],
        user_info: Dict[str, str]
    ) -> List[Dict[str, Any]]:
        """Generate insights about budget performance."""
        insights = []
        
        for budget in budget_status:
            if budget['status'] in ['warning', 'exceeded']:
                context = {
                    'category': budget['category'],
                    'budgeted': budget['budgeted'],
                    'spent': budget['spent'],
                    'percentage': budget['percentage'],
                    'over_amount': budget['spent'] - budget['budgeted'] if budget['status'] == 'exceeded' else 0
                }
                
                ai_result = await self.llm_client.generate_insight(
                    insight_type='budget_alert',
                    context=context,
                    user_name=user_info['name']
                )
                
                priority = InsightPriority.HIGH.value if budget['status'] == 'exceeded' else InsightPriority.NORMAL.value
                
                insights.append({
                    'user_id': str(user_id),
                    'type': InsightType.BUDGET_ALERT.value,
                    'priority': priority,
                    'title': ai_result.get('title', f'{budget["category"]} Budget Alert'),
                    'message': ai_result.get('message', f'You\'ve used {budget["percentage"]:.1f}% of your {budget["category"]} budget.'),
                    'category': budget['category'],
                    'amount': budget['spent'],
                    'context_data': context
                })
        
        return insights

    async def _generate_goal_insights(
        self,
        user_id: UUID,
        goals: List[Dict[str, Any]],
        user_info: Dict[str, str]
    ) -> List[Dict[str, Any]]:
        """Generate insights about goal progress."""
        insights = []
        
        for goal in goals:
            # Generate insight for goals that are behind or doing well
            if goal['progress_percentage'] >= 25:  # Only if significant progress
                context = {
                    'goal_name': goal['name'],
                    'progress_percentage': goal['progress_percentage'],
                    'current_amount': goal['current_amount'],
                    'target_amount': goal['target_amount'],
                    'is_on_track': goal['is_on_track']
                }
                
                insight_type_str = 'goal_progress' if goal['is_on_track'] else 'goal_behind'
                insight_type_enum = InsightType.GOAL_PROGRESS if goal['is_on_track'] else InsightType.GOAL_BEHIND
                
                ai_result = await self.llm_client.generate_insight(
                    insight_type=insight_type_str,
                    context=context,
                    user_name=user_info['name']
                )
                
                priority = InsightPriority.LOW.value if goal['is_on_track'] else InsightPriority.NORMAL.value
                
                insights.append({
                    'user_id': str(user_id),
                    'type': insight_type_enum.value,
                    'priority': priority,
                    'title': ai_result.get('title', f'{goal["name"]} Progress Update'),
                    'message': ai_result.get('message', f'You\'re {goal["progress_percentage"]:.1f}% of the way to your goal!'),
                    'context_data': context
                })
        
        return insights

    async def _generate_savings_insights(
        self,
        user_id: UUID,
        analysis: Dict[str, Any],
        user_info: Dict[str, str]
    ) -> List[Dict[str, Any]]:
        """Generate insights about savings opportunities."""
        insights = []
        
        # Look for potential savings from overspending categories
        spending = analysis.get('spending_patterns', {})
        if spending and spending.get('total_spending', 0) > 0:
            total = spending['total_spending']
            
            # Suggest saving 10% of spending
            potential_savings = total * 0.10
            
            context = {
                'total_spending': total,
                'potential_savings': potential_savings,
                'suggestion': 'reducing discretionary spending'
            }
            
            ai_result = await self.llm_client.generate_insight(
                insight_type='savings_opportunity',
                context=context,
                user_name=user_info['name']
            )
            
            insights.append({
                'user_id': str(user_id),
                'type': InsightType.SAVINGS_OPPORTUNITY.value,
                'priority': InsightPriority.NORMAL.value,
                'title': ai_result.get('title', 'Savings Opportunity'),
                'message': ai_result.get('message', f'You could save ${potential_savings:.2f} this month by optimizing your spending.'),
                'amount': potential_savings,
                'context_data': context
            })
        
        return insights

    async def _generate_anomaly_insights(
        self,
        user_id: UUID,
        anomalies: List[Dict[str, Any]],
        user_info: Dict[str, str]
    ) -> List[Dict[str, Any]]:
        """Generate insights about detected anomalies."""
        insights = []
        
        # Only create insight for the most significant anomaly
        if anomalies:
            anomaly = anomalies[0]  # Get largest anomaly
            
            context = {
                'amount': anomaly['amount'],
                'merchant': anomaly['merchant'],
                'category': anomaly['category'],
                'date': anomaly['date']
            }
            
            ai_result = await self.llm_client.generate_insight(
                insight_type='anomaly',
                context=context,
                user_name=user_info['name']
            )
            
            insights.append({
                'user_id': str(user_id),
                'type': InsightType.ANOMALY.value,
                'priority': InsightPriority.HIGH.value,
                'title': ai_result.get('title', 'Unusual Transaction Detected'),
                'message': ai_result.get('message', f'We noticed an unusually large transaction of ${anomaly["amount"]:.2f} at {anomaly["merchant"]}.'),
                'amount': anomaly['amount'],
                'context_data': context
            })
        
        return insights
