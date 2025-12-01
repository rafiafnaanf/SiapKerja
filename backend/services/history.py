from sqlalchemy.orm import Session
from backend import models
from backend.schemas import HistoryItem
from typing import List


def add_history(db: Session, user_id: str | None, type_: str, data: dict) -> models.History:
    history = models.History(user_id=user_id, type=type_, data=data)
    db.add(history)
    db.commit()
    db.refresh(history)
    return history


def list_history(db: Session, user_id: str) -> List[models.History]:
    return (
        db.query(models.History)
        .filter(models.History.user_id == user_id)
        .order_by(models.History.created_at.desc())
        .all()
    )
