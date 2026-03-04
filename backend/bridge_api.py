import os
import subprocess
import signal
from typing import List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="Polymarket HFT Bridge")

# Permite que o React (Frontend) converse com o Python (Backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- ESTADO GLOBAL DO SERVIDOR ---
bot_process = None
WALLET_PRIVATE_KEY = None

# Modelo de dados para receber a chave da carteira do Frontend
class WalletAuth(BaseModel):
    token: str

# --- GESTOR DE WEBSOCKET (O TÚNEL) ---
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()

# =========================================================
# ROTAS DE CONTROLE (FRONTEND -> BACKEND)
# =========================================================

@app.post("/sync-wallet")
async def sync_wallet(auth: WalletAuth):
    global WALLET_PRIVATE_KEY
    # Guarda o token apenas na memória volátil (RAM), não salva no HD!
    WALLET_PRIVATE_KEY = auth.token
    return {"status": "success", "message": "Carteira sincronizada com sucesso na memória."}

@app.post("/start")
async def start_bot():
    global bot_process, WALLET_PRIVATE_KEY
    
    if bot_process is not None and bot_process.poll() is None:
        return {"status": "error", "message": "O bot já está rodando!"}
        
    if not WALLET_PRIVATE_KEY:
         return {"status": "error", "message": "Sincronize o Token da Carteira primeiro!"}

    # Prepara o ambiente virtual injetando a chave privada de forma segura
    bot_env = os.environ.copy()
    bot_env["PRIVATE_KEY"] = WALLET_PRIVATE_KEY
    
    try:
        # Inicia o bot_autonomo.py em segundo plano!
        bot_process = subprocess.Popen(
            ["python", "bot_autonomo.py"], 
            env=bot_env,
            shell=False
        )
        return {"status": "success", "message": "Motor HFT iniciado em MODO SOMBRA!"}
    except Exception as e:
        return {"status": "error", "message": f"Falha ao iniciar: {str(e)}"}

@app.post("/stop")
async def stop_bot():
    global bot_process
    
    if bot_process is None or bot_process.poll() is not None:
        return {"status": "warning", "message": "O bot já está parado."}
        
    try:
        # Mata o processo do bot de forma forçada (Compatível com Windows e Linux)
        if os.name == 'nt': 
            subprocess.call(['taskkill', '/F', '/T', '/PID', str(bot_process.pid)])
        else:
            os.kill(bot_process.pid, signal.SIGTERM)
            
        bot_process = None
        
        # Avisa o frontend que o bot parou
        await manager.broadcast({"status": "OFFLINE", "message": "Bot parado pelo usuário."})
        return {"status": "success", "message": "Motor HFT desligado."}
    except Exception as e:
        return {"status": "error", "message": f"Erro ao parar o bot: {str(e)}"}

# =========================================================
# ROTAS DE DADOS DE ALTA FREQUÊNCIA (BOT -> FRONTEND)
# =========================================================

# O Frontend (React) liga-se aqui e fica à escuta
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Mantém a conexão viva
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# O Bot (Python) atira os dados para aqui, e o servidor espalha para o React
@app.post("/push")
async def push_data(data: dict):
    await manager.broadcast(data)
    return {"status": "Dados transmitidos à velocidade da luz!"}

if __name__ == "__main__":
    print("🚀 Bridge API rodando na porta 8000...")
    print("📡 Aguardando o Frontend conectar...")
    uvicorn.run(app, host="0.0.0.0", port=8000)