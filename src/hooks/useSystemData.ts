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

  // --- FUNÇÃO PARA LIGAR ---
  const startBot = async () => {
    setBotStatus('STARTING'); // Muda o texto para amarelo na hora
    try {
      const res = await fetch('http://127.0.0.1:8000/start', { method: 'POST' });
      const data = await res.json();
      if (data.status === 'success') {
        setBotStatus('RUNNING'); // Transforma no botão vermelho de STOP
      } else {
        alert("Erro da API: " + data.message);
        setBotStatus('OFFLINE');
      }
    } catch (error) {
      console.error("Erro de comunicação com o Backend:", error);
      // Hack salva-vidas: se o browser bloquear a resposta mas o bot ligou, forçamos o botão STOP a aparecer!
      setBotStatus('RUNNING'); 
    }
  };

  // --- FUNÇÃO PARA DESLIGAR ---
  const stopBot = async () => {
    setBotStatus('STOPPING');
    try {
      await fetch('http://127.0.0.1:8000/stop', { method: 'POST' });
      setBotStatus('OFFLINE'); // Volta a mostrar o botão verde de START
    } catch (error) {
      console.error("Erro a desligar:", error);
      setBotStatus('OFFLINE'); // Garante que volta ao estado inicial
    }
  };

  // --- O TÚNEL DE ALTA VELOCIDADE ---
  useEffect(() => {
    const ws = new WebSocket('ws://127.0.0.1:8000/ws');

    ws.onopen = () => console.log('✅ Conectado ao Motor HFT (WebSocket)');

    ws.onmessage = (event) => {
      try {
        const realData = JSON.parse(event.data);
        
        // Se a API mandar a ordem de OFFLINE, o painel obedece
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
        console.error("Erro a processar os dados:", error);
      }
    };

    ws.onclose = () => {
      console.warn('⚠️ Conexão perdida com o Motor HFT.');
      setState(prev => ({ ...prev, cities: prev.cities.map(c => ({ ...c, status: 'SYNCING' })) }));
      setBotStatus('OFFLINE');
    };

    return () => ws.close();
  }, []);

  return { state, botStatus, startBot, stopBot };
}