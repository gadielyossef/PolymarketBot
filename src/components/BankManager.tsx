import React from 'react';
import { BankState } from '../types';
import { DollarSign, TrendingUp, TrendingDown, ShieldAlert } from 'lucide-react';

interface BankManagerProps {
  bank: BankState;
}

export function BankManager({ bank }: BankManagerProps) {
  const isProfit = bank.dailyPL >= 0;

  return (
    <div className="flex flex-col h-full justify-between space-y-4">
      <div className="grid grid-cols-2 gap-4">
        {/* Total Balance */}
        <div className="bg-black/40 border border-[var(--color-border-card)] rounded p-3 flex flex-col">
          <div className="text-[10px] text-gray-500 mb-1 flex items-center gap-1">
            <DollarSign size={10} /> TOTAL BALANCE
          </div>
          <div className="text-2xl font-bold text-gray-100 font-mono tracking-tight">
            ${bank.balance.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </div>
        </div>

        {/* Daily P/L */}
        <div className="bg-black/40 border border-[var(--color-border-card)] rounded p-3 flex flex-col">
          <div className="text-[10px] text-gray-500 mb-1 flex items-center gap-1">
            {isProfit ? <TrendingUp size={10} className="text-green-500" /> : <TrendingDown size={10} className="text-red-500" />}
            DAILY P/L
          </div>
          <div className={`text-xl font-bold font-mono tracking-tight ${isProfit ? 'text-green-400' : 'text-red-400'}`}>
            {isProfit ? '+' : ''}${bank.dailyPL.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </div>
        </div>
      </div>

      {/* Kelly Criterion / Risk Exposure */}
      <div className="bg-black/40 border border-[var(--color-border-card)] rounded p-3 flex flex-col flex-1 justify-center">
        <div className="flex items-center justify-between mb-2">
          <div className="text-[10px] text-gray-500 flex items-center gap-1">
            <ShieldAlert size={10} className="text-yellow-500" /> RISK EXPOSURE (KELLY)
          </div>
          <div className="text-xs font-bold text-yellow-500 font-mono">{bank.kellyExposure.toFixed(1)}%</div>
        </div>
        
        {/* Progress Bar */}
        <div className="w-full h-2 bg-gray-800 rounded-full overflow-hidden">
          <div 
            className="h-full bg-yellow-500 transition-all duration-300"
            style={{ width: `${bank.kellyExposure}%` }}
          />
        </div>
        
        <div className="flex justify-between mt-2 text-[9px] text-gray-600">
          <span>SAFE (0%)</span>
          <span>OPTIMAL (10-15%)</span>
          <span>MAX (25%)</span>
        </div>
      </div>
    </div>
  );
}
