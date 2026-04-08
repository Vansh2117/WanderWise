from sqlalchemy.orm import Session
from backend.models import Preference
from backend.schemas import PreferenceCreate
import json


def create_preference(db: Session, pref: PreferenceCreate):
    activities = pref.preferred_activities
    activities_str = json.dumps(activities) if activities is not None else None
    db_pref = Preference(
        user_id=pref.user_id,
        preferred_climate=pref.preferred_climate,
        preferred_activities=activities_str,
        max_budget=pref.max_budget,
        travel_style=pref.travel_style
    )
    
    db.add(db_pref)
    db.commit()
    db.refresh(db_pref)
    return db_pref


def get_user_preferences(db: Session, user_id: int):
    return db.query(Preference).filter(Preference.user_id == user_id).all()


def update_preference(db: Session, pref_id: int, updated_data: dict):
    pref = db.query(Preference).filter(Preference.id == pref_id).first()
    
    if not pref:
        return None
    
    for key, value in updated_data.items():
        setattr(pref, key, value)

    db.commit()
    db.refresh(pref)
    return pref
