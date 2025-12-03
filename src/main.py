from fastapi import FastAPI, Request
from langchain_core.messages import HumanMessage
import uvicorn

# Importando o cérebro e os serviços
from src.cerebro_livinho.agent import cerebro_livinho
from src.services.whatsapp import enviar_mensagem
from src.cerebro_livinho.knowledge_base import carregar_e_indexar_manuais

app = FastAPI(title="Jarvis Livo API")

# Ao iniciar, o servidor já verifica se o cérebro está carregado
@app.on_event("startup")
async def startup_event():
    print("🧠 Inicializando o Jarvis...")
    # Descomente a linha abaixo se quiser re-indexar os PDFs toda vez que reiniciar
    # carregar_e_indexar_manuais()
    print("✅ Jarvis pronto para operar.")

@app.get("/")
def health_check():
    return {"status": "Jarvis está online! 🚀"}

@app.post("/webhook")
async def receive_whatsapp_message(request: Request):
    try:
        body = await request.json()
        event_type = body.get("event")

        # Filtra apenas mensagens novas de texto
        if event_type == "messages.upsert":
            data = body.get("data", {})
            message_content = data.get("message", {})
            key = data.get("key", {})
            
            sender = key.get("remoteJid")
            from_me = key.get("fromMe", False)

            # Evita que o Jarvis fale com ele mesmo (Loop Infinito)
            if from_me:
                return {"status": "IGNORADO"}

            # Extração segura do texto
            user_text = ""
            if "conversation" in message_content:
                user_text = message_content["conversation"]
            elif "extendedTextMessage" in message_content:
                user_text = message_content["extendedTextMessage"].get("text")
            
            if not user_text:
                return {"status": "SEM_TEXTO"}

            print(f"📩 Morador ({sender}) diz: {user_text}")

            # --- AQUI A MÁGICA ACONTECE ---
            
            # 1. Envia a pergunta para o Cérebro (Agent)
            # O Jarvis vai pensar, consultar manuais e decidir a resposta
            resultado = cerebro_livinho.invoke({"messages": [HumanMessage(content=user_text)]})
            
            # 2. Pega a última mensagem (A resposta final da IA)
            resposta_ia = resultado['messages'][-1].content
            
            # 3. Envia a resposta para o WhatsApp do morador
            enviar_mensagem(sender, resposta_ia)
            
            print(f"🤖 Jarvis respondeu: {resposta_ia}")

        return {"status": "OK"}

    except Exception as e:
        print(f"❌ Erro crítico: {e}")
        return {"status": "ERRO"}

if __name__ == "__main__":
    # Roda o servidor acessível na rede
    uvicorn.run("src.main:app", host="0.0.0.0", port=5000, reload=True)