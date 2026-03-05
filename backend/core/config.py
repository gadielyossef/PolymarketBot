from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # IA API
    gemini_api_key: str
    openrouter_api_key: str
    app_url: str
    
    # DB & Cache
    redis_url: str = "redis://localhost:6379/0"
    database_url: str
    
    # Polymarket
    polymarket_wallet_pk: str
    polymarket_api_key: str
    polymarket_api_secret: str
    polymarket_passphrase: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()