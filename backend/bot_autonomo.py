import asyncio
import websockets
import json
import time
from datetime import datetime
import requests
import aiohttp

import banco_dados
import agentes_claw

WS_POLYMARKET = "wss://ws-subscriptions-clob.polymarket.com/ws/market"
BANCA_ATUAL = 10.00 # Banca ajustada para 10 Dólares
posicoes_abertas = {}

def mapear_universo_valido():
    """Busca TODOS os mercados ativos na Polymarket (Focado em clima/temperatura)"""
    mercados = {}
    try:
        # Busca 20 mercados ativos para termos muita ação
        res = requests.get("https://gamma-api.polymarket.com/markets", params={"active": "true", "closed": "false", "limit": 20})
        for m in res.json():
            clob_raw = m.get("clobTokenIds")
            if not clob_raw: continue
            try:
                clob_ids = json.loads(clob_raw) if isinstance(clob_raw, str) else clob_raw
                if len(clob_ids) >= 2:
                    token_sim = str(clob_ids[0])
                    mercados[token_sim] = m.get("question")
            except: continue
    except: pass
    return mercados

async def enviar_para_dashboard(dados):
    try:
        async with aiohttp.ClientSession() as session:
            await session.post("http://127.0.0.1:8000/push", json=dados)
    except: pass

async def processar_tick_mercado(token_id, preco, start_time, pergunta_mercado):
    global BANCA_ATUAL, posicoes_abertas
    agora_ms = int(time.time() * 1000)
    
    decisao = await agentes_claw.agente_fury_risco(token_id, preco, probabilidade_clima=80)
    acao = decisao.get("acao", "HOLD")
    motivo = decisao.get("motivo", "")
    
    acao_log = "SCAN"
    
    if acao == "BUY" and token_id not in posicoes_abertas:
        investimento = 2.00 # Aposta 2 dólares por entrada
        posicoes_abertas[token_id] = {"compra": preco, "investido": investimento, "pergunta": pergunta_mercado}
        BANCA_ATUAL -= investimento
        acao_log = "BUY"
        banco_dados.registrar_trade(token_id, pergunta_mercado, "BUY", preco, investimento)
        
    elif acao == "SELL" and token_id in posicoes_abertas:
        lucro = (preco - posicoes_abertas[token_id]["compra"]) * (posicoes_abertas[token_id]["investido"] / posicoes_abertas[token_id]["compra"])
        BANCA_ATUAL += (posicoes_abertas[token_id]["investido"] + lucro)
        del posicoes_abertas[token_id]
        acao_log = "SELL"
        banco_dados.registrar_trade(token_id, pergunta_mercado, "SELL", preco, posicoes_abertas[token_id]["investido"], lucro)

    latency_ms = (time.perf_counter() - start_time) * 1000

    dados_front = {
        "bank": {
            "balance": BANCA_ATUAL, 
            "dailyPL": BANCA_ATUAL - 10.00, 
            "kellyExposure": len(posicoes_abertas) * 2.0, 
            "equityCurve": [{"time": datetime.now().strftime("%H:%M:%S"), "value": BANCA_ATUAL}] # Ponto do gráfico
        },
        "orders": [{"id": k[:6], "price": v["compra"], "status": "OPEN", "market": v["pergunta"]} for k, v in posicoes_abertas.items()],
        "logs": [{
            "id": str(agora_ms), 
            "timestamp": agora_ms, 
            "latency": round(latency_ms, 2), 
            "action": acao_log, 
            "agent": "FURY", # Identifica qual bot atuou!
            "tokenId": token_id[:6], 
            "executionTime": round(latency_ms, 2)
        }],
        "globalLatency": round(latency_ms, 2)
    }
    
    await enviar_para_dashboard(dados_front)

async def motor_hft_event_driven():
    banco_dados.inicializar_mission_control()
    print("\n🔍 A mapear TODOS os mercados abertos...")
    mercados_ativos = mapear_universo_valido()
    tokens_alvo = list(mercados_ativos.keys())
    
    if not tokens_alvo:
        print("⚠️ Nenhum mercado encontrado. Usando fallback.")
        tokens_alvo = ["21742633143463906290569050155826241533067272736897614950488156847949938836455"]
        mercados_ativos[tokens_alvo[0]] = "Will the max temperature in London be 24°C?"
    
    print(f"🎯 {len(tokens_alvo)} Mercados Mapeados e Injetados no Radar!")

    # Envia os mercados para o React desenhar a tabela Live Markets
    dados_iniciais = {
        "active_markets": [{"id": k[:8], "question": v, "price": 0, "status": "TRACKING"} for k, v in mercados_ativos.items()]
    }
    await enviar_para_dashboard(dados_iniciais)
    
    async with websockets.connect(WS_POLYMARKET) as ws:
        print("🎧 Conectado à Polymarket! Escutando flutuações...")
        await ws.send(json.dumps({"assets_ids": tokens_alvo, "type": "market"}))
        
        while True:
            mensagem = await ws.recv()
            start_time = time.perf_counter()
            dados = json.loads(mensagem)
            
            if isinstance(dados, list) and len(dados) > 0 and "asset_id" in dados[0]:
                token = dados[0]["asset_id"]
                if "bids" in dados[0] and len(dados[0]["bids"]) > 0:
                    novo_preco = float(dados[0]["bids"][0]["price"])
                    pergunta = mercados_ativos.get(token, "Mercado Dinâmico")
                    
                    # FURY entra em ação
                    asyncio.create_task(processar_tick_mercado(token, novo_preco, start_time, pergunta))

if __name__ == "__main__":
    print("\n" + "═"*50 + "\n🚀 MISSION CONTROL (HFT) INICIADO | BANCA: $10.00\n" + "═"*50)
    try:
        asyncio.run(motor_hft_event_driven())
    except KeyboardInterrupt:
        print("\n🛑 Sistema Encerrado.")