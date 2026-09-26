'use client';

import React, { useEffect, useState, useCallback } from 'react';
import { useNightly, COOKIE_CHAIN_RPC } from '@/contexts/SolanaProvider';
import { Connection, LAMPORTS_PER_SOL, PublicKey } from '@solana/web3.js';
import {
  Coins,
  TrendingUp,
  Ticket,
  Lock,
  PieChart,
  Layers,
  ArrowUpRight,
  Sparkles,
} from 'lucide-react';

interface MetricState {
  cookBalance: number;
  bCookStaked: number;
  vaultTvlCook: number;
  bCookApy: number;
  cookieboxApy: number;
  grailPotTickets: number;
  grailPotJackpotCook: number;
  activePoolsCount: number;
}

export const Dashboard: React.FC = () => {
  const { connected, publicKey } = useNightly();
  const connection = new Connection(COOKIE_CHAIN_RPC, 'confirmed');

  const [metrics, setMetrics] = useState<MetricState>({
    cookBalance: 0,
    bCookStaked: 42.5,
    vaultTvlCook: 1850.25,
    bCookApy: 7.8,
    cookieboxApy: 22.4,
    grailPotTickets: 148,
    grailPotJackpotCook: 125000,
    activePoolsCount: 3,
  });

  const [isLoading, setIsLoading] = useState(false);

  // Fetch actual COOK (SVM native lamports) balance from Cookie Chain RPC
  const fetchBalance = useCallback(async () => {
    if (!connected || !publicKey) return;
    try {
      setIsLoading(true);
      const balanceLamports = await connection.getBalance(new PublicKey(publicKey), 'confirmed');
      const cook = balanceLamports / LAMPORTS_PER_SOL;
      setMetrics((prev) => ({
        ...prev,
        cookBalance: Number(cook.toFixed(4)),
      }));
    } catch (err) {
      console.warn('[Autarch Dashboard] RPC balance fetch error (using fallback):', err);
    } finally {
      setIsLoading(false);
    }
  }, [connected, publicKey, connection]);

  useEffect(() => {
    fetchBalance();
    const interval = setInterval(fetchBalance, 10000);
    return () => clearInterval(interval);
  }, [fetchBalance]);

  return (
    <div className="space-y-6">
      {/* Top Banner / Hero Metric */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {/* $COOK Balance */}
        <div className="bg-cyber-card border border-cyber-border rounded-xl p-5 hover:border-cookie-400/50 transition-all">
          <div className="flex items-center justify-between text-neutral-400 mb-2">
            <span className="text-xs uppercase font-mono tracking-wider">Wallet Balance</span>
            <Coins className="w-4 h-4 text-cookie-300" />
          </div>
          <div className="text-2xl font-bold font-mono text-white flex items-baseline gap-2">
            <span>{connected ? metrics.cookBalance.toLocaleString() : '---'}</span>
            <span className="text-xs font-semibold text-cookie-300">$COOK</span>
          </div>
          <div className="mt-2 text-xs text-neutral-400 flex items-center justify-between">
            <span>Cookie Chain SVM</span>
            {isLoading && <span className="text-cookie-300 animate-pulse text-[10px]">Updating...</span>}
          </div>
        </div>

        {/* bCOOK Staked */}
        <div className="bg-cyber-card border border-cyber-border rounded-xl p-5 hover:border-emerald-500/50 transition-all">
          <div className="flex items-center justify-between text-neutral-400 mb-2">
            <span className="text-xs uppercase font-mono tracking-wider">bCOOK Liquid Staked</span>
            <Lock className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-bold font-mono text-white flex items-baseline gap-2">
            <span>{connected ? metrics.bCookStaked.toLocaleString() : '---'}</span>
            <span className="text-xs font-semibold text-emerald-400">bCOOK</span>
          </div>
          <div className="mt-2 text-xs text-emerald-400/90 flex items-center gap-1 font-mono">
            <TrendingUp className="w-3 h-3" />
            <span>{metrics.bCookApy}% Base APY (SPL Stake Pool)</span>
          </div>
        </div>

        {/* Grail Pot Jackpot & Tickets */}
        <div className="bg-cyber-card border border-cyber-border rounded-xl p-5 hover:border-amber-400/50 transition-all relative overflow-hidden group">
          <div className="absolute top-0 right-0 w-24 h-24 bg-amber-500/5 rounded-full blur-xl pointer-events-none group-hover:bg-amber-500/10 transition-all" />
          <div className="flex items-center justify-between text-neutral-400 mb-2">
            <span className="text-xs uppercase font-mono tracking-wider">Grail Pot Tickets</span>
            <Ticket className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-2xl font-bold font-mono text-amber-300 flex items-baseline gap-2">
            <span>{connected ? metrics.grailPotTickets.toLocaleString() : '---'}</span>
            <span className="text-xs font-semibold text-amber-400/80">Tickets</span>
          </div>
          <div className="mt-2 text-xs text-neutral-400 flex items-center justify-between">
            <span className="text-neutral-400">Jackpot Pool:</span>
            <span className="font-mono text-amber-300 font-semibold">
              {metrics.grailPotJackpotCook.toLocaleString()} $COOK
            </span>
          </div>
        </div>

        {/* Total Vault TVL */}
        <div className="bg-cyber-card border border-cyber-border rounded-xl p-5 hover:border-cyber-purple/50 transition-all">
          <div className="flex items-center justify-between text-neutral-400 mb-2">
            <span className="text-xs uppercase font-mono tracking-wider">Smart Vault TVL</span>
            <PieChart className="w-4 h-4 text-purple-400" />
          </div>
          <div className="text-2xl font-bold font-mono text-white flex items-baseline gap-2">
            <span>{connected ? metrics.vaultTvlCook.toLocaleString() : '---'}</span>
            <span className="text-xs font-semibold text-purple-400">$COOK</span>
          </div>
          <div className="mt-2 text-xs text-purple-300/80 flex items-center justify-between font-mono">
            <span>Non-Custodial PDA</span>
            <span className="text-emerald-400 font-semibold">+18.4% Net APY</span>
          </div>
        </div>
      </div>

      {/* Yield Vectors Breakdown */}
      <div className="bg-cyber-card border border-cyber-border rounded-xl p-6">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-4 border-b border-cyber-border">
          <div>
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              <Layers className="w-5 h-5 text-cookie-300" />
              Active Yield Vectors & Composable Pools
            </h3>
            <p className="text-xs text-neutral-400 mt-1">
              Real-time positions managed autonomously across Cookiebox, Cookieswap & Baked Bazaar.
            </p>
          </div>
          <div className="flex items-center gap-2 text-xs font-mono bg-cyber-bg px-3 py-1.5 rounded-lg border border-cyber-border text-cookie-300">
            <Sparkles className="w-3.5 h-3.5 text-cookie-300" />
            <span>PolicyLayer Monitored</span>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-5">
          {/* Vector 1 */}
          <div className="p-4 rounded-lg bg-cyber-bg border border-cyber-border/60 hover:border-cyber-border transition-colors">
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-semibold px-2 py-0.5 rounded bg-blue-500/10 text-blue-300 border border-blue-500/20">
                Liquid Staking
              </span>
              <a
                href="https://cookiescan.io"
                target="_blank"
                rel="noreferrer"
                className="text-neutral-400 hover:text-white"
              >
                <ArrowUpRight className="w-4 h-4" />
              </a>
            </div>
            <div className="text-sm font-semibold text-neutral-200">bCOOK SPL Stake Pool</div>
            <div className="text-xs text-neutral-400 mt-1">
              Idle capital accumulates base-layer staking yield while receipt tokens stay composable.
            </div>
            <div className="mt-4 pt-3 border-t border-cyber-border flex items-center justify-between text-xs font-mono">
              <span className="text-neutral-400">Current APY</span>
              <span className="text-emerald-400 font-bold">7.8%</span>
            </div>
          </div>

          {/* Vector 2 */}
          <div className="p-4 rounded-lg bg-cyber-bg border border-cyber-border/60 hover:border-cyber-border transition-colors">
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-semibold px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-300 border border-emerald-500/20">
                AMM Liquidity
              </span>
              <a
                href="https://cookiescan.io"
                target="_blank"
                rel="noreferrer"
                className="text-neutral-400 hover:text-white"
              >
                <ArrowUpRight className="w-4 h-4" />
              </a>
            </div>
            <div className="text-sm font-semibold text-neutral-200">Cookiebox DAMM v2 / CLMM</div>
            <div className="text-xs text-neutral-400 mt-1">
              Dynamic pool rebalancing with Candy Shop trade routing and automated fee compounding.
            </div>
            <div className="mt-4 pt-3 border-t border-cyber-border flex items-center justify-between text-xs font-mono">
              <span className="text-neutral-400">Fee Yield</span>
              <span className="text-emerald-400 font-bold">22.4% APY</span>
            </div>
          </div>

          {/* Vector 3 */}
          <div className="p-4 rounded-lg bg-cyber-bg border border-cyber-border/60 hover:border-cyber-border transition-colors">
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-semibold px-2 py-0.5 rounded bg-amber-500/10 text-amber-300 border border-amber-500/20">
                Gamified NFT Alpha
              </span>
              <a
                href="https://bakedbazaar.art/grail-pot"
                target="_blank"
                rel="noreferrer"
                className="text-neutral-400 hover:text-white"
              >
                <ArrowUpRight className="w-4 h-4" />
              </a>
            </div>
            <div className="text-sm font-semibold text-neutral-200">Baked Bazaar Grail Pot Engine</div>
            <div className="text-xs text-neutral-400 mt-1">
              High-frequency, break-even floor bids on liquid collections generating zero-cost jackpot tickets.
            </div>
            <div className="mt-4 pt-3 border-t border-cyber-border flex items-center justify-between text-xs font-mono">
              <span className="text-neutral-400">Estimated Win Prob.</span>
              <span className="text-amber-300 font-bold">4.2% / Round</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
