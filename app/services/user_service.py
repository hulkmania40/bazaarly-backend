from sqlmodel import select
from app.models.user import User
from app.models.seller import Seller
from app.schemas.auth import RegisterRequest
from app.core.security import hash_password


class UserService:
    @staticmethod
    async def get_by_email(session, email: str) -> User | None:
        result = await session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    @staticmethod
    async def create(session, data: RegisterRequest) -> User:
        user = User(
            name=data.name,
            email=data.email,
            password_hash=hash_password(data.password),
            role=data.role,
        )
        session.add(user)
        await session.flush()
        await session.refresh(user)
        return user
