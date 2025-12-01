from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.db.session import get_db
from backend.schemas import HistoryItem
from backend.services import history as history_service
from backend import models
import jwt
from backend.core.config import settings

router = APIRouter(prefix="/db/history", tags=["history"])


def get_current_user(db: Session = Depends(get_db), authorization: str = "") -> models.User:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")
    token = authorization.replace("Bearer ", "")
    try:
        payload = jwt.decode(token, settings.database_url, algorithms=["HS256"])
        user_id = payload.get("sub")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return user


@router.get("", response_model=list[HistoryItem])
def list_history(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    return history_service.list_history(db, user.id)


@router.post("", response_model=HistoryItem)
def add_history(
    payload: HistoryItem,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    hist = history_service.add_history(db, user.id, payload.type, payload.data)
    return hist
