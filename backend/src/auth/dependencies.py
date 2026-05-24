from typing import Annotated
from fastapi import Depends

from src.models import User
from .jwt_handler import get_current_user

user_dep = Annotated[User, Depends(get_current_user)]