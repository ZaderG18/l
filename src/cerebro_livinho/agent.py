# src/brain/agent.py
from typing import TypedDict, Annotated, List
import operator

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, BaseMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain.tools import tool

# --- IMPORTAÇÃO DAS FERRAMENTAS ---
# Importamos a função que lê os PDFs/Excel
from src.cerebro_livinho.knowledge_base import buscar_conhecimento
# Importamos a função que manda msg no grupo da TI
from src.cerebro_livinho.tools.ti_tools import reportar_erro_ti 
from src.core.config import settings

# --- 1. DEFININDO AS HABILIDADES (TOOLS) ---

@tool
def consultar_manual_livo(duvida: str):
    """
    Use esta ferramenta para responder QUALQUER dúvida sobre como usar o aplicativo Livo, 
    regras do condomínio, reservas, entregas, votações, pânico, etc.
    Ela busca na base de conhecimento (Manuais PDF e Scripts de Suporte).
    """
    # Chama a função do RAG que criamos no outro arquivo
    return buscar_conhecimento(duvida)

# Lista de ferramentas que o Jarvis tem na mochila
ferramentas = [consultar_manual_livo, reportar_erro_ti]

# --- 2. A PERSONALIDADE E REGRAS (CÉREBRO) ---

SYSTEM_PROMPT = """
Você é o **Livinho**, o assistente virtual oficial da **Livo**. 
Sua missão é dar suporte técnico e operacional sobre o aplicativo Livo para moradores e síndicos.

### 🛡️ SUAS REGRAS DE OURO (SEGURANÇA MÁXIMA):
1. **ZERO AÇÕES ADMINISTRATIVAS:** Você **NUNCA** deve desbloquear cadastros, liberar acessos, enviar boletos bancários ou documentos pessoais/financeiros.
   - Se o usuário pedir isso, sua resposta DEVE ser: "Por questões de segurança e privacidade, eu não tenho permissão para realizar desbloqueios ou acessar dados financeiros. Por favor, entre em contato diretamente com a administração do seu condomínio."
2. **NÃO INVENTE:** Se a informação não estiver na sua base de conhecimento (tools), diga que não sabe e sugira falar com o suporte humano.
3. **TOM DE VOZ:** Seja prestativo, moderno, ágil e use emojis moderados (🚀, 📦, ✅). Evite textos longos.
4. **SUPORTE TÉCNICO:** Se o usuário relatar um erro no app (bug, travamento), use a ferramenta `reportar_erro_ti`.

### 🧠 COMO USAR SUAS FERRAMENTAS:
- Sempre que o usuário fizer uma pergunta sobre o app ou regras, use `consultar_manual_livo`.
- Se o usuário relatar um problema técnico ("App fechou", "Deu erro 500"), use `reportar_erro_ti`.
"""

# --- 3. CONFIGURAÇÃO DO LANGGRAPH ---

# Define o estado da memória do agente (lista de mensagens)
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]

# Inicializa a IA (GPT-4o é recomendado para seguir regras complexas)
llm = ChatOpenAI(model="gpt-4o", api_key=settings.openai_apikey, temperature=0)

# Ensina as ferramentas para a IA
llm_com_ferramentas = llm.bind_tools(ferramentas)

# Nó 1: O Agente Pensa
def call_model(state: AgentState):
    messages = state['messages']
    # Garante que as regras (System Prompt) estejam sempre no contexto
    if not isinstance(messages[0], SystemMessage):
        messages.insert(0, SystemMessage(content=SYSTEM_PROMPT))
    
    response = llm_com_ferramentas.invoke(messages)
    return {"messages": [response]}

# Lógica de Decisão: Chamar Ferramenta ou Responder?
def should_continue(state: AgentState):
    messages = state['messages']
    last_message = messages[-1]
    
    # Se a IA decidiu chamar uma tool (ex: buscar no manual)
    if last_message.tool_calls:
        return "tools"
    # Se ela já tem a resposta final
    return END

# --- 4. MONTAGEM DO GRAFO ---

workflow = StateGraph(AgentState)

# Adiciona os nós (etapas)
workflow.add_node("agent", call_model)
workflow.add_node("tools", ToolNode(ferramentas))

# Define o ponto de partida
workflow.set_entry_point("agent")

# Define as conexões
workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        "tools": "tools",
        END: END
    }
)

# Depois de usar uma ferramenta, volta pro agente formular a resposta
workflow.add_edge("tools", "agent")

# Compila o cérebro final
jarvis_brain = workflow.compile()