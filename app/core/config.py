"""Settings from environment variables or `.env`. No secrets live in code."""

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "sqlite:///./data/synsara.db"
    content_file: Path = Field(
        default=ROOT / "content" / "synsara-2019.yaml", alias="SYNSARA_CONTENT"
    )
    upload_dir: Path = ROOT / "data" / "uploads"
    max_upload_mb: int = 5

    # Signs the admin session cookie. ALWAYS override outside local development.
    secret_key: str = Field(default="dev-only-insecure-secret-change-me", min_length=16)
    admin_username: str = "admin"
    # Default only suits local development; the app logs a warning when it's used.
    admin_password: str = "synsara-admin"
    cookie_secure: bool = False

    # Lets a past edition (like 2019) keep accepting demo registrations.
    registration_open: bool = True


@lru_cache
def get_settings() -> Settings:
    return Settings()
