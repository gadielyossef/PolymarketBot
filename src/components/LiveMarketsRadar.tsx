import React, { useEffect, useState } from 'react';
import { LiveMarket } from '../types';
import { Target, Activity } from 'lucide-react';

interface LiveMarketsRadarProps {
  markets?: LiveMarket[];
}

export function LiveMarketsRadar({ markets = [] }: LiveMarketsRadarProps) {
  const [flashingRows, setFlashingRows] = useState<Record<string, 'up' | 'down'>>({});
  const [prevPrices, setPrevPrices] = useState<Record<string, number>>({});

  // Proteção 1: Nunca deixar a lista ser undefined
  const safeMarkets = Array.isArray(markets) ? markets : [];

  useEffect(() => {
    const newFlashes: Record<string, 'up' | 'down'> = {};
    let hasChanges = false;

    safeMarkets.forEach((market, idx) => {
      // Proteção 2: Converter ID rigorosamente para String
      const marketId = String(market.id || market.token_id || `UNK-${idx}`);
      const currentPrice = Number(market.currentPrice ?? market.current_price ?? market.price ?? 0);
      
      const prevPrice = prevPrices[marketId];
      if (prevPrice !== undefined && prevPrice !== currentPrice) {
        newFlashes[marketId] = currentPrice > prevPrice ? 'up' : 'down';
        hasChanges = true;
      }
    });

    if (hasChanges) {
      setFlashingRows(prev => ({ ...prev, ...newFlashes }));
      
      const currentPrices = safeMarkets.reduce((acc, m, idx) => {
        const mId = String(m.id || m.token_id || `UNK-${idx}`);
        acc[mId] = Number(m.currentPrice ?? m.current_price ?? m.price ?? 0);
        return acc;
      }, {} as Record<string, number>);
      
      setPrevPrices(currentPrices);

      setTimeout(() => {
        setFlashingRows(prev => {
          const next = { ...prev };
          Object.keys(newFlashes).forEach(id => delete next[id]);
          return next;
        });
      }, 500);
    } else if (Object.keys(prevPrices).length === 0 && safeMarkets.length > 0) {
      const currentPrices = safeMarkets.reduce((acc, m, idx) => {
        const mId = String(m.id || m.token_id || `UNK-${idx}`);
        acc[mId] = Number(m.currentPrice ?? m.current_price ?? m.price ?? 0);
        return acc;
      }, {} as Record<string, number>);
      setPrevPrices(currentPrices);
    }
  }, [safeMarkets]);

  return (
    <div className="flex flex-col h-full overflow-hidden">
      <div className="flex items-center justify-between mb-3 shrink-0">
        <div className="text-xs text-gray-400 flex items-center gap-1">
          <Target size={12} className="text-[var(--color-neon-green)]" />
          LIVE MARKETS RADAR
        </div>
        <div className="text-[10px] text-[var(--color-neon-green)] animate-pulse flex items-center gap-1">
          <Activity size={10} /> TRACKING {safeMarkets.length} MARKETS
        </div>
      </div>
      
      <div className="flex-1 overflow-y-auto pr-2 scrollbar-thin scrollbar-track-transparent scrollbar-thumb-gray-800">
        <table className="w-full text-left border-collapse">
          <thead className="sticky top-0 bg-[var(--color-bg-card)] z-10">
            <tr className="text-[10px] text-gray-500 border-b border-[var(--color-border-card)]">
              <th className="pb-2 font-normal">TOKEN ID</th>
              <th className="pb-2 font-normal">MARKET QUESTION</th>
              <th className="pb-2 font-normal">TARGET DATE</th>
              <th className="pb-2 font-normal text-right">PRICE (YES)</th>
              <th className="pb-2 font-normal text-right">OUR PRED.</th>
              <th className="pb-2 font-normal text-right">STATUS</th>
            </tr>
          </thead>
          <tbody>
            {safeMarkets.map((market, idx) => {
              const marketIdStr = String(market.id || market.token_id || `UNK-${idx}`);
              const targetDate = String(market.targetDate || market.target_date || 'TBD');
              const price = Number(market.currentPrice ?? market.current_price ?? market.price ?? 0);
              const pred = Number(market.ourPrediction ?? market.prediction ?? 0);
              
              const flash = flashingRows[marketIdStr];
              let rowClass = "text-xs border-b border-[var(--color-border-card)] transition-colors duration-300";
              
              if (flash === 'up') rowClass += " bg-green-900/40";
              else if (flash === 'down') rowClass += " bg-red-900/40";
              else rowClass += " hover:bg-black/40";

              return (
                <tr key={marketIdStr} className={rowClass}>
                  <td className="py-3 px-2 font-mono text-[var(--color-neon-blue)]">
                    {marketIdStr.length > 8 ? marketIdStr.substring(0, 8) + '...' : marketIdStr}
                  </td>
                  <td className="py-2 text-gray-300 font-mono truncate max-w-[150px]" title={market.question || 'Mercado'}>
                    {market.question || 'Mercado Dinâmico'}
                  </td>
                  <td className="py-2 text-gray-500 font-mono text-[10px]">{targetDate}</td>
                  <td className={`py-2 text-right font-mono font-bold ${flash === 'up' ? 'text-green-400' : flash === 'down' ? 'text-red-400' : 'text-gray-300'}`}>
                    ${price.toFixed(2)}
                  </td>
                  <td className="py-2 text-right text-[var(--color-neon-green)] font-mono">
                    {pred.toFixed(1)}%
                  </td>
                  <td className="py-2 text-right">
                    <span className={`inline-flex px-1.5 py-0.5 rounded text-[9px] font-bold tracking-wider ${
                      market.status === 'BUYING' ? 'bg-green-900/40 text-green-400' : 
                      market.status === 'SELLING' ? 'bg-red-900/40 text-red-400' : 
                      'bg-blue-900/40 text-blue-400'
                    }`}>
                      {market.status || 'TRACKING'}
                    </span>
                  </td>
                </tr>
              );
            })}
            {safeMarkets.length === 0 && (
              <tr>
                <td colSpan={6} className="py-4 text-center text-xs text-gray-600">A AGUARDAR O RADAR...</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}