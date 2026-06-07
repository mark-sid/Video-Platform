import hashlib
from typing import Callable, Optional
from typing import Any, Callable, Dict, Optional, Tuple
from fastapi import Request, Response
from src.config import settings


def custom_key_builder(
    func,
    namespace: str = "",
    request = None,
    response = None,
    *args,
    **kwargs,
):
    return f"{namespace}:{func.__name__}:{str(kwargs)}"


