from langchain_openai import ChatOpenAI
from src.core.config import settings




def create_llm_with_tools(ferramentas, model_name="gpt-4o", temperature=0):
llm = ChatOpenAI(model=model_name, temperature=temperature, api_key=settings.openai_apikey)
return llm.bind_tools(ferramentas)