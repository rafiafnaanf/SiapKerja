import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, JSON, ForeignKey, Integer
from sqlalchemy.orm import relationship
from backend.db.session import Base


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    job_field_preference = Column(String, nullable=True)
    experience_level = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    histories = relationship("History", back_populates="user")


class History(Base):
    __tablename__ = "histories"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=True)  # nullable to support guest uploads if synced
    type = Column(String, nullable=False)  # cv_review, interview_session, career_roadmap
    data = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="histories")
