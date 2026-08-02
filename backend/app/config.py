from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://finvestor:finvestor@localhost:5432/finvestor"
    jwt_secret: str = "dev_only_secret_change_me"
    jwt_expire_minutes: int = 1440
    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"
    elevenlabs_api_key: str = ""
    elevenlabs_voice_id: str = ""
    cors_origin: str = "http://localhost:3000"

    class Config:
        env_file = ".env"

settings = Settings()
