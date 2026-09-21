import fs from 'fs';
import path from 'path';

export interface PolicyRule {
  id: string;
  tool: string;
  effect: 'allow' | 'deny';
  description: string;
  reason?: string;
  conditions?: Record<string, any>;
  rateLimit?: {
    maxRequests: number;
    windowSeconds: number;
    actionOnExceed: string;
  };
}

export interface PolicyLayerConfig {
  name: string;
  version: string;
  defaultEffect: string;
  policies: PolicyRule[];
}

export class PolicyGuard {
  private config: PolicyLayerConfig | null = null;
  private callTimestamps: Map<string, number[]> = new Map();

  // Environment fallback caps
  private maxTradeCook: number;
  private maxSlippageBps: number;

  constructor() {
    this.maxTradeCook = Number(process.env.COOKIE_MAX_TRADE_COOK || 100);
    this.maxSlippageBps = Number(process.env.COOKIE_SLIPPAGE_BPS || 500);
    this.loadPolicy();
  }

  private loadPolicy() {
    try {
      const policyPath =
        process.env.POLICY_PATH ||
        path.resolve(__dirname, '../../../docs/policy.json');
      if (fs.existsSync(policyPath)) {
        const raw = fs.readFileSync(policyPath, 'utf-8');
        this.config = JSON.parse(raw);
        console.log(`[PolicyGuard] Successfully loaded PolicyLayer config from ${policyPath}`);
      } else {
        console.warn(`[PolicyGuard] Warning: policy.json not found at ${policyPath}. Initializing fallback guardrails.`);
      }
    } catch (err) {
      console.error('[PolicyGuard] Error parsing policy.json:', err);
    }
  }

  /**
   * Evaluates if a given tool invocation conforms to PolicyLayer security specifications
   */
  public evaluate(toolName: string, args: Record<string, any> = {}): {
    allowed: boolean;
    reason?: string;
  } {
    // 1. Explicitly DENY destructive operations
    if (toolName === 'lock_liquidity') {
      return {
        allowed: false,
        reason: 'DENIED: lock_liquidity is permanently blocked by PolicyLayer to prevent bricking vault assets.',
      };
    }

    if (toolName === 'cancel_listing') {
      return {
        allowed: false,
        reason: 'DENIED: cancel_listing is blocked to preserve active marketplace liquidity & Grail Pot bidding state.',
      };
    }

    // 2. Financial bounds enforcement
    const cookAmount =
      Number(args.amount_in || args.amount_cook || args.price_cook || args.offer_amount_cook || 0);

    if (cookAmount > this.maxTradeCook) {
      return {
        allowed: false,
        reason: `DENIED: Requested ${cookAmount} $COOK exceeds COOKIE_MAX_TRADE_COOK limit (${this.maxTradeCook} $COOK).`,
      };
    }

    const slippageBps = Number(args.slippage_bps || 0);
    if (slippageBps > this.maxSlippageBps) {
      return {
        allowed: false,
        reason: `DENIED: Requested slippage ${slippageBps} BPS exceeds COOKIE_SLIPPAGE_BPS limit (${this.maxSlippageBps} BPS).`,
      };
    }

    // 3. Rate limiting enforcement on read operations (e.g., bridge_status, get_pools: max 60 req/min)
    if (toolName === 'bridge_status' || toolName === 'get_pools') {
      const now = Date.now();
      const windowMs = 60 * 1000;
      const history = (this.callTimestamps.get(toolName) || []).filter(
        (ts) => now - ts < windowMs
      );

      if (history.length >= 60) {
        return {
          allowed: false,
          reason: `RATE_LIMITED: Tool '${toolName}' exceeded 60 requests per minute to prevent RPC exhaustion.`,
        };
      }

      history.push(now);
      this.callTimestamps.set(toolName, history);
    }

    return { allowed: true };
  }
}

export const policyGuard = new PolicyGuard();
