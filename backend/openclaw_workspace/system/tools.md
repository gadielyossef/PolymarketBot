# 🛠️ TOOLS & SYSTEM CAPABILITIES

Estes são os recursos que a infraestrutura Python fornece a vocês:

1. **[API Polymarket L2 (py_clob_client)]:** Pode criar ordens reais no Orderbook.
2. **[Mission Control Database (SQLite)]:** Vocês podem ler e escrever dados de contexto aqui. Toda trade finalizada é salva na tabela `historico_trades`.
3. **[WebSocket Listener]:** Vocês não precisam pesquisar preços. O sistema empurrará o preço para vocês assim que ele mudar na rede Polygon.
4. **[Dashboard React (Frontend)]:** Qualquer ação que vocês tomarem será imediatamente refletida na tela do CEO humano (Gadiel) via túnel WebSocket.