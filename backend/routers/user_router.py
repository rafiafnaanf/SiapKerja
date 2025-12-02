from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.db.session import get_db
from backend.schemas import UserRead, UserCreate, UserUpdate, UserResponse
from backend import models

router = APIRouter(prefix="/db/user", tags=["user"])


def get_current_user(db: Session = Depends(get_db)) -> models.User:
    # Placeholder: replace with real JWT validation
    user = db.query(models.User).first()
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return user


@router.get("", response_model=UserResponse)
def me(db: Session = Depends(get_db)):
    user = db.query(models.User).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"user": user}


@router.put("", response_model=UserResponse)
def update(payload: UserUpdate, db: Session = Depends(get_db)):
    user = db.query(models.User).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if payload.name is not None:
        user.name = payload.name
    if payload.job_field_preference is not None:
        user.job_field_preference = payload.job_field_preference
    if payload.experience_level is not None:
        user.experience_level = payload.experience_level
    db.commit()
    db.refresh(user)
    return {"user": user}
