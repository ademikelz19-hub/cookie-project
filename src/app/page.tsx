'use client';

import React, { useState } from 'react';
import WalletButton from '@/components/WalletButton';
import Dashboard from '@/components/Dashboard';
import IntentConsole from '@/components/IntentConsole';
import ExecutionLogs from '@/components/ExecutionLogs';
import BridgeModal from '@/components/BridgeModal';
import {
  Cookie,
  Shield,
  Layers,
  ArrowRightLeft,
  Sparkles,
  ExternalLink,
  BookOpen,
} from 'lucide-react';

export default function Home() {
  const [isBridgeOpen, setIsBridgeOpen] = useState(false);

  return (
    <div className="min-h-screen flex flex-col bg-[#08090d] text-neutral-100">
      {/* Top Navigation */}
      <header className="border-b border-cyber-border/80 bg-cyber-card/60 backdrop-blur-md sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-cookie-500 to-cookie-300 flex items-center justify-center shadow-lg shadow-cookie-500/20">
              <Cookie className="w-5 h-5 text-neutral-950 font-bold" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-extrabold tracking-tight text-white font-mono text-base">
                  AUTARCH
                </span>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-cookie-500/20 text-cookie-300 border border-cookie-500/30 font-semibold">
                  Cookie Chain SVM
                </span>
              </div>
              <span className="text-[10px] text-neutral-400 block -mt-0.5 font-mono">
                Autonomous Intent-Centric Yield Infrastructure
              </span>
            </div>
          </div>

          {/* Right Action Bar */}
          <div className="flex items-center gap-3">
            {/* Bridge Modal Trigger */}
            <button
              onClick={() => setIsBridgeOpen(true)}
              className="flex items-center gap-1.5 text-xs font-mono bg-cyber-bg hover:bg-neutral-800 border border-cyber-border text-neutral-300 hover:text-white px-3 py-1.5 rounded-lg transition-colors"
            >
              <ArrowRightLeft className="w-3.5 h-3.5 text-cookie-300" />
              <span className="hidden sm:inline">Bridge via Hyperlane</span>
            </button>

            {/* Nightly Wallet Connection Button */}
            <WalletButton />
          </div>
        </div>
      </header>

      {/* Main Content Body */}
      <main className="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        {/* Banner with Protocol Value Prop */}
        <div className="relative overflow-hidden rounded-2xl border border-cyber-border bg-gradient-to-r from-cyber-card via-[#161824] to-cyber-card p-6 sm:p-8">
          <div className="absolute top-0 right-0 w-96 h-96 bg-cookie-400/5 rounded-full blur-3xl pointer-events-none" />
          <div className="relative z-10 max-w-3xl">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cookie-500/10 border border-cookie-500/30 text-cookie-300 text-xs font-mono font-medium mb-3">
              <Sparkles className="w-3.5 h-3.5" />
              <span>Superteam Earn Bounty Submission</span>
            </div>
            <h1 className="text-2xl sm:text-4xl font-extrabold text-white tracking-tight leading-tight">
              Self-Executing Yield Infrastructure Powered by AI Agents.
            </h1>
            <p className="mt-2 text-sm sm:text-base text-neutral-400 leading-relaxed font-sans">
              Connect your <strong className="text-neutral-200">Nightly Wallet</strong>, deposit into your non-custodial Smart Vault PDA, and type your intent. The <strong className="text-neutral-200">cookie-mcp</strong> agent engine routes liquidity across bCOOK staking, Cookiebox AMMs, and Baked Bazaar Grail Pot arbitrage under strict <strong className="text-neutral-200">PolicyLayer</strong> security rules.
            </p>
          </div>
        </div>

        {/* Dashboard Analytics & Metrics */}
        <section>
          <Dashboard />
        </section>

        {/* Intent Terminal + Live Execution Logs Grid */}
        <section className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          <div className="lg:col-span-7">
            <IntentConsole />
          </div>
          <div className="lg:col-span-5">
            <ExecutionLogs />
          </div>
        </section>

        {/* Ecosystem Composability Matrix */}
        <section className="bg-cyber-card border border-cyber-border rounded-xl p-6">
          <div className="flex items-center justify-between pb-4 border-b border-cyber-border mb-4">
            <div>
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <Layers className="w-5 h-5 text-cookie-300" />
                Integrated Cookie Chain Primitives
              </h3>
              <p className="text-xs text-neutral-400 mt-1">
                Full-spectrum composability with live ecosystem protocols.
              </p>
            </div>
            <div className="flex items-center gap-2 text-xs font-mono text-neutral-400">
              <Shield className="w-4 h-4 text-emerald-400" />
              <span>Non-Custodial PDA Architecture</span>
            </div>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-3 text-center">
            <div className="p-3 rounded-lg bg-cyber-bg border border-cyber-border/70 hover:border-cookie-400/40 transition-colors">
              <div className="text-xs font-bold text-white">bCOOK</div>
              <div className="text-[11px] text-neutral-400 mt-1">SPL Stake Pool</div>
            </div>
            <div className="p-3 rounded-lg bg-cyber-bg border border-cyber-border/70 hover:border-cookie-400/40 transition-colors">
              <div className="text-xs font-bold text-white">Cookiebox</div>
              <div className="text-[11px] text-neutral-400 mt-1">DAMM v2 / CLMM</div>
            </div>
            <div className="p-3 rounded-lg bg-cyber-bg border border-cyber-border/70 hover:border-cookie-400/40 transition-colors">
              <div className="text-xs font-bold text-white">Cookieswap</div>
              <div className="text-[11px] text-neutral-400 mt-1">SAMM AMM</div>
            </div>
            <div className="p-3 rounded-lg bg-cyber-bg border border-cyber-border/70 hover:border-cookie-400/40 transition-colors">
              <div className="text-xs font-bold text-white">Candy Shop</div>
              <div className="text-[11px] text-neutral-400 mt-1">DEX Aggregator</div>
            </div>
            <div className="p-3 rounded-lg bg-cyber-bg border border-cyber-border/70 hover:border-cookie-400/40 transition-colors">
              <div className="text-xs font-bold text-white">Baked Bazaar</div>
              <div className="text-[11px] text-neutral-400 mt-1">Metaplex Auction</div>
            </div>
            <div className="p-3 rounded-lg bg-cyber-bg border border-cyber-border/70 hover:border-cookie-400/40 transition-colors">
              <div className="text-xs font-bold text-white">Hyperlane</div>
              <div className="text-[11px] text-neutral-400 mt-1">Warp Routes</div>
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="border-t border-cyber-border/80 bg-cyber-card/40 py-6 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs font-mono text-neutral-500">
          <div>
            <span>Autarch Protocol © 2026. Built on Cookie Chain (SVM). MIT License.</span>
          </div>
          <div className="flex items-center gap-4">
            <a
              href="https://t.me/TheCookieNetChain"
              target="_blank"
              rel="noreferrer"
              className="hover:text-cookie-300 transition-colors flex items-center gap-1"
            >
              <span>Cookie Chain Telegram</span>
              <ExternalLink className="w-3 h-3" />
            </a>
            <a
              href="https://cookiescan.io"
              target="_blank"
              rel="noreferrer"
              className="hover:text-cookie-300 transition-colors flex items-center gap-1"
            >
              <span>CookieScan Explorer</span>
              <ExternalLink className="w-3 h-3" />
            </a>
          </div>
        </div>
      </footer>

      {/* Hyperlane Warp Route Modal */}
      <BridgeModal isOpen={isBridgeOpen} onClose={() => setIsBridgeOpen(false)} />
    </div>
  );
}
