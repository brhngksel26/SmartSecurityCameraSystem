from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Request
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPBearer
from passlib.context import CryptContext

from app.config import config
from app.models.user import User


class AuthHandler:
    security = HTTPBearer()
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    ALGORITHM = "HS256"
    SECRET_KEY = config.SECRET_KEY
    ACCESS_TOKEN_EXPIRE_MINUTES = 60

    def decode_token(self, token):
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            return payload["sub"]
        except Exception as e:
            return RedirectResponse(url="/login")

    def auth_wrapper(self, request: Request):
        token = request.cookies.get("access_token")
        return self.decode_token(token)

    def create_access_token(
        self,
        email: str,
        expires_delta: timedelta = None,
    ) -> str:
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES
            )
        payload = {
            "exp": expire,
            "sub": str(email),
        }
        return jwt.encode(payload, self.SECRET_KEY, algorithm=self.ALGORITHM)

    def get_hash_password(self, plain_password):
        return self.pwd_context.hash(plain_password)

    def verify_password(self, plain_password, hash_password):
        return self.pwd_context.verify(plain_password, hash_password)

    async def authenticate_user(self, email, password):
        try:
            user = await User.get(email=email)
            if user:
                password_check = self.verify_password(password, user.password)
                print(password_check)
                return password_check
            else:
                return False
        except:
            raise RequiresLoginException()


class RequiresLoginException(Exception):
    pass
