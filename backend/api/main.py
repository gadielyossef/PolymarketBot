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
    return [] # O Frontend será populado ativamente pelo Websocket

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # 1. EMPURRA A LISTA DE MERCADOS VIVOS PARA A TELA
            keys = await redis_client.client.keys("price:*")
            active_markets = []
            
            # Pega até 8 mercados que o robô achou para exibir
            for key in keys[:8]:
                key_str = key if isinstance(key, str) else key.decode()
                token_id_long = key_str.split(":")[1]
                short_id = token_id_long[:6]
                
                price_raw = await redis_client.client.get(key)
                price = float(price_raw) if price_raw else 0.50
                
                active_markets.append({
                    "id": short_id,
                    "question": f"Polymarket Live Event #{short_id}",
                    "targetDate": "2026",
                    "currentPrice": price,
                    "ourPrediction": 50.0, # Pode ser dinâmico depois
                    "status": "TRACKING"
                })

            if active_markets:
                # O React já entende "liveMarkets" e vai renderizar as linhas instantaneamente
                await websocket.send_json({"liveMarkets": active_markets})

            # 2. ATUALIZA A BANCA (Agora vai pegar os $10.00!)
            saldo_raw = await redis_client.client.get("fury:saldo_simulado")
            if saldo_raw:
                saldo = float(saldo_raw)
                await websocket.send_json({
                    "bank": {
                        "balance": saldo,
                        "dailyPL": saldo - 10.00,
                        "kellyExposure": 10.0,
                        "equityCurve": []
                    }
                })

            # 3. ATUALIZA O GRÁFICO DE CLIMA
            shuri_raw = await redis_client.client.get("agent:shuri:scenario")
            if shuri_raw:
                shuri_str = shuri_raw if isinstance(shuri_raw, str) else shuri_raw.decode()
                shuri_data = json.loads(shuri_str)
                temp = shuri_data.get("current_temp", 0)
                weather_update = [{
                    "time": "Agora",
                    "ECMWF": temp,
                    "GFS": temp + 0.5,
                    "ICON": temp - 0.3
                }]
                await websocket.send_json({"weatherData": weather_update})

            # 4. ATUALIZA OS LOGS DE EXECUÇÃO
            latest_log_raw = await redis_client.client.lpop("ui:logs")
            if latest_log_raw:
                log_str = latest_log_raw if isinstance(latest_log_raw, str) else latest_log_raw.decode()
                await websocket.send_json({"newLog": json.loads(log_str)})
                
            await asyncio.sleep(0.5)
            
    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"Erro no Websocket: {e}")