from typing import List, Optional, Dict, Any
from datetime import date, datetime, timedelta
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, or_, func, desc, select

from app.models.subscription import Subscription, SubscriptionStatus, BillingCycle, DetectionConfidence
from app.models.transaction import Transaction
from app.schemas.subscription import (
    SubscriptionCreate, SubscriptionUpdate, SubscriptionDetectionResponse,
    SubscriptionStats
)


class SubscriptionService:
    """Service for managing subscriptions and detecting recurring charges."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    def create_subscription(
        self,
        user_id: UUID,
        subscription_data: SubscriptionCreate
    ) -> Subscription:
        """Create a new subscription."""
        # Calculate next billing date
        next_billing_date = self._calculate_next_billing_date(
            subscription_data.first_charge_date,
            subscription_data.billing_cycle
        )
        
        subscription = Subscription(
            user_id=user_id,
            name=subscription_data.name,
            service_provider=subscription_data.service_provider,
            category=subscription_data.category,
            amount=subscription_data.amount,
            billing_cycle=subscription_data.billing_cycle.value,
            first_charge_date=subscription_data.first_charge_date,
            next_billing_date=next_billing_date,
            description=subscription_data.description,
            website_url=subscription_data.website_url,
            cancellation_url=subscription_data.cancellation_url,
            is_trial=subscription_data.is_trial,
            trial_end_date=subscription_data.trial_end_date,
            status=SubscriptionStatus.ACTIVE.value,
            detection_confidence=DetectionConfidence.MANUAL.value,
            confirmed_by_user=True
        )
        
        self.db.add(subscription)
        self.db.commit()
        self.db.refresh(subscription)
        return subscription
    
    def get_subscription(self, user_id: UUID, subscription_id: UUID) -> Subscription:
        """Get a subscription by ID."""
        subscription = self.db.query(Subscription).filter(
            and_(Subscription.id == subscription_id, Subscription.user_id == user_id)
        ).first()
        
        if not subscription:
            raise ValueError("Subscription not found")
        
        return subscription
    
    async def get_user_subscriptions(
        self,
        user_id: UUID,
        status: Optional[SubscriptionStatus] = None,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[Subscription]:
        """Get user's subscriptions with optional filtering."""
        query = select(Subscription).filter(Subscription.user_id == user_id)
        
        if status:
            query = query.filter(Subscription.status == status.value)
        
        query = query.order_by(desc(Subscription.created_at))
        
        if limit:
            query = query.limit(limit).offset(offset)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    def update_subscription(
        self,
        user_id: UUID,
        subscription_id: UUID,
        update_data: SubscriptionUpdate
    ) -> Subscription:
        """Update an existing subscription."""
        subscription = self.get_subscription(user_id, subscription_id)
        
        update_dict = update_data.dict(exclude_unset=True)
        
        # Recalculate next billing date if billing cycle changed
        if 'billing_cycle' in update_dict:
            subscription.next_billing_date = self._calculate_next_billing_date(
                subscription.last_charge_date or subscription.first_charge_date,
                BillingCycle(update_dict['billing_cycle'])
            )
        
        for field, value in update_dict.items():
            if field != 'billing_cycle':  # Already handled above
                setattr(subscription, field, value)
        
        self.db.commit()
        self.db.refresh(subscription)
        return subscription
    
    def cancel_subscription(self, user_id: UUID, subscription_id: UUID) -> Subscription:
        """Cancel a subscription."""
        subscription = self.get_subscription(user_id, subscription_id)
        subscription.status = SubscriptionStatus.CANCELLED.value
        subscription.cancelled_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(subscription)
        return subscription
    
    def detect_recurring_charges(self, user_id: UUID) -> List[SubscriptionDetectionResponse]:
        """
        Detect potential subscriptions from transaction patterns.
        
        Algorithm:
        1. Group transactions by merchant/description similarity
        2. Look for 28-31 day patterns (monthly) and other intervals
        3. Analyze amount consistency
        4. Calculate confidence scores
        """
        # Get user's transactions from the last 6 months for pattern analysis
        start_date = date.today() - timedelta(days=180)
        
        transactions = self.db.query(Transaction).filter(
            and_(
                Transaction.user_id == user_id,
                Transaction.date >= start_date,
                Transaction.amount < 0  # Only expenses
            )
        ).order_by(Transaction.date.asc()).all()
        
        if len(transactions) < 10:  # Need minimum transaction history
            return []
        
        # Group transactions by potential subscription patterns
        grouped_transactions = self._group_transactions_by_pattern(transactions)
        
        # Analyze each group for subscription patterns
        detections = []
        for group in grouped_transactions:
            detection = self._analyze_transaction_group(group)
            if detection:
                detections.append(detection)
        
        return detections
    
    def confirm_detected_subscription(
        self,
        user_id: UUID,
        detection_id: str,
        confirm: bool = True
    ) -> Optional[Subscription]:
        """Confirm or reject a detected subscription pattern."""
        if not confirm:
            # Just mark as rejected (could store in a rejection table)
            return None
        
        # This would normally retrieve the detection data from a temporary store
        # For now, we'll create a placeholder implementation
        raise NotImplementedError("Detection confirmation not yet implemented")
    
    async def get_subscription_stats(self, user_id: UUID) -> SubscriptionStats:
        """Get subscription statistics for a user."""
        subscriptions = await self.get_user_subscriptions(user_id)
        
        total_subscriptions = len(subscriptions)
        active_subscriptions = len([s for s in subscriptions if s.status == SubscriptionStatus.ACTIVE.value])
        cancelled_subscriptions = len([s for s in subscriptions if s.status == SubscriptionStatus.CANCELLED.value])
        
        # Calculate monthly cost for each subscription based on billing cycle
        def get_monthly_cost(subscription):
            amount = float(subscription.amount)
            if subscription.billing_cycle == BillingCycle.MONTHLY.value:
                return amount
            elif subscription.billing_cycle == BillingCycle.YEARLY.value:
                return amount / 12
            elif subscription.billing_cycle == BillingCycle.QUARTERLY.value:
                return amount / 3
            elif subscription.billing_cycle == BillingCycle.WEEKLY.value:
                return amount * 4.33  # Average weeks per month
            elif subscription.billing_cycle == BillingCycle.DAILY.value:
                return amount * 30
            else:
                return amount  # Default to monthly
        
        # Calculate costs
        total_monthly_cost = sum(
            get_monthly_cost(s) for s in subscriptions 
            if s.status == SubscriptionStatus.ACTIVE.value
        )
        total_annual_cost = total_monthly_cost * 12
        
        # Find most expensive
        most_expensive = max(
            subscriptions, 
            key=lambda s: get_monthly_cost(s)
        ) if subscriptions else None
        
        # Category breakdown
        category_breakdown = {}
        for subscription in subscriptions:
            if subscription.status == SubscriptionStatus.ACTIVE.value:
                category = subscription.category or "Other"
                monthly_cost = get_monthly_cost(subscription)
                category_breakdown[category] = category_breakdown.get(category, 0) + monthly_cost
        
        # Upcoming renewals (next 7 days)
        today = date.today()
        upcoming_date = today + timedelta(days=7)
        upcoming_renewals = [
            s for s in subscriptions 
            if s.status == SubscriptionStatus.ACTIVE.value 
            and s.next_billing_date 
            and today <= s.next_billing_date <= upcoming_date
        ]
        
        # Trials expiring soon
        trial_expiring_soon = [
            s for s in subscriptions
            if s.is_trial and s.trial_end_date and today <= s.trial_end_date <= upcoming_date
        ]
        
        return SubscriptionStats(
            total_subscriptions=total_subscriptions,
            active_subscriptions=active_subscriptions,
            cancelled_subscriptions=cancelled_subscriptions,
            total_monthly_cost=total_monthly_cost,
            total_annual_cost=total_annual_cost,
            most_expensive=most_expensive,
            category_breakdown=category_breakdown,
            upcoming_renewals=upcoming_renewals,
            trial_expiring_soon=trial_expiring_soon
        )
    
    def get_subscription_calendar(
        self,
        user_id: UUID,
        start_date: date,
        end_date: date
    ) -> List[dict]:
        """Get subscription calendar for a date range."""
        # Placeholder implementation
        return []
    
    def _calculate_next_billing_date(self, last_date: date, cycle: BillingCycle) -> date:
        """Calculate next billing date based on cycle."""
        if cycle == BillingCycle.MONTHLY:
            # Add one month
            if last_date.month == 12:
                return date(last_date.year + 1, 1, last_date.day)
            else:
                try:
                    return date(last_date.year, last_date.month + 1, last_date.day)
                except ValueError:
                    # Handle month-end edge cases (e.g., Jan 31 -> Feb 28/29)
                    return date(last_date.year, last_date.month + 1, 1) + timedelta(days=30)
        
        elif cycle == BillingCycle.QUARTERLY:
            # Add 3 months
            month = last_date.month + 3
            year = last_date.year
            if month > 12:
                year += month // 12
                month = month % 12
            return date(year, month, last_date.day)
        
        elif cycle == BillingCycle.ANNUALLY:
            # Add one year
            return date(last_date.year + 1, last_date.month, last_date.day)
        
        elif cycle == BillingCycle.WEEKLY:
            return last_date + timedelta(days=7)
        
        elif cycle == BillingCycle.BIWEEKLY:
            return last_date + timedelta(days=14)
        
        else:
            return last_date + timedelta(days=30)  # Default to monthly
    
    def _group_transactions_by_pattern(self, transactions: List[Transaction]) -> List[List[Transaction]]:
        """Group transactions by merchant similarity and amount patterns."""
        groups = []
        
        for transaction in transactions:
            # Find existing group for this transaction
            matched_group = None
            
            for group in groups:
                if self._transactions_match_pattern(transaction, group[0]):
                    matched_group = group
                    break
            
            if matched_group:
                matched_group.append(transaction)
            else:
                groups.append([transaction])
        
        # Filter groups that have potential subscription patterns (at least 2 transactions)
        return [group for group in groups if len(group) >= 2]
    
    def _transactions_match_pattern(self, transaction1: Transaction, transaction2: Transaction) -> bool:
        """Check if two transactions could be part of the same subscription."""
        # Check merchant similarity
        merchant_similarity = self._calculate_merchant_similarity(
            transaction1.merchant_name or transaction1.description,
            transaction2.merchant_name or transaction2.description
        )
        
        # Check amount similarity (within 20% variance)
        amount1 = abs(transaction1.amount)
        amount2 = abs(transaction2.amount)
        amount_variance = abs(amount1 - amount2) / max(amount1, amount2)
        
        return merchant_similarity > 0.8 and amount_variance < 0.2
    
    def _calculate_merchant_similarity(self, name1: str, name2: str) -> float:
        """Calculate similarity between merchant names."""
        if not name1 or not name2:
            return 0.0
        
        name1 = name1.lower().strip()
        name2 = name2.lower().strip()
        
        # Simple similarity check (could be enhanced with fuzzy matching)
        if name1 == name2:
            return 1.0
        
        # Check if one is contained in the other
        if name1 in name2 or name2 in name1:
            return 0.8
        
        # Check for common words
        words1 = set(name1.split())
        words2 = set(name2.split())
        common_words = words1.intersection(words2)
        
        if len(common_words) > 0:
            return len(common_words) / max(len(words1), len(words2))
        
        return 0.0
    
    def _analyze_transaction_group(self, transactions: List[Transaction]) -> Optional[SubscriptionDetectionResponse]:
        """Analyze a group of transactions for subscription patterns."""
        if len(transactions) < 2:
            return None
        
        # Sort by date
        transactions.sort(key=lambda t: t.date)
        
        # Calculate day differences between transactions
        day_differences = []
        for i in range(1, len(transactions)):
            diff = (transactions[i].date - transactions[i-1].date).days
            day_differences.append(diff)
        
        # Check for consistent billing cycles
        billing_cycle = self._detect_billing_cycle(day_differences)
        if not billing_cycle:
            return None
        
        # Calculate amount consistency
        amounts = [abs(t.amount) for t in transactions]
        avg_amount = sum(amounts) / len(amounts)
        amount_variance = max(amounts) - min(amounts)
        amount_variance_percent = (amount_variance / avg_amount) * 100 if avg_amount > 0 else 100
        
        # Calculate confidence score
        confidence = self._calculate_detection_confidence(
            len(transactions),
            amount_variance_percent,
            day_differences,
            billing_cycle
        )
        
        # Extract service information
        first_transaction = transactions[0]
        service_name = self._extract_service_name(first_transaction.merchant_name or first_transaction.description)
        service_provider = first_transaction.merchant_name or "Unknown"
        
        # Predict next billing date
        last_transaction = transactions[-1]
        cycle_days = self._get_cycle_days(billing_cycle)
        predicted_next_date = last_transaction.date + timedelta(days=cycle_days)
        
        return SubscriptionDetectionResponse(
            id=UUID(),  # Generate temporary ID
            name=service_name,
            service_provider=service_provider,
            amount=avg_amount,
            billing_cycle=billing_cycle,
            confidence=confidence,
            transaction_count=len(transactions),
            first_transaction_date=transactions[0].date,
            last_transaction_date=transactions[-1].date,
            predicted_next_date=predicted_next_date,
            average_days_between=sum(day_differences) / len(day_differences),
            amount_variance=amount_variance_percent,
            suggested_category=self._suggest_category(service_name, service_provider)
        )
    
    def _detect_billing_cycle(self, day_differences: List[int]) -> Optional[BillingCycle]:
        """Detect billing cycle from day differences."""
        if not day_differences:
            return None
        
        avg_days = sum(day_differences) / len(day_differences)
        
        # Monthly (28-31 days)
        if 28 <= avg_days <= 31:
            return BillingCycle.MONTHLY
        
        # Weekly (6-8 days)
        elif 6 <= avg_days <= 8:
            return BillingCycle.WEEKLY
        
        # Biweekly (13-15 days)
        elif 13 <= avg_days <= 15:
            return BillingCycle.BIWEEKLY
        
        # Quarterly (89-92 days)
        elif 89 <= avg_days <= 92:
            return BillingCycle.QUARTERLY
        
        # Annually (360-370 days)
        elif 360 <= avg_days <= 370:
            return BillingCycle.ANNUALLY
        
        return None
    
    def _calculate_detection_confidence(
        self,
        transaction_count: int,
        amount_variance: float,
        day_differences: List[int],
        billing_cycle: BillingCycle
    ) -> DetectionConfidence:
        """Calculate confidence level for subscription detection."""
        score = 0
        
        # Transaction count factor (more transactions = higher confidence)
        if transaction_count >= 6:
            score += 30
        elif transaction_count >= 4:
            score += 20
        elif transaction_count >= 3:
            score += 10
        
        # Amount consistency factor
        if amount_variance <= 5:
            score += 30
        elif amount_variance <= 15:
            score += 20
        elif amount_variance <= 25:
            score += 10
        
        # Timing consistency factor
        if day_differences:
            std_dev = self._calculate_std_dev(day_differences)
            if std_dev <= 2:
                score += 25
            elif std_dev <= 5:
                score += 15
            elif std_dev <= 10:
                score += 5
        
        # Billing cycle recognition factor
        if billing_cycle in [BillingCycle.MONTHLY, BillingCycle.ANNUALLY]:
            score += 15
        elif billing_cycle in [BillingCycle.WEEKLY, BillingCycle.QUARTERLY]:
            score += 10
        
        # Convert score to confidence level
        if score >= 80:
            return DetectionConfidence.HIGH
        elif score >= 60:
            return DetectionConfidence.MEDIUM
        else:
            return DetectionConfidence.LOW
    
    def _calculate_std_dev(self, values: List[int]) -> float:
        """Calculate standard deviation of values."""
        if len(values) <= 1:
            return 0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance ** 0.5
    
    def _extract_service_name(self, description: str) -> str:
        """Extract service name from transaction description."""
        if not description:
            return "Unknown Service"
        
        # Clean up common transaction prefixes/suffixes
        cleaned = description.replace("RECURRING", "").replace("SUBSCRIPTION", "").strip()
        
        # Take first few words as service name
        words = cleaned.split()[:3]
        return " ".join(words).title()
    
    def _suggest_category(self, service_name: str, provider: str) -> Optional[str]:
        """Suggest category based on service name and provider."""
        name_lower = (service_name + " " + provider).lower()
        
        if any(word in name_lower for word in ["netflix", "spotify", "youtube", "disney", "hulu", "prime"]):
            return "Entertainment"
        elif any(word in name_lower for word in ["gym", "fitness", "yoga", "workout"]):
            return "Health & Fitness"
        elif any(word in name_lower for word in ["adobe", "office", "dropbox", "github"]):
            return "Software"
        elif any(word in name_lower for word in ["phone", "internet", "mobile", "wireless"]):
            return "Utilities"
        
        return None
    
    def _get_cycle_days(self, cycle: BillingCycle) -> int:
        """Get approximate days for a billing cycle."""
        if cycle == BillingCycle.WEEKLY:
            return 7
        elif cycle == BillingCycle.BIWEEKLY:
            return 14
        elif cycle == BillingCycle.MONTHLY:
            return 30
        elif cycle == BillingCycle.QUARTERLY:
            return 90
        elif cycle == BillingCycle.ANNUALLY:
            return 365
        else:
            return 30
    
    def _is_billing_date(self, subscription: Subscription, check_date: date) -> bool:
        """Check if a date is a billing date for the subscription."""
        if check_date < subscription.first_charge_date:
            return False
        
        # For simplicity, check if it matches the next_billing_date
        # A more sophisticated implementation would calculate all billing dates
        return check_date == subscription.next_billing_date
    
    def update_billing_cycles(self):
        """Update next billing dates for all active subscriptions."""
        active_subscriptions = self.db.query(Subscription).filter(
            and_(
                Subscription.status == SubscriptionStatus.ACTIVE.value,
                Subscription.next_billing_date <= date.today()
            )
        ).all()
        
        for subscription in active_subscriptions:
            subscription.last_charge_date = subscription.next_billing_date
            subscription.next_billing_date = self._calculate_next_billing_date(
                subscription.next_billing_date,
                BillingCycle(subscription.billing_cycle)
            )
            subscription.total_charges += 1
        
        if active_subscriptions:
            self.db.commit()