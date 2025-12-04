import requests
from src.core.config import settings




def enviar_mensagem(number: str, text: str):
# Ajuste conforme a API do Evolution que você usa
url = f"{settings.evolution_api_url}/message/sendText?apikey={settings.evolution_apikey}"
payload = {"number": number, "text": text}
try:
requests.post(url, json=payload, timeout=5)
except Exception as e:
print("Erro ao enviar mensagem:", e)