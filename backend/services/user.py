from sqlalchemy.orm import Session
from backend import models
from backend.schemas import UserCreate
from werkzeug.security import generate_password_hash


def create_user(db: Session, payload: UserCreate) -> models.User:
    user = models.User(
        name=payload.name,
        email=payload.email,
        password_hash=generate_password_hash(payload.password),
        job_field_preference=payload.job_field_preference,
        experience_level=payload.experience_level,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_email(db: Session, email: str) -> models.User | None:
    return db.query(models.User).filter(models.User.email == email).first()
