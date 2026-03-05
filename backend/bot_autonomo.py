import asyncio
import websockets
import json
import time
from datetime import datetime
import requests
import aiohttp
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    import banco_dados
    import shuri_clima
    import agentes_claw
except Exception as e:
    print(f"🔥 [FURY FATAL ERROR] Falha de imports: {e}")
    sys.exit(1)

WS_POLYMARKET = "wss://ws-subscriptions-clob.polymarket.com/ws/market"
BANCA_ATUAL = 10.00
POSICOES_ABERTAS = {}

# =========================================================================
# 🧠 MEMÓRIA RAM DO FUNDO
# =========================================================================
# Mapeia token_id -> {"pergunta": q, "tipo": "YES" ou "NO", "token_base": token_yes}
MERCADOS_INFO = {} 
# Mapeia token_yes -> {"lado": "YES" ou "NO", "preco_justo": 0.45, "lote": 1.00}
MEMORIA_ESTRATEGIA = {}

def mapear_universo_climatico():
    global MERCADOS_INFO
    print("📡 SISTEMA: A mapear tokens YES e NO de mercados climáticos...")
    try:
        res = requests.get("https://gamma-api.polymarket.com/markets", params={"active": "true", "closed": "false", "limit": 200}, timeout=10)
        if res.status_code == 200:
            palavras = ['temperature', 'rain', 'weather', 'climate', 'degrees', '°c', '°f', 'hurricane']
            for m in res.json():
                pergunta = m.get("question", "")
                if any(k in pergunta.lower() for k in palavras):
                    clob_raw = m.get("clobTokenIds")
                    if not clob_raw: continue
                    try:
                        clob_ids = json.loads(clob_raw) if isinstance(clob_raw, str) else clob_raw
                        if len(clob_ids) >= 2:
                            token_yes = str(clob_ids[0])
                            token_no = str(clob_ids[1])
                            MERCADOS_INFO[token_yes] = {"pergunta": pergunta, "tipo": "YES", "token_base": token_yes}
                            MERCADOS_INFO[token_no] = {"pergunta": pergunta, "tipo": "NO", "token_base": token_yes}
                            MEMORIA_ESTRATEGIA[token_yes] = {"lado": "NENHUM", "preco_justo": 0.0, "lote": 0.0}
                    except: continue
                    if len(MEMORIA_ESTRATEGIA) >= 15: break
            print(f"✅ SISTEMA: {len(MEMORIA_ESTRATEGIA)} Mercados ({len(MERCADOS_INFO)} tokens) na RAM.")
    except Exception as e:
        print(f"⚠️ SISTEMA: Falha de rede: {e}")

async def enviar_para_dashboard(dados):
    try:
        async with aiohttp.ClientSession() as session:
            await session.post("http://127.0.0.1:8000/push", json=dados)
    except: pass

# =========================================================================
# 🐢 LOOP 1: A "WAR ROOM" (Decisões Estratégicas a cada 60s)
# =========================================================================
async def loop_estrategico_comite():
    """SHURI, FURY e AMORA decidem o que comprar."""
    while True:
        print("\n🧠 [WAR ROOM] A iniciar Reunião de Comitê...")
        # Iteramos pelos tokens_base (Os YES) para não analisar a mesma pergunta 2 vezes
        for token_base, estado in list(MEMORIA_ESTRATEGIA.items()):
            pergunta = MERCADOS_INFO[token_base]["pergunta"]
            
            # 1. Relatório SHURI
            relatorio = await shuri_clima.coletar_dados_puros(pergunta)
            
            if relatorio.get("sucesso"):
                # 2. Decisão FURY
                fury_decisao = await agentes_claw.agente_fury_risco(pergunta, relatorio)
                
                if fury_decisao["preco_justo"] > 0:
                    # 3. Alocação AMORA
                    lote = await agentes_claw.agente_amora_banca(BANCA_ATUAL, fury_decisao["probabilidade"])
                    
                    # Salva no Quadro Branco (RAM)
                    MEMORIA_ESTRATEGIA[token_base] = {
                        "lado": fury_decisao["lado"],
                        "preco_justo": fury_decisao["preco_justo"],
                        "lote": lote
                    }
                    print(f"   🎯 {relatorio['cidade']} -> FURY manda comprar [{fury_decisao['lado']}] até ${fury_decisao['preco_justo']:.2f} | AMORA libertou: ${lote:.2f}")
            
            await asyncio.sleep(2) # Evitar ban das APIs
            
        print("🧠 [WAR ROOM] Quadro Branco atualizado. A aguardar 60 segundos...\n")
        await asyncio.sleep(60)

