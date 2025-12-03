import os
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()

class Settings:
    openai_apikey = os.getenv("OPENAI_API_KEY")
    evolution_url = os.getenv("EVOLUTION_API_URL")
    evolution_apikey = os.getenv("EVOLUTION_API_KEY")
    instance_name = os.getenv("INSTANCE_NAME")
    ti_group_id = os.getenv("TI_GROUP_ID")

settings = Settings()