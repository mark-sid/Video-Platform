from slowapi import Limiter
from slowapi.util import get_remote_address

from src.config import settings


limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=settings.limiter_storage_uri,
    default_limits=settings.limiter_default_limits
)


