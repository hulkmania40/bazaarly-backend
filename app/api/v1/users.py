from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from app.db.session import get_session
from app.core.deps import get_current_user, require_role
from app.models.user import User
from app.models.seller import Seller
from app.schemas.user import UserRead, UserUpdate
from app.schemas.seller import SellerRead
from app.services.user_service import UserService
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.get("/users/me")
async def get_profile(current_user: User = Depends(get_current_user)):
    return UserRead.model_validate(current_user)


@router.patch("/users/me", response_model=UserRead)
async def update_profile(data: UserUpdate, session: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user)):
    user = await session.get(User, current_user.id)
    if data.name is not None:
        user.name = data.name
    if data.avatar_url is not None:
        user.avatar_url = data.avatar_url
    await session.commit()
    await session.refresh(user)
    return UserRead.model_validate(user)
