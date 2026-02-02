"""
Gamification API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.models.gamification import AchievementCategory, ChallengeType
from app.schemas.gamification import (
    AchievementResponse,
    AchievementsListResponse,
    UserAchievementResponse,
    UserAchievementsListResponse,
    StreakResponse,
    StreakUpdate,
    ChallengeResponse,
    ChallengesListResponse,
    UserChallengeResponse,
    UserChallengesListResponse,
    ChallengeAccept,
    ChallengeProgressUpdate,
    ChallengeStatus,
    XPHistoryResponse,
    XPHistoryListResponse,
    UserLevelResponse,
    GamificationDashboardResponse,
    LeaderboardResponse,
    LeaderboardEntry
)
from app.services.gamification_service import GamificationService
from sqlalchemy import select, func, desc

router = APIRouter()


# Dashboard
@router.get("/dashboard", response_model=GamificationDashboardResponse)
async def get_gamification_dashboard(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get complete gamification dashboard"""
    user_id = str(current_user.id)
    
    # Get user level info
    level_info = await GamificationService.get_user_level_info(db, user_id)
    
    # Get streak
    result = await db.execute(
        select(current_user.streak).select_from(User).where(User.id == current_user.id)
    )
    streak = current_user.streak
    
    # Get active challenges
    active_challenges = await GamificationService.get_user_challenges(
        db, user_id, status=ChallengeStatus.ACTIVE
    )
    
    # Get recent achievements
    recent_achievements = await GamificationService.get_user_achievements(db, user_id)
    recent_achievements = recent_achievements[:5]  # Last 5
    
    # Get achievement stats
    from app.models.gamification import Achievement, UserAchievement
    total_achievements_result = await db.execute(select(func.count(Achievement.id)))
    total_achievements = total_achievements_result.scalar_one()
    
    unlocked_result = await db.execute(
        select(func.count(UserAchievement.id)).where(UserAchievement.user_id == user_id)
    )
    unlocked_achievements = unlocked_result.scalar_one()
    
    completion_rate = (unlocked_achievements / total_achievements * 100) if total_achievements > 0 else 0
    
    return GamificationDashboardResponse(
        user_level=level_info,
        streak=streak,
        active_challenges=[
            UserChallengeResponse.model_validate(uc) for uc in active_challenges
        ],
        recent_achievements=[
            UserAchievementResponse.model_validate(ua) for ua in recent_achievements
        ],
        total_achievements=total_achievements,
        unlocked_achievements=unlocked_achievements,
        achievement_completion_rate=completion_rate,
        total_xp_earned=current_user.xp,
        level_progress=level_info.xp_progress_percentage
    )


