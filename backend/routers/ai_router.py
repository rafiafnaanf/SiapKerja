from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from backend.schemas import (
    CvReviewRequest,
    CvReviewResponse,
    InterviewQuestionsRequest,
    InterviewQuestionsResponse,
    InterviewFeedbackRequest,
    InterviewFeedbackResponse,
    CareerRoadmapRequest,
    CareerRoadmapResponse,
)
from backend.services.ai import AIService

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/cv-review", response_model=CvReviewResponse)
async def cv_review(
    req: CvReviewRequest,
    ai_service: AIService = Depends(lambda: AIService()),
):
    try:
        return await ai_service.cv_review(req)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/interview-questions", response_model=InterviewQuestionsResponse)
async def interview_questions(
    req: InterviewQuestionsRequest,
    ai_service: AIService = Depends(lambda: AIService()),
):
    try:
        return await ai_service.interview_questions(req)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/interview-feedback", response_model=InterviewFeedbackResponse)
async def interview_feedback(
    req: InterviewFeedbackRequest,
    ai_service: AIService = Depends(lambda: AIService()),
):
    try:
        return await ai_service.interview_feedback(req)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/career-roadmap", response_model=CareerRoadmapResponse)
async def career_roadmap(
    req: CareerRoadmapRequest,
    ai_service: AIService = Depends(lambda: AIService()),
):
    try:
        return await ai_service.career_pathway(req)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
