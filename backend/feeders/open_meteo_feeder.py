import asyncio
import httpx
import json
import logging
from datetime import datetime, timezone
from backend.core.redis_client import redis_client

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("PolyHTF.MeteoFeeder")

TARGET_CITIES = {
    "NYC": {"lat": 40.7128, "lon": -74.0060},
    "LON": {"lat": 51.5074, "lon": -0.1278}
}

async def fetch_weather_with_fallback(client: httpx.AsyncClient, city: str, lat: float, lon: float):
    """Tenta buscar o clima na API primária, com fallback para rotas alternativas."""
    
    # 1ª Tentativa: Open-Meteo (Principal)
    url_primary = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m"
    
    try:
        response = await client.get(url_primary)
        response.raise_for_status()
        data = response.json()
        temp = data.get("current", {}).get("temperature_2m")
        logger.debug(f"[Primária - Open-Meteo] Sucesso para {city}")
        return temp
    except Exception as e:
        logger.warning(f"⚠️ Falha na API primária para {city} ({type(e).__name__}). Acionando Fallback...")

    # 2ª Tentativa: Fallback Público (wttr.in JSON format)
    # Exemplo: wttr.in não precisa de chaves, apenas do nome/coordenada
    url_fallback = f"https://wttr.in/{lat},{lon}?format=j1"
    
    try:
        response = await client.get(url_fallback)
        response.raise_for_status()
        data = response.json()
        temp = float(data['current_condition'][0]['temp_C'])
        logger.info(f"[Secundária - Wttr.in] Sucesso no fallback para {city}")
        return temp
    except Exception as e:
        logger.error(f"❌ Falha crítica: Todas as APIs de clima caíram para {city} - {e}")
        return None

async def fetch_weather_loop():
    """Loop infinito de alta disponibilidade"""
    timeout = httpx.Timeout(20.0, connect=30.0)
    
    # Pool limits e keepalive aumentam a estabilidade no reuso de conexões HTTP
    limits = httpx.Limits(max_keepalive_connections=5, max_connections=10)
    
    headers = {
        "User-Agent": "PolyHTF-Bot/1.0 (High Availability Feeder)"
    }
    
    async with httpx.AsyncClient(timeout=timeout, headers=headers, limits=limits) as client:
        while True:
            for city, coords in TARGET_CITIES.items():
                temp = await fetch_weather_with_fallback(client, city, coords['lat'], coords['lon'])
                
                if temp is not None:
                    # Injeta no Redis com o timestamp exato de AGORA.
                    # O motor de trade vai usar esse timestamp para saber se o dado é "fresco".
                    now_iso = datetime.now(timezone.utc).isoformat()
                    await redis_client.client.set(f"weather:{city}", json.dumps({
                        "temp": temp,
                        "timestamp": now_iso
                    }))
                    logger.info(f"🌤️ Clima atualizado no Redis para {city}: {temp}°C")
                else:
                    # Se falhar tudo, NÃO apagamos o Redis. Mantemos o último dado.
                    # A defasagem do timestamp vai acionar o Circuit Breaker do motor de trade.
                    logger.warning(f"Mantendo dado antigo no Redis para {city} devido a falha geral.")

            # Descansa 60 segundos antes do próximo poll
            await asyncio.sleep(60)

if __name__ == "__main__":
    try:
        asyncio.run(fetch_weather_loop())
    except KeyboardInterrupt:
        logger.info("Feeder interrompido manualmente.")