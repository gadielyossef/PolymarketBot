import asyncio
import websockets
import json
import logging
import httpx
from backend.core.redis_client import redis_client

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("PolyHTF.PolyWS")

async def get_climate_assets():
    """Varre todas as páginas da API Gamma da Polymarket em busca de mercados climáticos"""
    logger.info("🌍 Iniciando varredura paginada em todo o banco de dados da Polymarket...")
    
    climate_tokens = []
    limit = 1000
    offset = 0
    keywords = ["temperature", "weather", "°c", "°f", "hottest", "warmest", "climate"]
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        while True:
            url = f"https://gamma-api.polymarket.com/events?limit={limit}&offset={offset}&active=true&closed=false"
            
            try:
                response = await client.get(url)
                if response.status_code != 200:
                    break
                    
                events = response.json()
                
                if not events:
                    break
                    
                for event in events:
                    title = event.get("title", "").lower()
                    slug = event.get("slug", "").lower()
                    
                    if any(kw in title for kw in keywords) or any(kw in slug for kw in keywords):
                        logger.info(f"🎯 Mercado-Alvo Encontrado: {event.get('title')}")
                        
                        # --- EXTRATOR ROBUSTO DE TOKENS ---
                        for market in event.get("markets", []):
                            tokens = market.get("clobTokenIds", [])
                            
                            if isinstance(tokens, str):
                                try:
                                    tokens = json.loads(tokens)
                                except json.JSONDecodeError:
                                    tokens = tokens.replace('[', '').replace(']', '').replace('"', '').replace("'", "").split(',')
                            
                            if not tokens and "tokens" in market:
                                tokens = [t.get("token_id") for t in market.get("tokens", [])]
                                
                            if isinstance(tokens, list):
                                valid_tokens = [str(t).strip() for t in tokens if t and str(t).strip() != "0" and len(str(t).strip()) > 10]
                                climate_tokens.extend(valid_tokens)
                        # -----------------------------------
                                
                offset += limit
                await asyncio.sleep(0.1) 
                
            except Exception as e:
                logger.error(f"❌ Erro na paginação (Offset {offset}): {e}")
                break

    if not climate_tokens:
        logger.warning("⚠️ Nenhum mercado de clima encontrado após varrer todas as páginas.")
        return ["21742633143463906290569050155826241533067272736897614950488156847949938836455"]
        
    climate_tokens = list(set(climate_tokens))
    logger.info(f"✅ Varredura completa! {len(climate_tokens)} tokens climáticos únicos carregados.")
    return climate_tokens

async def polymarket_ws_loop():
    """Conecta ao WebSocket da Polymarket e atualiza o Redis em milissegundos"""
    url = "wss://ws-subscriptions-clob.polymarket.com/ws/market"
    
    target_assets = await get_climate_assets()
    
    # 💥 O TESTE DE ESTRESSE: Adicionando o Token "Yes" do BTC para forçar ticks na tela
    token_btc = "21742633143463906290569050155826241533067272736897614950488156847949938836455"
    if token_btc not in target_assets:
        target_assets.append(token_btc)

    while True:
        try:
            async with websockets.connect(url, max_size=None) as websocket:
                logger.info(f"⚡ Conectado ao Websocket. Inscrevendo {len(target_assets)} tokens em lotes...")

                # --- O FOR LOOP DE INSCRIÇÃO ---
                chunk_size = 50
                for i in range(0, len(target_assets), chunk_size):
                    chunk = target_assets[i:i + chunk_size]
                    subscribe_msg = {
                        "assets_ids": chunk,
                        "type": "market"
                    }
                    await websocket.send(json.dumps(subscribe_msg))
                    await asyncio.sleep(0.1) # Pausa minúscula para não sobrecarregar
                
                # --- FORA DO FOR LOOP! Só avisa e escuta quando TERMINAR de enviar todos ---
                # --- FORA DO FOR LOOP! Só avisa e escuta quando TERMINAR de enviar todos ---
                logger.info("✅ Todas as inscrições foram enviadas! Escutando a rede...")

                while True:
                    msg = await websocket.recv()
                    
                    if msg == "OK":
                        continue
                        
                    try:
                        data = json.loads(msg)
                    except json.JSONDecodeError:
                        continue

                    # O Pulo do Gato: Lendo a chave "price_changes" do dicionário
                    if isinstance(data, dict):
                        # Se não for mensagem de preço (ex: {"status": "success"}), ignora na tela
                        if "price_changes" not in data:
                            continue
                        
                        # A CHUVA DE TICKS DE VERDADE!
                        for event in data["price_changes"]:
                            asset_id = event.get("asset_id")
                            price = event.get("price")
                            
                            if asset_id and price:
                                # Grava no Redis em nanossegundos!
                                await redis_client.client.set(f"price:{asset_id}", price)
                                
                                if asset_id == token_btc:
                                    logger.info(f"🪙 TICK BTC: ${price}")
                                else:
                                    logger.info(f"📈 TICK CLIMA - Token {asset_id[:6]}... : ${price}")

        except websockets.ConnectionClosed:
            logger.warning("⚠️ Websocket desconectado. Reconectando em 1s...")
            await asyncio.sleep(1)
        except Exception as e:
            logger.error(f"❌ Erro Crítico no Websocket: {e}")
            await asyncio.sleep(2)

if __name__ == "__main__":
    try:
        asyncio.run(polymarket_ws_loop())
    except KeyboardInterrupt:
        logger.info("Websocket interrompido manualmente.")