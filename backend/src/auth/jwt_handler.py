import jwt
from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from .schemas import TokenDataSchema
from .crud import get_user
from .auth import verify_password

from src.database  import session_dep
from src.models import User
from src.config import settings


oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"/api/{settings.api_version}/user/token/")


async def authenticate(session: AsyncSession, username: str, password: str) -> User | False:
    """Function to authenticate user"""
    user = await get_user(session, username)
    
    if not user or not verify_password(password, user.password):
        return False

    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Function for creating access tokens"""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    return encoded_jwt


async def get_current_user(session: session_dep, token: Annotated[str, Depends(oauth2_scheme)]) -> User:
    """Function to get user using token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials"
    )

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        username = payload.get("sub")
        token_data = TokenDataSchema(username=username)
                
        if username is None:
            raise credentials_exception

    except jwt.InvalidTokenError:
        raise credentials_exception
    
    user = await get_user(session, token_data.username)

    if user is None:
        raise credentials_exception

    return user

