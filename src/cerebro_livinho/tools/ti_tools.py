from langchain.tools import tool
from src.core.config import settings
import requests


@tool
def reportar_erro_ti(payload: str):
"""Envia um alerta ao grupo de TI via Evolution API (ou outro mecanismo)."""
try:
url = f"{settings.evolution_api_url}/message/sendText?apikey={settings.evolution_apikey}"
data = {"number": settings.evolution_apikey, "text": payload}
# ajustar payload conforme a API do Evolution
resp = requests.post(url, json=data, timeout=5)
return f"Enviado ao TI (status {resp.status_code})"
except Exception as e:
return f"Falha ao reportar TI: {e}"