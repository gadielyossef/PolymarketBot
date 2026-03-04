# 📈 PRD: Polymarket Quant Hedge Fund (OpenClaw Architecture)

## 1. Visão Geral
Transformar um bot de trading reativo num ecossistema proativo de múltiplos agentes de IA. O sistema preverá resultados climáticos e executará arbitragem de alta frequência (HFT) na Polymarket.

## 2. A Arquitetura (Mission Control)
- **Cérebro:** Modelos LLM rodando localmente (Ollama - Llama 3.2) para custo $0.
- **Mission Control (Banco de Dados):** SQLite atuando como a única fonte da verdade (Caixa de entrada de eventos, Memória de Longo Prazo e Histórico de Trades).
- **Ouvidos:** WebSockets nativos ligados à Polymarket (Zero delay).
- **Sistema Nervoso:** `Heartbeats` assíncronos que acordam os agentes a cada 3-5 segundos se houver novidades no Mission Control.

## 3. O Squad (O Time de Agentes)
1. **AMORA (A CEO / Squad Lead):** Coordena o time, faz o "Daily Standup" e avalia a performance financeira.
2. **FURY (Analista de Risco & Trader):** O executor. Frio e calculista. Analisa o preço da cota e a % de chance de vitória. Ele aperta o botão de BUY e SELL.
3. **SHURI (Analista Climático):** A oráculo. Ela consome dados do ECMWF, GFS e ICON. O trabalho dela é ser cética e encontrar a verdadeira probabilidade (%) de um evento climático ocorrer.

## 4. Regras de Ouro
1. **Zero Over-exposure:** Nunca comprar múltiplas cotas do mesmo evento a menos que a CEO autorize.
2. **Memória de Peixe Dourado Não:** Todo aprendizado deve ser salvo no arquivo `lessons.md` ou no banco de dados.
3. **Mãos de Diamante (Diamond Hands):** Não vender com pequenos prejuízos se o fundamento climático (Shuri) não mudou.