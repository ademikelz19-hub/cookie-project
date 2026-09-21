# Autarch Protocol: Autonomous Intent-Centric Yield Infrastructure on Cookie Chain

> **Autonomous, AI-driven, intent-centric Smart Vault & Yield Terminal built natively for Cookie Chain (SVM).**  
> Engineered for the **Superteam Earn Cookie Chain Hackathon Bounty**.

---

## 🌟 Executive Overview

**Autarch Protocol** shifts the Web3 interaction paradigm from manual, imperative transactions to autonomous, declarative intent execution. 

Instead of forcing users to manually bridge assets, calculate slippage across disjoint AMMs, manage concentrated liquidity positions, stake into liquid staking pools, and monitor NFT marketplaces, Autarch allows users to connect via the **Nightly Wallet**, deposit capital into a non-custodial **Program Derived Address (PDA) Smart Vault**, and submit a natural-language directive (e.g., *"Stake 40% of my capital in bCOOK, allocate 40% to Cookiebox DAMM v2 pools, and use 20% to farm Grail Pot jackpot tickets on Baked Bazaar"*).

Powered by the `cookie-mcp` (Model Context Protocol) integration, an intelligent agent framework, and strict **PolicyLayer** security guardrails, the Autarch Agent translates high-level intentions into real-time, deterministic on-chain actions across Cookie Chain's ecosystem primitives.

```
                                  ┌────────────────────────────────────────────────────────┐
                                  │                     USER INTERFACE                     │
                                  │            Next.js App Router + Tailwind CSS           │
                                  │      Nightly Wallet Standard (@solana/wallet-adapter)  │
                                  └──────────────────────────┬─────────────────────────────┘
                                                             │ 1. Natural Language Intent &
                                                             │    Deposit Delegation
                                                             ▼
                                  ┌────────────────────────────────────────────────────────┐
                                  │               AUTARCH AGENT ORCHESTRATOR               │
                                  │          Node.js Express + LangChain Framework         │
                                  └───────────────┬────────────────────────┬───────────────┘
                                                  │                        │
                                   2. Policy Check│                        │ 3. Tool Invocation
                                                  ▼                        ▼
               ┌──────────────────────────────────────────────┐ ┌──────────────────────────────────────┐
               │              POLICYGUARD GATEWAY             │ │          COOKIE-MCP CLIENT           │
               │   PolicyLayer Enforcement (docs/policy.json) │ │   STDIO client -> cookie-mcp server  │
               │   - Denies lock_liquidity & cancel_listing   │ │   32 Tools across 5 Categories       │
               │   - Enforces max 100 $COOK / 500 BPS limits  │ │   (Financial, Read, Execute, Write)  │
               │   - Rate limits bridge_status & get_pools    │ └──────────────────┬───────────────────┘
               └──────────────────────────────────────────────┘                    │
                                                                                   │ 4. Signs CPI Instruction
                                                                                   │    Payloads
                                                                                   ▼
                                  ┌────────────────────────────────────────────────────────┐
                                  │            ON-CHAIN AUTARCH SMART VAULT (PDA)          │
                                  │              Rust / Anchor SVM Smart Contract          │
                                  │       - Restricted delegated authority via agent key   │
                                  │       - Whitelisted CPI destinations only              │
                                  │       - Invariant: Withdrawals mathematically return   │
                                  │         only to owner's originating Nightly address    │
                                  └───────────────────────┬────────────────────────────────┘
                                                          │ 5. Cross-Program Invocations (CPI)
                     ┌────────────────────────────────────┼────────────────────────────────────┐
                     ▼                                    ▼                                    ▼
       ┌──────────────────────────┐         ┌──────────────────────────┐         ┌──────────────────────────┐
       │     LIQUID STAKING       │         │       DEX & SWAPS        │         │   GAMIFIED NFT ALPHA     │
       │    bCOOK SPL Stake Pool  │         │   Cookiebox (DAMM/CLMM)  │         │  Baked Bazaar Auction    │
       │  - Idle capital yields   │         │   Cookieswap (SAMM)      │         │  - Floor arbitrage flips │
       │  - Zero liquidity loss   │         │   Candy Shop Aggregator  │         │  - Grail Pot Ticket Farm │
       └──────────────────────────┘         └──────────────────────────┘         └──────────────────────────┘
```

---

## 🚀 Key Features

1. **Native Nightly Wallet Standard Integration**:
   - Zero legacy wallet bloat; initializes with standard wallet discovery (`wallets={[]}`).
   - Programmatic SVM network verification via `window.nightly.solana.changeNetwork()`.
   - Direct connection to `https://rpc.cookiescan.io`.

2. **Autonomous Intent Engine (cookie-mcp + LangChain)**:
   - Evaluates user intents into sequential tool executions.
   - Leverages the official `cookie-mcp` suite (32 tools covering swaps, pools, staking, bridging, and NFT marketplace actions).

