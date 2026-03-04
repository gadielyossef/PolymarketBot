import React, { useState } from 'react';
import { useSystemData } from './hooks/useSystemData';
import { Card } from './components/ui/Card';
import { MapWidget } from './components/MapWidget';
import { WeatherAnalyst } from './components/WeatherAnalyst';
import { MarketAnalyst } from './components/MarketAnalyst';
import { BankManager } from './components/BankManager';
import { ExecutionTerminal } from './components/ExecutionTerminal';
import { HistoryPerformance } from './components/HistoryPerformance';
import { WalletModal } from './components/WalletModal';
import { Activity, CloudRain, Briefcase, BarChart2, Zap, Play, Square, Wallet } from 'lucide-react';

export default function App() {
  const { state, botStatus, startBot, stopBot } = useSystemData();
  const [isWalletModalOpen, setIsWalletModalOpen] = useState(false);

  const handleSyncWallet = async (token: string) => {
    try {
      const res = await fetch('http://localhost:8000/sync-wallet', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token: token })
      });
      if (!res.ok) throw new Error('Failed to sync wallet');
      console.log('Wallet synchronized successfully');
    } catch (err) {
      console.error('Failed to sync wallet with real backend', err);
      // Mock success for preview
      await new Promise(resolve => setTimeout(resolve, 800));
    }
  };

  return (
    <div className="min-h-screen bg-[var(--color-bg-main)] text-[var(--color-neon-green)] font-mono flex flex-col p-4 gap-4 overflow-hidden">
      
      {/* Header / Top Navigation Bar */}
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
        
        {/* Top Right Controls */}
        <div className="flex items-center gap-6">
          
          {/* Global Latency Indicator */}
          <div className="flex flex-col items-end">
            <span className="text-[10px] text-gray-500">AVG LATENCY</span>
            <div className="flex items-center gap-2">
              <Activity size={12} className="text-yellow-500" />
              <span className="text-xs font-bold text-yellow-500">{state.globalLatency}ms</span>
            </div>
          </div>

          <div className="h-8 w-px bg-[var(--color-border-card)]" />

          {/* START / STOP Toggle Button */}
          <div className="flex items-center gap-3">
            <div className="flex flex-col items-end mr-2">
              <span className="text-[10px] text-gray-500">STATUS</span>
              <span className={`text-xs font-bold ${botStatus === 'RUNNING' ? 'text-[var(--color-neon-green)]' : botStatus === 'OFFLINE' ? 'text-red-500' : 'text-yellow-500'}`}>
                {botStatus}
              </span>
            </div>
            
            {botStatus === 'RUNNING' || botStatus === 'STARTING' ? (
              <button 
                onClick={stopBot}
                disabled={botStatus === 'STOPPING'}
                className="bg-red-900/20 hover:bg-red-900/40 text-red-500 border border-red-900/50 rounded px-4 py-1.5 flex items-center gap-2 text-xs font-bold transition-colors disabled:opacity-50"
              >
                <Square size={12} /> STOP
              </button>
            ) : (
              <button 
                onClick={startBot} // Pass dummy creds, real token is in wallet sync
                disabled={botStatus === 'STOPPING'}
                className="bg-green-900/20 hover:bg-green-900/40 text-[var(--color-neon-green)] border border-green-900/50 rounded px-4 py-1.5 flex items-center gap-2 text-xs font-bold transition-colors disabled:opacity-50"
              >
                <Play size={12} /> START
              </button>
            )}
          </div>

          <div className="h-8 w-px bg-[var(--color-border-card)]" />

          {/* Wallet Icon Button */}
          <button 
            onClick={() => setIsWalletModalOpen(true)}
            className="w-10 h-10 bg-black/40 hover:bg-black/60 border border-[var(--color-border-card)] hover:border-[var(--color-neon-green)] text-gray-400 hover:text-[var(--color-neon-green)] rounded flex items-center justify-center transition-colors"
            title="Configure Wallet"
          >
            <Wallet size={18} />
          </button>

        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 flex flex-col gap-4 min-h-0 overflow-hidden">
        
        {/* Top Section */}
        <div className="flex flex-col lg:flex-row gap-4 h-1/3 shrink-0">
          <Card title="Global Monitoring" icon={<Activity size={14} />} className="flex-1 min-h-[200px] lg:min-h-0">
            <MapWidget cities={state.cities} globalLatency={state.globalLatency} />
          </Card>
          <Card title="Bank Manager" icon={<Briefcase size={14} />} className="w-full lg:w-1/3 min-h-[200px] lg:min-h-0">
            <BankManager bank={state.bank} />
          </Card>
        </div>

        {/* Middle Section */}
        <div className="flex flex-col lg:flex-row gap-4 h-1/3 shrink-0">
          <Card title="Weather Analyst" icon={<CloudRain size={14} />} className="flex-1 min-h-[200px] lg:min-h-0">
            <WeatherAnalyst data={state.weatherData} certainty={state.certainty} />
          </Card>
          <Card title="Market Analyst" icon={<BarChart2 size={14} />} className="flex-1 min-h-[200px] lg:min-h-0">
            <MarketAnalyst orders={state.orders} />
          </Card>
        </div>

        {/* Bottom Section */}
        <div className="flex flex-col lg:flex-row gap-4 h-1/3 shrink-0">
          <Card title="History & Performance" icon={<BarChart2 size={14} />} className="w-full lg:w-1/2 min-h-[200px] lg:min-h-0">
            <HistoryPerformance bank={state.bank} orders={state.orders} />
          </Card>
          <Card title="Execution Terminal" icon={<Zap size={14} />} className="w-full lg:w-1/2 min-h-[200px] lg:min-h-0">
            <ExecutionTerminal logs={state.logs} />
          </Card>
        </div>

      </main>
      
      <WalletModal 
        isOpen={isWalletModalOpen} 
        onClose={() => setIsWalletModalOpen(false)} 
        onSync={handleSyncWallet}
      />
    </div>
  );
}
