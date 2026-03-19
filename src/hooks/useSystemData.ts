import { useState, useEffect, useRef } from 'react';
import { SystemState, BotCredentials, BotStatus } from '../types';

const INITIAL_BANK = { balance: 0, dailyPL: 0, kellyExposure: 0, equityCurve: [] };

export function useSystemData() {
  const [state, setState] = useState<SystemState>({
    weatherData: [],
    certainty: 0,
    orders: [],
    logs: [],
    cities: [
      { id: 'nyc', name: 'New York', lat: 40.7128, lng: -74.0060, latency: 12, status: 'ONLINE' },
      { id: 'lon', name: 'London', lat: 51.5074, lng: -0.1278, latency: 15, status: 'ONLINE' }
    ],
    bank: INITIAL_BANK,
    globalLatency: 14,
    liveMarkets: [],
  });

  const [botStatus, setBotStatus] = useState<BotStatus>('OFFLINE');
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    const fetchInitialMarkets = async () => {
      try {
        const res = await fetch('/markets'); 
        if (res.ok) {
          const data = await res.json();
          setState(prev => ({ ...prev, liveMarkets: data }));
        }
      } catch (err) {
        console.log('Aguardando API do Backend...');
      }
    };
    fetchInitialMarkets();
    connectWebSocket();
  }, []);

  const connectWebSocket = () => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) return;

    try {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsUrl = `${protocol}//${window.location.host}/ws`;
      
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          setState(prev => {
            let nextState = { ...prev };
            
            if (data.bank) nextState.bank = data.bank;
            
            if (data.weatherData) {
              nextState.weatherData = [...prev.weatherData, ...data.weatherData].slice(-20);
            }
            
            if (data.newLog) {
              nextState.logs = [...prev.logs, data.newLog].slice(-50);
            }

            if (data.liveMarkets) {
              nextState.liveMarkets = data.liveMarkets;
            }

            if (data.type === 'MARKET_UPDATE' && data.token_id && data.price !== undefined) {
              nextState.liveMarkets = prev.liveMarkets.map(m => 
                m.id === data.token_id ? { ...m, currentPrice: data.price } : m
              );
            }

            return nextState;
          });
        } catch (e) {
          console.error('Erro ao processar dados reais', e);
        }
      };

      ws.onclose = () => {
        setTimeout(connectWebSocket, 3000); 
      };
      
    } catch (err) {
      console.error('Falha de conexão WS', err);
    }
  };

  const startBot = async (credentials: BotCredentials) => {
    setBotStatus('STARTING');
    try {
      const res = await fetch('/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(credentials)
      });
      if (!res.ok) throw new Error('Falha ao iniciar robôs');
      setBotStatus('RUNNING');
    } catch (err) {
      setBotStatus('OFFLINE');
    }
  };

  const stopBot = async () => {
    setBotStatus('STOPPING');
    try {
      await fetch('/stop', { method: 'POST' });
    } catch (err) {} 
    finally {
      setBotStatus('OFFLINE');
    }
  };

  return { state, botStatus, startBot, stopBot };
}