import { useState, useEffect, useRef } from 'react';
import { SystemState, WeatherData, CityData, BankState, BotCredentials, BotStatus, LiveMarket } from '../types';

const INITIAL_WEATHER: WeatherData[] = [];
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

  // Busca os mercados iniciais no arranque
  useEffect(() => {
    const fetchInitialMarkets = async () => {
      try {
        const res = await fetch('http://127.0.0.1:8000/markets');
        if (res.ok) {
          const data = await res.json();
          if (data.markets) {
            setState(prev => ({ ...prev, liveMarkets: data.markets }));
          }
        }
      } catch (err) {
        console.log('Backend a dormir. Aguardando Start...');
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
            
            // O histórico infinito de Banca!
            if (data.bank) {
              nextState.bank = {
                ...data.bank,
                equityCurve: [...prev.bank.equityCurve, ...(data.bank.equityCurve || [])]
              };
            }

            // Radar de Mercados Ativos recebido do backend
            if (data.active_markets) {
              nextState.liveMarkets = data.active_markets;
            } else if (data.liveMarkets) {
              nextState.liveMarkets = data.liveMarkets;
            }

            // Tratamento de Logs (Evita sobrecarga na RAM limitando a 300 logs no UI)
            if (data.logs) {
              nextState.logs = [...data.logs, ...prev.logs].slice(0, 300);
            }

            if (data.orders) nextState.orders = data.orders;
            if (data.globalLatency !== undefined) nextState.globalLatency = data.globalLatency;

            return nextState;
          });
        } catch (e) {
          console.error('Erro a analisar WS', e);
        }
      };

      ws.onclose = () => {
        console.log('WS fechado');
        setBotStatus('OFFLINE');
      };
      
    } catch (err) {
      console.error('WS Falhou', err);
    }
  };

  const startBot = async (credentials: BotCredentials) => {
    setBotStatus('STARTING');
    try {
      const res = await fetch('http://127.0.0.1:8000/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(credentials)
      });
      if (res.ok) {
        setBotStatus('RUNNING');
        connectWebSocket();
      } else {
        setBotStatus('OFFLINE');
      }
    } catch (err) {
      console.error('Erro a contactar API.', err);
      setBotStatus('OFFLINE');
    }
  };

  const stopBot = async () => {
    setBotStatus('STOPPING');
    try {
      await fetch('http://127.0.0.1:8000/stop', { method: 'POST' });
    } catch (err) {
      console.error('Erro a parar API.', err);
    } finally {
      if (wsRef.current) wsRef.current.close();
      setBotStatus('OFFLINE');
    }
  };

  return { state, botStatus, startBot, stopBot };
}