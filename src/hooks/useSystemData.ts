import { useState, useEffect, useRef } from 'react';
import { SystemState, WeatherData, Order, LogEntry, CityData, BankState, BotCredentials, BotStatus, LiveMarket } from '../types';

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
  { id: 'tyo', name: 'Tokyo', lat: 35.6762, lng: 139.6503, latency: 110, status: 'SYNCING' },
  { id: 'fra', name: 'Frankfurt', lat: 50.1109, lng: 8.6821, latency: 5, status: 'ONLINE' },
];

const INITIAL_BANK: BankState = {
  balance: 10450.25,
  dailyPL: 145.50,
  kellyExposure: 12.5,
  equityCurve: Array.from({ length: 50 }, (_, i) => ({
    time: `10:${i < 10 ? '0' + i : i}`,
    value: 10000 + i * 10 + Math.random() * 50 - 25,
  })),
};

const INITIAL_MARKETS: LiveMarket[] = [
  { id: 'MKT-001', question: 'Will it rain in London tomorrow?', targetDate: '2026-03-05', currentPrice: 0.45, ourPrediction: 65.2, status: 'TRACKING' },
  { id: 'MKT-002', question: 'NYC Temp > 30C this week?', targetDate: '2026-03-08', currentPrice: 0.12, ourPrediction: 8.5, status: 'TRACKING' },
  { id: 'MKT-003', question: 'Tokyo Earthquake > 5.0 in March?', targetDate: '2026-03-31', currentPrice: 0.05, ourPrediction: 4.1, status: 'TRACKING' },
  { id: 'MKT-004', question: 'Sao Paulo Rain > 10mm today?', targetDate: '2026-03-04', currentPrice: 0.88, ourPrediction: 92.0, status: 'BUYING' },
];

