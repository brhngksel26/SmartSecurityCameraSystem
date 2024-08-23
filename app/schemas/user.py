# schemas/user.py
from typing import Optional

from pydantic import BaseModel

from app.dependencies.baseschema import BaseResponse


class UserCreate(BaseModel):
    email: str
    password: str


class UserUpdate(BaseModel):
    email: Optional[str] = None
    password: Optional[str] = None


class UserResponse(BaseResponse):
    email: str


# schemas/auth.py


class Login(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
