"""
Gamification service for XP, achievements, streaks, and challenges
"""
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
import math

from app.models.gamification import (
    Achievement, UserAchievement, Streak, Challenge, UserChallenge, XPHistory,
    AchievementCategory, AchievementTier, ChallengeType, ChallengeFrequency
)
from app.models.user import User
from app.schemas.gamification import (
    XPGainResponse, UserLevelResponse, ChallengeStatus
)


class GamificationService:
    """Service for gamification features"""
    
    # XP required for each level (exponential growth)
    @staticmethod
    def xp_for_level(level: int) -> int:
        """Calculate XP required for a specific level"""
        base_xp = 100
        multiplier = 1.5
        return int(base_xp * (multiplier ** (level - 1)))
    
    @staticmethod
    def level_from_xp(xp: int) -> int:
        """Calculate level from total XP"""
        level = 1
        total_xp_needed = 0
        
        while total_xp_needed <= xp:
            total_xp_needed += GamificationService.xp_for_level(level)
            if total_xp_needed > xp:
                break
            level += 1
        
        return level
    
    @staticmethod
    def xp_progress_for_level(xp: int, level: int) -> Dict[str, Any]:
        """Calculate XP progress for current level"""
        xp_for_current_level = GamificationService.xp_for_level(level)
        xp_for_next_level = GamificationService.xp_for_level(level + 1)
        
        # Calculate XP earned in current level
        total_xp_for_previous_levels = sum(
            GamificationService.xp_for_level(l) for l in range(1, level)
        )
        xp_in_current_level = xp - total_xp_for_previous_levels
        
        progress_percentage = (xp_in_current_level / xp_for_next_level) * 100
        
        return {
            "current_xp": xp_in_current_level,
            "xp_for_next_level": xp_for_next_level,
            "progress_percentage": min(progress_percentage, 100.0),
            "total_xp": xp
        }
    
    @staticmethod
    async def add_xp(
        db: AsyncSession,
        user_id: str,
        xp_amount: int,
        source: str,
        source_id: Optional[str] = None,
        description: Optional[str] = None
    ) -> XPGainResponse:
        """Add XP to user and check for level up"""
        # Get user
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            raise ValueError("User not found")
        
        old_xp = user.xp
        old_level = user.level
        
        # Add XP
        user.xp += xp_amount
        
        # Calculate new level
        new_level = GamificationService.level_from_xp(user.xp)
        level_up = new_level > old_level
        
        if level_up:
            user.level = new_level
        
        # Record XP history
        xp_history = XPHistory(
            user_id=user_id,
            xp_amount=xp_amount,
            source=source,
            source_id=source_id,
            description=description
        )
        db.add(xp_history)
        
        await db.commit()
        
        return XPGainResponse(
            xp_gained=xp_amount,
            new_total_xp=user.xp,
            source=source,
            description=description,
            level_up=level_up,
            new_level=new_level if level_up else None
        )
    
    @staticmethod
    async def get_user_level_info(db: AsyncSession, user_id: str) -> UserLevelResponse:
        """Get user's level and XP information"""
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            raise ValueError("User not found")
        
        progress = GamificationService.xp_progress_for_level(user.xp, user.level)
        
        return UserLevelResponse(
            user_id=str(user.id),
            level=user.level,
            current_xp=progress["current_xp"],
            xp_for_next_level=progress["xp_for_next_level"],
            xp_progress_percentage=progress["progress_percentage"],
            total_xp_earned=user.xp
        )
    
    @staticmethod
    async def update_streak(
        db: AsyncSession,
        user_id: str,
        activity_date: Optional[date] = None
    ) -> Streak:
        """Update user's activity streak"""
        if activity_date is None:
            activity_date = date.today()
        
        # Get or create streak
        result = await db.execute(
            select(Streak).where(Streak.user_id == user_id)
        )
        streak = result.scalar_one_or_none()
        
        if not streak:
            # Create new streak
            streak = Streak(
                user_id=user_id,
                current_streak=1,
                longest_streak=1,
                last_activity_date=activity_date,
                streak_start_date=activity_date,
                total_activity_days=1
            )
            db.add(streak)
        else:
            # Check if activity is for today
            if streak.last_activity_date == activity_date:
                # Already logged activity today
                return streak
            
            # Check if streak continues
            yesterday = activity_date - timedelta(days=1)
            
            if streak.last_activity_date == yesterday:
                # Streak continues
                streak.current_streak += 1
                streak.total_activity_days += 1
            else:
                # Streak broken, start new
                streak.current_streak = 1
                streak.streak_start_date = activity_date
                streak.total_activity_days += 1
            
            # Update longest streak
            if streak.current_streak > streak.longest_streak:
                streak.longest_streak = streak.current_streak
            
            streak.last_activity_date = activity_date
            streak.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(streak)
        
        # Award XP for streak milestones
        if streak.current_streak > 0 and streak.current_streak % 7 == 0:
            await GamificationService.add_xp(
                db, user_id, 50, "streak_milestone",
                description=f"{streak.current_streak} day streak!"
            )
        
        return streak
    
    @staticmethod
    async def check_and_unlock_achievement(
        db: AsyncSession,
        user_id: str,
        achievement_code: str,
        progress: int = 100,
        extra_data: Optional[Dict[str, Any]] = None
    ) -> Optional[UserAchievement]:
        """Check criteria and unlock achievement for user"""
        # Get achievement
        result = await db.execute(
            select(Achievement).where(Achievement.code == achievement_code)
        )
        achievement = result.scalar_one_or_none()
        
        if not achievement:
            return None
        
        # Check if already unlocked (for non-repeatable)
        if not achievement.is_repeatable:
            result = await db.execute(
                select(UserAchievement).where(
                    and_(
                        UserAchievement.user_id == user_id,
                        UserAchievement.achievement_id == achievement.id
                    )
                )
            )
            existing = result.scalar_one_or_none()
            if existing:
                return None
        
        # Create user achievement
        user_achievement = UserAchievement(
            user_id=user_id,
            achievement_id=achievement.id,
            progress=progress,
            extra_data=extra_data
        )
        db.add(user_achievement)
        
        # Award XP
        await GamificationService.add_xp(
            db, user_id, achievement.xp_reward, "achievement",
            source_id=str(achievement.id),
            description=f"Unlocked: {achievement.name}"
        )
        
        await db.commit()
        await db.refresh(user_achievement)
        
        return user_achievement
    
    @staticmethod
    async def get_user_achievements(
        db: AsyncSession,
        user_id: str,
        category: Optional[AchievementCategory] = None
    ) -> List[UserAchievement]:
        """Get user's unlocked achievements"""
        query = select(UserAchievement).where(
            UserAchievement.user_id == user_id
        ).options(selectinload(UserAchievement.achievement))
        
        if category:
            query = query.join(Achievement).where(
                Achievement.category == category
            )
        
        query = query.order_by(desc(UserAchievement.unlocked_at))
        
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def get_available_achievements(
        db: AsyncSession,
        user_id: str,
        category: Optional[AchievementCategory] = None,
        show_secret: bool = False
    ) -> List[Achievement]:
        """Get achievements not yet unlocked by user"""
        # Get unlocked achievement IDs
        unlocked_result = await db.execute(
            select(UserAchievement.achievement_id).where(
                UserAchievement.user_id == user_id
            )
        )
        unlocked_ids = [row[0] for row in unlocked_result.all()]
        
        # Query available achievements
        query = select(Achievement).where(
            Achievement.id.not_in(unlocked_ids) if unlocked_ids else True
        )
        
        if category:
            query = query.where(Achievement.category == category)
        
        if not show_secret:
            query = query.where(Achievement.is_secret == False)
        
        query = query.order_by(Achievement.sort_order, Achievement.tier)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def accept_challenge(
        db: AsyncSession,
        user_id: str,
        challenge_id: str
    ) -> UserChallenge:
        """User accepts a challenge"""
        # Get challenge
        result = await db.execute(
            select(Challenge).where(Challenge.id == challenge_id)
        )
        challenge = result.scalar_one_or_none()
        
        if not challenge:
            raise ValueError("Challenge not found")
        
        if not challenge.is_active:
            raise ValueError("Challenge is not active")
        
        # Check if already accepted
        result = await db.execute(
            select(UserChallenge).where(
                and_(
                    UserChallenge.user_id == user_id,
                    UserChallenge.challenge_id == challenge_id,
                    UserChallenge.status == "active"
                )
            )
        )
        existing = result.scalar_one_or_none()
        if existing:
            raise ValueError("Challenge already accepted")
        
        # Calculate expiration
        expires_at = None
        if challenge.duration_days:
            expires_at = datetime.utcnow() + timedelta(days=challenge.duration_days)
        elif challenge.end_date:
            expires_at = datetime.combine(challenge.end_date, datetime.min.time())
        
        # Create user challenge
        user_challenge = UserChallenge(
            user_id=user_id,
            challenge_id=challenge_id,
            status="active",
            progress=0,
            target_progress=challenge.target_value or 100,
            expires_at=expires_at
        )
        db.add(user_challenge)
        
        await db.commit()
        await db.refresh(user_challenge)
        
        return user_challenge
    
    @staticmethod
    async def update_challenge_progress(
        db: AsyncSession,
        user_challenge_id: str,
        progress: int,
        extra_data: Optional[Dict[str, Any]] = None
    ) -> UserChallenge:
        """Update challenge progress"""
        result = await db.execute(
            select(UserChallenge)
            .where(UserChallenge.id == user_challenge_id)
            .options(selectinload(UserChallenge.challenge))
        )
        user_challenge = result.scalar_one_or_none()
        
        if not user_challenge:
            raise ValueError("User challenge not found")
        
        if user_challenge.status != "active":
            raise ValueError("Challenge is not active")
        
        # Update progress
        user_challenge.progress = progress
        if extra_data:
            user_challenge.extra_data = {**(user_challenge.extra_data or {}), **extra_data}
        
        # Check if completed
        if progress >= (user_challenge.target_progress or 100):
            user_challenge.status = "completed"
            user_challenge.completed_at = datetime.utcnow()
            
            # Award XP
            await GamificationService.add_xp(
                db, str(user_challenge.user_id),
                user_challenge.challenge.xp_reward,
                "challenge",
                source_id=str(user_challenge.challenge_id),
                description=f"Completed: {user_challenge.challenge.name}"
            )
        
        user_challenge.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(user_challenge)
        
        return user_challenge
    
    @staticmethod
    async def get_user_challenges(
        db: AsyncSession,
        user_id: str,
        status: Optional[ChallengeStatus] = None
    ) -> List[UserChallenge]:
        """Get user's challenges"""
        query = select(UserChallenge).where(
            UserChallenge.user_id == user_id
        ).options(selectinload(UserChallenge.challenge))
        
        if status:
            query = query.where(UserChallenge.status == status.value)
        
        query = query.order_by(desc(UserChallenge.started_at))
        
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def get_available_challenges(
        db: AsyncSession,
        challenge_type: Optional[ChallengeType] = None
    ) -> List[Challenge]:
        """Get available active challenges"""
        query = select(Challenge).where(Challenge.is_active == True)
        
        if challenge_type:
            query = query.where(Challenge.challenge_type == challenge_type)
        
        # Filter by date range
        today = date.today()
        query = query.where(
            or_(
                Challenge.start_date == None,
                Challenge.start_date <= today
            )
        ).where(
            or_(
                Challenge.end_date == None,
                Challenge.end_date >= today
            )
        )
        
        query = query.order_by(Challenge.sort_order, Challenge.difficulty_level)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def get_leaderboard(
        db: AsyncSession,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get global leaderboard by XP"""
        query = select(
            User.id,
            User.first_name,
            User.last_name,
            User.level,
            User.xp,
            User.profile_picture_url,
            func.count(UserAchievement.id).label("achievements_count")
        ).outerjoin(
            UserAchievement, User.id == UserAchievement.user_id
        ).where(
            User.is_active == True
        ).group_by(
            User.id
        ).order_by(
            desc(User.xp)
        ).limit(limit).offset(offset)
        
        result = await db.execute(query)
        rows = result.all()
        
        leaderboard = []
        for idx, row in enumerate(rows, start=offset + 1):
            # Get streak info
            streak_result = await db.execute(
                select(Streak).where(Streak.user_id == row.id)
            )
            streak = streak_result.scalar_one_or_none()
            
            leaderboard.append({
                "rank": idx,
                "user_id": str(row.id),
                "display_name": f"{row.first_name} {row.last_name}",
                "level": row.level,
                "xp": row.xp,
                "achievements_count": row.achievements_count,
                "current_streak": streak.current_streak if streak else 0,
                "profile_picture_url": row.profile_picture_url
            })
        
        return leaderboard
    
    @staticmethod
    async def get_user_rank(db: AsyncSession, user_id: str) -> Optional[int]:
        """Get user's rank on leaderboard"""
        # Get user's XP
        result = await db.execute(select(User.xp).where(User.id == user_id))
        user_xp = result.scalar_one_or_none()
        
        if user_xp is None:
            return None
        
        # Count users with higher XP
        result = await db.execute(
            select(func.count(User.id)).where(
                and_(
                    User.xp > user_xp,
                    User.is_active == True
                )
            )
        )
        rank = result.scalar_one() + 1
        
        return rank
