from pydantic import BaseModel, ConfigDict

class ChannelCreateSchema(BaseModel):
    name: str
    description: str


class ChannelSchema(ChannelCreateSchema):
    id: int
    
    model_config = ConfigDict(
        from_attributes=True
    )
     