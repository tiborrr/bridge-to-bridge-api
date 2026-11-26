from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Bridge to Bridge API"

    # Database
    APP_POSTGRES_HOST: str = "localhost"
    APP_POSTGRES_PORT: str = "5432"
    APP_POSTGRES_USER: str = "bridge_user"
    APP_POSTGRES_PASSWORD: str = "bridge_password"
    APP_POSTGRES_DB: str = "bridge_app"

    @property
    def DATABASE_URL(self) -> str:  # noqa: N802 - matches the env-style names
        return (
            f"postgresql+psycopg://{self.APP_POSTGRES_USER}:{self.APP_POSTGRES_PASSWORD}"
            f"@{self.APP_POSTGRES_HOST}:{self.APP_POSTGRES_PORT}/{self.APP_POSTGRES_DB}"
        )

    # Keycloak
    KEYCLOAK_SERVER_URL: str = "http://localhost:8080"
    KEYCLOAK_REALM: str = "bridge-realm"
    KEYCLOAK_CLIENT_ID: str = "bridge-client"
    # Service account (client credentials) in KEYCLOAK_REALM used to invite users.
    KEYCLOAK_ADMIN_CLIENT_ID: str = "bridge-api-admin"
    KEYCLOAK_ADMIN_CLIENT_SECRET: str = ""
    # Local development fallback only: master admin login, used when no client
    # secret is set.
    KEYCLOAK_ADMIN_USERNAME: str = "admin"
    KEYCLOAK_ADMIN_PASSWORD: str = "admin"

    # API
    CORS_ORIGINS: str = "*"

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
