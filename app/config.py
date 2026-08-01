from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./finvestor.db"
    jwt_secret: str = "dev_secret_change_me"
    jwt_expire_minutes: int = 1440
    groq_api_key: str = ""
    groq_model: str = "llama-3.1-8b-instant"
    llamaparse_api_key: str = ""
    deepgram_api_key: str = ""
    elevenlabs_api_key: str = ""
    elevenlabs_voice_id: str = "21m00Tcm4TlvDq8ikWAM"
    frontend_origin: str = "http://localhost:3000"

    class Config:
        env_file = ".env"


settings = Settings()