export function useSystemData() {
  const [state, setState] = useState<SystemState>({
    weatherData: INITIAL_WEATHER,
    certainty: 78.5,
    orders: [
      { id: 'ORD-101', market: 'LON_RAIN_TMRW', type: 'BUY', spread: 0.05, ev: 1.2, status: 'ACTIVE', timestamp: Date.now() - 5000, price: 0.45 },
      { id: 'ORD-102', market: 'GRU_TEMP_>30', type: 'SELL', spread: 0.02, ev: 0.8, status: 'ACTIVE', timestamp: Date.now() - 12000, price: 0.88 },
    ],
    logs: [
      { id: 'L1', timestamp: Date.now() - 20000, latency: 14, action: 'SCAN', tokenId: 'LON_RAIN', executionTime: 4 },
      { id: 'L2', timestamp: Date.now() - 15000, latency: 12, action: 'BUY', tokenId: 'LON_RAIN_TMRW', executionTime: 8 },
    ],
    cities: INITIAL_CITIES,
    bank: INITIAL_BANK,
    globalLatency: 14,
    liveMarkets: INITIAL_MARKETS,
  });

  const [botStatus, setBotStatus] = useState<BotStatus>('OFFLINE');
  const wsRef = useRef<WebSocket | null>(null);
  const mockIntervalRef = useRef<NodeJS.Timeout | null>(null);

  // Initial Data Fetch
  useEffect(() => {
    const fetchInitialMarkets = async () => {
      try {
        const res = await fetch('http://127.0.0.1:8000/markets');
        if (res.ok) {
          const data = await res.json();
          setState(prev => ({ ...prev, liveMarkets: data }));
        }
      } catch (err) {
        console.log('Failed to fetch initial markets from real backend, using mock data.');
      }
    };
    fetchInitialMarkets();
  }, []);

  const startMockData = () => {
    if (mockIntervalRef.current) return;
    mockIntervalRef.current = setInterval(() => {
      setState(prev => {
        // Update Weather
        const newWeather = [...prev.weatherData.slice(1)];
        const lastW = prev.weatherData[prev.weatherData.length - 1];
        newWeather.push({
          time: `T-0`,
          ECMWF: Math.max(0, Math.min(100, lastW.ECMWF + (Math.random() - 0.5) * 5)),
          GFS: Math.max(0, Math.min(100, lastW.GFS + (Math.random() - 0.5) * 6)),
          ICON: Math.max(0, Math.min(100, lastW.ICON + (Math.random() - 0.5) * 4)),
        });

        // Update Certainty (convergence of models)
        const currentW = newWeather[newWeather.length - 1];
        const avg = (currentW.ECMWF + currentW.GFS + currentW.ICON) / 3;
        const variance = Math.abs(currentW.ECMWF - avg) + Math.abs(currentW.GFS - avg) + Math.abs(currentW.ICON - avg);
        const certainty = Math.max(0, 100 - variance * 2);

        // Update Cities Latency
        const newCities = prev.cities.map(c => ({
          ...c,
          latency: Math.max(2, c.latency + (Math.random() - 0.5) * 10),
          status: Math.random() > 0.95 ? (c.status === 'ONLINE' ? 'SYNCING' : 'ONLINE') : c.status
        }));

        // Generate Logs randomly
        const newLogs = [...prev.logs];
        if (Math.random() > 0.7) {
          const isBuy = Math.random() > 0.5;
          const latency = Math.floor(Math.random() * 50) + 5;
          const execTime = Math.floor(Math.random() * 20) + 2;
          newLogs.push({
            id: `L${Date.now()}`,
            timestamp: Date.now(),
            latency,
            action: isBuy ? 'BUY' : 'SELL',
            tokenId: `MKT_${Math.floor(Math.random() * 1000)}`,
            executionTime: execTime,
          });
          if (newLogs.length > 50) newLogs.shift();
        }

        // Update Bank slightly
        const plChange = (Math.random() - 0.48) * 10;
        const newBank = { ...prev.bank };
        newBank.balance += plChange;
        newBank.dailyPL += plChange;
        newBank.equityCurve = [...newBank.equityCurve.slice(1), {
          time: new Date().toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' }),
          value: newBank.balance
        }];

        // Update Live Markets randomly
        const newMarkets = prev.liveMarkets.map(m => {
          if (Math.random() > 0.8) {
            const priceChange = (Math.random() - 0.5) * 0.05;
            return {
              ...m,
              currentPrice: Math.max(0.01, Math.min(0.99, m.currentPrice + priceChange))
            };
          }
          return m;
        });

        return {
          ...prev,
          weatherData: newWeather,
          certainty,
          cities: newCities,
          logs: newLogs,
          bank: newBank,
          globalLatency: Math.floor(newCities.reduce((acc, c) => acc + c.latency, 0) / newCities.length),
          liveMarkets: newMarkets,
        };
      });
    }, 1000);
  };

  const stopMockData = () => {
    if (mockIntervalRef.current) {
      clearInterval(mockIntervalRef.current);
      mockIntervalRef.current = null;
    }
  };

  const connectWebSocket = () => {
    try {
      const ws = new WebSocket('ws://localhost:8000/ws');
      wsRef.current = ws;

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          setState(prev => {
            let nextState = { ...prev };
            
            // Handle general state updates
            if (data.weatherData) nextState.weatherData = data.weatherData;
            if (data.certainty !== undefined) nextState.certainty = data.certainty;
            if (data.orders) nextState.orders = data.orders;
            if (data.cities) nextState.cities = data.cities;
            if (data.bank) nextState.bank = data.bank;
            if (data.globalLatency !== undefined) nextState.globalLatency = data.globalLatency;
            
            // Handle new logs
            if (data.newLog) {
              nextState.logs = [...prev.logs, data.newLog].slice(-50);
            }

            // Handle specific MARKET_UPDATE
            if (data.type === 'MARKET_UPDATE' && data.token_id && data.price !== undefined) {
              nextState.liveMarkets = prev.liveMarkets.map(m => 
                m.id === data.token_id ? { ...m, currentPrice: data.price } : m
              );
            } else if (data.liveMarkets) {
              nextState.liveMarkets = data.liveMarkets;
            }

            return nextState;
          });
        } catch (e) {
          console.error('Failed to parse WS message', e);
        }
      };

      ws.onclose = () => {
        console.log('WS closed');
        if (botStatus === 'RUNNING') {
           startMockData();
        }
      };
      
      ws.onerror = () => {
        console.error('WS error');
      }
    } catch (err) {
      console.error('WS connection failed', err);
      startMockData();
    }
  };

  const startBot = async (credentials: BotCredentials) => {
    setBotStatus('STARTING');
    try {
      const res = await fetch('http://localhost:8000/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(credentials)
      });
      if (!res.ok) throw new Error('Failed to start bot');
      setBotStatus('RUNNING');
      connectWebSocket();
    } catch (err) {
      console.error('Failed to connect to real backend, falling back to mock mode', err);
      setBotStatus('RUNNING');
      startMockData();
    }
  };

  const stopBot = async () => {
    setBotStatus('STOPPING');
    try {
      await fetch('http://localhost:8000/stop', { method: 'POST' });
    } catch (err) {
      console.error('Failed to stop real backend', err);
    } finally {
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
      stopMockData();
      setBotStatus('OFFLINE');
    }
  };

  useEffect(() => {
    return () => {
      stopMockData();
      if (wsRef.current) wsRef.current.close();
    };
  }, []);

  return { state, botStatus, startBot, stopBot };
}
