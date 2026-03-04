import { useState, useEffect } from 'react';
import { SystemState, BankState } from '../types';

const INITIAL_BANK: BankState = {
  balance: 0.00,
  dailyPL: 0.00,
  kellyExposure: 0.0,
  equityCurve: [],
};

const INITIAL_STATE: SystemState = {
  weatherData: [],
  certainty: 0,
  orders: [],
  logs: [],
  cities: [
    { id: 'lon', name: 'London', lat: 51.5074, lng: -0.1278, latency: 0, status: 'SYNCING' },
    { id: 'gru', name: 'São Paulo', lat: -23.5505, lng: -46.6333, latency: 0, status: 'SYNCING' },
  ],
  bank: INITIAL_BANK,
  globalLatency: 0,
};

export function useSystemData() {
  const [state, setState] = useState<SystemState>(INITIAL_STATE);

  useEffect(() => {
    // 🔌 Inicia o Túnel WebSocket
    const ws = new WebSocket('ws://localhost:8000/ws');

    ws.onopen = () => {
      console.log('✅ Conectado ao Motor HFT (WebSocket)');
    };

    // ⚡ Dispara instantaneamente no exato milissegundo em que o bot atira os dados
    ws.onmessage = (event) => {
      try {
        const realData = JSON.parse(event.data);
        
        if (realData && realData.bank) {
          setState((prevState) => ({
            ...prevState,
            bank: {
              ...realData.bank,
              equityCurve: [...prevState.bank.equityCurve.slice(-49), ...(realData.bank.equityCurve || [])]
            },
            certainty: realData.certainty || 0,
            weatherData: realData.weatherData || [],
            orders: realData.orders || [],
            logs: realData.logs ? [...prevState.logs.slice(-49), ...realData.logs] : prevState.logs,
            globalLatency: realData.globalLatency || 0,
            cities: prevState.cities.map(c => ({ ...c, status: 'ONLINE', latency: realData.globalLatency || 15 }))
          }));
        }
      } catch (error) {
        console.error("Erro a processar os dados em tempo real:", error);
      }
    };

    ws.onclose = () => {
      console.warn('⚠️ Conexão perdida com o Motor HFT.');
      // Coloca os indicadores visuais a vermelho (SYNCING) se a ligação cair
      setState(prev => ({ ...prev, cities: prev.cities.map(c => ({ ...c, status: 'SYNCING' })) }));
    };

    // Limpa a conexão se o utilizador fechar a página
    return () => ws.close();
  }, []);

  return state;
}