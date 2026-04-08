from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from backend import models, schemas
from backend.database import engine, get_db

from backend.CRUD.user import create_user, get_user_by_email
from backend.CRUD.trip import create_trip, get_trip, get_all_trips
from backend.CRUD.trip_member import add_member_to_trip, remove_member_from_trip, get_trip_members, is_user_member
from backend.CRUD.preference import create_preference, get_user_preferences

from backend.security import verify_password, create_access_token
from backend.auth import get_current_user


models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="WanderWise API",
    description="Backend API for Smart Trip Recommendation System",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# AUTH ROUTES

@app.post("/signup", response_model=schemas.UserResponse)
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    db_user = create_user(db, user)
    return db_user


@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(),
          db: Session = Depends(get_db)):

    user = get_user_by_email(db, form_data.username)
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=30)
    )
    return {"access_token": access_token, "token_type": "bearer"}


# TRIP ROUTES (Fixed to tie trips with user ID)

@app.post("/trips", response_model=schemas.TripResponse)
def create_new_trip(
    trip: schemas.TripCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return create_trip(db, trip, user_id=current_user.id)



@app.get("/trips", response_model=list[schemas.TripResponse])
def list_trips(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Show only user's trips for now
    return db.query(models.Trip).filter(models.Trip.creator_id == current_user.id).all()


@app.get("/trips/{trip_id}", response_model=schemas.TripResponse)
def get_trip_by_id(
    trip_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    trip = get_trip(db, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    if not trip.is_public and trip.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    return trip


@app.put("/trips/{trip_id}", response_model=schemas.TripResponse)
def update_trip(
    trip_id: int,
    updated_trip: schemas.TripCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    trip = get_trip(db, trip_id)

    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    if trip.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    for key, value in updated_trip.model_dump().items():
        setattr(trip, key, value)

    db.commit()
    db.refresh(trip)
    return trip


@app.delete("/trips/{trip_id}")
def delete_trip_by_id(
    trip_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    trip = get_trip(db, trip_id)

    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    if trip.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    db.delete(trip)
    db.commit()
    return {"message": "Trip deleted successfully"}


# PREFERENCE ROUTES

@app.post("/preferences", response_model=schemas.PreferenceResponse)
def create_user_preference(
    preference: schemas.PreferenceCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Force user_id to always be the authenticated user
    # Ignore whatever user_id the client might have sent in the body
    preference.user_id = current_user.id
    return create_preference(db, preference)


@app.get("/preferences", response_model=list[schemas.PreferenceResponse])
def get_preferences(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return get_user_preferences(db, current_user.id)


# TRIP MEMBER ROUTES

@app.post("/trips/{trip_id}/members", response_model=schemas.TripMemberResponse)
def add_member(
    trip_id: int,
    member: schemas.TripMemberCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Only the trip creator can add members
    trip = get_trip(db, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    if trip.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the trip creator can add members")

    # Prevent adding the same user twice
    if is_user_member(db, trip_id, member.user_id):
        raise HTTPException(status_code=400, detail="User is already a member of this trip")

    return add_member_to_trip(db, trip_id, member.user_id)


@app.delete("/trips/{trip_id}/members/{user_id}")
def remove_member(
    trip_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Only the trip creator can remove members
    trip = get_trip(db, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    if trip.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the trip creator can remove members")

    # Can't remove someone who isn't a member
    if not is_user_member(db, trip_id, user_id):
        raise HTTPException(status_code=404, detail="User is not a member of this trip")

    remove_member_from_trip(db, trip_id, user_id)
    return {"message": "Member removed successfully"}


@app.get("/trips/{trip_id}/members", response_model=list[schemas.TripMemberResponse])
def list_members(
    trip_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    trip = get_trip(db, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    # Only creator or members can see the member list
    if not trip.is_public and trip.creator_id != current_user.id:
        if not is_user_member(db, trip_id, current_user.id):
            raise HTTPException(status_code=403, detail="Not authorized")

    return get_trip_members(db, trip_id)


@app.get("/")
def root():
    return {"message": "WanderWise API is running successfully!"}
