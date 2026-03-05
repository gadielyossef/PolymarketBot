<<<<<<< HEAD
# Placeholder for Autonomous Bot
=======
import asyncio
import websockets
import json
import time
import requests
import aiohttp

WS_POLYMARKET = "wss://ws-subscriptions-clob.polymarket.com/ws/market"
MERCADOS_INFO = {}

def mapear_universo_climatico():
    global MERCADOS_INFO
    print("📡 DATA-FEED: A varrer todos os mercados em busca de 'temperature' (Força Bruta)...")
    
    try:
        # Puxa até 500 mercados ativos para garantir que apanhamos as temperaturas
        res = requests.get("https://gamma-api.polymarket.com/markets", params={"active": "true", "closed": "false", "limit": 500}, timeout=15)
        
        if res.status_code == 200:
            dados = res.json()
            mercados_encontrados = 0
            
            # Palavras-chave inegáveis de clima
            palavras_chave = ["temperature", "weather", "°c", "°f"]
            
            for m in dados:
                pergunta = str(m.get("question", "")).lower()
                
                # Se a pergunta contém "temperature" ou "°c", é nosso alvo!
                if any(palavra in pergunta for palavra in palavras_chave):
                    
                    # Filtra falsos positivos se houver
                    if "hockey" in pergunta or "nhl" in pergunta:
                        continue

                    clob_raw = m.get("clobTokenIds")
                    if not clob_raw: continue
                    
                    try:
                        clob_ids = json.loads(clob_raw) if isinstance(clob_raw, str) else clob_raw
                        if len(clob_ids) >= 2:
                            token_yes = str(clob_ids[0]) # ID do "YES"
                            
                            # Guarda o mercado
                            MERCADOS_INFO[token_yes] = {
                                "id": token_yes, 
                                "question": m.get("question", "Desconhecido"), 
                                "price": 0.0, 
                                "prediction": 0.0, 
                                "status": "TRACKING"
                            }
                            mercados_encontrados += 1
                    except Exception as parse_e:
                        continue
                        
                # Limite para não explodir o dashboard visualmente
                if mercados_encontrados >= 20:
                    break
                    
            print(f"✅ DATA-FEED: {mercados_encontrados} Mercados de Temperatura encontrados via busca de texto!")
        else:
            print(f"⚠️ Erro da API: HTTP {res.status_code}")
            
    except Exception as e:
        print(f"🔥 ERRO na busca de mercados: {e}")
        
async def enviar_para_dashboard(dados, session):
    try:
        # Mantém a conexão selada para não congelar o React
        async with session.post("http://127.0.0.1:8000/push", json=dados) as resp:
            await resp.read()
    except: pass

async def motor_dados_puros():
    print("\n" + "═"*50 + "\n📡 MODO DATA-FEED: TEMPERATURAS (IA DESLIGADA)\n" + "═"*50)
    
    mapear_universo_climatico()
    if not MERCADOS_INFO:
        print("⚠️ Ainda sem dados. A Polymarket pode estar a bloquear o IP ou não há mercados hoje.")
        return
        
    tokens_alvo = list(MERCADOS_INFO.keys())
    
    async with aiohttp.ClientSession() as http_session:
        print("💻 A desenhar a tabela Live Markets no teu ecrã...")
        await enviar_para_dashboard({"active_markets": list(MERCADOS_INFO.values())}, http_session)
        
        try:
            async with websockets.connect(WS_POLYMARKET) as ws:
                print("🟢 WEB-SOCKET: Ligado à Bolsa. À espera de variações nos termómetros...")
                
                await ws.send(json.dumps({"assets_ids": tokens_alvo, "type": "market"}))
                
                while True:
                    try:
                        mensagem = await asyncio.wait_for(ws.recv(), timeout=8.0)
                    except asyncio.TimeoutError:
                        await ws.send("PING") 
                        continue
                    
                    if mensagem == "PONG": continue
                        
                    start_time = time.perf_counter()
                    
                    try: dados = json.loads(mensagem)
                    except: continue
                    
                    if isinstance(dados, dict) and dados.get("event_type") == "price_change":
                        alterou_algo = False
                        for pc in dados.get("price_changes", []):
                            token = pc.get("asset_id")
                            if token in MERCADOS_INFO:
                                preco = float(pc.get("price", 0))
                                MERCADOS_INFO[token]["price"] = preco
                                alterou_algo = True
                                print(f"🌡️ PREÇO TICK: {MERCADOS_INFO[token]['question'][:40]}... -> ${preco:.3f}")
                                
                        if alterou_algo:
                            agora_ms = int(time.time() * 1000)
                            latency_ms = (time.perf_counter() - start_time) * 1000
                            
                            payload = {
                                "liveMarkets": list(MERCADOS_INFO.values()),
                                "logs": [{
                                    "id": str(agora_ms),
                                    "timestamp": agora_ms,
                                    "latency": round(latency_ms, 2),
                                    "action": "SCAN",
                                    "agent": "TEMPERATURA",
                                    "tokenId": "UPDATE",
                                    "executionTime": round(latency_ms, 2)
                                }],
                                "globalLatency": round(latency_ms, 2)
                            }
                            await enviar_para_dashboard(payload, http_session)

        except Exception as e:
            print(f"🔥 ERRO WS: {e}")

if __name__ == "__main__":
    try: asyncio.run(motor_dados_puros())
    except KeyboardInterrupt: print("\n🛑 Encerrado.")
>>>>>>> f24cb41 (- novo backennd)
