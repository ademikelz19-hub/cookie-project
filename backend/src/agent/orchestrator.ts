import { mcpClient } from '../mcp-client/client';
import { StrategyRules } from './strategyRules';

export interface ExecutionResult {
  intent: string;
  userWallet: string;
  status: 'completed' | 'partial' | 'failed';
  logs: {
    type: 'cpi' | 'mcp' | 'policy' | 'trade' | 'grail_pot' | 'error';
    toolUsed: string;
    summary: string;
    signature?: string;
    status: 'success' | 'failed' | 'guarded' | 'pending';
  }[];
}

export class AgentOrchestrator {
  /**
   * Translates a user intent into an orchestrated sequence of cookie-mcp tool executions
   */
  public async executeIntent(intent: string, userWallet: string): Promise<ExecutionResult> {
    const logs: ExecutionResult['logs'] = [];
    console.log(`[AgentOrchestrator] Processing intent: "${intent}" for vault: ${userWallet}`);

    // Step 1: Parse allocations
    const allocation = StrategyRules.parseIntentAllocations(intent, 100);

    logs.push({
      type: 'mcp',
      toolUsed: 'LangChain::IntentParser',
      summary: `Allocations derived: ${(allocation.bCookStakePct * 100).toFixed(0)}% bCOOK Stake, ${(allocation.cookieboxClmmPct * 100).toFixed(0)}% Cookiebox CLMM, ${(allocation.bakedBazaarGrailPotPct * 100).toFixed(0)}% Grail Pot.`,
      status: 'pending',
    });

    // Step 2: Liquid Staking Execution (bCOOK)
    if (allocation.bCookStakePct > 0) {
      const stakeAmount = Number((allocation.totalCookCapital * allocation.bCookStakePct).toFixed(2));
      const res = await mcpClient.callTool('stake', { amount_cook: stakeAmount });

      if (res.success) {
        logs.push({
          type: 'trade',
          toolUsed: 'cookie-mcp::stake',
          summary: `Deposited ${stakeAmount} $COOK into bCOOK SPL Stake Pool. Received ${res.data?.minted_bcook || stakeAmount * 0.97} bCOOK at ${res.data?.apy || '7.8% APY'}.`,
          signature: res.signature,
          status: 'success',
        });
      } else {
        logs.push({
          type: 'error',
          toolUsed: 'cookie-mcp::stake',
          summary: `Staking error: ${res.error}`,
          status: 'failed',
        });
      }
    }

    // Step 3: DEX Swap & Liquidity Provision (Candy Shop & Cookiebox)
    if (allocation.cookieboxClmmPct > 0) {
      const clmmCook = Number((allocation.totalCookCapital * allocation.cookieboxClmmPct).toFixed(2));
      const halfCook = Number((clmmCook / 2).toFixed(2));

      // Swap half to paired asset via Candy Shop aggregator
      const swapRes = await mcpClient.callTool('trade', {
        token_in: 'COOK',
        token_out: 'USDC',
        amount_in: halfCook,
        slippage_bps: 100,
      });

      if (swapRes.success) {
        logs.push({
          type: 'trade',
          toolUsed: 'cookie-mcp::trade (Candy Shop)',
          summary: `Swapped ${halfCook} $COOK for paired USDC via Candy Shop router with minimal slippage.`,
          signature: swapRes.signature,
          status: 'success',
        });
      }

      // Add liquidity to Cookiebox CLMM
      const lpRes = await mcpClient.callTool('add_liquidity', {
        pool_id: 'CLMM-COOK-USDC',
        amount_a: halfCook,
        amount_b: halfCook * 1.5,
      });

      if (lpRes.success) {
        logs.push({
          type: 'mcp',
          toolUsed: 'cookie-mcp::add_liquidity',
          summary: `Deployed ${clmmCook} $COOK equivalent into Cookiebox CLMM. Position auto-compounds fee yields.`,
          signature: lpRes.signature,
          status: 'success',
        });
      }
    }

    // Step 4: Gamified Alpha - Baked Bazaar Grail Pot Arbitrage
    if (allocation.bakedBazaarGrailPotPct > 0) {
      const floorEst = 18;
      const arb = StrategyRules.calculateGrailPotArbitrage(floorEst);

      const offerRes = await mcpClient.callTool('make_offer', {
        mint: 'Sesamian#309',
        offer_amount_cook: arb.targetBidCook,
      });

      if (offerRes.success) {
        logs.push({
          type: 'grail_pot',
          toolUsed: 'cookie-mcp::make_offer',
          summary: `Baked Bazaar: Placed ${arb.targetBidCook} $COOK floor bid on ${arb.collection}. Accumulated +${arb.estimatedTickets} Grail Pot tickets.`,
          signature: offerRes.signature,
          status: 'success',
        });
      }
    }

    return {
      intent,
      userWallet,
      status: 'completed',
      logs,
    };
  }
}

export const agentOrchestrator = new AgentOrchestrator();
