import os
import time
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv

from py_clob_client.client import ClobClient
from py_clob_client.constants import POLYGON

# Importações dos teus Agentes (certifica-te que os ficheiros estão na mesma pasta)
from analista_tempo import consultar_consenso_modelos
from analista_mercado import analisar_oportunidade
from gerente_banca import calcular_tamanho_posicao, monitorizar_posicao

load_dotenv()
GAMMA_URL = "https://gamma-api.polymarket.com"

# --- MEMÓRIA GLOBAL ---
posicoes_abertas = {} 
BANCA_ATUAL = 10.00
cache_clima = {} # Guarda: {"London": {"dados": {...}, "expira": timestamp}}

# =========================================================
# FUNÇÕES DE INFRAESTRUTURA
# =========================================================

def get_clob_client():
    """Conecta à Polymarket derivando as chaves apenas com a Private Key injetada."""
    chave_privada = os.getenv("PRIVATE_KEY")
    if not chave_privada:
        raise ValueError("Chave privada não encontrada na memória! Sincronize o Front-end primeiro.")
        
    print("🔐 Inicializando conexão L2 e derivando credenciais automaticamente...")
    
    client = ClobClient("https://clob.polymarket.com", key=chave_privada, chain_id=POLYGON)
    client.create_or_derive_api_creds()
    return client

def mapear_universo_valido():
    """O RADAR: Busca mercados futuros de clima"""
    mercados_vivos = []
    try:
        res_tag = requests.get(f"{GAMMA_URL}/tags/slug/temperature")
        tag_id = res_tag.json().get('id') if isinstance(res_tag.json(), dict) else res_tag.json()[0].get('id')
        res = requests.get(f"{GAMMA_URL}/markets", params={"active": "true", "closed": "false", "tag_id": tag_id, "limit": 50})
        
        for m in res.json():
            clob_raw = m.get("clobTokenIds")
            if not clob_raw: continue
            try:
                import json
                clob_ids = json.loads(clob_raw) if isinstance(clob_raw, str) else clob_raw
                if len(clob_ids) >= 2:
                    mercados_vivos.append({"question": m.get("question"), "token_id": str(clob_ids[0])})
            except: continue
        return mercados_vivos
    except:
        return []

def obter_clima_com_cache(cidade, data_iso):
    """Evita o erro de Max Retries guardando a previsão na RAM por 10 min"""
    agora = time.time()
    if cidade in cache_clima:
        if agora < cache_clima[cidade]["expira"]:
            return cache_clima[cidade]["dados"]
    
    print(f"☁️  Consultando Oráculo para {cidade}...")
    dados = consultar_consenso_modelos(cidade, data_iso)
    if dados:
        cache_clima[cidade] = {"dados": dados, "expira": agora + 600} # 10 min
    return dados

# =========================================================
# O MAESTRO (LOOP PRINCIPAL)
# =========================================================

def iniciar_operacao(client):
    global BANCA_ATUAL, posicoes_abertas
    print("\n" + "═"*50 + "\n🤖 MAESTRO HFT V2 - CONECTADO AO DASHBOARD (MODO SOMBRA)\n" + "═"*50)
    
    arsenal = mapear_universo_valido()
    if not arsenal:
        print("A aguardar mercados...")
    
    while True:
        print(f"\n🔄 CICLO | Banca: ${BANCA_ATUAL:.2f} | Posições: {len(posicoes_abertas)}")
        
        for mercado in arsenal[:15]:
            start_time = time.perf_counter() # Inicia o cronómetro de latência
            
            token_id = mercado['token_id']
            pergunta = mercado['question']
            
            # 1. PEGAR PREÇO (CLOB)
            try:
                ob = client.get_order_book(token_id)
                if not ob.asks or not ob.bids: continue
                melhor_venda = float(ob.asks[0].price)
                melhor_compra = float(ob.bids[0].price)
            except: 
                continue

            # 2. IDENTIFICAR CIDADE E DATA
            cidade = next((c for c in ["London", "Sao Paulo", "Buenos Aires", "Chicago", "Seattle", "Paris", "New York", "Toronto", "Seoul"] if c in pergunta), None)
            data_iso = f"{datetime.now().year}-03-04" 
            exat_atual = 90.0

            # 3. GESTÃO DE POSIÇÃO EXISTENTE
            if token_id in posicoes_abertas:
                pos = posicoes_abertas[token_id]
                consenso = obter_clima_com_cache(cidade, data_iso) if cidade else None
                exat_atual = consenso['certeza_pct'] if consenso else 90.0
                
                if melhor_compra > pos["topo"]: pos["topo"] = melhor_compra
                
                status_risco = monitorizar_posicao(pos["compra"], melhor_compra, pos["topo"], exat_atual)
                
                if "VENDER" in status_risco["acao"]:
                    print(f"🚨 SAÍDA: {status_risco['motivo']}")
                    del posicoes_abertas[token_id]

            # 4. BUSCA DE OPORTUNIDADE
            elif cidade:
                consenso = obter_clima_com_cache(cidade, data_iso)
                if consenso:
                    exat_atual = consenso['certeza_pct']
                    oportunidade = analisar_oportunidade(pergunta, consenso, melhor_venda)
                    
                    if oportunidade["status"] == "COMPRA FORTE":
                        invest = calcular_tamanho_posicao(BANCA_ATUAL, consenso["certeza_pct"])
                        print(f"🔥 OPORTUNIDADE: {pergunta[:30]}... | Preço: ${melhor_venda}")
                        
                        # Simulação de Compra
                        posicoes_abertas[token_id] = {"compra": melhor_venda, "topo": melhor_venda, "investido": invest}
                        print(f"✅ Posição aberta (Sombra) a ${melhor_venda}")

            # 5. CÁLCULO DE LATÊNCIA E ENVIO PARA O DASHBOARD (A CADA VARREDURA)
            end_time = time.perf_counter()
            latency_ms = (end_time - start_time) * 1000
            
            agora_ms = int(time.time() * 1000) # Tempo em milissegundos para o React

            dados_para_front = {
                "bank": {
                    "balance": BANCA_ATUAL,
                    "dailyPL": BANCA_ATUAL - 10.00,
                    "kellyExposure": 5.0,
                    "equityCurve": [{"time": datetime.now().strftime("%H:%M:%S"), "value": BANCA_ATUAL}]
                },
                "certainty": exat_atual,
                "weatherData": [
                    {"time": "Agora", "ECMWF": 15.5, "GFS": 15.8, "ICON": 15.3} 
                ],
                "orders": list(posicoes_abertas.values()),
                "logs": [
                    {
                        "id": f"log_{agora_ms}", 
                        "timestamp": agora_ms, 
                        "latency": round(latency_ms, 2), 
                        "action": "SCAN", 
                        "tokenId": token_id[:8] + "...", 
                        "executionTime": round(latency_ms, 2)
                    }
                ],
                "globalLatency": round(latency_ms, 2)
            }

            # Empurra os dados via WebSocket usando a nossa Bridge API!
            try:
                requests.post("http://localhost:8000/push", json=dados_para_front, timeout=1)
            except:
                pass # Se o front/API estiver desligado, o bot continua a trabalhar em silêncio

        time.sleep(5) # Pausa maior para respeitar os limites de API da Polymarket

if __name__ == "__main__":
    try:
        client = get_clob_client()
        iniciar_operacao(client)
    except KeyboardInterrupt:
        print("\n🛑 Bot parado manualmente.")