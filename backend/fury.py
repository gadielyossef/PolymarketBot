import asyncio
import json
import logging
from datetime import datetime, timezone
from backend.core.redis_client import redis_client
from backend.core.config import settings

# SDK Oficial da Polymarket
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs
from py_clob_client.constants import POLYGON

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("PolyHTF.Fury")

class FuryEngine:
    def __init__(self):
        # -------------------------------------------------------
        # CONFIGURAÇÃO DE SEGURANÇA
        self.MODO_REAL = False    # Altere para True para gastar dinheiro real
        self.VALOR_TRADE = 10.0   # Valor fixo para seus testes
        # -------------------------------------------------------
        
        logger.info(f"⚔️ Fury Inicializado | MODO_REAL: {self.MODO_REAL} | VALOR: ${self.VALOR_TRADE}")
        
        try:
            self.client = ClobClient(
                host="https://clob.polymarket.com",
                key=settings.polymarket_wallet_pk,
                chain_id=POLYGON,
            )
            self.client.set_api_creds(self.client.create_or_derive_api_creds())
            logger.info("✅ Conexão Criptográfica com Polymarket estabelecida.")
        except Exception as e:
            logger.warning(f"⚠️ SDK operando com limitações (Verifique Private Key): {e}")

    async def run_loop(self):
        logger.info(f"🚀 Fury monitorando... (Simulando: {not self.MODO_REAL})")
        
        while True:
            try:
                # 1. CAPTURA DE DADOS
                risk_raw = await redis_client.client.get("agent:gerente:risk_rules")
                shuri_raw = await redis_client.client.get("agent:shuri:scenario")
                
                if not risk_raw or not shuri_raw:
                    await asyncio.sleep(0.5)
                    continue

                risk = json.loads(risk_raw)
                shuri = json.loads(shuri_raw)

                # 2. CIRCUIT BREAKER
                if risk.get("trading_status") != "AUTHORIZED":
                    await asyncio.sleep(2)
                    continue

                # 3. LÓGICA DE DECISÃO
                analysis = shuri.get("analysis", "").lower()
                current_temp = shuri.get("current_temp", 0)
                
                # Exemplo de lógica: Comprar se a Shuri prever alta ou se estiver frio demais em NYC
                # (Ajuste essa lógica conforme sua estratégia vencedora)
                condicao_compra = "alta" in analysis or current_temp < 5.0

                if condicao_compra:
                    logger.info(f"🎯 GATILHO DETECTADO! Análise: {analysis[:50]}... | Temp: {current_temp}°C")
                    
                    if not self.MODO_REAL:
                        logger.info(f"🧪 [TESTE] Simulação de compra de ${self.VALOR_TRADE} executada com sucesso.")
                    else:
                        logger.info(f"💰 [REAL] ENVIANDO ORDEM DE ${self.VALOR_TRADE} PARA A REDE POLYGON!")
                        
                        # Exemplo de envio Real (Descomente apenas quando tiver saldo e confiança)
                        # order_args = OrderArgs(
                        #     price=0.95, # Preço máximo aceitável
                        #     size=self.VALOR_TRADE,
                        #     side="BUY",
                        #     token_id="TOKEN_ID_CLIMA_AQUI"
                        # )
                        # resp = self.client.create_and_post_order(order_args)
                        # logger.info(f"✅ RESPOSTA DA REDE: {resp}")

                    # Trava de segurança (Cooldown) para não comprar repetidamente
                    await asyncio.sleep(60)

            except Exception as e:
                logger.error(f"❌ Erro no Loop Fury: {e}")
            
            await asyncio.sleep(0.05) # Ciclo de 50ms

if __name__ == "__main__":
    fury = FuryEngine()
    try:
        asyncio.run(fury.run_loop())
    except KeyboardInterrupt:
        logger.info("Fury desligado.")