# =========================================================================
# ⚡ LOOP 2: O ATIRADOR HFT (Milissegundos)
# =========================================================================
async def processar_tick_hft(token_id, preco_mercado, start_time):
    global BANCA_ATUAL, POSICOES_ABERTAS
    agora_ms = int(time.time() * 1000)
    
    info = MERCADOS_INFO.get(token_id)
    if not info: return
    
    token_base = info["token_base"]
    estrategia = MEMORIA_ESTRATEGIA.get(token_base)
    
    if not estrategia or estrategia["lote"] == 0: return

    acao_log = "SCAN"
    
    # 1. VERIFICAÇÃO DE GATILHO: O tick é do LADO que o FURY mandou vigiar?
    if info["tipo"] == estrategia["lado"]:
        # 2. A MATEMÁTICA: O mercado está mais barato que o nosso preço justo?
        if preco_mercado <= estrategia["preco_justo"] - 0.02: # Margem de lucro
            if token_id not in POSICOES_ABERTAS:
                # COMPRA INSTANTÂNEA
                POSICOES_ABERTAS[token_id] = {"compra": preco_mercado, "investido": estrategia["lote"], "pergunta": info["pergunta"]}
                BANCA_ATUAL -= estrategia["lote"]
                acao_log = "BUY"
                print(f"⚡ HFT SNIPER: Comprado {info['tipo']} a ${preco_mercado}!")
                try: banco_dados.registrar_trade(token_id, info["pergunta"], "BUY", preco_mercado, estrategia["lote"])
                except: pass
                
        # 3. SAÍDA (Take Profit): Preço voltou ao normal ou subiu!
        elif token_id in POSICOES_ABERTAS and preco_mercado >= estrategia["preco_justo"] + 0.05:
            investido = POSICOES_ABERTAS[token_id]["investido"]
            compra = POSICOES_ABERTAS[token_id]["compra"]
            lucro = (preco_mercado - compra) * (investido / compra)
            BANCA_ATUAL += (investido + lucro)
            del POSICOES_ABERTAS[token_id]
            acao_log = "SELL"
            print(f"💰 HFT SNIPER: Lucro Capturado! Vendido a ${preco_mercado}!")
            try: banco_dados.registrar_trade(token_id, info["pergunta"], "SELL", preco_mercado, investido, lucro)
            except: pass

    latency_ms = (time.perf_counter() - start_time) * 1000

    dados_front = {
        "bank": {
            "balance": BANCA_ATUAL, 
            "dailyPL": BANCA_ATUAL - 10.00, 
            "kellyExposure": sum(v["investido"] for v in POSICOES_ABERTAS.values()), 
            "equityCurve": [{"time": datetime.now().strftime("%H:%M:%S"), "value": BANCA_ATUAL}]
        },
        "orders": [{"id": k[:6], "price": v["compra"], "status": "OPEN", "market": f"[{MERCADOS_INFO[k]['tipo']}] {v['pergunta']}"} for k, v in POSICOES_ABERTAS.items()],
        "logs": [{
            "id": str(agora_ms), "timestamp": agora_ms, "latency": round(latency_ms, 2), 
            "action": acao_log, "agent": "HFT", "tokenId": token_id[:6], "executionTime": round(latency_ms, 2)
        }],
        "globalLatency": round(latency_ms, 2),
        "liveMarkets": [{"id": token_id, "price": preco_mercado, "prediction": estrategia["preco_justo"] * 100, "status": acao_log}]
    }
    
    await enviar_para_dashboard(dados_front)

# =========================================================================
# 🚀 MOTOR DE INICIALIZAÇÃO
# =========================================================================
async def motor_hft_event_driven():
    print("\n" + "═"*50 + "\n🚀 MISSION CONTROL BIDIRECIONAL INICIADO\n" + "═"*50)
    
    try: banco_dados.inicializar_mission_control()
    except: pass
    
    mapear_universo_climatico()
    tokens_alvo = list(MERCADOS_INFO.keys())
    
    if not tokens_alvo: return
    
    asyncio.create_task(loop_estrategico_comite())
    
    try:
        async with websockets.connect(WS_POLYMARKET) as ws:
            print("🟢 HFT: WebSocket L2 Aberto.")
            await ws.send(json.dumps({"assets_ids": tokens_alvo, "type": "market"}))
            
            while True:
                mensagem = await ws.recv()
                start_time = time.perf_counter()
                dados = json.loads(mensagem)
                
                if isinstance(dados, list) and len(dados) > 0 and "asset_id" in dados[0]:
                    if "bids" in dados[0] and len(dados[0]["bids"]) > 0:
                        token = dados[0]["asset_id"]
                        novo_preco = float(dados[0]["bids"][0]["price"])
                        asyncio.create_task(processar_tick_hft(token, novo_preco, start_time))
    except Exception as e:
        print(f"🔥 ERRO WS: {e}")

if __name__ == "__main__":
    try: asyncio.run(motor_hft_event_driven())
    except KeyboardInterrupt: print("\n🛑 Encerrado.")