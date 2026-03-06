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
    rpcUrl: str = None

@app.post("/start")
async def start_bot(creds: BotCredentials):
    await redis_client.client.set("bot:wallet_key", creds.walletKey)
    await redis_client.client.set("ui:bot_status", "RUNNING")
    return {"status": "started"}

@app.post("/stop")
async def stop_bot():
    await redis_client.client.set("ui:bot_status", "STOPPED")
    await redis_client.client.delete("bot:wallet_key")
    return {"status": "stopped"}

@app.get("/markets")
async def get_markets():
    return [
        {
            "id": "589656", 
            "question": "Highest temperature in NYC?", 
            "targetDate": "2026-03-05",
            "currentPrice": 0.50, 
            "ourPrediction": 65.2,
            "status": "TRACKING"
        },
        {
            "id": "513824", 
            "question": "Highest temperature in London?", 
            "targetDate": "2026-03-05",
            "currentPrice": 0.50, 
            "ourPrediction": 45.1,
            "status": "TRACKING"
        }
    ]

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # 1. Pega TODOS os preços gravados no Redis
            keys = await redis_client.client.keys("price:*")
            
            for key in keys:
                # CORREÇÃO AQUI: Como "key" já é string, removemos o .decode()
                # Se ainda for bytes (dependendo do ambiente), o str() resolve com segurança
                key_str = key if isinstance(key, str) else key.decode()
                token_id_long = key_str.split(":")[1]
                
                # 2. É o mercado de NYC?
                if token_id_long.startswith("589656"):
                    price_raw = await redis_client.client.get(key)
                    if price_raw is not None:
                        await websocket.send_json({
                            "type": "MARKET_UPDATE",
                            "token_id": "589656", 
                            "price": float(price_raw)
                        })
                        
                # 3. É o mercado de London?
                elif token_id_long.startswith("513824"):
                    price_raw = await redis_client.client.get(key)
                    if price_raw is not None:
                        await websocket.send_json({
                            "type": "MARKET_UPDATE",
                            "token_id": "513824", 
                            "price": float(price_raw)
                        })

            # 4. Envia os logs do Fury para o terminal "Execution"
            latest_log_raw = await redis_client.client.lpop("ui:logs")
            if latest_log_raw:
                # O log também pode vir como bytes ou string, tratamos com segurança:
                log_str = latest_log_raw if isinstance(latest_log_raw, str) else latest_log_raw.decode()
                log_data = json.loads(log_str)
                await websocket.send_json({"newLog": log_data})
                
            # Atualiza o gráfico a cada meio segundo
            await asyncio.sleep(0.5)
            
    except WebSocketDisconnect:
        print("Frontend Desconectado")
    except Exception as e:
        print(f"Erro no Websocket: {e}")