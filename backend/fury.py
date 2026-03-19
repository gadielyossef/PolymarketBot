import asyncio
import json
import logging
import time
from backend.core.redis_client import redis_client
from py_clob_client.client import ClobClient
from py_clob_client.constants import POLYGON

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("PolyHTF.Fury.Scalper")

class FuryScalper:
    def __init__(self):
        self.MODO_REAL = False         
        self.SALDO_SIMULADO = 10.00    
        self.MICRO_LOTE = 1.00         
        self.LUCRO_ALVO = 0.03         
        self.posicoes_abertas = {} 
        self.client = None 

    async def emitir_log_ui(self, acao, token, latencia):
        log_entry = {
            "id": f"L{int(time.time() * 1000)}",
            "timestamp": int(time.time() * 1000),
            "latency": latencia,
            "action": acao,
            "tokenId": token,
            "executionTime": 4
        }
        await redis_client.client.rpush("ui:logs", json.dumps(log_entry))

    async def run_loop(self):
        logger.info(f"🛡️ FURY INICIADO EM MODO SEGURO | Banca Virtual: ${self.SALDO_SIMULADO:.2f}")
        
        while True:
            try:
                # 🔥 MUDANÇA: Atualiza a banca SEMPRE, mesmo pausado!
                await redis_client.client.set("fury:saldo_simulado", str(self.SALDO_SIMULADO))

                # 1. Verifica se o Frontend clicou em "Start"
                ui_status = await redis_client.client.get("ui:bot_status")
                if not ui_status or ui_status.decode() != "RUNNING":
                    if self.client is not None:
                        logger.info("⏸️ Bot pausado pelo Frontend.")
                        self.client = None
                    await asyncio.sleep(1)
                    continue

                await redis_client.client.set("fury:saldo_simulado", str(self.SALDO_SIMULADO))

                if self.client is None:
                    wallet_raw = await redis_client.client.get("bot:wallet_key")
                    if wallet_raw:
                        pk = wallet_raw.decode()
                        try:
                            self.client = ClobClient(host="https://clob.polymarket.com", key=pk, chain_id=POLYGON)
                            self.client.set_api_creds(self.client.create_or_derive_api_creds())
                            logger.info("✅ Chave da UI Validada!")
                        except Exception as e:
                            await asyncio.sleep(2)
                            continue

                shuri_raw = await redis_client.client.get("agent:shuri:scenario")
                shuri = json.loads(shuri_raw if isinstance(shuri_raw, str) else shuri_raw.decode()) if shuri_raw else {}
                tendencia_clima = shuri.get("analysis", "").lower()

                # 🔥 BUSCA OS MERCADOS QUE ESTÃO ATIVOS AGORA NO REDIS
                keys_prices = await redis_client.client.keys("price:*")
                
                # Opera em cima dos 2 primeiros mercados que encontrar
                for key in keys_prices[:2]:
                    key_str = key if isinstance(key, str) else key.decode()
                    token_id_long = key_str.split(":")[1]
                    nome_mercado = f"MKT-{token_id_long[:6]}"
                    
                    price_raw = await redis_client.client.get(key)
                    if not price_raw: continue
                    current_price = float(price_raw)

                    # --- LÓGICA DE VENDA ---
                    if nome_mercado in self.posicoes_abertas:
                        preco_compra = self.posicoes_abertas[nome_mercado]
                        if current_price >= preco_compra + self.LUCRO_ALVO:
                            lucro = current_price - preco_compra
                            self.SALDO_SIMULADO += self.MICRO_LOTE + lucro 
                            await redis_client.client.set("fury:saldo_simulado", str(self.SALDO_SIMULADO))
                            logger.info(f"💸 [TESTE] TAKE PROFIT! {nome_mercado} Vendido a {current_price}. Lucro: ${lucro:.2f}")
                            await self.emitir_log_ui("SELL", nome_mercado, 12)
                            del self.posicoes_abertas[nome_mercado]
                    
                    # --- LÓGICA DE COMPRA ---
                    else:
                        if current_price < 0.40 and "alta" in tendencia_clima and self.SALDO_SIMULADO >= self.MICRO_LOTE:
                            self.SALDO_SIMULADO -= self.MICRO_LOTE 
                            await redis_client.client.set("fury:saldo_simulado", str(self.SALDO_SIMULADO))
                            logger.info(f"⚡ [TESTE] COMPRA! {nome_mercado} a {current_price}")
                            await self.emitir_log_ui("BUY", nome_mercado, 8)
                            self.posicoes_abertas[nome_mercado] = current_price

            except Exception as e:
                pass
            
            await asyncio.sleep(0.05)

if __name__ == "__main__":
    fury = FuryScalper()
    asyncio.run(fury.run_loop())