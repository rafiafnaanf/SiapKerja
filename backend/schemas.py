from datetime import datetime
from typing import List, Optional, Any
from pydantic import BaseModel, EmailStr


# User schemas
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    job_field_preference: Optional[str] = None
    experience_level: Optional[str] = None


class LoginPayload(BaseModel):
    email: EmailStr
    password: str
    device_id: Optional[str] = None


class UserRead(BaseModel):
    id: str
    name: str
    email: EmailStr
    job_field_preference: Optional[str] = None
    experience_level: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    user: UserRead


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    refresh_token: Optional[str] = None


class UserUpdate(BaseModel):
    name: Optional[str] = None
    job_field_preference: Optional[str] = None
    experience_level: Optional[str] = None


class AuthResponse(BaseModel):
    user: UserRead
    access_token: str
    refresh_token: str | None = None
    token_type: str = "bearer"
    expires_in: int


# AI payloads
class CvReviewRequest(BaseModel):
    job_field: str
    target_role: Optional[str] = None
    language: str = "id"
    cv_file_url: Optional[str] = None
    cv_file_base64: Optional[str] = None


class CvReviewResponse(BaseModel):
    review_id: str
    job_field: str
    target_role: Optional[str] = None
    language: str
    overall_score: int
    rating_label: str
    summary: str
    strengths: List[str]
    weaknesses: List[str]
    recommendations: List[str]
    suggested_career_paths: Optional[List[str]] = None


class InterviewQuestionsRequest(BaseModel):
    job_field: str
    target_role: Optional[str] = None
    difficulty: str
    language: str = "id"
    num_questions: int = 5


class InterviewQuestionPayload(BaseModel):
    id: str
    text: str
    topic: Optional[str] = None
    suggested_duration_sec: Optional[int] = None


class InterviewQuestionsResponse(BaseModel):
    session_template_id: str
    job_field: str
    target_role: Optional[str]
    difficulty: str
    language: str
    questions: List[InterviewQuestionPayload]


class InterviewFeedbackQuestion(BaseModel):
    id: Optional[str] = None
    text: str


class InterviewFeedbackAnswer(BaseModel):
    text: str


class InterviewFeedbackRequest(BaseModel):
    job_field: str
    target_role: Optional[str] = None
    difficulty: str
    language: str = "id"
    question: InterviewFeedbackQuestion
    answer: InterviewFeedbackAnswer


class InterviewFeedbackResponse(BaseModel):
    question_id: Optional[str]
    job_field: str
    difficulty: str
    language: str
    answer_score: int
    strengths: List[str]
    improvements: List[str]
    ideal_answer: str
    tips: Optional[List[str]] = None


class CareerRoadmapRequest(BaseModel):
    job_field: str
    target_role: str
    current_level: str = "ENTRY"
    known_skills: List[str] = []
    language: str = "id"


class RoadmapResource(BaseModel):
    title: str
    url: str
    type: str


class RoadmapStage(BaseModel):
    id: str
    title: str
    description: str
    estimated_duration_months: int
    skills_to_learn: List[str]
    resources: List[RoadmapResource]


class CareerRoadmapResponse(BaseModel):
    roadmap_id: str
    job_field: str
    target_role: str
    current_level: str
    stages: List[RoadmapStage]


# History schemas
class HistoryItem(BaseModel):
    id: str
    type: str
    data: Any
    created_at: datetime

    class Config:
        orm_mode = True
