import React, { useState } from 'react';
import { BotCredentials } from '../types';
import { Wallet, X, RefreshCw, Save } from 'lucide-react';

interface WalletModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSync: (token: string) => Promise<void>;
}

export function WalletModal({ isOpen, onClose, onSync }: WalletModalProps) {
  const [token, setToken] = useState('');
  const [isSyncing, setIsSyncing] = useState(false);

  if (!isOpen) return null;

  const handleSync = async () => {
    if (!token) return;
    setIsSyncing(true);
    try {
      await onSync(token);
    } finally {
      setIsSyncing(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm">
      <div className="bg-[var(--color-bg-card)] border border-[var(--color-border-card)] rounded-lg w-full max-w-md overflow-hidden shadow-2xl shadow-[var(--color-neon-green)]/5">
        
        {/* Header */}
        <div className="px-4 py-3 border-b border-[var(--color-border-card)] flex items-center justify-between bg-black/40">
          <div className="flex items-center gap-2">
            <Wallet size={16} className="text-[var(--color-neon-green)]" />
            <h3 className="text-sm font-bold tracking-wider uppercase text-gray-200">Wallet Configuration</h3>
          </div>
          <button 
            onClick={onClose}
            className="text-gray-500 hover:text-gray-300 transition-colors"
          >
            <X size={16} />
          </button>
        </div>

        {/* Body */}
        <div className="p-6 space-y-6">
          <div className="space-y-2">
            <label className="text-xs text-gray-400 font-bold tracking-wider flex items-center gap-2">
              WALLET TOKEN (PRIVATE KEY)
            </label>
            <input 
              type="password" 
              value={token}
              onChange={(e) => setToken(e.target.value)}
              placeholder="Enter your private key..."
              className="w-full bg-black/60 border border-[var(--color-border-card)] rounded px-3 py-2 text-sm text-[var(--color-neon-green)] font-mono focus:outline-none focus:border-[var(--color-neon-green)] transition-colors placeholder:text-gray-700"
            />
            <p className="text-[10px] text-gray-500">
              The backend will handle derivation. Your key is never stored locally.
            </p>
          </div>

          {/* Actions */}
          <div className="flex gap-3 pt-2">
            <button 
              onClick={handleSync}
              disabled={isSyncing || !token}
              className="flex-1 bg-black border border-[var(--color-border-card)] hover:border-[var(--color-neon-green)] text-gray-300 hover:text-[var(--color-neon-green)] rounded py-2 flex items-center justify-center gap-2 text-xs font-bold transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <RefreshCw size={14} className={isSyncing ? "animate-spin" : ""} />
              {isSyncing ? 'SYNCHRONIZING...' : 'SYNCHRONIZE'}
            </button>
            <button 
              onClick={onClose}
              className="flex-1 bg-[var(--color-neon-green)]/10 border border-[var(--color-neon-green)]/50 hover:bg-[var(--color-neon-green)]/20 text-[var(--color-neon-green)] rounded py-2 flex items-center justify-center gap-2 text-xs font-bold transition-colors"
            >
              <Save size={14} />
              SAVE & CLOSE
            </button>
          </div>
        </div>

      </div>
    </div>
  );
}
