from fastapi import FastAPI, Request
import uvicorn


from src.cerebro_livinho.agents.livinho_agent import livinho_brain
from src.services.whatsapp import enviar_mensagem


app = FastAPI(title="Jarvis Livo API")


@app.on_event("startup")
async def startup_event():
print("🧠 Inicializando o Jarvis...")
print("✅ Jarvis pronto para operar.")


@app.get("/")
def health_check():
return {"status": "Jarvis está online! 🚀"}


@app.post("/webhook")
async def receive_whatsapp_message(request: Request):
body = await request.json()
event_type = body.get("event")


if event_type == "messages.upsert":
data = body.get("data", {})
message_content = data.get("message", {})
key = data.get("key", {})


sender = key.get("remoteJid")
from_me = key.get("fromMe", False)


if from_me:
return {"status": "IGNORADO"}


user_text = (
message_content.get("conversation")
or message_content.get("extendedTextMessage", {}).get("text")
or ""
)


if not user_text:
return {"status": "SEM_TEXTO"}


print(f"📩 Morador ({sender}) diz: {user_text}")


# Exemplo de chamada ao brain (ajuste conforme sua API do langgraph)
resultado = jarvis_brain.invoke({"messages": [{"type": "human", "content": user_text}]})


# Extrai resposta (ajuste conforme formato de retorno)
resposta_ia = None
if resultado and resultado.get("messages"):
resposta_ia = resultado["messages"][-1].get("content")


if resposta_ia:
enviar_mensagem(sender, resposta_ia)
print(f"🤖 Jarvis respondeu: {resposta_ia}")


return {"status": "OK"}


if __name__ == "__main__":
uvicorn.run("src.main:app", host="0.0.0.0", port=5000, reload=True)