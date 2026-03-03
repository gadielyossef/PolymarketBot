import React from 'react';
import { useSystemData } from './hooks/useSystemData';
import { Card } from './components/ui/Card';
import { MapWidget } from './components/MapWidget';
import { WeatherAnalyst } from './components/WeatherAnalyst';
import { MarketAnalyst } from './components/MarketAnalyst';
import { BankManager } from './components/BankManager';
import { ExecutionTerminal } from './components/ExecutionTerminal';
import { HistoryPerformance } from './components/HistoryPerformance';
import { Activity, CloudRain, Briefcase, BarChart2, Zap } from 'lucide-react';

export default function App() {
  const state = useSystemData();

  return (
    <div className="min-h-screen bg-[var(--color-bg-main)] text-[var(--color-neon-green)] font-mono flex flex-col p-4 gap-4 overflow-hidden">
      
      {/* Header */}
      <header className="flex items-center justify-between border-b border-[var(--color-border-card)] pb-4 shrink-0">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-[var(--color-neon-green)]/10 border border-[var(--color-neon-green)] rounded flex items-center justify-center">
            <Zap size={18} className="text-[var(--color-neon-green)]" />
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-widest uppercase text-gray-100">Polymarket HFT</h1>
            <p className="text-[10px] text-gray-500 tracking-widest">WEATHER ARBITRAGE TERMINAL</p>
          </div>
        </div>
        
        <div className="flex items-center gap-6">
          <div className="flex flex-col items-end">
            <span className="text-[10px] text-gray-500">SYSTEM STATUS</span>
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-[var(--color-neon-green)] rounded-full animate-pulse" />
              <span className="text-xs font-bold text-[var(--color-neon-green)]">ONLINE</span>
            </div>
          </div>
          <div className="flex flex-col items-end">
            <span className="text-[10px] text-gray-500">AVG LATENCY</span>
            <span className="text-xs font-bold text-yellow-500">{state.globalLatency}ms</span>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 flex flex-col gap-4 min-h-0 overflow-hidden">
        
        {/* Top Section */}
        <div className="flex flex-col lg:flex-row gap-4 h-1/3">
          <Card title="Global Monitoring" icon={<Activity size={14} />} className="flex-1">
            <MapWidget cities={state.cities} globalLatency={state.globalLatency} />
          </Card>
          <Card title="Bank Manager" icon={<Briefcase size={14} />} className="w-full lg:w-1/3">
            <BankManager bank={state.bank} />
          </Card>
        </div>

        {/* Middle Section */}
        <div className="flex flex-col lg:flex-row gap-4 h-1/3">
          <Card title="Weather Analyst" icon={<CloudRain size={14} />} className="flex-1">
            <WeatherAnalyst data={state.weatherData} certainty={state.certainty} />
          </Card>
          <Card title="Market Analyst" icon={<BarChart2 size={14} />} className="flex-1">
            <MarketAnalyst orders={state.orders} />
          </Card>
        </div>

        {/* Bottom Section */}
        <div className="flex flex-col lg:flex-row gap-4 h-1/3">
          <Card title="History & Performance" icon={<BarChart2 size={14} />} className="w-full lg:w-1/2">
            <HistoryPerformance bank={state.bank} orders={state.orders} />
          </Card>
          <Card title="Execution Terminal" icon={<Zap size={14} />} className="w-full lg:w-1/2">
            <ExecutionTerminal logs={state.logs} />
          </Card>
        </div>

      </main>
      
    </div>
  );
}
