from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import Optional, List
import secrets


class Settings(BaseSettings):
    # App
    APP_NAME: str = "AI Hospital Camera"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    DEMO_MODE: bool = False  # Production mode: Demo disabled
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"
    
    # Database
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "ai_hospital_camera"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    
    # Redis (optional)
    REDIS_URL: Optional[str] = None
    
    # Evidence storage
    EVIDENCE_STORAGE_PATH: str = "./evidence_storage"
    EVIDENCE_MAX_SIZE_GB: float = 50.0
    
    # AI Engine
    AI_ENABLED: bool = True
    AI_BACKEND: str = "cpu"  # cpu | cuda | mock
    AI_MODEL_PATH: str = "./models"
    AI_MAX_CONCURRENT_STREAMS: int = 10
    AI_INFERENCE_FPS: float = 2.0
    
    # Video Gateway
    MEDIAMTX_API_URL: str = "http://localhost:9997"
    MEDIAMTX_RTSP_PORT: int = 8554
    
    # Security
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    RATE_LIMIT_PER_MINUTE: int = 100
    
    # Privacy & Anonymization
    PRIVACY_FACE_BLUR: bool = True

    # External Notifications (Telegram & Webhook)
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    TELEGRAM_CHAT_ID: Optional[str] = None
    WEBHOOK_URL: Optional[str] = None
    NOTIFICATION_MIN_SEVERITY: str = "high"  # low | medium | high | critical

    # Camera network allowlist (CIDR notation)
    CAMERA_ALLOWED_SUBNETS: List[str] = ["192.168.0.0/16", "10.0.0.0/8", "172.16.0.0/12"]
    
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    @property
    def ASYNC_DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


settings = Settings()
