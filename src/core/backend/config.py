"""Application configuration loaded from environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration from environment variables."""

    # Database
    DATABASE_URL: str

    # Authentication (EdDSA with JWKS verification)
    FRONTEND_URL: str = "http://localhost:3000"  # Better Auth JWKS endpoint location

    # Application
    DEBUG: bool = False

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
