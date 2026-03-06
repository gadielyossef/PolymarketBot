import asyncio
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from backend.core.redis_client import redis_client

app = FastAPI(title="PolyHTF API Bridge", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class BotCredentials(BaseModel):
    walletKey: str
    rpcUrl: str = None # Opcional caso o frontend envie

@app.post("/start")
async def start_bot(creds: BotCredentials):
    # 1. Salva a chave da carteira no Redis em memória (mais seguro que .env)
    await redis_client.client.set("bot:wallet_key", creds.walletKey)
    
    # 2. Libera a trava para os bots começarem a operar
    await redis_client.client.set("ui:bot_status", "RUNNING")
    return {"status": "started"}

@app.post("/stop")
async def stop_bot():
    # 1. Trava os bots imediatamente
    await redis_client.client.set("ui:bot_status", "STOPPED")
    
    # 2. (Opcional) Apaga a chave da carteira da memória por segurança
    await redis_client.client.delete("bot:wallet_key")
    return {"status": "stopped"}

@app.get("/markets")
async def get_markets():
    # Retorna o formato inicial que o React espera
    return [
        {"id": "MKT-NYC", "question": "Highest temperature in NYC?", "currentPrice": 0.50, "status": "TRACKING"},
        {"id": "MKT-LON", "question": "Highest temperature in London?", "currentPrice": 0.50, "status": "TRACKING"}
    ]

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # 1. Lê os preços reais do Redis (O Websocket do feeder gravou isso)
            # Substitua pelos IDs reais dos seus tokens
            nyc_price_raw = await redis_client.client.get("price:ID_DO_TOKEN_NYC")
            lon_price_raw = await redis_client.client.get("price:ID_DO_TOKEN_LON")
            
            # 2. Lê os Logs do Fury no Redis para jogar no Terminal do Frontend
            latest_log_raw = await redis_client.client.lpop("ui:logs")
            
            # 3. Formata os dados EXATAMENTE como o useSystemData.ts do React espera
            update_data = {}
            
            if nyc_price_raw:
                update_data = {
                    "type": "MARKET_UPDATE",
                    "token_id": "MKT-NYC",
                    "price": float(nyc_price_raw)
                }
                await websocket.send_json(update_data)
                
            if latest_log_raw:
                log_data = json.loads(latest_log_raw)
                await websocket.send_json({"newLog": log_data})
                
            # Dispara os dados para o gráfico a cada 500ms
            await asyncio.sleep(0.5)
            
    except WebSocketDisconnect:
        print("Frontend Desconectado")