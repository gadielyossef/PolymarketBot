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
        # =========================================================
        # 🛡️ TRAVAS DE SEGURANÇA (MODO TESTE ABSOLUTO)
        # =========================================================
        self.MODO_REAL = False         # <-- Mantenha False. Bloqueia qualquer envio real.
        self.SALDO_SIMULADO = 10.00    # A sua banca virtual de $10
        self.MICRO_LOTE = 1.00         # Cada "tiro" custa $1.00
        self.LUCRO_ALVO = 0.03         # Lucro esperado para vender (+3 centavos)
        # =========================================================
        
        # Mercados que o bot vai vigiar
        self.MERCADOS = {
            "MKT-NYC": "ID_DO_TOKEN_YES_NYC",
            "MKT-LON": "ID_DO_TOKEN_YES_LON"
        }
        
        self.posicoes_abertas = {} 
        self.client = None # Começa desarmado

    async def emitir_log_ui(self, acao, token, latencia):
        """Envia o log para a API Bridge jogar no Frontend"""
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
                # 1. Verifica se o Frontend clicou em "Start"
                ui_status = await redis_client.client.get("ui:bot_status")
                if not ui_status or ui_status.decode() != "RUNNING":
                    if self.client is not None:
                        logger.info("⏸️ Bot pausado pelo Frontend. Desarmando motor...")
                        self.client = None
                    await asyncio.sleep(1)
                    continue

                # 2. Arma o SDK usando a chave que você colocou no Frontend
                if self.client is None:
                    wallet_raw = await redis_client.client.get("bot:wallet_key")
                    if wallet_raw:
                        pk = wallet_raw.decode()
                        try:
                            self.client = ClobClient(host="https://clob.polymarket.com", key=pk, chain_id=POLYGON)
                            self.client.set_api_creds(self.client.create_or_derive_api_creds())
                            logger.info("✅ Chave da UI Validada! O bot está pronto, mas o MODO_REAL está DESLIGADO.")
                        except Exception as e:
                            logger.error(f"❌ Chave inválida fornecida no Frontend: {e}")
                            await asyncio.sleep(2)
                            continue

                # 3. LÊ O CLIMA E O MERCADO
                shuri_raw = await redis_client.client.get("agent:shuri:scenario")
                shuri = json.loads(shuri_raw) if shuri_raw else {}
                tendencia_clima = shuri.get("analysis", "").lower()

                for nome_mercado, token_id in self.MERCADOS.items():
                    price_raw = await redis_client.client.get(f"price:{token_id}")
                    if not price_raw: continue
                    current_price = float(price_raw)

                    # --- LÓGICA DE VENDA (SIMULADA) ---
                    if nome_mercado in self.posicoes_abertas:
                        preco_compra = self.posicoes_abertas[nome_mercado]
                        if current_price >= preco_compra + self.LUCRO_ALVO:
                            lucro = current_price - preco_compra
                            self.SALDO_SIMULADO += self.MICRO_LOTE + lucro # Devolve o lote + lucro
                            logger.info(f"💸 [TESTE] TAKE PROFIT! Vendido a {current_price}. Lucro: ${lucro:.2f} | Nova Banca: ${self.SALDO_SIMULADO:.2f}")
                            await self.emitir_log_ui("SELL", nome_mercado, 12)
                            del self.posicoes_abertas[nome_mercado]
                    
                    # --- LÓGICA DE COMPRA (SIMULADA) ---
                    else:
                        # Exemplo: Comprar se o preço estiver bom e Shuri indicar alta
                        if current_price < 0.40 and "alta" in tendencia_clima and self.SALDO_SIMULADO >= self.MICRO_LOTE:
                            self.SALDO_SIMULADO -= self.MICRO_LOTE # Desconta da banca virtual
                            logger.info(f"⚡ [TESTE] COMPRA! {nome_mercado} a {current_price} | Investido: ${self.MICRO_LOTE} | Restante: ${self.SALDO_SIMULADO:.2f}")
                            await self.emitir_log_ui("BUY", nome_mercado, 8)
                            self.posicoes_abertas[nome_mercado] = current_price

                            # Se o MODO_REAL estivesse True, a ordem iria para a corretora aqui.
                            if self.MODO_REAL:
                                logger.critical("⚠️ ISSO NUNCA DEVE APARECER ENQUANTO MODO_REAL=FALSE")

            except Exception as e:
                pass
            
            await asyncio.sleep(0.05)

if __name__ == "__main__":
    fury = FuryScalper()
    asyncio.run(fury.run_loop())