import React, { useState } from 'react';
import { BankState, Order } from '../types';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { History, Activity, TrendingUp } from 'lucide-react';

interface HistoryPerformanceProps {
  bank: BankState;
  orders: Order[];
}

export function HistoryPerformance({ bank, orders }: HistoryPerformanceProps) {
  const [activeTab, setActiveTab] = useState<'EQUITY' | 'ACTIVE' | 'HISTORY'>('EQUITY');

  return (
    <div className="flex flex-col h-full">
      {/* Tabs */}
      <div className="flex border-b border-[var(--color-border-card)] mb-4">
        <button 
          onClick={() => setActiveTab('EQUITY')}
          className={`px-4 py-2 text-xs font-bold tracking-wider flex items-center gap-2 border-b-2 transition-colors ${
            activeTab === 'EQUITY' ? 'border-[var(--color-neon-green)] text-[var(--color-neon-green)]' : 'border-transparent text-gray-500 hover:text-gray-300'
          }`}
        >
          <TrendingUp size={12} /> EQUITY
        </button>
        <button 
          onClick={() => setActiveTab('ACTIVE')}
          className={`px-4 py-2 text-xs font-bold tracking-wider flex items-center gap-2 border-b-2 transition-colors ${
            activeTab === 'ACTIVE' ? 'border-[var(--color-neon-green)] text-[var(--color-neon-green)]' : 'border-transparent text-gray-500 hover:text-gray-300'
          }`}
        >
          <Activity size={12} /> ACTIVE
        </button>
        <button 
          onClick={() => setActiveTab('HISTORY')}
          className={`px-4 py-2 text-xs font-bold tracking-wider flex items-center gap-2 border-b-2 transition-colors ${
            activeTab === 'HISTORY' ? 'border-[var(--color-neon-green)] text-[var(--color-neon-green)]' : 'border-transparent text-gray-500 hover:text-gray-300'
          }`}
        >
          <History size={12} /> HISTORY
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-hidden relative">
        {activeTab === 'EQUITY' && (
          <div className="absolute inset-0">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={bank.equityCurve} margin={{ top: 5, right: 0, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#00ff41" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#00ff41" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#222" vertical={false} />
                <XAxis dataKey="time" stroke="#555" fontSize={10} tickMargin={5} />
                <YAxis stroke="#555" fontSize={10} domain={['auto', 'auto']} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#111', borderColor: '#333', fontSize: '12px' }}
                  itemStyle={{ color: '#00ff41' }}
                  formatter={(value: number) => [`$${value.toFixed(2)}`, 'Equity']}
                />
                <Area type="monotone" dataKey="value" stroke="#00ff41" fillOpacity={1} fill="url(#colorValue)" isAnimationActive={false} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        )}

        {activeTab === 'ACTIVE' && (
          <div className="absolute inset-0 overflow-y-auto pr-2">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="text-[10px] text-gray-500 border-b border-[var(--color-border-card)]">
                  <th className="pb-2 font-normal">ID</th>
                  <th className="pb-2 font-normal">MARKET</th>
                  <th className="pb-2 font-normal">TYPE</th>
                  <th className="pb-2 font-normal text-right">PRICE</th>
                </tr>
              </thead>
              <tbody>
                {orders.map((order) => (
                  <tr key={order.id} className="text-xs border-b border-[var(--color-border-card)] hover:bg-black/40">
                    <td className="py-2 text-gray-500 font-mono">{order.id}</td>
                    <td className="py-2 text-gray-300 font-mono">{order.market}</td>
                    <td className="py-2">
                      <span className={`inline-flex px-1.5 py-0.5 rounded text-[10px] font-bold ${
                        order.type === 'BUY' ? 'bg-green-900/40 text-green-400' : 'bg-red-900/40 text-red-400'
                      }`}>
                        {order.type}
                      </span>
                    </td>
                    <td className="py-2 text-right text-gray-400 font-mono">${order.price.toFixed(2)}</td>
                  </tr>
                ))}
                {orders.length === 0 && (
                  <tr>
                    <td colSpan={4} className="py-4 text-center text-xs text-gray-600">NO ACTIVE ORDERS</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}

        {activeTab === 'HISTORY' && (
          <div className="absolute inset-0 flex items-center justify-center text-xs text-gray-600 font-mono">
            [HISTORY_DATA_STREAM_PENDING]
          </div>
        )}
      </div>
    </div>
  );
}
