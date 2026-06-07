from typing_extensions import Self
from pydantic import BaseModel, model_validator, ConfigDict


class UserCreateSchema(BaseModel):
    """Schema for user creating"""
    username: str
    password: str
    password_repeat: str

    @model_validator(mode="after")
    def check_passwords_match(self) -> Self:
        if self.password != self.password_repeat:
            raise ValueError("Passwords do not match")
        
        return self

class UserSchema(BaseModel):
    """Schema for user"""
    id: int
    username: str

    model_config = ConfigDict(
        from_attributes=True
    )


class TokenSchema(BaseModel):
    """Schema for token"""
    access_token: str
    token_type: str


class TokenDataSchema(BaseModel):
    """Schema for token data"""
    username: str | None = None


