from typing import Annotated
from fastapi import Depends

from .jwt_handler import get_current_user
from src.models import User


user_dep = Annotated[User, Depends(get_current_user)]
