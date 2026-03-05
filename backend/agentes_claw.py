import json
import aiohttp
import os
from dotenv import load_dotenv

load_dotenv()
WORKSPACE_DIR = os.path.join(os.path.dirname(__file__), "openclaw_workspace")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

def ler_arquivo_md(caminho_relativo):
    try:
        with open(os.path.join(WORKSPACE_DIR, caminho_relativo), 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return ""

async def pensar_como_agente_async(soul_prompt, contexto_trabalho):
    if not OPENROUTER_API_KEY:
        return {}

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:5173",
        "X-Title": "Polymarket HFT Bot"
    }
    
    payload = {
        "model": "nvidia/nemotron-3-nano-30b-a3b:free", 
        "messages": [
            {"role": "system", "content": soul_prompt},
            {"role": "user", "content": contexto_trabalho}
        ],
        "response_format": {"type": "json_object"} 
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload, timeout=5.0) as response:
                res_json = await response.json()
                if "error" in res_json: return {}
                conteudo = res_json["choices"][0]["message"]["content"]
                conteudo_limpo = conteudo.replace('```json', '').replace('```', '').strip()
                return json.loads(conteudo_limpo)
    except:
        return {}

async def agente_fury_risco(pergunta_mercado, relatorio_shuri):
    """FURY avalia a direção (YES ou NO) e o Preço Justo."""
    soul = ler_arquivo_md("agents/fury_soul.md")
    soul += "\nSua saída DEVE ser um JSON estrito: {'lado': 'YES' ou 'NO', 'probabilidade_calculada': 0-100, 'preco_justo_maximo': 0.00-1.00}."
    
    contexto = (
        f"MERCADO: {pergunta_mercado}\n"
        f"DADOS SHURI: Alvo {relatorio_shuri['alvo_temp']}°. "
        f"GFS prevê: {relatorio_shuri['leitura_modelos']['GFS']}°. ICON prevê: {relatorio_shuri['leitura_modelos']['ICON']}°.\n"
        f"Decida se apostamos a favor (YES) ou contra (NO) e defina o preço máximo a pagar."
    )
    
    resposta = await pensar_como_agente_async(soul, contexto)
    return {
        "lado": resposta.get("lado", "YES"),
        "probabilidade": float(resposta.get("probabilidade_calculada", 0)),
        "preco_justo": float(resposta.get("preco_justo_maximo", 0.0))
    }

async def agente_amora_banca(banca_atual, probabilidade):
    """AMORA define o tamanho do lote."""
    soul = ler_arquivo_md("agents/amora_soul.md")
    contexto = f"Banca Atual: ${banca_atual:.2f} | Confiança da Operação: {probabilidade}%"
    resposta = await pensar_como_agente_async(soul, contexto)
    return float(resposta.get("lote_aprovado", 0.0))