import requests
import statistics
from datetime import datetime

# Coordenadas estratégicas
COORDENADAS = {
    "London": {"lat": 51.5085, "lon": -0.1257, "tz": "Europe/London"},
    "Sao Paulo": {"lat": -23.5505, "lon": -46.6333, "tz": "America/Sao_Paulo"},
    "Buenos Aires": {"lat": -34.6037, "lon": -58.3816, "tz": "America/Argentina/Buenos_Aires"},
    "Chicago": {"lat": 41.8500, "lon": -87.6500, "tz": "America/Chicago"},
    "Seattle": {"lat": 47.6062, "lon": -122.3321, "tz": "America/Los_Angeles"},
    "Paris": {"lat": 48.8534, "lon": 2.3488, "tz": "Europe/Paris"},
    "New York": {"lat": 40.7143, "lon": -74.0060, "tz": "America/New_York"}
}

def consultar_consenso_modelos(cidade, data_alvo_iso):
    """
    Puxa os 3 maiores modelos climáticos do mundo na mesma requisição
    e calcula a taxa de certeza matemática (exatidão).
    """
    if cidade not in COORDENADAS:
        return None
        
    dados = COORDENADAS[cidade]
    
    # O PULO DO GATO: Pedimos 3 modelos climáticos na mesma chamada!
    modelos = "ecmwf_ifs04,gfs_seamless,icon_global"
    
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={dados['lat']}&longitude={dados['lon']}"
        f"&daily=temperature_2m_max"
        f"&models={modelos}"
        f"&timezone={dados['tz']}"
    )
    
    try:
        res = requests.get(url)
        res.raise_for_status()
        json_data = res.json()
        
        # Pega as listas de datas
        datas = json_data["daily"]["time"]
        
        if data_alvo_iso not in datas:
            return None
            
        # Descobre qual é o índice (posição) da nossa data alvo na lista
        indice_data = datas.index(data_alvo_iso)
        
        # Extrai a previsão exata para aquele dia nos 3 modelos
        temp_ecmwf = json_data["daily"]["temperature_2m_max_ecmwf_ifs04"][indice_data]
        temp_gfs = json_data["daily"]["temperature_2m_max_gfs_seamless"][indice_data]
        temp_icon = json_data["daily"]["temperature_2m_max_icon_global"][indice_data]
        
        # Consolida as previsões válidas (caso algum modelo falhe)
        previsoes_validas = [t for t in (temp_ecmwf, temp_gfs, temp_icon) if t is not None]
        
        if not previsoes_validas:
            return None
            
        # --- MATEMÁTICA DO CONSENSO ---
        media_temp = statistics.mean(previsoes_validas)
        max_temp = max(previsoes_validas)
        min_temp = min(previsoes_validas)
        divergencia = max_temp - min_temp
        
        # Calcula a Certeza (Exatidão):
        # Se a diferença entre os modelos for menor que 0.5°C, temos 95%+ de certeza.
        # Cada 0.1°C de divergência derruba a confiança em ~2.5%.
        certeza = max(10, 100 - (divergencia * 25))
        
        return {
            "media": round(media_temp, 2),
            "modelos": {
                "Europeu (ECMWF)": temp_ecmwf,
                "Americano (GFS)": temp_gfs,
                "Alemão (ICON)": temp_icon
            },
            "divergencia": round(divergencia, 2),
            "certeza_pct": round(certeza, 1)
        }
        
    except Exception as e:
        print(f"❌ Erro no Analista de Tempo: {e}")
        return None

def gerar_grafico_volatilidade(dados_consenso):
    """Gera um visual rápido para o terminal."""
    certeza = dados_consenso['certeza_pct']
    
    # Monta a barra de confiabilidade visual
    blocos_cheios = int(certeza / 10)
    blocos_vazios = 10 - blocos_cheios
    barra = ("█" * blocos_cheios) + ("░" * blocos_vazios)
    
    if certeza >= 85:
        status = "🟢 ALTA PREVISIBILIDADE (Sinal Forte)"
    elif certeza >= 60:
        status = "🟡 VOLATILIDADE MODERADA (Atenção)"
    else:
        status = "🔴 CAOS CLIMÁTICO (Fique de fora)"
        
    print(f"\n🔬 ANALISTA DE TEMPO: Consenso Matemático")
    print(f"Temperatura Média Projetada: {dados_consenso['media']}°C")
    print(f"Divergência entre Modelos: {dados_consenso['divergencia']}°C")
    for modelo, temp in dados_consenso['modelos'].items():
        print(f"  -> {modelo}: {temp}°C")
    print(f"Exatidão: [{barra}] {certeza}%")
    print(f"Decisão: {status}\n")

# --- TESTE DO AGENTE ---
if __name__ == "__main__":
    cidade_teste = "London"
    data_teste = "2026-03-04" # Dia de amanhã!
    
    print(f"Acordando o Agente para analisar {cidade_teste} em {data_teste}...")
    analise = consultar_consenso_modelos(cidade_teste, data_teste)
    
    if analise:
        gerar_grafico_volatilidade(analise)