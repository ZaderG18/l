from pydantic import BaseSettings


class Settings(BaseSettings):
openai_apikey: str = ""
evolution_api_url: str = "http://localhost:8081"
evolution_apikey: str = ""


class Config:
env_file = ".env"


settings = Settings()