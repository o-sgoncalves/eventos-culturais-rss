from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


# --- Events ---

class EventBase(BaseModel):
    title: str
    description: Optional[str] = None
    event_date: Optional[datetime] = None
    event_time: Optional[str] = None
    location: Optional[str] = None
    address: Optional[str] = None
    region: Optional[str] = None
    price: Optional[str] = None
    is_free: bool = False
    category: Optional[str] = None
    source_url: Optional[str] = None
    image_url: Optional[str] = None


class EventCreate(EventBase):
    title: str


class EventUpdate(EventBase):
    pass


class EventOut(EventBase):
    id: int
    approved: bool
    submitted_by_user: bool
    created_at: datetime

    class Config:
        from_attributes = True


class EventSuggest(BaseModel):
    title: str
    description: Optional[str] = None
    event_date: Optional[datetime] = None
    location: Optional[str] = None
    price: Optional[str] = None
    category: Optional[str] = None


# --- Sources ---

class SourceCreate(BaseModel):
    username: str
    platform: str = "instagram"


class SourceOut(BaseModel):
    id: int
    platform: str
    username: str
    active: bool
    last_scraped: Optional[datetime]
    error_count: int
    created_at: datetime

    class Config:
        from_attributes = True


# --- Auth ---

class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# --- Stats ---

class StatsOut(BaseModel):
    total_events: int
    pending_events: int
    approved_events: int
    by_category: dict[str, int]
