import React from 'react';
import { LogEntry } from '../types';
import { Terminal } from 'lucide-react';

interface ExecutionTerminalProps {
  logs: LogEntry[];
}

export function ExecutionTerminal({ logs }: ExecutionTerminalProps) {
  // Reverse logs to show newest at the top
  const reversedLogs = [...logs].reverse();

  return (
    <div className="flex flex-col h-full font-mono text-[10px] overflow-hidden">
      <div className="flex items-center gap-2 text-[var(--color-neon-green)] mb-2 px-2 py-1 bg-black/40 rounded border border-[var(--color-border-card)] shrink-0">
        <Terminal size={12} />
        <span className="font-bold tracking-widest uppercase">EXECUTION_TERMINAL_v1.0.4</span>
        <span className="ml-auto animate-pulse">_</span>
      </div>
      
      {/* Strict fixed height container with custom scrollbar */}
      <div className="flex-1 overflow-y-auto pr-2 space-y-1 max-h-[300px] scrollbar-thin scrollbar-track-transparent scrollbar-thumb-[var(--color-neon-green)]/20 hover:scrollbar-thumb-[var(--color-neon-green)]/40">
        {reversedLogs.map((log) => {
          const date = new Date(log.timestamp);
          const timeStr = date.toISOString().split('T')[1].slice(0, 12); // HH:mm:ss.SSS
          
          let actionColor = 'text-gray-400';
          if (log.action === 'BUY') actionColor = 'text-green-400 font-bold';
          if (log.action === 'SELL') actionColor = 'text-red-400 font-bold';
          if (log.action === 'SCAN') actionColor = 'text-blue-400';

          return (
            <div key={log.id} className="flex items-start gap-2 hover:bg-white/5 p-0.5 rounded transition-colors">
              <span className="text-gray-600 shrink-0">[{timeStr}]</span>
              <span className={`shrink-0 ${log.latency > 50 ? 'text-yellow-500' : 'text-gray-500'}`}>
                [{log.latency.toString().padStart(3, ' ')}ms]
              </span>
              <span className="text-gray-400 shrink-0">AGENT_ACTION:</span>
              <span className={`shrink-0 w-12 ${actionColor}`}>[{log.action}]</span>
              <span className="text-gray-300 shrink-0">|</span>
              <span className="text-purple-400 shrink-0 w-24 truncate">{log.tokenId}</span>
              <span className="text-gray-300 shrink-0">|</span>
              <span className="text-gray-500 shrink-0">EXECUTION_TIME:</span>
              <span className="text-[var(--color-neon-green)]">{log.executionTime}ms</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
