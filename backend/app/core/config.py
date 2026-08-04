from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    supabase_url: str
    supabase_anon_key: str
    supabase_service_role_key: str
    supabase_jwt_secret: str = ""

    groq_api_key: str
    groq_reasoning_model: str = "llama-3.3-70b-versatile"
    groq_fast_model: str = "llama-3.1-8b-instant"

    environment: str = "development"
    cors_origins: str = "http://localhost:3000"

    # Paritok — hosted GPU compression endpoint, called directly per-request
    # (no local proxy/sidecar process needed). See app/services/paritok_client.py.
    paritok_enabled: bool = True
    paritok_api_key: str = ""

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
