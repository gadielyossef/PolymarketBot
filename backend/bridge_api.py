from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import subprocess
import sys

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Memória de clientes ligados (o teu navegador)
connected_clients = []
bot_process = None

# =========================================================
# ROTA DO RADAR: Alimenta a nova tabela do Frontend
# =========================================================
@app.get("/markets")
async def get_markets():
    """Devolve os mercados ativos para a tabela do Front-end"""
    return {
        "status": "success",
        "markets": [
            {
                "token_id": "21742633143463906290569050155826241533067272736897614950488156847949938836455",
                "question": "Will the max temperature in London be 24°C?",
                "target_date": "2026-03-10",
                "current_price": 0.35,
                "prediction": 80.0,
                "status": "TRACKING"
            }
        ]
    }

# =========================================================
# CONTROLO DO MOTOR: Iniciar e Parar
# =========================================================
@app.post("/start")
async def start_bot():
    global bot_process
    if bot_process is None or bot_process.poll() is not None:
        # Inicia o motor HFT em background
        bot_process = subprocess.Popen([sys.executable, "backend/bot_autonomo.py"])
        return {"status": "success", "message": "Motor HFT (Nvidia Nemotron) Iniciado!"}
    return {"status": "error", "message": "O bot já está a correr."}

@app.post("/stop")
async def stop_bot():
    global bot_process
    if bot_process is not None:
        bot_process.terminate()
        bot_process = None
        # Avisa o frontend para colocar o botão verde (OFFLINE)
        for client in connected_clients:
            try:
                await client.send_json({"status": "OFFLINE"})
            except:
                pass
        return {"status": "success", "message": "Bot desligado."}
    return {"status": "error", "message": "Nenhum bot a correr."}

# =========================================================
# O TÚNEL DE ALTA VELOCIDADE (Bot -> React)
# =========================================================
@app.post("/push")
async def push_data(data: dict):
    """O bot_autonomo.py manda para aqui, e nós atiramos para o React em tempo real"""
    for client in connected_clients:
        try:
            await client.send_json(data)
        except WebSocketDisconnect:
            connected_clients.remove(client)
    return {"status": "ok"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        connected_clients.remove(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("bridge_api:app", host="127.0.0.1", port=8000, reload=True)