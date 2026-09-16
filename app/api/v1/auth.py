from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from app.db.session import get_session
from app.models.user import User
from app.models.seller import Seller
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse
from app.schemas.user import UserRead
from app.services.user_service import UserService
from app.core.security import verify_password, create_access_token, create_refresh_token, decode_token
from app.core.deps import get_current_user
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.post("/register", status_code=201)
async def register(data: RegisterRequest, session: AsyncSession = Depends(get_session)):
    if data.role not in ("customer", "seller"):
        raise HTTPException(status_code=400, detail="INVALID_ROLE")
    existing = await session.execute(select(User).where(User.email == data.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="EMAIL_EXISTS")
    user = await UserService.create(session, data)
    if data.role == "seller":
        seller = Seller(user_id=user.id, store_name=user.name, description="")
        session.add(seller)
        await session.flush()
    await session.commit()
    await session.refresh(user)
    return {"user": UserRead.model_validate(user)}


@router.post("/login")
async def login(data: LoginRequest, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="UNAUTHENTICATED")
    access = create_access_token(str(user.id), user.role.value)
    refresh = create_refresh_token(str(user.id), user.role.value)
    user_data = UserRead(id=str(user.id), name=user.name, email=user.email, role=user.role.value, avatar_url=None, created_at=str(user.created_at)).model_dump()
    return TokenResponse(access_token=access, refresh_token=refresh).model_dump() | {"user": user_data}


@router.post("/refresh")
async def refresh(body: dict):
    token = body.get("refresh_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="UNAUTHENTICATED")
    try:
        payload = decode_token(token)
        if payload.get("typ") != "refresh":
            raise ValueError()
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="UNAUTHENTICATED")
    return {"access_token": create_access_token(payload["sub"], payload["role"])}


@router.post("/logout")
async def logout():
    return {"ok": True}


@router.get("/me")
async def me(current_user: User = Depends(get_current_user)):
    return {"user": UserRead.model_validate(current_user)}
