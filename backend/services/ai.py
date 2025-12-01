import json
import uuid
import httpx
from backend.core.config import settings
from backend.schemas import (
    CvReviewRequest,
    CvReviewResponse,
    InterviewQuestionsRequest,
    InterviewQuestionsResponse,
    InterviewQuestionPayload,
    InterviewFeedbackRequest,
    InterviewFeedbackResponse,
    CareerRoadmapRequest,
    CareerRoadmapResponse,
    RoadmapStage,
    RoadmapResource,
)


class AIService:
    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = api_key or settings.gemini_api_key
        self.model = model or settings.gemini_model
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        # System prompts
        self.system_cv = (
            "Kamu adalah SiapKerja-CV-Reviewer, asisten AI untuk review CV di konteks Indonesia. "
            "Tugas: (1) Analisis CV terhadap pekerjaan target. "
            "(2) Beri feedback spesifik dan actionable. "
            "Aturan: jangan mengarang pengalaman/skill baru, gunakan info user saja, gunakan Bahasa Indonesia profesional, "
            "fokus relevansi, pencapaian terukur, struktur CV, kata kunci. "
            "Jika user minta format khusus, ikuti. Jika tidak, hanya keluarkan JSON yang diminta di user prompt."
        )
        self.system_interview = (
            "Kamu adalah SiapKerja-Interview-Coach. "
            "Buat pertanyaan interview relevan (behavioral STAR, teknis, motivation) sesuai role/level. "
            "Jika memberi feedback jawaban: nilai struktur, relevansi, kejelasan, kedalaman contoh, profesionalisme. "
            "Gunakan Bahasa Indonesia profesional. Jangan tambahkan teks di luar format yang diminta."
        )
        self.system_career = (
            "Kamu adalah SiapKerja-Career-Roadmap, career coach AI. "
            "Susun roadmap realistis (Indonesia), gunakan info user saja, tanpa janji berlebihan. "
            "Berikan langkah konkret per horizon waktu, Bahasa Indonesia jelas."
        )

    async def _call_gemini(
        self,
        prompt: str,
        system_prompt: str | None = None,
        response_schema: dict | None = None
    ) -> str:
        if not self.api_key:
            raise RuntimeError("Gemini API key is missing")
        url = f"{self.base_url}/models/{self.model}:generateContent"
        async with httpx.AsyncClient(timeout=settings.request_timeout_sec) as client:
            payload = {
                "contents": [{"parts": [{"text": prompt}]}]
            }
            if system_prompt:
                payload["system_instruction"] = {"parts": [{"text": system_prompt}]}
            if response_schema:
                payload["generationConfig"] = {
                    "response_mime_type": "application/json",
                    "response_schema": response_schema
                }
            resp = await client.post(
                url,
                params={"key": self.api_key},
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()
            return (
                data.get("candidates", [{}])[0]
                .get("content", {})
                .get("parts", [{}])[0]
                .get("text", "")
            )

    async def cv_review(self, req: CvReviewRequest) -> CvReviewResponse:
        prompt = f"""
Anda adalah asisten karir. Analisis CV untuk bidang {req.job_field} dan peran {req.target_role}.
Berikan output JSON valid (tanpa teks lain) dengan schema:
{{
 "overall_score": number 0-100,
 "rating_label": string,
 "summary": string,
 "strengths": [string],
 "weaknesses": [string],
 "recommendations": [string]
}}
        """.strip()
        raw = await self._call_gemini(
            prompt,
            system_prompt=self.system_cv,
            response_schema={
                "type": "object",
                "properties": {
                    "overall_score": {"type": "number"},
                    "rating_label": {"type": "string"},
                    "summary": {"type": "string"},
                    "strengths": {"type": "array", "items": {"type": "string"}},
                    "weaknesses": {"type": "array", "items": {"type": "string"}},
                    "recommendations": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["overall_score", "rating_label", "summary"]
            }
        )
        try:
            parsed = json.loads(raw)
        except Exception:
            parsed = {}
        return CvReviewResponse(
            review_id=str(uuid.uuid4()),
            job_field=req.job_field,
            target_role=req.target_role,
            language=req.language,
            overall_score=int(parsed.get("overall_score", 0)),
            rating_label=parsed.get("rating_label", "Tidak Tersedia"),
            summary=parsed.get("summary", raw[:400]),
            strengths=parsed.get("strengths", []),
            weaknesses=parsed.get("weaknesses", []),
            recommendations=parsed.get("recommendations", []),
            suggested_career_paths=parsed.get("suggested_career_paths"),
        )

    async def interview_questions(self, req: InterviewQuestionsRequest) -> InterviewQuestionsResponse:
        prompt = f"""
Buat {req.num_questions} pertanyaan interview untuk bidang {req.job_field} level {req.difficulty}.
Jawab dalam JSON list:
[{{"id": "q1", "text": "...", "topic": "Technical", "suggested_duration_sec": 90}}, ...]
        """.strip()
        raw = await self._call_gemini(
            prompt,
            system_prompt=self.system_interview,
            response_schema={
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "text": {"type": "string"},
                        "topic": {"type": "string"},
                        "suggested_duration_sec": {"type": "number"}
                    },
                    "required": ["id", "text"]
                }
            }
        )
        parsed = None
        try:
            parsed = json.loads(raw)
        except Exception:
            cleaned = self._extract_json(raw)
            try:
                parsed = json.loads(cleaned)
            except Exception:
                raise ValueError(f"LLM tidak mengembalikan JSON pertanyaan yang valid: {raw[:200]}")
        if parsed is None:
            raise ValueError("LLM tidak mengembalikan JSON pertanyaan yang valid (parsed None)")
        questions = [
            InterviewQuestionPayload(
                id=item.get("id", f"q{i}"),
                text=item.get("text", ""),
                topic=item.get("topic"),
                suggested_duration_sec=item.get("suggested_duration_sec"),
            )
            for i, item in enumerate(parsed, start=1)
        ]
        if not questions:
            raise ValueError("Pertanyaan kosong dari LLM")
        return InterviewQuestionsResponse(
            session_template_id=str(uuid.uuid4()),
            job_field=req.job_field,
            target_role=req.target_role,
            difficulty=req.difficulty,
            language=req.language,
            questions=questions,
        )

    async def interview_feedback(self, req: InterviewFeedbackRequest) -> InterviewFeedbackResponse:
        prompt = f"""
Nilai jawaban interview berikut.
Pertanyaan: {req.question.text}
Jawaban: {req.answer.text}
Berikan JSON:
{{
 "answer_score": number 0-100,
 "strengths": [string],
 "improvements": [string],
 "ideal_answer": string,
 "tips": [string]
}}
        """.strip()
        raw = await self._call_gemini(
            prompt,
            system_prompt=self.system_interview,
            response_schema={
                "type": "object",
                "properties": {
                    "answer_score": {"type": "number"},
                    "strengths": {"type": "array", "items": {"type": "string"}},
                    "improvements": {"type": "array", "items": {"type": "string"}},
                    "ideal_answer": {"type": "string"},
                    "tips": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["answer_score", "strengths", "improvements"]
            }
        )
        cleaned = self._extract_json(raw)
        try:
            parsed = json.loads(cleaned)
        except Exception:
            parsed = {}
        return InterviewFeedbackResponse(
            question_id=req.question.id,
            job_field=req.job_field,
            difficulty=req.difficulty,
            language=req.language,
            answer_score=int(parsed.get("answer_score", 0)),
            strengths=parsed.get("strengths", []),
            improvements=parsed.get("improvements", []),
            ideal_answer=parsed.get("ideal_answer", cleaned),
            tips=parsed.get("tips", []),
        )

    async def career_pathway(self, req: CareerRoadmapRequest) -> CareerRoadmapResponse:
        prompt = f"""
Buat roadmap karir untuk peran {req.target_role} di bidang {req.job_field}, level {req.current_level}.
Jawab JSON:
{{
 "stages": [
   {{"id":"s1","title":"...","description":"...","estimated_duration_months":2,"skills_to_learn":["..."],"resources":[{{"title":"...","url":"...","type":"COURSE"}}]}}
 ]
}}
        """.strip()
        raw = await self._call_gemini(
            prompt,
            system_prompt=self.system_career,
            response_schema={
                "type": "object",
                "properties": {
                    "stages": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "string"},
                                "title": {"type": "string"},
                                "description": {"type": "string"},
                                "estimated_duration_months": {"type": "number"},
                                "skills_to_learn": {"type": "array", "items": {"type": "string"}},
                                "resources": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "title": {"type": "string"},
                                            "url": {"type": "string"},
                                            "type": {"type": "string"}
                                        },
                                        "required": ["title", "url", "type"]
                                    }
                                }
                            },
                            "required": ["id", "title", "description", "estimated_duration_months"]
                        }
                    }
                },
                "required": ["stages"]
            }
        )
        try:
            parsed = json.loads(raw)
        except Exception:
            parsed = {}
        stages_payload = parsed.get("stages", [])
        stages = [
            RoadmapStage(
                id=item.get("id", f"s{i}"),
                title=item.get("title", ""),
                description=item.get("description", ""),
                estimated_duration_months=int(item.get("estimated_duration_months", 1)),
                skills_to_learn=item.get("skills_to_learn", []),
                resources=[
                    RoadmapResource(
                        title=r.get("title", ""),
                        url=r.get("url", ""),
                        type=r.get("type", "LINK"),
                    )
                    for r in item.get("resources", [])
                ],
            )
            for i, item in enumerate(stages_payload, start=1)
        ]
        if not stages:
            stages = [
                RoadmapStage(
                    id="s1",
                    title="Fondasi",
                    description="Pelajari dasar algoritma, struktur data, dan pemrograman.",
                    estimated_duration_months=2,
                    skills_to_learn=["Algoritma", "Struktur Data"],
                    resources=[],
                )
            ]
        return CareerRoadmapResponse(
            roadmap_id=str(uuid.uuid4()),
            job_field=req.job_field,
            target_role=req.target_role,
            current_level=req.current_level,
            stages=stages,
        )

    @staticmethod
    def _extract_json(text: str) -> str:
        """
        Remove markdown fences and try to keep only the JSON portion.
        """
        stripped = text.strip()
        # remove ```json ... ``` fences
        if stripped.startswith("```"):
            stripped = stripped.strip("`")
        # try to slice between first { and last }
        start = stripped.find("{")
        end = stripped.rfind("}")
        if start != -1 and end != -1 and end > start:
            return stripped[start:end + 1]
        return stripped
