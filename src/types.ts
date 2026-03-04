export interface WeatherData {
  time: string;
  ECMWF: number;
  GFS: number;
  ICON: number;
}

export interface Order {
  id: string;
  market: string;
  type: 'BUY' | 'SELL';
  spread: number;
  ev: number;
  status: 'ACTIVE' | 'FILLED' | 'CANCELLED';
  timestamp: number;
  price: number;
}

export interface LogEntry {
  id: string;
  timestamp: number;
  latency: number;
  action: 'BUY' | 'SELL' | 'SCAN' | 'CANCEL';
  tokenId: string;
  executionTime: number;
  message?: string;
}

export interface CityData {
  id: string;
  name: string;
  lat: number;
  lng: number;
  latency: number;
  status: 'ONLINE' | 'OFFLINE' | 'SYNCING';
}

export interface BankState {
  balance: number;
  dailyPL: number;
  kellyExposure: number;
  equityCurve: { time: string; value: number }[];
}

export interface BotCredentials {
  privateKey: string;
}

export type BotStatus = 'OFFLINE' | 'STARTING' | 'RUNNING' | 'STOPPING';

export interface LiveMarket {
  id: string;
  question: string;
  targetDate: string;
  currentPrice: number;
  ourPrediction: number;
  status: 'TRACKING' | 'BUYING' | 'SELLING';
}

export interface SystemState {
  weatherData: WeatherData[];
  certainty: number;
  orders: Order[];
  logs: LogEntry[];
  cities: CityData[];
  bank: BankState;
  globalLatency: number;
  liveMarkets: LiveMarket[];
}
