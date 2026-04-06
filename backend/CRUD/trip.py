from sqlalchemy.orm import Session
from backend.models import Trip
from backend.schemas import TripCreate


def create_trip(db: Session, trip: TripCreate, user_id: int):
    db_trip = Trip(
        destination=trip.destination,
        start_date=trip.start_date,
        end_date=trip.end_date,
        budget_per_person=trip.budget_per_person,
        is_public=trip.is_public,
        creator_id=user_id
    )

    db.add(db_trip)
    db.commit()
    db.refresh(db_trip)
    return db_trip



def get_trip(db: Session, trip_id: int):
    return db.query(Trip).filter(Trip.id == trip_id).first()


def get_all_trips(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Trip).offset(skip).limit(limit).all()


def delete_trip(db: Session, trip_id: int):
    trip = get_trip(db, trip_id)
    if trip:
        db.delete(trip)
        db.commit()
    return trip
