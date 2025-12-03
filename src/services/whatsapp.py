import requests
import json
from src.core.config import settings

def enviar_mensagem(numero_destino: str, texto: str):
    """
    Envia uma mensagem de texto via Evolution API.
    """
    url = f"{settings.evolution_url}/message/sendText/{settings.instance_name}"
    
    headers = {
        "apikey": settings.evolution_apikey,
        "Content-Type": "application/json"
    }
    
    payload = {
        "number": numero_destino,
        "text": texto,
        "delay": 1200, # Delay simulando digitação humana (1.2s)
        "linkPreview": True
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code != 201:
            print(f"⚠️ Erro ao enviar Zap: {response.text}")
    except Exception as e:
        print(f"❌ Falha na conexão com WhatsApp: {e}")