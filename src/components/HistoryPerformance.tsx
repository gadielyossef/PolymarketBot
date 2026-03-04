import React, { useState } from 'react';
import { Card } from './ui/Card';

interface DataPoint {
  time: string;
  value: number;
}

export function HistoryPerformance({ data }: { data: DataPoint[] }) {
  const [viewMode, setViewMode] = useState<'REALTIME' | 'ALL'>('REALTIME');

  // Se REALTIME, mostra apenas os últimos 20 pontos. Se ALL, mostra tudo.
  const displayData = viewMode === 'REALTIME' ? data.slice(-20) : data;
  
  const min = Math.min(...displayData.map(d => d.value), 9.0);
  const max = Math.max(...displayData.map(d => d.value), 11.0);
  const range = max - min || 1;

  return (
    <Card title="Equity Curve (Performance)" icon="chart">
      <div className="flex justify-end gap-2 mb-4">
        <button 
          onClick={() => setViewMode('REALTIME')}
          className={`text-xs px-2 py-1 rounded border ${viewMode === 'REALTIME' ? 'bg-[var(--color-neon-green)] text-black font-bold' : 'border-gray-700 text-gray-400 hover:text-white'}`}
        >
          Tempo Real
        </button>
        <button 
          onClick={() => setViewMode('ALL')}
          className={`text-xs px-2 py-1 rounded border ${viewMode === 'ALL' ? 'bg-[var(--color-neon-green)] text-black font-bold' : 'border-gray-700 text-gray-400 hover:text-white'}`}
        >
          Geral
        </button>
      </div>

      <div className="relative h-48 w-full border-b border-l border-green-900/30 flex items-end">
        {displayData.length === 0 ? (
          <div className="absolute inset-0 flex items-center justify-center text-green-900/50 text-sm font-mono">
            A aguardar processamento HFT...
          </div>
        ) : (
          displayData.map((d, i) => {
            const heightPct = Math.max(5, ((d.value - min) / range) * 100);
            return (
              <div 
                key={i} 
                className="flex-1 bg-[var(--color-neon-green)] opacity-80 hover:opacity-100 transition-all relative group"
                style={{ height: `${heightPct}%`, margin: '0 1px' }}
              >
                <div className="absolute -top-8 left-1/2 -translate-x-1/2 bg-black text-[var(--color-neon-green)] text-[10px] px-2 py-1 rounded opacity-0 group-hover:opacity-100 z-10 whitespace-nowrap border border-green-900/50">
                  ${d.value.toFixed(2)}
                </div>
              </div>
            );
          })
        )}
      </div>
    </Card>
  );
}