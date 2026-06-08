from typing import Annotated
from datetime import timedelta

from fastapi import HTTPException, APIRouter, Depends, status, Request
from fastapi.security import OAuth2PasswordRequestForm

from .schemas import UserCreateSchema, TokenSchema, UserSchema
from .jwt_handler import create_access_token, authenticate
from .dependencies import user_dep
from .crud import get_user, create_user

from src.database import session_dep
from src.config import settings
from src.limiter import limiter


auth_router = APIRouter(prefix="/user")


@auth_router.post("/", status_code=201, response_model=UserSchema)
@limiter.limit("10/minute")
async def create(request: Request, session: session_dep, user_data: UserCreateSchema):
    """Controller to create user"""
    try:
        username = user_data.username
        # verifying username uniqueness
        user = await get_user(session, username)

        if user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already exists"
            )
        # creating new user
        new_user = await create_user(session, username=username, password=user_data.password)

        return UserSchema.model_validate(new_user)

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Passwords don't match"
        )


@auth_router.post("/token/", status_code=200, response_model=TokenSchema)
@limiter.limit("3/minute")
async def login(
    request: Request, 
    session: session_dep, 
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> dict:
    """Controller to get access token"""
    user = await authenticate(session, form_data.username, form_data.password)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    return TokenSchema(access_token=access_token, token_type="bearer")


@auth_router.get("/me/", status_code=200, response_model=UserSchema)
async def read_users_me(
    request: Request, 
    user: user_dep
) -> dict:
    """Controller to get authorized user"""
    return UserSchema.model_validate(user)
