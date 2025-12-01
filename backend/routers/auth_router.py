from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.db.session import get_db
from backend.schemas import UserCreate, LoginPayload, TokenResponse
from backend.services import user as user_service
from werkzeug.security import check_password_hash
import datetime
import jwt
from backend.core.config import settings

router = APIRouter(prefix="/db/auth", tags=["auth"])


def create_token(user_id: str) -> TokenResponse:
    expires_in = 60 * 60 * 2
    payload = {
        "sub": user_id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=expires_in),
    }
    token = jwt.encode(payload, settings.database_url, algorithm="HS256")
    return TokenResponse(access_token=token, expires_in=expires_in)


@router.post("/register", response_model=TokenResponse)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    existing = user_service.get_user_by_email(db, payload.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = user_service.create_user(db, payload)
    return create_token(user.id)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginPayload, db: Session = Depends(get_db)):
    user = user_service.get_user_by_email(db, payload.email)
    if not user or not check_password_hash(user.password_hash, payload.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return create_token(user.id)
