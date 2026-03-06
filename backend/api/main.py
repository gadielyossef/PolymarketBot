from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.core.redis_client import redis_client
import json

app = FastAPI(title="PolyHTF API", version="1.0.0")

# Permite que o Frontend (React/Vite) consuma a API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/dashboard/live")
async def get_live_dashboard():
    """Retorna o estado instantâneo do mercado e do clima lendo 100% em memória"""
    
    # Busca todas as chaves relevantes no Redis
    weather_keys = await redis_client.client.keys("weather:*")
    price_keys = await redis_client.client.keys("price:*")
    
    dashboard_data = {
        "weather": {},
        "prices": {}
    }
    
    # Mapeia clima
    for key in weather_keys:
        city = key.split(":")[1]
        data = await redis_client.client.get(key)
        dashboard_data["weather"][city] = json.loads(data) if data else None
        
    # Mapeia preços da Polymarket
    for key in price_keys:
        asset_id = key.split(":")[1]
        price = await redis_client.client.get(key)
        dashboard_data["prices"][asset_id] = float(price) if price else None

    return dashboard_data