# Achievements
@router.get("/achievements", response_model=AchievementsListResponse)
async def list_achievements(
    category: Optional[AchievementCategory] = None,
    show_locked: bool = Query(True, description="Show locked achievements"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all achievements (locked and unlocked)"""
    from app.models.gamification import Achievement, UserAchievement
    
    user_id = str(current_user.id)
    
    # Get all achievements
    query = select(Achievement)
    
    if category:
        query = query.where(Achievement.category == category)
    
    query = query.order_by(Achievement.sort_order)
    
    result = await db.execute(query)
    achievements = result.scalars().all()
    
    # Filter secret achievements that aren't unlocked
    if not show_locked:
        unlocked_ids_result = await db.execute(
            select(UserAchievement.achievement_id).where(UserAchievement.user_id == user_id)
        )
        unlocked_ids = [row[0] for row in unlocked_ids_result.all()]
        achievements = [a for a in achievements if not a.is_secret or a.id in unlocked_ids]
    
    return AchievementsListResponse(
        achievements=[AchievementResponse.model_validate(a) for a in achievements],
        total=len(achievements)
    )


@router.get("/achievements/mine", response_model=UserAchievementsListResponse)
async def get_my_achievements(
    category: Optional[AchievementCategory] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's unlocked achievements"""
    user_id = str(current_user.id)
    
    user_achievements = await GamificationService.get_user_achievements(db, user_id, category)
    
    # Calculate total XP earned from achievements
    total_xp = sum(ua.achievement.xp_reward * ua.times_completed for ua in user_achievements)
    
    # Get total achievements count
    from app.models.gamification import Achievement
    total_result = await db.execute(select(func.count(Achievement.id)))
    total_achievements = total_result.scalar_one()
    
    completion_rate = (len(user_achievements) / total_achievements * 100) if total_achievements > 0 else 0
    
    return UserAchievementsListResponse(
        achievements=[UserAchievementResponse.model_validate(ua) for ua in user_achievements],
        total=len(user_achievements),
        total_xp_earned=total_xp,
        completion_rate=completion_rate
    )


# Challenges
@router.get("/challenges", response_model=ChallengesListResponse)
async def list_challenges(
    challenge_type: Optional[ChallengeType] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get all available challenges"""
    challenges = await GamificationService.get_available_challenges(db, challenge_type)
    
    return ChallengesListResponse(
        challenges=[ChallengeResponse.model_validate(c) for c in challenges],
        total=len(challenges)
    )


@router.get("/challenges/mine", response_model=UserChallengesListResponse)
async def get_my_challenges(
    status: Optional[ChallengeStatus] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's challenges"""
    user_id = str(current_user.id)
    
    user_challenges = await GamificationService.get_user_challenges(db, user_id, status)
    
    # Count by status
    active_count = sum(1 for uc in user_challenges if uc.status == "active")
    completed_count = sum(1 for uc in user_challenges if uc.status == "completed")
    
    return UserChallengesListResponse(
        challenges=[UserChallengeResponse.model_validate(uc) for uc in user_challenges],
        total=len(user_challenges),
        active_count=active_count,
        completed_count=completed_count
    )


@router.post("/challenges/accept", response_model=UserChallengeResponse, status_code=status.HTTP_201_CREATED)
async def accept_challenge(
    challenge_accept: ChallengeAccept,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Accept a challenge"""
    user_id = str(current_user.id)
    
    try:
        user_challenge = await GamificationService.accept_challenge(
            db, user_id, challenge_accept.challenge_id
        )
        await db.refresh(user_challenge)
        
        return UserChallengeResponse.model_validate(user_challenge)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put("/challenges/{user_challenge_id}/progress", response_model=UserChallengeResponse)
async def update_challenge_progress(
    user_challenge_id: str,
    progress_update: ChallengeProgressUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update challenge progress"""
    try:
        user_challenge = await GamificationService.update_challenge_progress(
            db, user_challenge_id, progress_update.progress, progress_update.extra_data
        )
        
        return UserChallengeResponse.model_validate(user_challenge)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# Streaks
@router.get("/streak", response_model=StreakResponse)
async def get_my_streak(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's current streak"""
    from app.models.gamification import Streak
    
    result = await db.execute(
        select(Streak).where(Streak.user_id == current_user.id)
    )
    streak = result.scalar_one_or_none()
    
    if not streak:
        # Create initial streak
        streak = Streak(user_id=current_user.id)
        db.add(streak)
        await db.commit()
        await db.refresh(streak)
    
    return StreakResponse.model_validate(streak)


@router.post("/streak/update", response_model=StreakResponse)
async def update_my_streak(
    streak_update: StreakUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Log activity and update streak"""
    user_id = str(current_user.id)
    
    streak = await GamificationService.update_streak(db, user_id)
    
    return StreakResponse.model_validate(streak)


# XP and Levels
@router.get("/level", response_model=UserLevelResponse)
async def get_my_level(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's level and XP info"""
    user_id = str(current_user.id)
    
    level_info = await GamificationService.get_user_level_info(db, user_id)
    
    return level_info


@router.get("/xp/history", response_model=XPHistoryListResponse)
async def get_xp_history(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's XP history"""
    from app.models.gamification import XPHistory
    
    user_id = str(current_user.id)
    
    # Get history
    query = select(XPHistory).where(
        XPHistory.user_id == user_id
    ).order_by(desc(XPHistory.created_at)).limit(limit).offset(offset)
    
    result = await db.execute(query)
    history = result.scalars().all()
    
    # Get total count
    count_result = await db.execute(
        select(func.count(XPHistory.id)).where(XPHistory.user_id == user_id)
    )
    total = count_result.scalar_one()
    
    return XPHistoryListResponse(
        history=[XPHistoryResponse.model_validate(h) for h in history],
        total=total,
        total_xp=current_user.xp
    )


# Leaderboard
@router.get("/leaderboard", response_model=LeaderboardResponse)
async def get_leaderboard(
    limit: int = Query(100, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get global leaderboard"""
    user_id = str(current_user.id)
    
    # Get leaderboard
    leaderboard = await GamificationService.get_leaderboard(db, limit, offset)
    
    # Get user's rank
    user_rank = await GamificationService.get_user_rank(db, user_id)
    
    # Get total users
    total_result = await db.execute(
        select(func.count(User.id)).where(User.is_active == True)
    )
    total_users = total_result.scalar_one()
    
    return LeaderboardResponse(
        entries=[LeaderboardEntry(**entry) for entry in leaderboard],
        user_rank=user_rank,
        total_users=total_users,
        leaderboard_type="global"
    )
