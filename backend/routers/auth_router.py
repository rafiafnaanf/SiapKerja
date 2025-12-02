from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.db.session import get_db
from backend.schemas import UserCreate, LoginPayload, TokenResponse, AuthResponse, UserRead
from backend.services import user as user_service
from werkzeug.security import check_password_hash
import datetime
import jwt
from backend.core.config import settings
from backend import models

router = APIRouter(prefix="/db/auth", tags=["auth"])


def create_auth_response(user: models.User) -> AuthResponse:
    expires_in = 60 * 60 * 2
    payload = {
        "sub": user.id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=expires_in),
    }
    token = jwt.encode(payload, settings.database_url, algorithm="HS256")
    return AuthResponse(
        access_token=token,
        expires_in=expires_in,
        refresh_token=None,
        user=UserRead.model_validate(user),
    )


@router.post("/register", response_model=AuthResponse)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    existing = user_service.get_user_by_email(db, payload.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = user_service.create_user(db, payload)
    return create_auth_response(user)


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginPayload, db: Session = Depends(get_db)):
    user = user_service.get_user_by_email(db, payload.email)
    if not user or not check_password_hash(user.password_hash, payload.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return create_auth_response(user)
