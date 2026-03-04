import re

def extrair_alvo_polymarket(pergunta):
    """Extrai o número alvo em Celsius da frase do Polymarket"""
    match_temp = re.search(r'be (.*?)°C(?: or higher| or below)? on', pergunta)
    if match_temp:
        try:
            return float(match_temp.group(1).strip())
        except ValueError:
            return None
    return None

def analisar_oportunidade(pergunta, dados_consenso, preco_venda_mercado):
    """
    O cérebro do Analista de Mercado.
    Cruza o consenso meteorológico com o preço do livro de ofertas.
    """
    alvo_mercado = extrair_alvo_polymarket(pergunta)
    
    if alvo_mercado is None:
        return {"status": "IGNORAR", "motivo": "Alvo não numérico ou em Fahrenheit."}
        
    media_real = dados_consenso["media"]
    certeza = dados_consenso["certeza_pct"]
    
    print(f"📊 [MERCADO] Preço Alvo do 'SIM': ${preco_venda_mercado:.3f}")
    
    # REGRA 1: Proteção de Capital (Filtro de Certeza)
    if certeza < 80.0:
        return {
            "status": "ABORTAR", 
            "motivo": f"Risco alto. Certeza de {certeza}% é menor que o limite exigido de 80%."
        }
        
    # REGRA 2: Cálculo de Distância Absoluta
    distancia = abs(media_real - alvo_mercado)
    
    # Se a pergunta for exata (ex: "be 14°C") e a distância for menor que 0.3°C, 
    # a nossa chance de estar certo é gigantesca.
    if distancia <= 0.3:
        # Nossa probabilidade real de ganhar é próxima da nossa "Certeza" (ex: 95%).
        # O preço "justo" dessa cota deveria ser $0.95.
        preco_justo = certeza / 100.0
        
        # O SEGREDO DO HFT: Comprar barato!
        if preco_venda_mercado < preco_justo - 0.20: # Exigimos pelo menos 20% de margem de lucro
            ev = preco_justo - preco_venda_mercado
            return {
                "status": "COMPRA FORTE", 
                "motivo": f"Distorção detectada! Preço justo é ~${preco_justo:.2f}, mas estão vendendo a ${preco_venda_mercado:.3f}. EV Positivo: +${ev:.3f} por cota."
            }
        else:
            return {
                "status": "IGNORAR", 
                "motivo": f"Cota cara (${preco_venda_mercado:.3f}). O mercado já precificou a vitória."
            }
            
    # Se a distância for gigantesca (ex: Polymarket pergunta 14°C, e a previsão é 17°C)
    elif distancia > 1.5:
        # A chance de ser "SIM" é praticamente zero. 
        # Nós NÃO compramos o SIM. A orientação aqui seria comprar o "NÃO",
        # mas como estamos focados na chave do Token YES, apenas ignoramos.
        return {
            "status": "VENDER / FICAR DE FORA",
            "motivo": f"A realidade ({media_real}°C) está muito distante do alvo ({alvo_mercado}°C)."
        }
        
    else:
         return {
            "status": "IGNORAR", 
            "motivo": f"Distância perigosa de {distancia:.1f}°C. O clima pode oscilar até a liquidação."
        }

# --- TESTE DO AGENTE DE MERCADO ---
if __name__ == "__main__":
    print("📈 Acordando o Analista de Mercado...\n")
    
    pergunta_teste = "Will the highest temperature in London be 16°C on March 4?"
    
    # Simulando um cenário perfeito com base no que você gerou:
    consenso_simulado = {
        "media": 16.1,           # Quase cravado no 16°C
        "certeza_pct": 92.5      # Os três modelos concordam!
    }
    
    # Simulando que no Polymarket (Asks) um humano impaciente está vendendo a 40 centavos
    preco_ask_simulado = 0.400 
    
    print(f"🎯 ALVO: {pergunta_teste}")
    print(f"🌤️ INFO DO ORÁCULO: Média {consenso_simulado['media']}°C | Exatidão {consenso_simulado['certeza_pct']}%")
    
    decisao = analisar_oportunidade(pergunta_teste, consenso_simulado, preco_ask_simulado)
    
    print(f"\n⚡ DECISÃO DO AGENTE: {decisao['status']}")
    print(f"📝 JUSTIFICATIVA: {decisao['motivo']}")