3. **PolicyLayer Security Guardrails (`docs/policy.json`)**:
   - Hard bans on destructive operations (`lock_liquidity`, `cancel_listing`).
   - Transaction spend ceilings (`COOKIE_MAX_TRADE_COOK = 100 $COOK`).
   - Slippage protection bounds (`COOKIE_SLIPPAGE_BPS = 500` / 5%).
   - RPC exhaustion defense (capped at 60 requests/min on `bridge_status` & `get_pools`).

4. **Multi-Vector Yield Generation**:
   - **bCOOK Liquid Staking**: Idle token yield with liquid staking receipt tokens.
   - **Cookiebox & Cookieswap**: Concentrated & dynamic AMM liquidity farming with automatic fee claiming and compounding.
   - **Grail Pot NFT Arbitrage Engine**: High-frequency, break-even bidding on liquid collections (e.g., Sesamian) through Baked Bazaar's Metaplex Auction House to continuously farm tickets for the 0.5% progressive $COOK jackpot.
   - **Hyperlane Interchain Warp Routes**: Seamless asset ingestion (USDC, TIA, SOL, ETH) across EVM, Solana, and Cosmos into the Smart Vault.

5. **Non-Custodial Anchor Smart Vault**:
   - Safe PDA derivation per user (`[b"vault", user_pubkey]`).
   - AI agent only holds delegated authority to trigger whitelisted CPI calls.
   - Invariant: Unstaked or withdrawn funds can never route to an EOA or third party—only back to the user's connected wallet address.

---

## 📁 Repository Structure

```
autarch-protocol/
├── frontend/                     # Next.js App Router Client
│   ├── src/
│   │   ├── app/                  # Layout, Home, Dashboard pages
│   │   │   ├── globals.css       # Tailwind CSS styles & animations
│   │   │   ├── layout.tsx        # Root layout with SolanaProvider
│   │   │   └── page.tsx          # Terminal, Intent input, & Metrics UI
│   │   ├── components/           # UI Components
│   │   │   ├── Dashboard.tsx     # Real-time balances, APY, TVL, Grail Pot stats
│   │   │   ├── ExecutionLogs.tsx # WebSocket RPC live execution visualizer
│   │   │   ├── IntentConsole.tsx # Natural language prompt & intent executor
│   │   │   ├── BridgeModal.tsx   # Hyperlane Warp Route guidance modal
│   │   │   └── WalletButton.tsx  # Nightly wallet connect & network switch button
│   │   └── contexts/
│   │       └── SolanaProvider.tsx# Clean @solana/wallet-adapter-react setup
│   ├── package.json
│   ├── tailwind.config.js
│   └── tsconfig.json
│
├── backend/                      # Node.js Agent Executor & MCP Client
│   ├── src/
│   │   ├── agent/                # Intent parsing & execution planning
│   │   │   ├── orchestrator.ts   # LangChain intent decomposition
│   │   │   └── strategyRules.ts  # Yield optimization & arbitrage logic
│   │   ├── mcp-client/           # cookie-mcp connection & execution
│   │   │   ├── client.ts         # STDIO client to cookie-mcp
│   │   │   └── policyGuard.ts    # PolicyLayer evaluation engine
│   │   └── index.ts              # Express API server & WebSocket dispatcher
│   ├── .env.example              # Environment variable template
│   ├── package.json
│   └── tsconfig.json
│
├── contracts/                    # Anchor / Rust SVM Smart Contract
│   ├── programs/
│   │   └── autarch_vault/
│   │       └── src/
│   │           └── lib.rs        # PDA Smart Vault, delegated CPIs, whitelist
│   ├── Anchor.toml
│   └── Cargo.toml
│
└── docs/                         # Security policies & architecture specs
    ├── policy.json               # PolicyLayer access control & sandbox configuration
    └── architecture.md           # System specification and protocol flow
```

---

## 🛠️ Setup and Installation

### Prerequisites
- **Node.js**: v18.0.0 or higher
- **Rust & Cargo**: Latest stable version
- **Solana CLI & Anchor CLI**: 0.30.0+
- **Nightly Wallet Extension**: Installed in browser (configured for SVM)

---

### 1. Backend Setup (`/backend`)

1. Navigate to the backend directory:
   ```bash
   cd backend
   npm install
   ```
2. Create and configure your `.env` file:
   ```bash
   cp .env.example .env
   ```
   Configure the following parameters:
   ```env
   PORT=4000
   COOKIE_RPC_URL=https://rpc.cookiescan.io
   COOKIE_PRIVATE_KEY=<YOUR_DELEGATED_AGENT_PRIVATE_KEY_BASE58>
   COOKIE_MAX_TRADE_COOK=100
   COOKIE_SLIPPAGE_BPS=500
   POLICY_PATH=../docs/policy.json
   COOKIE_MCP_SERVER_COMMAND=npx
   COOKIE_MCP_SERVER_ARGS=-y @cookiechain/cookie-mcp
   ```
