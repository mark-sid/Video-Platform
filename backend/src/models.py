from typing import List
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True, index=True)
    password: Mapped[str]
    channels: Mapped[List["Channel"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class Channel(Base):
    __tablename__ = "channels"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    name: Mapped[str] = mapped_column(unique=True)
    description: Mapped[str]
    user: Mapped["User"] = relationship(back_populates="channels") 
    videos: Mapped[List["Video"]] = relationship(back_populates="channel", cascade="all, delete-orphan")


class Media(Base):
    __tablename__ = 'media'

    id: Mapped[int] = mapped_column(primary_key=True)
    filename: Mapped[str] = mapped_column(unique=True)
    file_path: Mapped[str]
    media_type: Mapped[str]


class Video(Base):
    __tablename__ = "videos"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    description: Mapped[str]
    
    channel_id: Mapped[int] = mapped_column(ForeignKey("channels.id"))
    channel: Mapped["Channel"] = relationship(back_populates="videos")
    
    video_media_id: Mapped[int] = mapped_column(ForeignKey("media.id", ondelete="CASCADE"))
    video_media: Mapped[Media] = relationship(
        foreign_keys=[video_media_id],
        viewonly=True
    )

    cover_media_id: Mapped[int] = mapped_column(ForeignKey("media.id", ondelete="CASCADE"))
    cover_media: Mapped[Media] = relationship(
        foreign_keys=[cover_media_id],
        viewonly=True    
    )
    
    

