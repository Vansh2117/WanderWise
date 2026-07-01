import json

from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List, Dict, Any
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


# RECOMMENDATION SCHEMAS
class RecommendationRequest(BaseModel):
    slider_scores: Optional[Dict[str, float]] = None
    preferred_climate: Optional[str] = None
    preferred_activities: Optional[List[str]] = None
    travel_style: Optional[str] = None
    travel_month: Optional[str] = None
    max_budget_inr: Optional[float] = None
    top_k: int = 10


class GroupRecommendationRequest(BaseModel):
    strategy: str = "weighted_average"  # options: weighted_average, least_miserable, nash_social_welfare
    travel_month: Optional[str] = None
    max_budget_inr: Optional[float] = None
    top_k: int = 10


class DestinationRecommendation(BaseModel):
    destination_id: int
    place_name: str
    city: str
    state: str
    category: str
    rating: float
    entrance_fee_inr: float
    match_score: float
    preference_match_pct: Optional[float] = None
    group_preference_score: Optional[float] = None
    strategy_used: Optional[str] = None
    member_satisfaction_scores: Optional[List[float]] = None
    seasonal_score: float
    explanation: str


class PersonalityProfileMatch(BaseModel):
    personality_type: str
    description: str
    match_percentage: float
    preferred_climate: str


class RecommendationResponse(BaseModel):
    assigned_personalities: List[PersonalityProfileMatch]
    recommendations: List[DestinationRecommendation]
