from typing import List, Optional, Dict, Any
from datetime import date, datetime, timedelta
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, or_, func, desc, asc, select

from app.models.bill import Bill, BillPayment, BillFrequency, BillStatus, BillCategory
from app.models.transaction import Transaction
from app.schemas.bill import (
    BillCreate, BillUpdate, BillPaymentCreate, BillPaymentUpdate,
    BillStats, BillDetectionResult
)


class BillService:
    """Service for managing bills and tracking payments."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    def create_bill(self, user_id: UUID, bill_data: BillCreate) -> Bill:
        """Create a new bill."""
        # Calculate next due date
        next_due_date = self._calculate_next_due_date(
            bill_data.first_due_date,
            BillFrequency(bill_data.frequency)
        )
        
        bill = Bill(
            user_id=user_id,
            account_id=bill_data.account_id,
            name=bill_data.name,
            payee=bill_data.payee,
            category=bill_data.category.value,
            amount=bill_data.amount,
            estimated_amount=bill_data.estimated_amount,
            min_amount=bill_data.min_amount,
            max_amount=bill_data.max_amount,
            is_variable_amount=bill_data.is_variable_amount,
            frequency=bill_data.frequency.value,
            first_due_date=bill_data.first_due_date,
            next_due_date=next_due_date,
            autopay_enabled=bill_data.autopay_enabled,
            autopay_account_id=bill_data.autopay_account_id,
            reminder_days_before=bill_data.reminder_days_before,
            description=bill_data.description,
            website_url=bill_data.website_url,
            account_number=bill_data.account_number,
            notes=bill_data.notes,
            status=BillStatus.PENDING.value,
            confirmed_by_user=True
        )
        
        self.db.add(bill)
        self.db.commit()
        self.db.refresh(bill)
        return bill
    
    def get_bill(self, user_id: UUID, bill_id: UUID) -> Bill:
        """Get a bill by ID."""
        bill = self.db.query(Bill).filter(
            and_(Bill.id == bill_id, Bill.user_id == user_id)
        ).first()
        
        if not bill:
            raise ValueError("Bill not found")
        
        return bill
    
    def get_user_bills(
        self,
        user_id: UUID,
        status: Optional[BillStatus] = None,
        category: Optional[BillCategory] = None,
        is_active: Optional[bool] = None,
        due_soon: Optional[bool] = None,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[Bill]:
        """Get user's bills with optional filtering."""
        query = self.db.query(Bill).filter(Bill.user_id == user_id)
        
        if status:
            query = query.filter(Bill.status == status.value)
        
        if category:
            query = query.filter(Bill.category == category.value)
        
        if is_active is not None:
            query = query.filter(Bill.is_active == is_active)
        
        if due_soon:
            upcoming_date = date.today() + timedelta(days=7)
            query = query.filter(Bill.next_due_date <= upcoming_date)
        
        query = query.order_by(asc(Bill.next_due_date))
        
        if limit:
            query = query.limit(limit).offset(offset)
        
        return query.all()
    
    def update_bill(self, user_id: UUID, bill_id: UUID, update_data: BillUpdate) -> Bill:
        """Update an existing bill."""
        bill = self.get_bill(user_id, bill_id)
        
        update_dict = update_data.dict(exclude_unset=True)
        
        # Recalculate next due date if frequency changed
        if 'frequency' in update_dict:
            bill.next_due_date = self._calculate_next_due_date(
                bill.next_due_date,
                BillFrequency(update_dict['frequency'])
            )
        
        for field, value in update_dict.items():
            if field != 'frequency':  # Already handled above
                setattr(bill, field, value)
        
        self.db.commit()
        self.db.refresh(bill)
        return bill
    
    def delete_bill(self, user_id: UUID, bill_id: UUID) -> None:
        """Delete a bill."""
        bill = self.get_bill(user_id, bill_id)
        self.db.delete(bill)
        self.db.commit()
    
    def deactivate_bill(self, user_id: UUID, bill_id: UUID) -> Bill:
        """Deactivate a bill instead of deleting."""
        bill = self.get_bill(user_id, bill_id)
        bill.is_active = False
        bill.status = BillStatus.CANCELLED.value
        
        self.db.commit()
        self.db.refresh(bill)
        return bill
    
    def create_payment(
        self,
        user_id: UUID,
        bill_id: UUID,
        payment_data: BillPaymentCreate
    ) -> BillPayment:
        """Record a bill payment."""
        bill = self.get_bill(user_id, bill_id)
        
        # Get the due date for this payment period
        due_date = bill.next_due_date
        if payment_data.payment_date < bill.next_due_date:
            # Payment was for a previous period, calculate which one
            due_date = self._find_due_date_for_payment(bill, payment_data.payment_date)
        
        payment = BillPayment(
            bill_id=bill_id,
            user_id=user_id,
            transaction_id=payment_data.transaction_id,
            amount_paid=payment_data.amount_paid,
            payment_date=payment_data.payment_date,
            due_date=due_date,
            payment_method=payment_data.payment_method,
            confirmation_number=payment_data.confirmation_number,
            notes=payment_data.notes,
            is_late=payment_data.payment_date > due_date,
            status="completed"
        )
        
        # Update bill status and tracking
        if payment_data.payment_date >= bill.next_due_date:
            bill.last_paid_date = payment_data.payment_date
            bill.last_paid_amount = payment_data.amount_paid
            bill.status = BillStatus.PAID.value
            
            # Calculate next due date
            bill.next_due_date = self._calculate_next_due_date(
                bill.next_due_date,
                BillFrequency(bill.frequency)
            )
        
        self.db.add(payment)
        self.db.commit()
        self.db.refresh(payment)
        return payment
    
    def get_bill_payments(
        self,
        user_id: UUID,
        bill_id: Optional[UUID] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[BillPayment]:
        """Get bill payments with filtering."""
        query = self.db.query(BillPayment).filter(BillPayment.user_id == user_id)
        
        if bill_id:
            query = query.filter(BillPayment.bill_id == bill_id)
        
        if start_date:
            query = query.filter(BillPayment.payment_date >= start_date)
        
        if end_date:
            query = query.filter(BillPayment.payment_date <= end_date)
        
        query = query.order_by(desc(BillPayment.payment_date))
        
        if limit:
            query = query.limit(limit).offset(offset)
        
        return query.all()
    
    def get_payment(self, user_id: UUID, payment_id: UUID) -> BillPayment:
        """Get a payment by ID."""
        payment = self.db.query(BillPayment).filter(
            and_(BillPayment.id == payment_id, BillPayment.user_id == user_id)
        ).first()
        
        if not payment:
            raise ValueError("Payment not found")
        
        return payment
    
    def update_payment(
        self,
        user_id: UUID,
        payment_id: UUID,
        update_data: BillPaymentUpdate
    ) -> BillPayment:
        """Update a bill payment."""
        payment = self.get_payment(user_id, payment_id)
        
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(payment, field, value)
        
        # Recalculate if late based on updated payment date
        if 'payment_date' in update_dict:
            payment.is_late = payment.payment_date > payment.due_date
        
        self.db.commit()
        self.db.refresh(payment)
        return payment
    
    def delete_payment(self, user_id: UUID, payment_id: UUID) -> None:
        """Delete a bill payment."""
        payment = self.get_payment(user_id, payment_id)
        self.db.delete(payment)
        self.db.commit()
    
    def get_bill_stats(self, user_id: UUID) -> BillStats:
        """Get bill statistics for a user."""
        bills = self.get_user_bills(user_id)
        
        total_bills = len(bills)
        active_bills = len([b for b in bills if b.is_active])
        overdue_bills = len([b for b in bills if b.is_overdue])
        due_soon_bills = len([b for b in bills if b.is_due_soon])
        
        # Calculate costs
        total_monthly_amount = sum(b.monthly_amount for b in bills if b.is_active)
        total_annual_amount = total_monthly_amount * 12
        
        # Category breakdown
        category_breakdown = {}
        for bill in bills:
            if bill.is_active:
                category = bill.category
                category_breakdown[category] = category_breakdown.get(category, 0) + bill.monthly_amount
        
        # Frequency breakdown
        frequency_breakdown = {}
        for bill in bills:
            if bill.is_active:
                freq = bill.frequency
                frequency_breakdown[freq] = frequency_breakdown.get(freq, 0) + 1
        
        # Autopay percentage
        autopay_bills = len([b for b in bills if b.is_active and b.autopay_enabled])
        autopay_percentage = (autopay_bills / active_bills * 100) if active_bills > 0 else 0
        
        # Average payment delay
        payments = self.get_bill_payments(user_id, limit=100)  # Get recent payments
        late_payments = [p for p in payments if p.is_late]
        average_payment_delay = (
            sum(p.days_late for p in late_payments) / len(late_payments)
            if late_payments else 0
        )
        
        return BillStats(
            total_bills=total_bills,
            active_bills=active_bills,
            overdue_bills=overdue_bills,
            due_soon_bills=due_soon_bills,
            total_monthly_amount=total_monthly_amount,
            total_annual_amount=total_annual_amount,
            category_breakdown=category_breakdown,
            frequency_breakdown=frequency_breakdown,
            autopay_percentage=autopay_percentage,
            average_payment_delay=average_payment_delay
        )
    
    def get_bill_calendar(
        self,
        user_id: UUID,
        start_date: date,
        end_date: date
    ) -> dict:
        """Get bill calendar for a date range."""
        # Placeholder implementation
        return {"message": "Calendar functionality coming soon"}
    
    def detect_bills_from_transactions(self, user_id: UUID) -> List[BillDetectionResult]:
        """Detect potential bills from transaction patterns."""
        # Get user's transactions from the last year for pattern analysis
        start_date = date.today() - timedelta(days=365)
        
        transactions = self.db.query(Transaction).filter(
            and_(
                Transaction.user_id == user_id,
                Transaction.date >= start_date,
                Transaction.amount < 0,  # Only expenses
                Transaction.amount <= -10  # Minimum amount to consider as a bill
            )
        ).order_by(Transaction.date.asc()).all()
        
        if len(transactions) < 5:  # Need minimum transaction history
            return []
        
        # Group transactions by potential bill patterns
        grouped_transactions = self._group_transactions_by_bill_pattern(transactions)
        
        # Analyze each group for bill patterns
        detections = []
        for group in grouped_transactions:
            detection = self._analyze_bill_pattern(group)
            if detection:
                detections.append(detection)
        
        return detections
    
    def update_overdue_bills(self):
        """Update status for overdue bills."""
        today = date.today()
        
        overdue_bills = self.db.query(Bill).filter(
            and_(
                Bill.is_active == True,
                Bill.next_due_date < today,
                Bill.status != BillStatus.PAID.value
            )
        ).all()
        
        for bill in overdue_bills:
            bill.status = BillStatus.OVERDUE.value
        
        if overdue_bills:
            self.db.commit()
    
    def get_upcoming_bills(self, user_id: UUID, days_ahead: int = 7) -> List[Bill]:
        """Get bills due in the next N days."""
        end_date = date.today() + timedelta(days=days_ahead)
        
        return self.db.query(Bill).filter(
            and_(
                Bill.user_id == user_id,
                Bill.is_active == True,
                Bill.next_due_date <= end_date,
                Bill.next_due_date >= date.today()
            )
        ).order_by(asc(Bill.next_due_date)).all()
    
    def _calculate_next_due_date(self, current_date: date, frequency: BillFrequency) -> date:
        """Calculate next due date based on frequency."""
        if frequency == BillFrequency.WEEKLY:
            return current_date + timedelta(days=7)
        
        elif frequency == BillFrequency.BIWEEKLY:
            return current_date + timedelta(days=14)
        
        elif frequency == BillFrequency.MONTHLY:
            # Add one month
            if current_date.month == 12:
                return date(current_date.year + 1, 1, current_date.day)
            else:
                try:
                    return date(current_date.year, current_date.month + 1, current_date.day)
                except ValueError:
                    # Handle month-end edge cases (e.g., Jan 31 -> Feb 28/29)
                    return date(current_date.year, current_date.month + 1, 1) + timedelta(days=27)
        
        elif frequency == BillFrequency.QUARTERLY:
            # Add 3 months
            month = current_date.month + 3
            year = current_date.year
            if month > 12:
                year += month // 12
                month = month % 12
            return date(year, month, current_date.day)
        
        elif frequency == BillFrequency.SEMI_ANNUALLY:
            # Add 6 months
            month = current_date.month + 6
            year = current_date.year
            if month > 12:
                year += month // 12
                month = month % 12
            return date(year, month, current_date.day)
        
        elif frequency == BillFrequency.ANNUALLY:
            return date(current_date.year + 1, current_date.month, current_date.day)
        
        else:  # ONE_TIME
            return current_date
    
    def _find_due_date_for_payment(self, bill: Bill, payment_date: date) -> date:
        """Find the due date that corresponds to a payment date."""
        # Work backwards from current due date to find the right one
        due_date = bill.next_due_date
        frequency = BillFrequency(bill.frequency)
        
        while due_date > payment_date:
            due_date = self._calculate_previous_due_date(due_date, frequency)
        
        return due_date
    
    def _calculate_previous_due_date(self, current_date: date, frequency: BillFrequency) -> date:
        """Calculate previous due date based on frequency."""
        if frequency == BillFrequency.WEEKLY:
            return current_date - timedelta(days=7)
        
        elif frequency == BillFrequency.BIWEEKLY:
            return current_date - timedelta(days=14)
        
        elif frequency == BillFrequency.MONTHLY:
            # Subtract one month
            if current_date.month == 1:
                return date(current_date.year - 1, 12, current_date.day)
            else:
                try:
                    return date(current_date.year, current_date.month - 1, current_date.day)
                except ValueError:
                    # Handle month-end edge cases
                    return date(current_date.year, current_date.month - 1, 1) + timedelta(days=27)
        
        elif frequency == BillFrequency.QUARTERLY:
            # Subtract 3 months
            month = current_date.month - 3
            year = current_date.year
            if month <= 0:
                year -= 1
                month += 12
            return date(year, month, current_date.day)
        
        else:
            return current_date - timedelta(days=30)  # Default
    
    def _is_due_on_date(self, bill: Bill, check_date: date) -> bool:
        """Check if a bill is due on a specific date."""
        # This is a simplified implementation
        # A more sophisticated version would calculate all due dates in a range
        return check_date == bill.next_due_date
    
    def _group_transactions_by_bill_pattern(self, transactions: List[Transaction]) -> List[List[Transaction]]:
        """Group transactions that could represent the same bill."""
        groups = []
        
        for transaction in transactions:
            # Find existing group for this transaction
            matched_group = None
            
            for group in groups:
                if self._transactions_match_bill_pattern(transaction, group[0]):
                    matched_group = group
                    break
            
            if matched_group:
                matched_group.append(transaction)
            else:
                groups.append([transaction])
        
        # Filter groups that have potential bill patterns (at least 3 transactions)
        return [group for group in groups if len(group) >= 3]
    
    def _transactions_match_bill_pattern(self, transaction1: Transaction, transaction2: Transaction) -> bool:
        """Check if two transactions could be part of the same bill."""
        # Check merchant similarity
        merchant_similarity = self._calculate_merchant_similarity(
            transaction1.merchant_name or transaction1.description,
            transaction2.merchant_name or transaction2.description
        )
        
        # Check amount similarity (bills should have consistent amounts)
        amount1 = abs(transaction1.amount)
        amount2 = abs(transaction2.amount)
        amount_variance = abs(amount1 - amount2) / max(amount1, amount2)
        
        return merchant_similarity > 0.85 and amount_variance < 0.1  # Stricter than subscriptions
    
    def _calculate_merchant_similarity(self, name1: str, name2: str) -> float:
        """Calculate similarity between merchant names."""
        if not name1 or not name2:
            return 0.0
        
        name1 = name1.lower().strip()
        name2 = name2.lower().strip()
        
        if name1 == name2:
            return 1.0
        
        if name1 in name2 or name2 in name1:
            return 0.9
        
        # Check for common words
        words1 = set(name1.split())
        words2 = set(name2.split())
        common_words = words1.intersection(words2)
        
        if len(common_words) > 0:
            return len(common_words) / max(len(words1), len(words2))
        
        return 0.0
    
    def _analyze_bill_pattern(self, transactions: List[Transaction]) -> Optional[BillDetectionResult]:
        """Analyze a group of transactions for bill patterns."""
        if len(transactions) < 3:
            return None
        
        # Sort by date
        transactions.sort(key=lambda t: t.date)
        
        # Calculate day differences between transactions
        day_differences = []
        for i in range(1, len(transactions)):
            diff = (transactions[i].date - transactions[i-1].date).days
            day_differences.append(diff)
        
        # Check for consistent billing cycles
        frequency = self._detect_bill_frequency(day_differences)
        if not frequency:
            return None
        
        # Calculate amount consistency
        amounts = [abs(t.amount) for t in transactions]
        avg_amount = sum(amounts) / len(amounts)
        amount_variance = (max(amounts) - min(amounts)) / avg_amount * 100 if avg_amount > 0 else 100
        
        # Bills should have very low variance (< 5%)
        if amount_variance > 5:
            return None
        
        # Calculate confidence
        confidence = self._calculate_bill_confidence(len(transactions), amount_variance, day_differences)
        
        # Extract bill information
        first_transaction = transactions[0]
        bill_name = self._extract_bill_name(first_transaction.merchant_name or first_transaction.description)
        payee = first_transaction.merchant_name or "Unknown"
        category = self._suggest_bill_category(bill_name, payee)
        
        # Predict next due date
        last_transaction = transactions[-1]
        cycle_days = self._get_frequency_days(frequency)
        predicted_next_due = last_transaction.date + timedelta(days=cycle_days)
        
        return BillDetectionResult(
            id=UUID(),  # Generate temporary ID
            name=bill_name,
            payee=payee,
            category=category,
            frequency=frequency,
            amount=avg_amount,
            confidence=confidence,
            transaction_count=len(transactions),
            first_transaction_date=transactions[0].date,
            last_transaction_date=transactions[-1].date,
            predicted_next_due=predicted_next_due,
            amount_variance=amount_variance
        )
    
    def _detect_bill_frequency(self, day_differences: List[int]) -> Optional[BillFrequency]:
        """Detect bill frequency from day differences."""
        if not day_differences:
            return None
        
        avg_days = sum(day_differences) / len(day_differences)
        
        # Bills are more regular than subscriptions
        if 28 <= avg_days <= 32:
            return BillFrequency.MONTHLY
        elif 6 <= avg_days <= 8:
            return BillFrequency.WEEKLY
        elif 13 <= avg_days <= 15:
            return BillFrequency.BIWEEKLY
        elif 89 <= avg_days <= 93:
            return BillFrequency.QUARTERLY
        elif 180 <= avg_days <= 186:
            return BillFrequency.SEMI_ANNUALLY
        elif 360 <= avg_days <= 370:
            return BillFrequency.ANNUALLY
        
        return None
    
    def _calculate_bill_confidence(self, transaction_count: int, amount_variance: float, day_differences: List[int]) -> float:
        """Calculate confidence level for bill detection."""
        score = 0
        
        # Transaction count factor
        if transaction_count >= 6:
            score += 40
        elif transaction_count >= 4:
            score += 25
        elif transaction_count >= 3:
            score += 15
        
        # Amount consistency factor (bills should be very consistent)
        if amount_variance <= 1:
            score += 35
        elif amount_variance <= 3:
            score += 25
        elif amount_variance <= 5:
            score += 15
        
        # Timing consistency factor
        if day_differences:
            std_dev = self._calculate_std_dev(day_differences)
            if std_dev <= 1:
                score += 25
            elif std_dev <= 2:
                score += 15
            elif std_dev <= 3:
                score += 5
        
        return min(score / 100, 1.0)  # Normalize to 0-1
    
    def _calculate_std_dev(self, values: List[int]) -> float:
        """Calculate standard deviation of values."""
        if len(values) <= 1:
            return 0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance ** 0.5
    
    def _extract_bill_name(self, description: str) -> str:
        """Extract bill name from transaction description."""
        if not description:
            return "Unknown Bill"
        
        # Clean up common transaction prefixes/suffixes
        cleaned = description.replace("AUTOPAY", "").replace("BILL PAY", "").strip()
        
        # Take first few words as bill name
        words = cleaned.split()[:3]
        return " ".join(words).title()
    
    def _suggest_bill_category(self, bill_name: str, payee: str) -> BillCategory:
        """Suggest category based on bill name and payee."""
        name_lower = (bill_name + " " + payee).lower()
        
        if any(word in name_lower for word in ["electric", "gas", "water", "sewer", "trash", "utility"]):
            return BillCategory.UTILITIES
        elif any(word in name_lower for word in ["rent", "mortgage", "property", "hoa"]):
            return BillCategory.HOUSING
        elif any(word in name_lower for word in ["insurance", "policy", "premium"]):
            return BillCategory.INSURANCE
        elif any(word in name_lower for word in ["phone", "mobile", "internet", "cable", "wireless"]):
            return BillCategory.COMMUNICATION
        elif any(word in name_lower for word in ["medical", "health", "hospital", "doctor", "prescription"]):
            return BillCategory.HEALTHCARE
        elif any(word in name_lower for word in ["credit", "loan", "card", "payment"]):
            return BillCategory.PERSONAL
        elif any(word in name_lower for word in ["car", "auto", "vehicle", "parking"]):
            return BillCategory.TRANSPORTATION
        elif any(word in name_lower for word in ["school", "tuition", "student", "education"]):
            return BillCategory.EDUCATION
        else:
            return BillCategory.OTHER
    
    def _get_frequency_days(self, frequency: BillFrequency) -> int:
        """Get approximate days for a billing frequency."""
        if frequency == BillFrequency.WEEKLY:
            return 7
        elif frequency == BillFrequency.BIWEEKLY:
            return 14
        elif frequency == BillFrequency.MONTHLY:
            return 30
        elif frequency == BillFrequency.QUARTERLY:
            return 90
        elif frequency == BillFrequency.SEMI_ANNUALLY:
            return 180
        elif frequency == BillFrequency.ANNUALLY:
            return 365
        else:
            return 30