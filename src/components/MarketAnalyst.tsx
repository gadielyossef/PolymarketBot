import React from 'react';
import { Order } from '../types';
import { ArrowUpRight, ArrowDownRight, Activity } from 'lucide-react';

interface MarketAnalystProps {
  orders: Order[];
}

export function MarketAnalyst({ orders }: MarketAnalystProps) {
  return (
    <div className="flex flex-col h-full overflow-hidden">
      <div className="flex items-center justify-between mb-3">
        <div className="text-xs text-gray-400 flex items-center gap-1">
          <Activity size={12} className="text-[var(--color-neon-green)]" />
          ORDER FLOW
        </div>
        <div className="text-[10px] text-[var(--color-neon-green)] animate-pulse">SCANNING MARKETS...</div>
      </div>
      
      <div className="flex-1 overflow-y-auto pr-2">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="text-[10px] text-gray-500 border-b border-[var(--color-border-card)]">
              <th className="pb-2 font-normal">MARKET</th>
              <th className="pb-2 font-normal">TYPE</th>
              <th className="pb-2 font-normal text-right">SPREAD</th>
              <th className="pb-2 font-normal text-right">EV</th>
              <th className="pb-2 font-normal text-right">PRICE</th>
            </tr>
          </thead>
          <tbody>
            {orders.map((order, idx) => (
              <tr 
                key={order.id} 
                className="text-xs border-b border-[var(--color-border-card)] hover:bg-black/40 transition-colors"
              >
                <td className="py-2 text-gray-300 font-mono">{order.market}</td>
                <td className="py-2">
                  <span className={`inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-bold ${
                    order.type === 'BUY' ? 'bg-green-900/40 text-green-400' : 'bg-red-900/40 text-red-400'
                  }`}>
                    {order.type === 'BUY' ? <ArrowUpRight size={10} /> : <ArrowDownRight size={10} />}
                    {order.type}
                  </span>
                </td>
                <td className="py-2 text-right text-yellow-400 font-mono">{(order.spread * 100).toFixed(1)}%</td>
                <td className="py-2 text-right text-[var(--color-neon-green)] font-mono">{order.ev.toFixed(2)}</td>
                <td className="py-2 text-right text-gray-400 font-mono">${order.price.toFixed(2)}</td>
              </tr>
            ))}
            {orders.length === 0 && (
              <tr>
                <td colSpan={5} className="py-4 text-center text-xs text-gray-600">NO ACTIVE ORDERS</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
