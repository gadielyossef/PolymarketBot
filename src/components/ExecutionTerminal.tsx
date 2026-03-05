import React from 'react';
import { LogEntry } from '../types';
import { Terminal } from 'lucide-react';

interface ExecutionTerminalProps {
  logs?: LogEntry[];
}

export function ExecutionTerminal({ logs = [] }: ExecutionTerminalProps) {
  const safeLogs = Array.isArray(logs) ? logs : [];

  return (
    <div className="flex flex-col h-full font-mono text-[10px] overflow-hidden">
      <div className="flex items-center gap-2 text-[var(--color-neon-green)] mb-2 px-2 py-1 bg-black/40 rounded border border-[var(--color-border-card)] shrink-0">
        <Terminal size={12} />
        <span className="font-bold tracking-widest uppercase">EXECUTION_TERMINAL_v1.0.4</span>
        <span className="ml-auto animate-pulse">_</span>
      </div>
      
      <div className="flex-1 overflow-y-auto pr-2 space-y-1 max-h-[300px] scrollbar-thin scrollbar-track-transparent scrollbar-thumb-[var(--color-neon-green)]/20">
        {safeLogs.length === 0 ? (
           <div className="text-gray-600 text-center mt-4">A aguardar logs do sistema...</div>
        ) : (
          safeLogs.map((log, index) => {
            let timeStr = "00:00:00";
            try {
              timeStr = new Date(log.timestamp).toISOString().split('T')[1].slice(0, 12);
            } catch(e) {}
            
            let actionColor = 'text-gray-400';
            if (log.action === 'BUY') actionColor = 'text-green-400 font-bold bg-green-900/20 px-1 rounded';
            if (log.action === 'SELL') actionColor = 'text-red-400 font-bold bg-red-900/20 px-1 rounded';
            if (log.action === 'SCAN') actionColor = 'text-blue-400';

            const logIdStr = String(log.tokenId || 'UNK');
            const latencyStr = String(log.latency || 0).padStart(3, ' ');

            return (
              <div key={`${log.id}-${index}`} className="flex items-start gap-2 hover:bg-white/5 p-0.5 rounded transition-colors">
                <span className="text-gray-600 shrink-0">[{timeStr}]</span>
                
                <span className="text-[var(--color-neon-blue)] font-bold shrink-0">
                  [{log.agent || 'SYSTEM'}]
                </span>

                <span className={`shrink-0 ${(log.latency || 0) > 50 ? 'text-yellow-500' : 'text-gray-500'}`}>
                  ({latencyStr}ms)
                </span>
                
                <span className={`shrink-0 w-12 ${actionColor}`}>{log.action}</span>
                <span className="text-gray-300 shrink-0">|</span>
                <span className="text-purple-400 shrink-0 w-24 truncate" title={logIdStr}>{logIdStr}</span>
                <span className="text-gray-300 shrink-0">|</span>
                <span className="text-[var(--color-neon-green)]">{log.executionTime || 0}ms</span>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}