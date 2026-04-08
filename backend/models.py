from sqlalchemy import Column, Integer, String, Boolean, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)

    # Relationship: one user can create many trips
    trips = relationship("Trip", back_populates="creator")
    preferences = relationship("Preference", back_populates="user")


class Trip(Base):
    __tablename__ = "trips"

    id = Column(Integer, primary_key=True, index=True)
    destination = Column(String, index=True, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    budget_per_person = Column(Float, nullable=True)
    is_public = Column(Boolean, default=True)  # For inclusive/exclusive groups

    # Foreign key → trip owner
    creator_id = Column(Integer, ForeignKey("users.id"))
    creator = relationship("User", back_populates="trips")

    # Trip members (many-to-many)
    members = relationship("TripMember", back_populates="trip")

class TripMember(Base):
    __tablename__ = "trip_members"

    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id"))
    user_id = Column(Integer, ForeignKey("users.id"))

    # Relationships
    trip = relationship("Trip", back_populates="members")


class Preference(Base):
    __tablename__ = "preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # This is where we store data for ML recommendations
    preferred_climate = Column(String, nullable=True)  # "cold / beach / mountains"
    preferred_activities = Column(String, nullable=True)  # stored as JSON string e.g. '["hiking","beach"]'
    max_budget = Column(Float, nullable=True)
    travel_style = Column(String, nullable=True)  # "adventure / luxury / chill"

    user = relationship("User", back_populates="preferences")
