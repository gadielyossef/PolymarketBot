def calcular_tamanho_posicao(banca_total, certeza_exatidao):
    """
    Define quantos dólares vamos investir numa operação usando uma 
    versão simplificada do Critério de Kelly.
    Para uma banca de $10, começa conservador (3% a 10%).
    """
    if certeza_exatidao >= 95.0:
        risco = 0.10 # 10% da banca ($1.00) se for uma "certeza absoluta"
    elif certeza_exatidao >= 85.0:
        risco = 0.05 # 5% da banca ($0.50)
    else:
        risco = 0.03 # 3% da banca ($0.30)
        
    investimento = banca_total * risco
    return round(investimento, 2)

def monitorizar_posicao(preco_compra, preco_atual, maior_preco_atingido, exatidao_tempo_atual):
    """
    O cão de guarda da tua operação. Decide quando é a hora de fechar a posição 
    (vender as cotas) para garantir lucro ou cortar perdas mínimas.
    """
    lucro_atual = preco_atual - preco_compra
    queda_desde_o_topo = maior_preco_atingido - preco_atual

    # 1. SAÍDA DE EMERGÊNCIA (Fundamentos)
    # Se o modelo climático mudar de ideias no meio do dia e a certeza cair para menos de 70%
    if exatidao_tempo_atual < 70.0:
        return {
            "acao": "VENDER URGENTE", 
            "motivo": f"O clima mudou drasticamente! Exatidão caiu para {exatidao_tempo_atual}%. Abortar para proteger capital."
        }

    # 2. TRAILING STOP (Garantir o Lucro - O teu exemplo perfeito)
    # Se já subimos pelo menos 20 centavos, ativamos o "cinto de segurança".
    if maior_preco_atingido >= preco_compra + 0.20:
        # Se o preço recuar 10 centavos a partir do topo máximo alcançado, nós vendemos.
        if queda_desde_o_topo >= 0.10:
            return {
                "acao": "VENDER (TRAILING STOP)", 
                "motivo": f"Garantindo lucro! O preço bateu ${maior_preco_atingido:.3f}, mas recuou para ${preco_atual:.3f}."
            }

    # 3. TAKE PROFIT (Alvo Final)
    # Se o preço chegar a 90 centavos, vendemos logo. Não vale a pena arriscar os últimos 10 centavos.
    if preco_atual >= 0.90:
         return {
            "acao": "VENDER (TAKE PROFIT)", 
            "motivo": f"Alvo de segurança atingido (${preco_atual:.3f}). Dinheiro no bolso!"
        }

    # 4. STOP LOSS (Corte de Perdas)
    # Nunca deixamos a operação sangrar mais de 10 centavos por cota.
    if preco_atual <= preco_compra - 0.10:
         return {
            "acao": "VENDER (STOP LOSS)", 
            "motivo": f"A cota caiu contra a previsão. Cortando perdas mínimas a ${preco_atual:.3f}."
        }

    # Se nenhum alarme disparou, deixamos os lucros correrem.
    return {
        "acao": "MANTER POSIÇÃO", 
        "motivo": f"Tudo sob controlo. Lucro atual no papel: +${lucro_atual:.3f} por cota."
    }

# --- TESTE DO GERENTE DE BANCA ---
if __name__ == "__main__":
    print("🛡️ Acordando o Gerente de Banca...\n")
    
    banca_real = 10.00 # Os teus $10
    
    # 1. Simulando a entrada
    exatidao_inicial = 92.5
    investimento = calcular_tamanho_posicao(banca_real, exatidao_inicial)
    preco_de_entrada = 0.400 # Comprámos a 40 centavos
    
    print(f"💵 Banca Atual: ${banca_real:.2f}")
    print(f"📥 Investimento aprovado para esta operação: ${investimento:.2f}\n")
    
    # 2. Simulando o decorrer do tempo (O preço subiu para 0.70 e recuou para 0.55)
    cenarios_de_mercado = [
        {"preco_agora": 0.450, "topo": 0.450, "exatidao": 92.5}, # Subiu um pouco, tudo ok
        {"preco_agora": 0.700, "topo": 0.700, "exatidao": 90.0}, # Subiu muito, tudo lindo
        {"preco_agora": 0.550, "topo": 0.700, "exatidao": 88.0}, # RECUA PARA 0.55! (Gatilho do Trailing Stop)
        {"preco_agora": 0.400, "topo": 0.450, "exatidao": 60.0}, # Cenário alternativo: Clima enlouqueceu
    ]
    
    for i, cenario in enumerate(cenarios_de_mercado, 1):
        print(f"⏱️ MOMENTO {i} | Preço: ${cenario['preco_agora']:.3f} | Topo: ${cenario['topo']:.3f} | Exatidão Clima: {cenario['exatidao']}%")
        decisao = monitorizar_posicao(preco_de_entrada, cenario['preco_agora'], cenario['topo'], cenario['exatidao'])
        print(f"   => AÇÃO: {decisao['acao']}")
        print(f"   => NOTA: {decisao['motivo']}\n")