from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.db.session import get_db
from backend.schemas import UserRead, UserCreate
from backend import models

router = APIRouter(prefix="/db/user", tags=["user"])


def get_current_user(db: Session = Depends(get_db)) -> models.User:
    # Placeholder: replace with real JWT validation
    user = db.query(models.User).first()
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return user


@router.get("", response_model=UserRead)
def me(db: Session = Depends(get_db)):
    user = db.query(models.User).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("", response_model=UserRead)
def update(payload: UserCreate, db: Session = Depends(get_db)):
    user = db.query(models.User).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.name = payload.name
    user.job_field_preference = payload.job_field_preference
    user.experience_level = payload.experience_level
    db.commit()
    db.refresh(user)
    return user