3. Run the backend development server:
   ```bash
   npm run dev
   ```

---

### 2. Frontend Setup (`/frontend`)

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   npm install
   ```
2. Create a `.env.local` file:
   ```env
   NEXT_PUBLIC_RPC_URL=https://rpc.cookiescan.io
   NEXT_PUBLIC_WS_RPC_URL=wss://rpc.cookiescan.io
   NEXT_PUBLIC_API_URL=http://localhost:4000
   NEXT_PUBLIC_COOKIE_EXPLORER_URL=https://cookiescan.io
   ```
3. Run the Next.js development server:
   ```bash
   npm run dev
   ```
4. Open [http://localhost:3000](http://localhost:3000) in your browser with the **Nightly Wallet** extension active.

---

### 3. Smart Contract Build & Deployment (`/contracts`)

1. Navigate to the contracts directory:
   ```bash
   cd contracts
   ```
2. Build the Anchor program:
   ```bash
   anchor build
   ```
3. Deploy to Cookie Chain SVM:
   ```bash
   anchor deploy --provider.cluster https://rpc.cookiescan.io
   ```

---

## 🌉 Hyperlane Warp Route Bridge Guide

To onboard liquidity from other networks into Cookie Chain:

1. **Access Hyperlane Warp Route Portal**: Navigate to the official bridge interface or trigger the in-app **Bridge Assets** modal.
2. **Select Origin Network**: Choose from supported ecosystems (Ethereum, Arbitrum, Solana, Celestia, etc.).
3. **Select Asset**: Select native tokens or stablecoins (such as **USDC** or **TIA**).
4. **Destination Chain**: Select **Cookie Chain (SVM)**.
5. **Recipient Address**: Enter your **Autarch Smart Vault PDA** or your connected **Nightly Wallet address**.
6. **Initiate Transfer & Finalize**:
   - Approve the transfer in your origin wallet.
   - The Hyperlane Relayer verifies the interchain message with sub-minute latency.
   - The Autarch Backend Agent monitors `bridge_status` tool updates and automatically triggers your intent upon arrival!

---

## 🧵 X (Twitter) Thread Demonstration Script

```text
🧵 1/7 Introducing Autarch Protocol: The first autonomous, intent-centric yield terminal built natively on @TheCookieNet SVM! 🍪🤖

Say goodbye to manual swaps, disjointed LPing, and fragmented clicks. Simply type your goal in plain English, and Autarch executes it on-chain with verified AI agents. 👇

🧵 2/7 ⚡ Why Cookie Chain?
AI agents require sub-second finality and predictable fee markets to execute complex multi-step transaction trees. With $0.05 average fees and SVM speed, Autarch executes swaps, liquidity additions, and staking without front-running risks or stale state delays.

🧵 3/7 🧠 Deep Ecosystem Composability:
Autarch integrates the entire Cookie Chain landscape in one interface:
🔹 Liquid Staking in $bCOOK
🔹 Yield farming on @Cookiebox_dex (DAMM v2 / CLMM) & Cookieswap
🔹 Candy Shop liquidity routing
🔹 High-frequency break-even NFT flips on Baked Bazaar to farm the Grail Pot!

🧵 4/7 🏆 The Grail Pot Engine:
Baked Bazaar features the "Grail Pot"—a progressive jackpot funded by 0.5% of marketplace volume. 
Autarch calculates floor bids on liquid collections (like Sesamians), flips them at break-even, and systematically farms thousands of jackpot tickets for you on autopilot.

🧵 5/7 🛡️ Battle-Tested Security with PolicyLayer:
Autonomous execution requires mathematical boundaries:
✅ All actions run through PolicyLayer JSON guardrails
🚫 Destructive actions (like lock_liquidity or cancel_listing) are strictly DENIED
🔒 Non-custodial Anchor Smart Vault (PDA) ensures funds can ONLY withdraw back to your Nightly Wallet.

🧵 6/7 🌉 Frictionless Onboarding via @Hyperlane_xyz:
Deposit USDC, TIA, or SOL from Ethereum, Solana, or Cosmos straight into your Autarch Vault using Hyperlane Warp Routes. The agent detects finality and immediately deploys your strategy.

🧵 7/7 🚀 Live Demo & Hackathon Submission:
Explore our open-source codebase, test the live app with Nightly Wallet, and inspect our PolicyLayer configs!
🔗 GitHub: https://github.com/autarch-protocol/autarch-protocol
🌐 Live App: https://autarch-protocol.vercel.app
💬 Join the discussion: t.me/TheCookieNetChain
```

---

## 📜 License
Distributed under the **MIT License**.
