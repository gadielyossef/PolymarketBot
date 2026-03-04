import asyncio
import websockets
import json
import time
import aiohttp

import banco_dados
import agentes_claw

WS_POLYMARKET = "wss://ws-subscriptions-clob.polymarket.com/ws/market"
BANCA_ATUAL = 1000.00
posicoes_abertas = {}

async def enviar_para_dashboard(dados):
    """Envia dados pro React via a nossa Bridge API (Porta 8000) de forma não bloqueante"""
    try:
        async with aiohttp.ClientSession() as session:
            await session.post("http://127.0.0.1:8000/push", json=dados)
    except:
        pass

async def processar_tick_mercado(token_id, preco, start_time):
    """
    Esta função roda em paralelo (Background Task). 
    O Agente FURY avalia o preço sem travar o WebSocket principal.
    """
    global BANCA_ATUAL, posicoes_abertas
    agora_ms = int(time.time() * 1000)
    
    decisao = await agentes_claw.agente_fury_risco(token_id, preco, probabilidade_clima=80)
    
    acao = decisao.get("acao", "HOLD")
    motivo = decisao.get("motivo", "")
    
    acao_log = "SCAN"
    
    # 2. Execução Imediata
    if acao == "BUY" and token_id not in posicoes_abertas:
        print(f"⚡ FURY COMPROU: {token_id[:6]} a ${preco} | Motivo: {motivo}")
        posicoes_abertas[token_id] = {"compra": preco, "investido": 50.0}
        BANCA_ATUAL -= 50.0
        acao_log = "BUY"
        banco_dados.registrar_trade(token_id, "Mercado Dinâmico", "BUY", preco, 50.0)
        
    elif acao == "SELL" and token_id in posicoes_abertas:
        lucro = (preco - posicoes_abertas[token_id]["compra"]) * (50.0 / posicoes_abertas[token_id]["compra"])
        print(f"💰 FURY VENDEU: {token_id[:6]} a ${preco} | Lucro: ${lucro:.2f} | Motivo: {motivo}")
        BANCA_ATUAL += (50.0 + lucro)
        del posicoes_abertas[token_id]
        acao_log = "SELL"
        banco_dados.registrar_trade(token_id, "Mercado Dinâmico", "SELL", preco, 50.0, lucro)

    # 3. Calcula a latência exata (WebSocket -> Llama -> Execução)
    latency_ms = (time.perf_counter() - start_time) * 1000

    # 4. Atualiza o React
    dados_front = {
        "bank": {
            "balance": BANCA_ATUAL, 
            "dailyPL": BANCA_ATUAL - 1000.00, 
            "kellyExposure": len(posicoes_abertas) * 5, 
            "equityCurve": []
        },
        "orders": [{"id": k[:6], "price": v["compra"], "status": "OPEN"} for k, v in posicoes_abertas.items()],
        "logs": [{
            "id": str(agora_ms), 
            "timestamp": agora_ms, 
            "latency": round(latency_ms, 2), 
            "action": acao_log, 
            "tokenId": token_id[:6], 
            "executionTime": round(latency_ms, 2)
        }],
        "globalLatency": round(latency_ms, 2)
    }
    
    await enviar_para_dashboard(dados_front)

async def motor_hft_event_driven():
    """Ouvidos do Mission Control - Escuta a Polymarket em TEMPO REAL"""
    banco_dados.inicializar_mission_control()
    
    async with websockets.connect(WS_POLYMARKET) as ws:
        print("🎧 Conectado à Polymarket! Latência Zero Ativada.")
        
        # Tokens de exemplo para assinar (substitua pelos seus mercados mapeados)
        tokens_alvo = ["21742633143463906290569050155826241533067272736897614950488156847949938836455"] 
        await ws.send(json.dumps({"assets_ids": tokens_alvo, "type": "market"}))
        
        while True:
            mensagem = await ws.recv()
            start_time = time.perf_counter() # Inicia o relógio de latência no frame exato da rede
            
            dados = json.loads(mensagem)
            
            if isinstance(dados, list) and len(dados) > 0 and "asset_id" in dados[0]:
                token = dados[0]["asset_id"]
                if "bids" in dados[0] and len(dados[0]["bids"]) > 0:
                    novo_preco = float(dados[0]["bids"][0]["price"])
                    
                    # Dispara a inteligência em uma Task paralela instantânea! Não usa Await aqui.
                    asyncio.create_task(processar_tick_mercado(token, novo_preco, start_time))

if __name__ == "__main__":
    print("\n" + "═"*50 + "\n🚀 MISSION CONTROL (EVENT-DRIVEN HFT) INICIADO\n" + "═"*50)
    try:
        asyncio.run(motor_hft_event_driven())
    except KeyboardInterrupt:
        print("\n🛑 Sistema Encerrado.")