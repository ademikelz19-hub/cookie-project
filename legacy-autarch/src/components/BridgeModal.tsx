'use client';

import React, { useState } from 'react';
import { useNightly } from '@/contexts/SolanaProvider';
import { X, ArrowRight, ExternalLink, ShieldCheck, Zap, Info } from 'lucide-react';

interface BridgeModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const BridgeModal: React.FC<BridgeModalProps> = ({ isOpen, onClose }) => {
  const { publicKey } = useNightly();
  const [originChain, setOriginChain] = useState('Ethereum');
  const [asset, setAsset] = useState('USDC');
  const [amount, setAmount] = useState('100');

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
      <div className="bg-cyber-card border border-cyber-border rounded-2xl w-full max-w-lg p-6 shadow-2xl relative">
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-5 right-5 text-neutral-400 hover:text-white transition-colors"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Modal Header */}
        <div className="mb-5">
          <div className="flex items-center gap-2 text-cookie-300 font-mono text-xs font-semibold uppercase tracking-wider mb-1">
            <Zap className="w-4 h-4" />
            <span>Hyperlane Warp Routes</span>
          </div>
          <h2 className="text-xl font-bold text-white">Bridge Assets to Cookie Chain</h2>
          <p className="text-xs text-neutral-400 mt-1">
            Permissionless cross-chain liquidity ingestion directly into your Autarch Smart Vault PDA.
          </p>
        </div>

        {/* Origin Chain & Asset Selector */}
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-mono text-neutral-400 mb-1.5">Origin Network</label>
              <select
                value={originChain}
                onChange={(e) => setOriginChain(e.target.value)}
                className="w-full bg-cyber-bg border border-cyber-border rounded-lg px-3 py-2 text-sm text-neutral-200 font-mono focus:border-cookie-400 outline-none"
              >
                <option value="Ethereum">Ethereum (EVM)</option>
                <option value="Solana">Solana (SVM)</option>
                <option value="Arbitrum">Arbitrum (EVM)</option>
                <option value="Celestia">Celestia (Cosmos)</option>
                <option value="Base">Base (EVM)</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-mono text-neutral-400 mb-1.5">Asset</label>
              <select
                value={asset}
                onChange={(e) => setAsset(e.target.value)}
                className="w-full bg-cyber-bg border border-cyber-border rounded-lg px-3 py-2 text-sm text-neutral-200 font-mono focus:border-cookie-400 outline-none"
              >
                <option value="USDC">USDC (Stablecoin)</option>
                <option value="TIA">TIA (Celestia)</option>
                <option value="SOL">SOL (Native)</option>
                <option value="ETH">ETH (Native)</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-xs font-mono text-neutral-400 mb-1.5">Deposit Amount</label>
            <input
              type="number"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              className="w-full bg-cyber-bg border border-cyber-border rounded-lg px-3 py-2 text-sm text-neutral-200 font-mono focus:border-cookie-400 outline-none"
              placeholder="0.00"
            />
          </div>

          {/* Destination Preview */}
          <div className="p-3.5 rounded-lg bg-cyber-bg border border-cyber-border text-xs space-y-2">
            <div className="flex items-center justify-between text-neutral-400 font-mono">
              <span>Destination Chain:</span>
              <span className="text-white font-semibold">Cookie Chain SVM</span>
            </div>
            <div className="flex items-center justify-between text-neutral-400 font-mono">
              <span>Target Vault Recipient:</span>
              <span className="text-cookie-300 font-mono">
                {publicKey ? `${publicKey.slice(0, 6)}...${publicKey.slice(-4)}` : 'Connect Nightly'}
              </span>
            </div>
            <div className="flex items-center justify-between text-neutral-400 font-mono">
              <span>Slippage / Relayer:</span>
              <span className="text-emerald-400 font-semibold">0% (Warp Route)</span>
            </div>
          </div>

          {/* Informational Callout */}
          <div className="flex items-start gap-2.5 p-3 rounded-lg bg-cookie-500/10 border border-cookie-500/20 text-xs text-cookie-200">
            <Info className="w-4 h-4 text-cookie-300 shrink-0 mt-0.5" />
            <p>
              Once initiated, the Hyperlane relayer will finalize the interchain message. The Autarch backend agent detects confirmation via the <code className="text-cookie-300">bridge_status</code> tool and immediately deploys your capital into active yield strategies.
            </p>
          </div>
        </div>

        {/* Modal Buttons */}
        <div className="mt-6 flex items-center justify-end gap-3">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg text-sm font-mono text-neutral-400 hover:text-white transition-colors"
          >
            Cancel
          </button>
          <a
            href="https://www.hyperlane.xyz"
            target="_blank"
            rel="noreferrer"
            className="flex items-center gap-2 bg-cookie-400 hover:bg-cookie-500 text-neutral-950 font-bold px-5 py-2 rounded-lg text-sm font-mono shadow-lg transition-all"
          >
            <span>Proceed via Hyperlane</span>
            <ExternalLink className="w-4 h-4" />
          </a>
        </div>
      </div>
    </div>
  );
};

export default BridgeModal;
