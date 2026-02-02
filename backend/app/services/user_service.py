from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from uuid import UUID

from app.models.user import User, UserPreferences
from app.schemas.user import UserPreferencesUpdate


class UserService:
    """Service for user operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID."""
        return await self.db.get(User, user_id)
    
    async def get_preferences(self, user_id: UUID) -> Optional[UserPreferences]:
        """Get user preferences."""
        return await self.db.get(UserPreferences, user_id)
    
    async def update_preferences(
        self, 
        user_id: UUID, 
        preferences_data: UserPreferencesUpdate
    ) -> UserPreferences:
        """Update user preferences."""
        preferences = await self.get_preferences(user_id)
        
        if not preferences:
            # Create preferences if they don't exist
            preferences = UserPreferences(user_id=user_id)
            self.db.add(preferences)
        
        # Update only provided fields
        for field, value in preferences_data.model_dump(exclude_unset=True).items():
            setattr(preferences, field, value)
        
        await self.db.commit()
        await self.db.refresh(preferences)
        return preferences
