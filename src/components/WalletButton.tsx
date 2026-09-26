'use client';

import React from 'react';
import { useNightly } from '@/contexts/SolanaProvider';
import { Wallet, Globe, AlertTriangle, CheckCircle2, RefreshCw, ExternalLink } from 'lucide-react';

export const WalletButton: React.FC = () => {
  const {
    connected,
    publicKey,
    connecting,
    isNightlyInstalled,
    isCookieChainNetwork,
    connect,
    disconnect,
    switchToCookieChain,
  } = useNightly();

  const truncate = (addr: string) => `${addr.slice(0, 4)}...${addr.slice(-4)}`;

  if (!connected || !publicKey) {
    return (
      <div className="flex items-center gap-3">
        {!isNightlyInstalled && (
          <a
            href="https://nightly.app"
            target="_blank"
            rel="noreferrer"
            className="text-xs text-cookie-300 hover:underline hidden sm:flex items-center gap-1"
          >
            Get Nightly Wallet
            <ExternalLink className="w-3 h-3" />
          </a>
        )}
        <button
          onClick={connect}
          disabled={connecting}
          className="flex items-center gap-2 bg-gradient-to-r from-cookie-400 to-cookie-300 hover:from-cookie-500 hover:to-cookie-400 disabled:opacity-50 text-neutral-950 font-semibold px-4 py-2 rounded-lg shadow-lg shadow-cookie-500/20 transition-all text-sm"
        >
          <Wallet className="w-4 h-4" />
          {connecting ? 'Connecting...' : isNightlyInstalled ? 'Connect Nightly' : 'Install Nightly'}
        </button>
      </div>
    );
  }

  return (
    <div className="flex flex-wrap items-center gap-2">
      {/* Network Badge */}
      <div
        className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg border text-xs font-mono font-medium ${
          isCookieChainNetwork
            ? 'bg-emerald-950/40 border-emerald-500/40 text-emerald-300'
            : 'bg-amber-950/40 border-amber-500/40 text-amber-300'
        }`}
      >
        <Globe className="w-3.5 h-3.5" />
        <span>{isCookieChainNetwork ? 'Cookie Chain SVM' : 'Switch Network'}</span>
        {isCookieChainNetwork ? (
          <CheckCircle2 className="w-3 h-3 text-emerald-400" />
        ) : (
          <AlertTriangle className="w-3 h-3 text-amber-400" />
        )}
      </div>

      {/* Switch Network Button if not on Cookie Chain */}
      {!isCookieChainNetwork && (
        <button
          onClick={switchToCookieChain}
          className="flex items-center gap-1.5 bg-amber-500/20 hover:bg-amber-500/30 border border-amber-500/50 text-amber-200 text-xs px-2.5 py-1.5 rounded-lg transition-colors font-mono"
        >
          <RefreshCw className="w-3 h-3" />
          <span className="hidden sm:inline">Switch to Cookie Chain</span>
        </button>
      )}

      {/* Wallet Pill + Disconnect */}
      <div className="flex items-center gap-2 bg-cyber-card border border-cyber-border px-3 py-1.5 rounded-lg">
        <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
        <span className="font-mono text-xs text-neutral-200">{truncate(publicKey)}</span>
        <button
          onClick={disconnect}
          className="text-xs text-neutral-400 hover:text-rose-400 transition-colors ml-1"
        >
          Disconnect
        </button>
      </div>
    </div>
  );
};

export default WalletButton;
