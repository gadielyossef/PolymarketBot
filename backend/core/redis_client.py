import redis.asyncio as redis
from backend.core.config import settings
import logging

logger = logging.getLogger("PolyHTF.Redis")

class RedisManager:
    def __init__(self):
        self.pool = redis.ConnectionPool.from_url(
            settings.redis_url, 
            decode_responses=True # Retorna strings diretamente em vez de bytes
        )
        self.client = redis.Redis.from_pool(self.pool)

    async def ping(self):
        try:
            pong = await self.client.ping()
            if pong:
                logger.info("✅ Redis conectado com sucesso. Latência em ms garantida.")
            return pong
        except Exception as e:
            logger.error(f"❌ Erro crítico ao conectar no Redis: {e}")
            raise e

    async def close(self):
        await self.client.aclose()
        await self.pool.disconnect()

# Instância Singleton
redis_client = RedisManager()