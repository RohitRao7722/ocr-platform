import json
from typing import List, Union

from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str

    # Redis
    REDIS_URL: str

    # Application
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    APP_NAME: str = "OCR System"
    APP_VERSION: str = "1.0.0"

    # Upload Settings
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 10485760  # 10MB in bytes
    ALLOWED_EXTENSIONS: List[str] = ["jpg", "jpeg", "png", "pdf", "tiff", "bmp"]

    # OCR Engine Settings
    DEFAULT_OCR_ENGINE: str = "paddleocr"
    OCR_LANGUAGE: str = "en"
    OCR_CONFIDENCE_THRESHOLD: float = 0.7

    # Tesseract Settings
    TESSERACT_ENABLED: bool = True
    TESSERACT_CMD: str = "tesseract"  # Will use system PATH

    # Celery Settings
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str

    # Security
    SECRET_KEY: str

    @field_validator("ALLOWED_EXTENSIONS", mode="before")
    @classmethod
    def parse_allowed_extensions(cls, value: Union[str, List[str]]) -> List[str]:
        if isinstance(value, list):
            return value

        if isinstance(value, str):
            try:
                parsed = json.loads(value)
                if isinstance(parsed, list):
                    return [str(item) for item in parsed]
            except json.JSONDecodeError:
                return [item.strip() for item in value.split(",") if item.strip()]

        raise ValueError("Invalid ALLOWED_EXTENSIONS format")

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
