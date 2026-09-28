import os
from typing import List, Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Grant Agent"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./grant_agent.db")

    # Security & Auth
    SECRET_KEY: str = os.getenv("SECRET_KEY", "grant-agent-super-secret-key-change-in-production-123456789")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:8080",
        "*"
    ]

    # Google Cloud & AI Settings
    GCP_PROJECT_ID: Optional[str] = os.getenv("GCP_PROJECT_ID", "grant-agent-gcp")
    GCS_BUCKET_NAME: Optional[str] = os.getenv("GCS_BUCKET_NAME", "grant-agent-documents-vault")
    GCS_SCREENSHOTS_BUCKET: Optional[str] = os.getenv("GCS_SCREENSHOTS_BUCKET", "grant-agent-browser-screenshots")

    # Three Gemini API keys — tried in order (key 1 → key 2 → key 3)
    # If key 1 hits a rate limit or quota error, the system automatically
    # switches to key 2, then key 3, before giving up.
    GEMINI_API_KEY_1: Optional[str] = os.getenv("GEMINI_API_KEY_1", os.getenv("GEMINI_API_KEY", ""))
    GEMINI_API_KEY_2: Optional[str] = os.getenv("GEMINI_API_KEY_2", "")
    GEMINI_API_KEY_3: Optional[str] = os.getenv("GEMINI_API_KEY_3", "")

    # Backward-compat alias: GEMINI_API_KEY still works and maps to key 1
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY", "")

    # Resilient Gemini Tier Hierarchy & Retry Configuration
    PRIMARY_GEMINI_MODEL: str = os.getenv("PRIMARY_GEMINI_MODEL", os.getenv("GEMINI_MODEL", "gemini-2.0-flash"))
    FALLBACK_GEMINI_MODEL: str = os.getenv("FALLBACK_GEMINI_MODEL", os.getenv("GEMINI_FLASH_MODEL", "gemini-1.5-flash"))
    SECONDARY_FALLBACK_GEMINI_MODEL: str = os.getenv("SECONDARY_FALLBACK_GEMINI_MODEL", "gemini-1.5-flash-8b")
    GEMINI_MAX_RETRIES: int = int(os.getenv("GEMINI_MAX_RETRIES", "3"))
    GEMINI_RETRY_BASE_SECONDS: float = float(os.getenv("GEMINI_RETRY_BASE_SECONDS", "1.0"))
    GEMINI_REQUEST_TIMEOUT_SECONDS: float = float(os.getenv("GEMINI_REQUEST_TIMEOUT_SECONDS", "30.0"))

    @property
    def active_api_keys(self) -> List[str]:
        """Returns all non-empty API keys in priority order (key 1 → 2 → 3)."""
        candidates = [self.GEMINI_API_KEY_1, self.GEMINI_API_KEY_2, self.GEMINI_API_KEY_3]
        return [k for k in candidates if k and not k.startswith("YOUR_") and not k.startswith("ENTER_")]

    # Backward compatibility
    @property
    def GEMINI_MODEL(self) -> str:
        return self.PRIMARY_GEMINI_MODEL

    @property
    def GEMINI_FLASH_MODEL(self) -> str:
        return self.FALLBACK_GEMINI_MODEL

    # Storage directory (for local file fallback)
    STORAGE_DIR: str = os.getenv("STORAGE_DIR", "./vault_storage")
    SCREENSHOTS_DIR: str = os.getenv("SCREENSHOTS_DIR", "./browser_screenshots")

    # Worker & Automation
    WORKER_TIMEOUT_SECONDS: int = 900  # 15 minutes
    MOCK_PORTAL_URL: str = os.getenv("MOCK_PORTAL_URL", "http://127.0.0.1:8088")

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"


settings = Settings()
