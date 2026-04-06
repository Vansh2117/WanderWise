from sqlalchemy.orm import Session
from backend.models import TripMember, Trip, User

# Add a user to a trip (join)
def add_member_to_trip(db: Session, trip_id: int, user_id: int):
    # Prevent duplicate membership
    existing = (
        db.query(TripMember)
        .filter(TripMember.trip_id == trip_id, TripMember.user_id == user_id)
        .first()
    )
    if existing:
        return existing

    # Optional: check that trip and user exist
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    user = db.query(User).filter(User.id == user_id).first()
    if not trip or not user:
        return None

    member = TripMember(trip_id=trip_id, user_id=user_id)
    db.add(member)
    db.commit()
    db.refresh(member)
    return member


# Remove a user from a trip (leave)
def remove_member_from_trip(db: Session, trip_id: int, user_id: int):
    member = (
        db.query(TripMember)
        .filter(TripMember.trip_id == trip_id, TripMember.user_id == user_id)
        .first()
    )
    if not member:
        return None
    db.delete(member)
    db.commit()
    return member


# Get all members (TripMember rows) for a trip
def get_trip_members(db: Session, trip_id: int):
    return db.query(TripMember).filter(TripMember.trip_id == trip_id).all()


# Check if a user is already a member of a trip (bool)
def is_user_member(db: Session, trip_id: int, user_id: int) -> bool:
    return (
        db.query(TripMember)
        .filter(TripMember.trip_id == trip_id, TripMember.user_id == user_id)
        .first()
        is not None
    )
