import aiohttp
import asyncio
import re

MAPA_CIDADES = {
    "london": {"lat": 51.5085, "lon": -0.1257},
    "new york": {"lat": 40.7143, "lon": -74.006},
    "sao paulo": {"lat": -23.5475, "lon": -46.6361},
    "tokyo": {"lat": 35.6895, "lon": 139.6917},
    "paris": {"lat": 48.8534, "lon": 2.3488},
    "chicago": {"lat": 41.8500, "lon": -87.6500},
    "miami": {"lat": 25.7743, "lon": -80.1937}
}

def extrair_cidade_da_pergunta(pergunta):
    pergunta_lower = pergunta.lower()
    for cidade in MAPA_CIDADES.keys():
        if cidade in pergunta_lower:
            return cidade
    return None

async def coletar_dados_puros(pergunta_mercado):
    """SHURI apenas recolhe os dados dos satélites e entrega os factos brutos."""
    cidade = extrair_cidade_da_pergunta(pergunta_mercado)
    if not cidade:
        return {"sucesso": False, "motivo": "Cidade não mapeada"}

    coord = MAPA_CIDADES[cidade]
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={coord['lat']}&longitude={coord['lon']}"
        f"&daily=temperature_2m_max"
        f"&models=ecmwf_ifs04,gfs_seamless,icon_seamless"
        f"&timezone=auto&forecast_days=3"
    )

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=4) as response:
                if response.status != 200:
                    return {"sucesso": False, "motivo": f"Erro HTTP {response.status}"}
                
                dados = await response.json()
                temp_ecmwf = dados["daily"]["temperature_2m_max_ecmwf_ifs04"][0]
                temp_gfs = dados["daily"]["temperature_2m_max_gfs_seamless"][0]
                temp_icon = dados["daily"]["temperature_2m_max_icon_seamless"][0]
                
                numeros = re.findall(r'\d+', pergunta_mercado)
                alvo_temp = float(numeros[0]) if numeros else 20.0
                
                return {
                    "sucesso": True,
                    "cidade": cidade,
                    "alvo_temp": alvo_temp,
                    "leitura_modelos": {
                        "ECMWF": temp_ecmwf,
                        "GFS": temp_gfs,
                        "ICON": temp_icon
                    }
                }
    except Exception as e:
        return {"sucesso": False, "motivo": str(e)}