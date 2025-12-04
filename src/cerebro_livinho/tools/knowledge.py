from langchain.tools import tool
from src.cerebro_livinho.knowledge_base import buscar_conhecimento


@tool
def consultar_manual_livo(duvida: str):
"""
Busca respostas na base de conhecimento (RAG).
"""
return buscar_conhecimento(duvida)