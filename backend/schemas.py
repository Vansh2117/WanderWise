from pydantic import BaseModel, EmailStr, Field
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
        orm_mode = True


# PREFERENCE SCHEMAS 
class PreferenceBase(BaseModel):
    preferred_climate: Optional[str] = None
    preferred_activities: Optional[List[str]] = None
    max_budget: Optional[float] = None
    travel_style: Optional[str] = None


class PreferenceCreate(PreferenceBase):
    user_id: int


class PreferenceResponse(PreferenceBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True


# TRIP MEMBER SCHEMAS
class TripMemberBase(BaseModel):
    user_id: int


class TripMemberCreate(TripMemberBase):
    trip_id: int


class TripMemberResponse(TripMemberBase):
    id: int
    trip_id: int

    class Config:
        orm_mode = True


# TRIP SCHEMAS
class TripBase(BaseModel):
    destination: str
    start_date: date
    end_date: date
    budget_per_person: Optional[float] = None
    is_public: bool = True


class TripCreate(BaseModel):
    destination: str
    start_date: str
    end_date: str
    budget_per_person: float
    is_public: bool = True



class TripResponse(TripBase):
    id: int
    creator_id: int
    members: List[TripMemberResponse] = []

    class Config:
        orm_mode = True
