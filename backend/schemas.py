import json

from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List
from datetime import date


# USER SCHEMAS
class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str = Field(..., min_length=6, description="Minimum 6 characters")


class UserResponse(UserBase):
    id: int

    class Config:
        from_attributes=True


# PREFERENCE SCHEMAS 
class PreferenceBase(BaseModel):
    preferred_climate: Optional[str] = None
    preferred_activities: Optional[List[str]] = None
    max_budget: Optional[float] = None
    travel_style: Optional[str] = None

    @field_validator("preferred_activities", mode="before")
    @classmethod
    def parse_activities(cls, v):
        #Coming from DB, stored as '["hiking","beach"]' string, convert to list
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                # Handele legacy comma-separated string format "trekking,shopping" if any
                return [item.strip() for item in v.split(",") if item.strip()]
        # Coming from API, should already be a list
        return v


class PreferenceCreate(PreferenceBase):
    user_id: int


class PreferenceResponse(PreferenceBase):
    id: int
    user_id: int

    class Config:
        from_attributes=True


# TRIP MEMBER SCHEMAS
class TripMemberBase(BaseModel):
    user_id: int


class TripMemberCreate(TripMemberBase):
    trip_id: int


class TripMemberResponse(TripMemberBase):
    id: int
    trip_id: int

    class Config:
        from_attributes=True


# TRIP SCHEMAS
class TripBase(BaseModel):
    destination: str
    start_date: date
    end_date: date
    budget_per_person: Optional[float] = None
    is_public: bool = True


class TripCreate(TripBase):
    # Inherits destination, start_date, end_date, is_public from TripBase
    # budget_per_person is required here (no Optional, no None default)
    budget_per_person: float



class TripResponse(TripBase):
    id: int
    creator_id: int
    members: List[TripMemberResponse] = []

    class Config:
        from_attributes=True
