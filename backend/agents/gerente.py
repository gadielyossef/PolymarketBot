import asyncio
import json
import logging
from datetime import datetime, timezone
from backend.core.redis_client import redis_client

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("PolyHTF.Gerente")

async def gerente_loop():
    """Roda a cada 1 minuto. Define as diretrizes financeiras de operação."""
    while True:
        try:
            # Na Fase 4 e 5 conectaremos na carteira real da Polymarket. 
            # Por enquanto, ele define o hard limit de segurança para o motor HFT.
            max_trade_size = 50.0  # Max de $50 por operação
            daily_loss_limit = 100.0 # Se perder $100 no dia, ele trava o bot
            status = "AUTHORIZED" # Pode ser "HALTED" se o risco for excedido

            now_iso = datetime.now(timezone.utc).isoformat()
            regras = {
                "max_trade_size_usd": max_trade_size,
                "daily_loss_limit_usd": daily_loss_limit,
                "trading_status": status,
                "timestamp": now_iso
            }

            # Grava as regras no barramento HFT
            await redis_client.client.set("agent:gerente:risk_rules", json.dumps(regras))
            logger.info(f"💼 Gerente de Banca atualizou as regras de risco. Status: {status} | Max Lote: ${max_trade_size}")

        except Exception as e:
            logger.error(f"❌ Erro no Gerente de Banca: {e}")

        # Atualiza o risco a cada 60 segundos
        await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(gerente_loop())