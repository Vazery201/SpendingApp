from functools import lru_cache
from typing import Literal

from pydantic import Field, AliasChoices
from pydantic_settings import BaseSettings, SettingsConfigDict


def plaid_base_url(env: str) -> str:
    env = env.lower()
    if env == "sandbox":
        return "https://sandbox.plaid.com"
    if env == "development":
        return "https://development.plaid.com"
    if env == "production":
        return "https://production.plaid.com"
    # default to sandbox if unknown
    return "https://sandbox.plaid.com"


class Settings(BaseSettings):
    # Plaid
    PLAID_ENV: Literal["sandbox", "development", "production"] = "sandbox"
    PLAID_CLIENT_ID: str = ""
    PLAID_SECRET: str = ""

    # App
    APP_NAME: str = "SpendingBot"

    # Database URL: accept DB_URL or db_url from .env
    DB_URL: str = Field(
        default="sqlite+aiosqlite:///./spendingbot.db",
        validation_alias=AliasChoices("DB_URL", "db_url"),
    )

    # Encryption key for Fernet: accept ENCRYPTION_KEY or encryption_key
    ENCRYPTION_KEY: str = Field(
        default="",
        validation_alias=AliasChoices("ENCRYPTION_KEY", "encryption_key"),
    )

    # Accept unknown keys without failing (handy while experimenting)
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
