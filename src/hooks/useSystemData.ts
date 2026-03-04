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
  const [botStatus, setBotStatus] = useState<'OFFLINE' | 'STARTING' | 'RUNNING' | 'STOPPING'>('OFFLINE');

  // Função para ligar o Bot no Backend
  const startBot = async () => {
    setBotStatus('STARTING');
    try {
      const res = await fetch('http://localhost:8000/start', { method: 'POST' });
      const data = await res.json();
      if (data.status === 'success') {
        setBotStatus('RUNNING');
      } else {
        alert("Erro: " + data.message); // Avisa se esqueceres de sincronizar a carteira
        setBotStatus('OFFLINE');
      }
    } catch (error) {
      console.error(error);
      setBotStatus('OFFLINE');
    }
  };

  // Função para parar o Bot no Backend
  const stopBot = async () => {
    setBotStatus('STOPPING');
    try {
      await fetch('http://localhost:8000/stop', { method: 'POST' });
      setBotStatus('OFFLINE');
    } catch (error) {
      console.error(error);
      setBotStatus('RUNNING');
    }
  };

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000/ws');

    ws.onopen = () => console.log('✅ Conectado ao Motor HFT (WebSocket)');

    ws.onmessage = (event) => {
      try {
        const realData = JSON.parse(event.data);
        
        // Se o Backend mandar um aviso que o bot parou
        if (realData.status === "OFFLINE") {
            setBotStatus("OFFLINE");
            return;
        }

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
      setState(prev => ({ ...prev, cities: prev.cities.map(c => ({ ...c, status: 'SYNCING' })) }));
    };

    return () => ws.close();
  }, []);

  // Agora sim estamos a devolver os botões e o estado para o App.tsx usar!
  return { state, botStatus, startBot, stopBot };
}