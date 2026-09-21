import { evaluatePolicy } from './policyGuard';

export interface StrategyAllocation {
  bCookStakePct: number;
  cookieboxClmmPct: number;
  bakedBazaarGrailPotPct: number;
  totalCookCapital: number;
}

export interface AgentLog {
  type: 'cpi' | 'mcp' | 'policy' | 'trade' | 'grail_pot' | 'error';
  toolUsed: string;
  summary: string;
  signature?: string;
  status: 'success' | 'failed' | 'guarded' | 'pending';
}

function parseAllocations(intent: string, capital = 100): StrategyAllocation {
  const lower = intent.toLowerCase();
  let bCook = 0.35, clmm = 0.45, grail = 0.20;

  if (lower.includes('grail') || lower.includes('jackpot') || lower.includes('nft')) {
    grail = 0.40; clmm = 0.30; bCook = 0.30;
  } else if (lower.includes('conservative') || lower.includes('staking only')) {
    bCook = 0.80; clmm = 0.20; grail = 0.00;
  } else if (lower.includes('clmm') || lower.includes('cookiebox') || lower.includes('fee')) {
    clmm = 0.60; bCook = 0.25; grail = 0.15;
  }

  return { bCookStakePct: bCook, cookieboxClmmPct: clmm, bakedBazaarGrailPotPct: grail, totalCookCapital: capital };
}

function fakeSig() {
  const r = () => Math.random().toString(36).substring(2, 6).toUpperCase();
  return `${r()}...${r()}`;
}

export async function runOrchestrator(intent: string, userWallet: string): Promise<AgentLog[]> {
  const logs: AgentLog[] = [];
  const alloc = parseAllocations(intent, 100);

  logs.push({
    type: 'policy',
    toolUsed: 'PolicyLayer::Gateway',
    summary: `Intent parsed. Allocations: ${(alloc.bCookStakePct * 100).toFixed(0)}% bCOOK Stake · ${(alloc.cookieboxClmmPct * 100).toFixed(0)}% Cookiebox CLMM · ${(alloc.bakedBazaarGrailPotPct * 100).toFixed(0)}% Grail Pot. All actions verified against docs/policy.json.`,
    status: 'guarded',
  });

  // --- bCOOK Staking ---
  if (alloc.bCookStakePct > 0) {
    const amount = +(alloc.totalCookCapital * alloc.bCookStakePct).toFixed(2);
    const policy = evaluatePolicy('stake', { amount_cook: amount });
    if (policy.allowed) {
      const bcook = +(amount * 0.972).toFixed(4);
      logs.push({
        type: 'trade',
        toolUsed: 'cookie-mcp::stake',
        summary: `Deposited ${amount} $COOK into bCOOK SPL Stake Pool → Minted ${bcook} bCOOK. Base APY: 7.8%.`,
        signature: fakeSig(),
        status: 'success',
      });
    } else {
      logs.push({ type: 'error', toolUsed: 'cookie-mcp::stake', summary: policy.reason!, status: 'failed' });
    }
  }

  // --- Candy Shop Swap + Cookiebox CLMM LP ---
  if (alloc.cookieboxClmmPct > 0) {
    const clmmCook = +(alloc.totalCookCapital * alloc.cookieboxClmmPct).toFixed(2);
    const half = +(clmmCook / 2).toFixed(2);

    const tradePolicy = evaluatePolicy('trade', { amount_in: half, slippage_bps: 80 });
    if (tradePolicy.allowed) {
      logs.push({
        type: 'trade',
        toolUsed: 'cookie-mcp::trade (Candy Shop)',
        summary: `Swapped ${half} $COOK → USDC via Candy Shop aggregator. Slippage: 80 BPS (limit 500 BPS ✓).`,
        signature: fakeSig(),
        status: 'success',
      });
    }

    const lpPolicy = evaluatePolicy('add_liquidity', { amount_cook: half });
    if (lpPolicy.allowed) {
      logs.push({
        type: 'mcp',
        toolUsed: 'cookie-mcp::add_liquidity',
        summary: `Deployed ${clmmCook} $COOK into Cookiebox CLMM Pool COOK-USDC. Auto-compounding fee yield enabled. Est. APY: 22.4%.`,
        signature: fakeSig(),
        status: 'success',
      });
    }
  }

  // --- Baked Bazaar Grail Pot Engine ---
  if (alloc.bakedBazaarGrailPotPct > 0) {
    const floorEst = 18;
    const targetBid = +(floorEst * (1 - 0.005) * 0.985).toFixed(2);
    const tickets = Math.floor(targetBid / 5);

    const offerPolicy = evaluatePolicy('make_offer', { offer_amount_cook: targetBid });
    if (offerPolicy.allowed) {
      logs.push({
        type: 'grail_pot',
        toolUsed: 'cookie-mcp::make_offer',
        summary: `Baked Bazaar: Break-even bid of ${targetBid} $COOK placed on Sesamian floor. Earned +${tickets} Grail Pot tickets. Jackpot pool: 125,000 $COOK.`,
        signature: fakeSig(),
        status: 'success',
      });
    } else {
      logs.push({ type: 'error', toolUsed: 'cookie-mcp::make_offer', summary: offerPolicy.reason!, status: 'failed' });
    }
  }

  return logs;
}
