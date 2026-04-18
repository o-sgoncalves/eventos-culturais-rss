from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text, func

from database import Base


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    event_date = Column(DateTime)
    event_time = Column(String(50))
    location = Column(String(255))
    address = Column(Text)
    region = Column(String(100))
    price = Column(String(100))
    is_free = Column(Boolean, default=False)
    category = Column(String(50))
    source_url = Column(Text, unique=True)
    image_url = Column(Text)
    approved = Column(Boolean, default=False)
    submitted_by_user = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class Source(Base):
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True)
    platform = Column(String(50), default="instagram")
    username = Column(String(100), nullable=False, unique=True)
    active = Column(Boolean, default=True)
    last_scraped = Column(DateTime)
    error_count = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(255), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    is_admin = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
