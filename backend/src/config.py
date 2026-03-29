from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

APP_NAME = "better-calendar-holidays"
REQUEST_TIMEOUT_SECONDS = 12.0
NAGER_BASE_URL = "https://date.nager.at/api/v3"
CALENDARIFIC_BASE_URL = "https://calendarific.com/api/v2"
CALENDARIFIC_MONTHLY_LIMIT = 500


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    cors_allow_origins: str = Field(
        default="http://localhost:4200,http://127.0.0.1:4200",
        alias="CORS_ALLOW_ORIGINS",
    )

    cache_ttl_days: int = Field(default=30, alias="CACHE_TTL_DAYS")
    redis_url: str | None = Field(default=None, alias="REDIS_URL")
    redis_key_prefix: str = Field(default="better-calendar-holidays", alias="REDIS_KEY_PREFIX")

    calendarific_api_key: str | None = Field(default=None, alias="CALENDARIFIC_API_KEY")


settings = Settings()
