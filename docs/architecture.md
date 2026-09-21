# Autarch Protocol: Deep Architecture & Security Specification

This document details the architectural topology, security boundary invariants, Cross-Program Invocation (CPI) flow, and ecosystem integrations of the **Autarch Protocol** on **Cookie Chain (SVM)**.

---

## 1. System Topology

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                             CLIENT LAYER (Next.js)                          │
│                                                                             │
│   • Nightly Wallet Standard (@solana/wallet-adapter-base / discovery)      │
│   • Dynamic Network Verification (window.nightly.solana.changeNetwork)     │
│   • WebSocket RPC Event Listener (wss://rpc.cookiescan.io)                 │
│   • Natural Language Intent Console & Real-Time Dashboard                   │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ HTTP / WebSocket (Intent Directives)
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                     AUTONOMOUS AGENT LAYER (Node.js)                        │
│                                                                             │
│   • LangChain Intent Decomposition & Strategy Allocator                     │
│   • PolicyGuard Gateway (docs/policy.json Enforcement)                      │
│   • STDIO Client to cookie-mcp Server (32 Tools, 5 Categories)              │
│   • Cookie DAS API & CookieScan RPC Telemetry Polling                       │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ Signed Instructions (COOKIE_PRIVATE_KEY)
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SMART CONTRACT LAYER (Anchor / SVM)                      │
│                                                                             │
│   Autarch Smart Vault Program (PDA: [b"smart_vault", user_pubkey])          │
│   ├── deposit_cook: Non-custodial funding                                   │
│   ├── execute_delegated_cpi: Restricted to verified ecosystem whitelist    │
│   └── withdraw_to_owner: Enforces invariant: funds return ONLY to owner     │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ CPI Execution via Signer Seeds
          ┌────────────────────────────┼────────────────────────────┐
          ▼                            ▼                            ▼
┌─────────────────────┐      ┌─────────────────────┐      ┌─────────────────────┐
│     DEX & SWAP      │      │   LIQUID STAKING    │      │ GAMIFIED NFT ALPHA  │
│                     │      │                     │      │                     │
│ • Candy Shop Router │      │ • bCOOK Stake Pool  │      │ • Baked Bazaar      │
│ • Cookiebox CLMM/   │      │   - Idle capital    │      │   Auction House     │
│   DAMM v2           │      │     yields          │      │ • Grail Pot Jackpot │
│ • Cookieswap SAMM   │      │   - Receipt tokens  │      │   Arbitrage Engine  │
└─────────────────────┘      └─────────────────────┘      └─────────────────────┘
```

---

## 2. On-Chain Smart Vault Security Invariants

### 2.1 Non-Custodial Ownership & PDA Derivation
The Smart Vault is a Program Derived Address defined by the seeds:
$$\text{PDA} = \text{Pubkey}::\text{find\_program\_address}([b\text{"smart\_vault"}, \text{user\_pubkey}], \text{program\_id})$$

Because the PDA derivation incorporates the user's public key, each user maintains an isolated, independent vault account. The contract guarantees:
1. **Immutable Ownership**: Only the user whose public key matches `vault.owner` can initiate deposits and withdrawals.
2. **Zero Custodial Escrow**: Funds are stored directly inside the user's PDA account on the SVM, not in a pooled treasury or externally owned developer wallet.

### 2.2 Mathematical Withdrawal Invariant
```rust
**vault.to_account_info().try_borrow_mut_lamports()? -= amount_lamports;
**ctx.accounts.owner.try_borrow_mut_lamports()? += amount_lamports;
```
Withdrawals do not accept an arbitrary destination address. The destination account is constrained to `ctx.accounts.owner`, which is mathematically verified via `has_one = owner` against the state saved at initialization. **Even if the AI agent or server key is compromised, capital cannot be exfiltrated to a rogue address.**

### 2.3 Ecosystem Program Whitelist
The delegated agent key (`COOKIE_PRIVATE_KEY`) can only request Cross-Program Invocations (`execute_delegated_cpi`) to explicitly hardcoded program IDs:
- **Candy Shop Aggregator**: Swap routing.
- **Cookiebox DAMM v2 / CLMM**: Dynamic liquidity provisioning.
- **Cookieswap SAMM**: Constant-product pool interactions.
- **bCOOK SPL Stake Pool**: Native staking yield accrual.
- **Baked Bazaar Metaplex Auction House**: Bidding, buying, and listing.

Any CPI request targeting an unapproved program fails immediately with `VaultError::ProgramNotWhitelisted`.

---

## 3. PolicyLayer Enforcement Specification

The Autarch backend intercepts every potential `cookie-mcp` tool call through the `PolicyGuard` engine before it reaches the network:

| Category | Tool | Policy Action | Rule Mechanism |
| :--- | :--- | :--- | :--- |
| **Destructive** | `lock_liquidity` | **DENY** | Irreversible locking in Cookiebox DAMM v2 permanently forbidden. |
| **Destructive** | `cancel_listing` | **DENY** | Prevents erratic state cancellation during ongoing arbitrage loops. |
| **Financial** | `trade` | **SANDBOX** | Max cap: 100 $COOK. Max slippage: 500 BPS (5%). |
| **Financial** | `buy_nft` / `make_offer` | **SANDBOX** | Max cap: 100 $COOK per transaction. |
| **Read / API** | `bridge_status` | **RATE LIMIT** | 60 requests / rolling 60-second window to prevent RPC throttling. |
| **Read / API** | `get_pools` | **RATE LIMIT** | 60 requests / rolling 60-second window. |

---

## 4. Multi-Vector Yield Mechanics

### 4.1 bCOOK Liquid Staking
When capital enters the vault, idle balances are swept into the `bCOOK SPL Stake Pool`. 
- **Yield**: Generates ~7.8% base staking APY from Cookie Chain validator rewards.
- **Composability**: Liquid staking receipt tokens (`bCOOK`) are retained by the vault and can be deployed into `bCOOK-COOK` liquidity pools on Cookiebox.

### 4.2 Cookiebox Dynamic & Concentrated Liquidity (CLMM)
- Active capital is allocated across highest-volume trading pairs using `Candy Shop` routing.
- The agent tracks fee accrual and invokes `claim_fees` on a scheduled epoch to compound earnings back into the pool.

### 4.3 The Grail Pot NFT Arbitrage Engine
Baked Bazaar diverts **0.5% of all marketplace volume** into a progressive jackpot pool (the "Grail Pot"). Every 5 $COOK in marketplace volume awards **1 lottery ticket**.

The Autarch algorithm exploits this mechanism through break-even high-frequency flipping:
1. **Floor Detection**: Monitors floor listings on high-liquidity collections (e.g., Sesamians).
2. **Break-Even Offer Calculation**:
   $$\text{Bid} = \text{Floor} \times (1 - \text{Fee}_{\text{marketplace}}) \times 0.985$$
3. **Execution**: Places offer via `make_offer`. Upon acceptance, immediately lists at the current floor via `list_nft`.
4. **Result**: Capital turns over with near-zero principal loss, generating thousands of jackpot tickets on autopilot and socializing risk across automated bids.

---

## 5. Hyperlane Warp Route Interoperability

Cross-chain liquidity ingestion utilizes Hyperlane's Warp Route smart contracts:
1. **Source Chain**: Assets (USDC, TIA, SOL, ETH) are deposited via Warp Route portal.
2. **Interchain Gas Payment & Relayer**: Relayers dispatch the message across domains with sub-minute latency.
3. **SVM Finality**: Assets are minted/transferred directly into the Autarch Smart Vault PDA on Cookie Chain.
4. **Autonomous Deployment**: The backend continuously checks `bridge_status`. Upon confirmation, the newly bridged funds are immediately routed into bCOOK or Cookiebox strategies.
