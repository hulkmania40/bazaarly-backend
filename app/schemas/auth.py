from pydantic import BaseModel, EmailStr
from typing import Literal
from app.models.user import Role


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str


class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: Literal["customer", "seller"]


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str
