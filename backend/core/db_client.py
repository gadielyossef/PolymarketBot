import asyncpg
from backend.core.config import settings
import logging

logger = logging.getLogger("PolyHTF.Postgres")

class DBManager:
    def __init__(self):
        self.pool = None

    async def connect(self):
        try:
            # Cria um pool de conexões para evitar overhead a cada query
            self.pool = await asyncpg.create_pool(dsn=settings.database_url)
            logger.info("✅ PostgreSQL conectado com sucesso (Histórico e Aprendizado).")
        except Exception as e:
            logger.error(f"❌ Erro ao conectar no PostgreSQL: {e}")
            raise e

    async def execute(self, query: str, *args):
        if not self.pool:
            raise Exception("Pool de banco de dados não inicializado.")
        async with self.pool.acquire() as connection:
            return await connection.execute(query, *args)

    async def fetch(self, query: str, *args):
        if not self.pool:
            raise Exception("Pool de banco de dados não inicializado.")
        async with self.pool.acquire() as connection:
            return await connection.fetch(query, *args)

    async def close(self):
        if self.pool:
            await self.pool.close()

# Instância Singleton
pg_client = DBManager()