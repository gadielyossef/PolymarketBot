import React, { useState } from 'react';
import { Card } from './ui/Card';

interface DataPoint {
  time: string;
  value: number;
}

export function HistoryPerformance({ data = [] }: { data?: DataPoint[] }) {
  const [viewMode, setViewMode] = useState<'REALTIME' | 'ALL'>('REALTIME');

  const safeData = Array.isArray(data) ? data : [];
  const displayData = viewMode === 'REALTIME' ? safeData.slice(-30) : safeData;
  
  let min = 9.5;
  let max = 10.5;
  
  if (displayData.length > 0) {
    min = Number(displayData[0].value) || 0;
    max = Number(displayData[0].value) || 0;
    for (let i = 1; i < displayData.length; i++) {
      const val = Number(displayData[i].value) || 0;
      if (val < min) min = val;
      if (val > max) max = val;
    }
  }

  min -= 0.5;
  max += 0.5;
  const range = max - min || 1;

  return (
    <Card title="Equity Curve (Performance)" icon="chart">
      <div className="flex justify-end gap-2 mb-4">
        <button 
          onClick={() => setViewMode('REALTIME')}
          className={`text-[10px] px-2 py-1 rounded border transition-colors ${viewMode === 'REALTIME' ? 'bg-[var(--color-neon-green)] text-black font-bold border-[var(--color-neon-green)]' : 'border-gray-700 text-gray-400 hover:text-white'}`}
        >
          TEMPO REAL
        </button>
        <button 
          onClick={() => setViewMode('ALL')}
          className={`text-[10px] px-2 py-1 rounded border transition-colors ${viewMode === 'ALL' ? 'bg-[var(--color-neon-green)] text-black font-bold border-[var(--color-neon-green)]' : 'border-gray-700 text-gray-400 hover:text-white'}`}
        >
          HISTÓRICO GERAL
        </button>
      </div>

      <div className="relative h-48 w-full border-b border-l border-green-900/30 flex items-end">
        {displayData.length === 0 ? (
          <div className="absolute inset-0 flex items-center justify-center text-green-900/50 text-sm font-mono">
            A aguardar operações do FURY...
          </div>
        ) : (
          displayData.map((d, i) => {
            const val = Number(d.value) || 0;
            const heightPct = Math.max(2, ((val - min) / range) * 100);
            return (
              <div 
                key={i} 
                className="flex-1 bg-[var(--color-neon-green)] opacity-80 hover:opacity-100 transition-all relative group"
                style={{ height: `${heightPct}%`, margin: '0 1px' }}
              >
                <div className="absolute -top-8 left-1/2 -translate-x-1/2 bg-black text-[var(--color-neon-green)] text-[10px] px-2 py-1 rounded opacity-0 group-hover:opacity-100 z-10 whitespace-nowrap border border-green-900/50">
                  ${val.toFixed(2)}
                </div>
              </div>
            );
          })
        )}
      </div>
    </Card>
  );
}