from pydantic import BaseModel, ConfigDict, BeforeValidator
from typing import Optional, Annotated
from uuid import UUID
from datetime import datetime
from decimal import Decimal


def _coerce_str(v):
    if isinstance(v, (str, int, float, UUID, datetime, Decimal)):
        return str(v)
    return v


UserId = Annotated[str, BeforeValidator(_coerce_str)]
UserCreatedAt = Annotated[str, BeforeValidator(_coerce_str)]


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UserId
    name: str
    email: str
    role: str
    avatar_url: Optional[str] = None
    created_at: UserCreatedAt


class UserUpdate(BaseModel):
    name: Optional[str] = None
    avatar_url: Optional[str] = None
