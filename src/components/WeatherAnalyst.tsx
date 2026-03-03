import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts';
import { WeatherData } from '../types';

interface WeatherAnalystProps {
  data: WeatherData[];
  certainty: number;
}

export function WeatherAnalyst({ data, certainty }: WeatherAnalystProps) {
  return (
    <div className="flex flex-col h-full space-y-4">
      <div className="flex items-center justify-between">
        <div className="text-xs text-gray-400">MODEL CONVERGENCE</div>
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-500">CERTAINTY:</span>
          <div className="relative w-24 h-2 bg-gray-800 rounded-full overflow-hidden">
            <div 
              className="absolute top-0 left-0 h-full bg-[var(--color-neon-green)] transition-all duration-500"
              style={{ width: `${certainty}%` }}
            />
          </div>
          <span className="text-xs font-bold text-[var(--color-neon-green)]">{certainty.toFixed(1)}%</span>
        </div>
      </div>
      
      <div className="flex-1 min-h-[150px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 5, right: 5, left: -20, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#222" vertical={false} />
            <XAxis dataKey="time" stroke="#555" fontSize={10} tickMargin={5} />
            <YAxis stroke="#555" fontSize={10} domain={['auto', 'auto']} />
            <Tooltip 
              contentStyle={{ backgroundColor: '#111', borderColor: '#333', fontSize: '12px' }}
              itemStyle={{ color: '#00ff41' }}
            />
            <Line type="monotone" dataKey="ECMWF" stroke="#00ff41" strokeWidth={2} dot={false} isAnimationActive={false} />
            <Line type="monotone" dataKey="GFS" stroke="#00aaff" strokeWidth={2} dot={false} isAnimationActive={false} />
            <Line type="monotone" dataKey="ICON" stroke="#ffaa00" strokeWidth={2} dot={false} isAnimationActive={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
      
      <div className="flex justify-between text-[10px] text-gray-500 border-t border-[var(--color-border-card)] pt-2">
        <div className="flex items-center gap-1"><div className="w-2 h-2 bg-[#00ff41] rounded-full" /> ECMWF</div>
        <div className="flex items-center gap-1"><div className="w-2 h-2 bg-[#00aaff] rounded-full" /> GFS</div>
        <div className="flex items-center gap-1"><div className="w-2 h-2 bg-[#ffaa00] rounded-full" /> ICON</div>
      </div>
    </div>
  );
}
