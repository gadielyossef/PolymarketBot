import { useState, useEffect, useRef } from 'react';
import { SystemState, WeatherData, CityData, BankState, BotCredentials, BotStatus, LiveMarket } from '../types';

// 1. SALVAGUARDA: O Clima não pode ser vazio senão o WeatherAnalyst crasha!
const INITIAL_WEATHER: WeatherData[] = Array.from({ length: 20 }, (_, i) => ({
  time: `T-${20 - i}`,
  ECMWF: 50 + Math.random() * 20,
  GFS: 45 + Math.random() * 25,
  ICON: 55 + Math.random() * 15,
}));

const INITIAL_CITIES: CityData[] = [
  { id: 'lon', name: 'London', lat: 51.5074, lng: -0.1278, latency: 12, status: 'ONLINE' },
  { id: 'gru', name: 'São Paulo', lat: -23.5505, lng: -46.6333, latency: 45, status: 'ONLINE' },
  { id: 'nyc', name: 'New York', lat: 40.7128, lng: -74.0060, latency: 8, status: 'ONLINE' },
];

const INITIAL_BANK: BankState = {
  balance: 10.00,
  dailyPL: 0.00,
  kellyExposure: 0.0,
  equityCurve: [],
};

export function useSystemData() {
  const [state, setState] = useState<SystemState>({
    weatherData: INITIAL_WEATHER,
    certainty: 80.0,
    orders: [],
    logs: [],
    cities: INITIAL_CITIES,
    bank: INITIAL_BANK,
    globalLatency: 0,
    liveMarkets: [],
  });

  const [botStatus, setBotStatus] = useState<BotStatus>('OFFLINE');
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    const fetchInitialMarkets = async () => {
      try {
        const res = await fetch('http://127.0.0.1:8000/markets');
        if (res.ok) {
          const data = await res.json();
          // SALVAGUARDA: Validar se data.markets é realmente um Array
          if (data.markets && Array.isArray(data.markets)) {
            setState(prev => ({ ...prev, liveMarkets: data.markets }));
          }
        }
      } catch (err) {
        console.log('Backend offline. Aguardando Start...');
      }
    };
    fetchInitialMarkets();
  }, []);

  const connectWebSocket = () => {
    try {
      const ws = new WebSocket('ws://127.0.0.1:8000/ws');
      wsRef.current = ws;

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          setState(prev => {
            let nextState = { ...prev };
            
            // Tratamento hiper-seguro da Banca
            if (data.bank) {
              const newPoints = Array.isArray(data.bank.equityCurve) ? data.bank.equityCurve : [];
              const oldPoints = Array.isArray(prev.bank?.equityCurve) ? prev.bank.equityCurve : [];
              nextState.bank = {
                ...data.bank,
                equityCurve: [...oldPoints, ...newPoints]
              };
            }

            // Radar de Mercados
            if (Array.isArray(data.active_markets)) {
              nextState.liveMarkets = data.active_markets;
            } else if (Array.isArray(data.liveMarkets)) {
              nextState.liveMarkets = data.liveMarkets;
            }

            // Logs limitados e seguros
            if (Array.isArray(data.logs)) {
              nextState.logs = [...data.logs, ...prev.logs].slice(0, 300);
            }

            if (Array.isArray(data.orders)) nextState.orders = data.orders;
            if (data.globalLatency !== undefined) nextState.globalLatency = data.globalLatency;

            return nextState;
          });
        } catch (e) {
          console.error('Erro no parse do WS', e);
        }
      };

      ws.onclose = () => setBotStatus('OFFLINE');
      
    } catch (err) {
      console.error('WS Falhou', err);
    }
  };

  const startBot = async (credentials: BotCredentials) => {
      setBotStatus('STARTING');
      console.log("🚀 [DEBUG] A enviar comando de START para o Backend na porta 8000...");
      
      try {
        const res = await fetch('http://127.0.0.1:8000/start', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(credentials)
        });
        
        const data = await res.json();
        console.log("📥 [DEBUG] Resposta do Backend:", data);

        if (res.ok && data.status === 'success') {
          setBotStatus('RUNNING');
          connectWebSocket();
        } else {
          console.error('❌ [DEBUG] Backend recusou o arranque:', data.message);
          alert(`O Backend recusou iniciar: ${data.message}`);
          setBotStatus('OFFLINE');
        }
      } catch (err) {
        console.error('🔥 [DEBUG] Erro Fatal de Conexão:', err);
        alert('FALHA DE LIGAÇÃO: O servidor Python (bridge_api.py) não está a responder. Tens a certeza que ele está a correr num segundo terminal?');
        setBotStatus('OFFLINE');
      }
    };

  const stopBot = async () => {
    setBotStatus('STOPPING');
    try { await fetch('http://127.0.0.1:8000/stop', { method: 'POST' }); } 
    catch (err) {} 
    finally {
      if (wsRef.current) wsRef.current.close();
      setBotStatus('OFFLINE');
    }
  };

  return { state, botStatus, startBot, stopBot };
}