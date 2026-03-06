import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

# Localiza a raiz do projeto e carrega o .env explicitamente
BASE_DIR = Path(__file__).resolve().parent.parent.parent
env_path = os.path.join(BASE_DIR, ".env")
load_dotenv(dotenv_path=env_path)

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

    # Configuração do Pydantic para ler do ambiente do sistema
    model_config = SettingsConfigDict(extra="ignore")

settings = Settings()