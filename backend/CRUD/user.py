from sqlalchemy.orm import Session
from backend.models import User
from backend.schemas import UserCreate
from backend.security import hash_password, verify_password


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def create_user(db: Session, user: UserCreate):
    hashed_pwd = hash_password(user.password)

    db_user = User(
        email=user.email,
        password=hashed_pwd
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def verify_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    
    if not user:
        return False

    if not verify_password(password, user.password):
        return False
    
    return user
