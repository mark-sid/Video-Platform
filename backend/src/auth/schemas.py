from pydantic import BaseModel, model_validator, ConfigDict
from typing_extensions import Self

class UserCreateSchema(BaseModel):
    username: str
    password: str
    password_repeat: str

    @model_validator(mode="after")
    def check_passwords_match(self) -> Self:
        if self.password != self.password_repeat:
            raise ValueError("Passwords do not match")
        return self


class UserSchema(BaseModel):
    id: int
    username: str

    model_config = ConfigDict(
        from_attributes=True
    )


class TokenSchema(BaseModel):
    access_token: str
    token_type: str


class TokenDataSchema(BaseModel):
    username: str | None = None


