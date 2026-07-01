import json
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

from ml_models.data_ingestion import load_all
from ml_models.data_transformation import transform_user_preferences
from ml_models.model_trainer import PersonalityClassifier, DestinationRecommender

# Initialize ML engine on startup
ml_data = load_all()
personality_classifier = PersonalityClassifier(ml_data["personalities"])
destination_recommender = DestinationRecommender(ml_data["destinations"], ml_data["seasons"])


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


# ML RECOMMENDATION ROUTES

@app.post("/recommendations/solo", response_model=schemas.RecommendationResponse)
def get_solo_recommendations(
    req: schemas.RecommendationRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Check if user provided preference input in body, or fall back to saved DB preferences
    slider_scores = req.slider_scores
    pref_climate = req.preferred_climate
    pref_activities = req.preferred_activities
    travel_style = req.travel_style
    max_budget = req.max_budget_inr

    if not slider_scores and not pref_climate and not pref_activities and not travel_style:
        # Load from DB if available
        user_prefs = get_user_preferences(db, current_user.id)
        if user_prefs:
            latest_pref = user_prefs[-1]
            pref_climate = latest_pref.preferred_climate
            pref_activities = json.loads(latest_pref.preferred_activities) if isinstance(latest_pref.preferred_activities, str) else latest_pref.preferred_activities
            travel_style = latest_pref.travel_style
            max_budget = max_budget or latest_pref.max_budget

    user_vec = transform_user_preferences(
        slider_scores=slider_scores,
        preferred_climate=pref_climate,
        preferred_activities=pref_activities,
        travel_style=travel_style
    )

    personalities = personality_classifier.classify(user_vec, top_k=2)
    recommendations = destination_recommender.recommend_for_user(
        user_vector=user_vec,
        travel_month=req.travel_month,
        max_budget_inr=max_budget,
        top_k=req.top_k
    )

    return {
        "assigned_personalities": personalities,
        "recommendations": recommendations
    }


@app.post("/recommendations/group/{trip_id}", response_model=schemas.RecommendationResponse)
def get_group_recommendations(
    trip_id: int,
    req: schemas.GroupRecommendationRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    trip = get_trip(db, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    if not trip.is_public and trip.creator_id != current_user.id:
        if not is_user_member(db, trip_id, current_user.id):
            raise HTTPException(status_code=403, detail="Not authorized for this group trip")

    # Fetch all members
    members = get_trip_members(db, trip_id)
    # Include creator if not already in members table
    member_user_ids = {m.user_id for m in members}
    member_user_ids.add(trip.creator_id)

    member_vectors = []
    for uid in member_user_ids:
        user_prefs = get_user_preferences(db, uid)
        if user_prefs:
            lp = user_prefs[-1]
            acts = lp.preferred_activities
            if isinstance(acts, str):
                import json
                try:
                    acts = json.loads(acts)
                except Exception:
                    acts = [acts]
            vec = transform_user_preferences(
                preferred_climate=lp.preferred_climate,
                preferred_activities=acts,
                travel_style=lp.travel_style
            )
        else:
            # Default balanced vector if user hasn't set preferences yet
            vec = [5.0, 5.0, 5.0, 5.0, 5.0]
        member_vectors.append(vec)

    # Calculate group average vector for personality profile assignment
    avg_vec = [sum(x) / len(x) for x in zip(*member_vectors)] if member_vectors else [5.0]*5
    personalities = personality_classifier.classify(avg_vec, top_k=2)

    travel_month = req.travel_month
    if not travel_month and trip.start_date:
        travel_month = trip.start_date.strftime("%b").lower()

    max_budget = req.max_budget_inr or trip.budget_per_person

    recommendations = destination_recommender.recommend_for_group(
        member_vectors=member_vectors,
        strategy=req.strategy,
        travel_month=travel_month,
        max_budget_inr=max_budget,
        top_k=req.top_k
    )

    return {
        "assigned_personalities": personalities,
        "recommendations": recommendations
    }


@app.get("/")
def root():
    return {"message": "WanderWise API is running successfully!"}
