import json
import aiohttp
import os
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()

# Caminho para os arquivos de personalidade (Souls)
WORKSPACE_DIR = os.path.join(os.path.dirname(__file__), "openclaw_workspace")

# Pega a chave do OpenRouter do arquivo .env
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

def ler_arquivo_md(caminho_relativo):
    try:
        with open(os.path.join(WORKSPACE_DIR, caminho_relativo), 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Erro ao ler {caminho_relativo}: {e}")
        return "SOUL NÃO ENCONTRADA."

async def pensar_como_agente_async(soul_prompt, contexto_trabalho):
    """
    Comunicação ultra-rápida usando a API gratuita do OpenRouter.
    """
    if not OPENROUTER_API_KEY:
        print("⚠️ ERRO: Chave OPENROUTER_API_KEY não encontrada no .env!")
        return {"acao": "HOLD", "motivo": "Falta a chave da API."}

    url = "https://openrouter.ai/api/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:5173", # Opcional, exigido pelo OpenRouter
        "X-Title": "Polymarket HFT Bot"          # Opcional, exigido pelo OpenRouter
    }
    
    payload = {
        # O novo Cérebro de Alta Frequência (Nvidia Nemotron)
        "model": "nvidia/nemotron-3-nano-30b-a3b:free", 
        "messages": [
            {"role": "system", "content": soul_prompt},
            {"role": "user", "content": contexto_trabalho}
        ],

        "response_format": {"type": "json_object"} 
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            # Timeout de 4 segundos. Se a IA na nuvem demorar mais que isso, abortamos.
            async with session.post(url, headers=headers, json=payload, timeout=4.0) as response:
                res_json = await response.json()
                
                if "error" in res_json:
                    print(f"⚠️ Erro no OpenRouter: {res_json['error']['message']}")
                    return {"acao": "HOLD", "motivo": "Rate limit ou erro na API Cloud."}
                    
                conteudo = res_json["choices"][0]["message"]["content"]
                
                # Trava de Segurança: Remove blocos markdown (```json) caso a IA seja "tagarela"
                conteudo_limpo = conteudo.replace('```json', '').replace('```', '').strip()
                
                return json.loads(conteudo_limpo)
                
    except Exception as e:
        print(f"⚠️ Falha de comunicação com a Nuvem: {e}")
        return {"acao": "HOLD", "motivo": f"Falha na latência neural: {e}"}

async def agente_fury_risco(token_id, preco_agora, probabilidade_clima):
    """
    Instancia o FURY lendo o arquivo Markdown da alma dele.
    """
    soul = ler_arquivo_md("agents/fury_soul.md")
    contexto = f"Token_ID: {token_id} | Preço Atual: ${preco_agora} | Probabilidade Climática: {probabilidade_clima}%"
    
    return await pensar_como_agente_async(soul, contexto)