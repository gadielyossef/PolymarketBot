import React from 'react';
import { CityData } from '../types';
import { Globe } from 'lucide-react';

interface MapWidgetProps {
  cities: CityData[];
  globalLatency: number;
}

export function MapWidget({ cities, globalLatency }: MapWidgetProps) {
  return (
    <div className="relative w-full h-full min-h-[200px] bg-black/40 rounded-md border border-[var(--color-border-card)] overflow-hidden flex flex-col">
      <div className="absolute top-3 left-3 z-10 flex items-center gap-2 bg-black/60 px-2 py-1 rounded border border-[var(--color-border-card)]">
        <Globe size={14} className="text-[var(--color-neon-green)] animate-pulse" />
        <span className="text-xs text-gray-400">GLOBAL LATENCY:</span>
        <span className="text-xs font-bold text-[var(--color-neon-green)]">{globalLatency}ms</span>
      </div>
      
      {/* Abstract Map Representation */}
      <div className="flex-1 relative w-full h-full opacity-30 pointer-events-none">
        {/* Grid lines */}
        <div className="absolute inset-0" style={{
          backgroundImage: 'linear-gradient(to right, #333 1px, transparent 1px), linear-gradient(to bottom, #333 1px, transparent 1px)',
          backgroundSize: '20px 20px'
        }} />
        
        {/* Simplified World Map SVG Path (very rough approximation for aesthetic) */}
        <svg viewBox="0 0 1000 500" className="absolute inset-0 w-full h-full fill-none stroke-[var(--color-neon-green)] stroke-[0.5] opacity-40">
           <path d="M 200 100 Q 300 50 400 150 T 600 100 T 800 200" />
           <path d="M 150 200 Q 250 300 350 250 T 550 350 T 750 250" />
           <path d="M 250 350 Q 400 450 500 400 T 700 450" />
           {/* Just decorative curves to look like data streams or map contours */}
           <path d="M 100 250 C 200 100, 300 400, 400 250 C 500 100, 600 400, 700 250 C 800 100, 900 400, 950 250" strokeDasharray="5,5" />
        </svg>
      </div>

      {/* City Nodes */}
      <div className="absolute inset-0">
        {cities.map(city => {
          // Map lat/lng to roughly fit the 1000x500 viewBox or percentage
          // Longitude: -180 to 180 -> 0% to 100%
          // Latitude: 90 to -90 -> 0% to 100%
          const x = ((city.lng + 180) / 360) * 100;
          const y = ((-city.lat + 90) / 180) * 100;
          
          const isOnline = city.status === 'ONLINE';
          
          return (
            <div 
              key={city.id} 
              className="absolute flex flex-col items-center transform -translate-x-1/2 -translate-y-1/2"
              style={{ left: `${x}%`, top: `${y}%` }}
            >
              <div className="relative flex items-center justify-center">
                <div className={`w-2 h-2 rounded-full ${isOnline ? 'bg-[var(--color-neon-green)]' : 'bg-yellow-500'}`} />
                {isOnline && (
                  <div className="absolute w-6 h-6 rounded-full border border-[var(--color-neon-green)] animate-ping opacity-50" />
                )}
              </div>
              <div className="mt-1 bg-black/80 px-1.5 py-0.5 rounded border border-[var(--color-border-card)] whitespace-nowrap">
                <div className="text-[9px] font-bold text-gray-300">{city.name}</div>
                <div className={`text-[8px] ${isOnline ? 'text-[var(--color-neon-green)]' : 'text-yellow-500'}`}>
                  {Math.round(city.latency)}ms
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
