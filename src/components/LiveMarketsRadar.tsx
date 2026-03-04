import React, { useEffect, useState } from 'react';
import { LiveMarket } from '../types';
import { Target, Activity } from 'lucide-react';

interface LiveMarketsRadarProps {
  markets: LiveMarket[];
}

export function LiveMarketsRadar({ markets }: LiveMarketsRadarProps) {
  const [flashingRows, setFlashingRows] = useState<Record<string, 'up' | 'down'>>({});
  const [prevPrices, setPrevPrices] = useState<Record<string, number>>({});

  useEffect(() => {
    const newFlashes: Record<string, 'up' | 'down'> = {};
    let hasChanges = false;

    markets.forEach((market) => {
      const prevPrice = prevPrices[market.id];
      if (prevPrice !== undefined && prevPrice !== market.currentPrice) {
        newFlashes[market.id] = market.currentPrice > prevPrice ? 'up' : 'down';
        hasChanges = true;
      }
    });

    if (hasChanges) {
      setFlashingRows(prev => ({ ...prev, ...newFlashes }));
      
      // Update prev prices
      const currentPrices = markets.reduce((acc, m) => {
        acc[m.id] = m.currentPrice;
        return acc;
      }, {} as Record<string, number>);
      setPrevPrices(currentPrices);

      // Clear flashes after 500ms
      setTimeout(() => {
        setFlashingRows(prev => {
          const next = { ...prev };
          Object.keys(newFlashes).forEach(id => delete next[id]);
          return next;
        });
      }, 500);
    } else if (Object.keys(prevPrices).length === 0 && markets.length > 0) {
      // Initialize prev prices
      const currentPrices = markets.reduce((acc, m) => {
        acc[m.id] = m.currentPrice;
        return acc;
      }, {} as Record<string, number>);
      setPrevPrices(currentPrices);
    }
  }, [markets]);

  return (
    <div className="flex flex-col h-full overflow-hidden">
      <div className="flex items-center justify-between mb-3 shrink-0">
        <div className="text-xs text-gray-400 flex items-center gap-1">
          <Target size={12} className="text-[var(--color-neon-green)]" />
          LIVE MARKETS RADAR
        </div>
        <div className="text-[10px] text-[var(--color-neon-green)] animate-pulse flex items-center gap-1">
          <Activity size={10} /> TRACKING {markets.length} MARKETS
        </div>
      </div>
      
      <div className="flex-1 overflow-y-auto pr-2">
        <table className="w-full text-left border-collapse">
          <thead className="sticky top-0 bg-[var(--color-bg-card)] z-10">
            <tr className="text-[10px] text-gray-500 border-b border-[var(--color-border-card)]">
              <th className="pb-2 font-normal">ID do Token</th>
              <th className="pb-2 font-normal">MARKET QUESTION</th>
              <th className="pb-2 font-normal">TARGET DATE</th>
              <th className="pb-2 font-normal text-right">PRICE (YES)</th>
              <th className="pb-2 font-normal text-right">OUR PRED.</th>
              <th className="pb-2 font-normal text-right">STATUS</th>
            </tr>
          </thead>
          <tbody>
            {markets.map((market) => {
              const flash = flashingRows[market.id];
              let rowClass = "text-xs border-b border-[var(--color-border-card)] transition-colors duration-300";
              
              if (flash === 'up') {
                rowClass += " bg-green-900/40";
              } else if (flash === 'down') {
                rowClass += " bg-red-900/40";
              } else {
                rowClass += " hover:bg-black/40";
              }

              return (
                <tr key={market.id} className={rowClass}>
                  <td className="py-3 px-4 font-mono text-[var(--color-neon-blue)]">
                    {market.id.substring(0, 8)}...
                  </td>
                  <td className="py-2 text-gray-300 font-mono truncate max-w-[150px]" title={market.question}>
                    {market.question}
                  </td>
                  <td className="py-2 text-gray-500 font-mono text-[10px]">{market.targetDate}</td>
                  <td className={`py-2 text-right font-mono font-bold ${flash === 'up' ? 'text-green-400' : flash === 'down' ? 'text-red-400' : 'text-gray-300'}`}>
                    ${market.currentPrice.toFixed(2)}
                  </td>
                  <td className="py-2 text-right text-[var(--color-neon-green)] font-mono">
                    {market.ourPrediction.toFixed(1)}%
                  </td>
                  <td className="py-2 text-right">
                    <span className={`inline-flex px-1.5 py-0.5 rounded text-[9px] font-bold tracking-wider ${
                      market.status === 'BUYING' ? 'bg-green-900/40 text-green-400' : 
                      market.status === 'SELLING' ? 'bg-red-900/40 text-red-400' : 
                      'bg-blue-900/40 text-blue-400'
                    }`}>
                      {market.status}
                    </span>
                  </td>
                </tr>
              );
            })}
            {markets.length === 0 && (
              <tr>
                <td colSpan={5} className="py-4 text-center text-xs text-gray-600">NO MARKETS TRACKED</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
