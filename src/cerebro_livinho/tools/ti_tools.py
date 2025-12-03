from langchain.tools import tool
from src.services.whatsapp import enviar_mensagem
from src.core.config import settings

@tool
def reportar_erro_ti(descricao_erro: str, usuario_afetado: str):
    """
    Use esta ferramenta APENAS quando o usuário relatar explicitamente um erro técnico, 
    bug, travamento ou falha no aplicativo Livo.
    NÃO use para dúvidas gerais.
    """
    msg_formatada = f"""
    🚨 *JARVIS REPORT - ERRO TÉCNICO* 🚨
    
    👤 *Usuário:* {usuario_afetado}
    🛠️ *Relato:* {descricao_erro}
    
    _Notificação automática do Assistente Virtual._
    """
    
    # Envia para o Grupo de TI definido no .env
    # Se não tiver grupo configurado, ele avisa no log
    if settings.ti_group_id:
        enviar_mensagem(settings.ti_group_id, msg_formatada)
        return "Erro reportado com sucesso para a equipe de engenharia."
    else:
        print(f"⚠️ TI_GROUP_ID não configurado. Erro não enviado: {descricao_erro}")
        return "Erro registrado localmente (Grupo TI não configurado)."