from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from db.models import User
from typing import Any
import logging

class UserService:

    async def update_user(self, user: User, user_data: dict, session: AsyncSession):
        try:
            for key, value in user_data.items():
                setattr(user, key, value)
            await session.commit()
            await session.refresh(user)
            return user
        except Exception as e:
            await session.rollback()
            logging.error(f"Error updating user: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while updating the user."
            )