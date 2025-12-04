from typing import TypedDict, Annotated, List
import operator


from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import SystemMessage, BaseMessage


from src.cerebro_livinho.agents.prompts import SYSTEM_PROMPT
from src.cerebro_livinho.tools.knowledge import consultar_manual_livo
from src.cerebro_livinho.tools.ti_tools import reportar_erro_ti
from src.cerebro_livinho.models.llm import create_llm_with_tools


# --- STATE ---
class AgentState(TypedDict):
messages: Annotated[List[BaseMessage], operator.add]


# --- TOOLS ---
ferramentas = [consultar_manual_livo, reportar_erro_ti]


# --- LLM COM FERRAMENTAS ---
llm_com_ferramentas = create_llm_with_tools(ferramentas)


# --- CALL MODEL ---
def call_model(state: AgentState):
msgs = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
response = llm_com_ferramentas.invoke(msgs)
return {"messages": [response]}


# --- DECISÃO ---
def should_continue(state: AgentState):
last = state["messages"][-1]
if hasattr(last, "tool_calls") and last.tool_calls:
return "tools"
return END


# --- GRAPH ---
workflow = StateGraph(AgentState)
workflow.add_node("agent", call_model)
workflow.add_node("tools", ToolNode(ferramentas))
workflow.set_entry_point("agent")
workflow.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
workflow.add_edge("tools", "agent")
jarvis_brain = workflow.compile()