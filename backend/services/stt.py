import os
import tempfile
from typing import Optional

from faster_whisper import WhisperModel

MODEL_ID = os.getenv("STT_MODEL_ID", "cahya/faster-whisper-medium-id")
DEVICE = os.getenv("STT_DEVICE", "cpu")  # set to "cuda" if GPU available
COMPUTE_TYPE = os.getenv("STT_COMPUTE_TYPE", "int8")  # e.g., "float16" on GPU

# Load once at module import to avoid cold start per request
whisper_model = WhisperModel(
    MODEL_ID,
    device=DEVICE,
    compute_type=COMPUTE_TYPE,
)


def transcribe_bytes(audio_bytes: bytes, language: str = "id") -> str:
    """
    Transcribe audio bytes (wav/m4a/etc.) using faster-whisper.
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name
    try:
        segments, _ = whisper_model.transcribe(
            tmp_path,
            language=language,
            beam_size=5,
            vad_filter=True,
        )
        text = " ".join(seg.text for seg in segments).strip()
        return text
    finally:
        try:
            os.remove(tmp_path)
        except OSError:
            pass
