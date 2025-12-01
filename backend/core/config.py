from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "SiapKerja API"
    api_prefix: str = "/api"
    database_url: str = Field(..., env="DATABASE_URL")
    firebase_bucket: str = Field("", env="FIREBASE_BUCKET")
    gemini_api_key: str = Field("", env="GEMINI_API_KEY")
    gemini_model: str = Field("gemini-2.0-flash", env="GEMINI_MODEL")
    request_timeout_sec: int = 30
    ai_enabled: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
