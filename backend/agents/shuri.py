import asyncio
import httpx
import json
import logging
from datetime import datetime, timezone
from backend.core.redis_client import redis_client
from backend.core.config import settings

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("PolyHTF.Shuri")

async def shuri_loop():
    """Roda a cada 5 minutos. Analisa o clima no Redis e atualiza o cenário."""
    # URL sem barras extras ou espaços
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {settings.openrouter_api_key.strip()}",
        "Content-Type": "application/json",
        # OpenRouter exige estes headers para identificar o app em alguns casos
        "HTTP-Referer": "https://github.com/gadielyossef/PolymarketBot", 
        "X-Title": "PolymarketBot_HFT"
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        while True:
            try:
                nyc_data_raw = await redis_client.client.get("weather:NYC")
                
                if not nyc_data_raw:
                    logger.warning("Shuri aguardando dados climáticos no Redis...")
                    await asyncio.sleep(10)
                    continue

                nyc_data = json.loads(nyc_data_raw)
                temp_nyc = nyc_data.get("temp")

                # Prompt otimizado para economia de tokens
                prompt = f"Analise técnica: Temperatura NYC {temp_nyc}°C. Projete tendência climática curta."

                payload = {
                    # Modelo Llama 3.1 8B (Free) - Alta disponibilidade no OpenRouter
                    "model": "liquid/lfm-2.5-1.2b-instruct:free", 
                    "messages": [{"role": "user", "content": prompt}]
                }

                # 3. Consulta o LLM
                response = await client.post(url, headers=headers, json=payload)
                
                if response.status_code != 200:
                    logger.error(f"❌ Erro API {response.status_code}: {response.text}")
                    await asyncio.sleep(20)
                    continue

                analysis = response.json()["choices"][0]["message"]["content"]

                # 4. Salva no Redis
                await redis_client.client.set("agent:shuri:scenario", json.dumps({
                    "analysis": analysis,
                    "target_city": "NYC",
                    "current_temp": temp_nyc,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }))
                
                logger.info(f"🧠 Shuri atualizou o cenário: {analysis[:50]}...")

            except Exception as e:
                logger.error(f"❌ Erro Crítico: {e}")

            await asyncio.sleep(300)

if __name__ == "__main__":
    asyncio.run(shuri_loop())