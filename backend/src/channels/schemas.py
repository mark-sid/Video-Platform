from pydantic import BaseModel, ConfigDict


class ChannelCreateSchema(BaseModel):
    """Schema for channel creating"""
    name: str
    description: str


class ChannelSchema(ChannelCreateSchema):
    """Schema for channel"""
    id: int
    
    model_config = ConfigDict(
        from_attributes=True
    )
     