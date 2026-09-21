import fs from 'fs';
import path from 'path';

export interface PolicyRule {
  id: string;
  tool: string;
  effect: 'allow' | 'deny';
  conditions?: Record<string, any>;
  rateLimit?: {
    maxRequests: number;
    windowSeconds: number;
  };
}

// In-memory rate limit store (resets per serverless invocation - sufficient for hackathon)
const callTimestamps: Map<string, number[]> = new Map();

const MAX_TRADE_COOK = Number(process.env.COOKIE_MAX_TRADE_COOK || 100);
const MAX_SLIPPAGE_BPS = Number(process.env.COOKIE_SLIPPAGE_BPS || 500);

const DENIED_TOOLS = ['lock_liquidity', 'cancel_listing'];
const RATE_LIMITED_TOOLS = ['bridge_status', 'get_pools'];

export function evaluatePolicy(toolName: string, args: Record<string, any> = {}): {
  allowed: boolean;
  reason?: string;
} {
  // 1. Hard deny destructive tools
  if (DENIED_TOOLS.includes(toolName)) {
    return {
      allowed: false,
      reason: `DENIED by PolicyLayer: '${toolName}' is permanently blocked — irreversible operation.`,
    };
  }

  // 2. Financial bounds
  const cookAmount = Number(
    args.amount_in ?? args.amount_cook ?? args.price_cook ?? args.offer_amount_cook ?? 0
  );
  if (cookAmount > MAX_TRADE_COOK) {
    return {
      allowed: false,
      reason: `DENIED: ${cookAmount} $COOK exceeds max allowed (${MAX_TRADE_COOK} $COOK).`,
    };
  }

  const slippage = Number(args.slippage_bps ?? 0);
  if (slippage > MAX_SLIPPAGE_BPS) {
    return {
      allowed: false,
      reason: `DENIED: ${slippage} BPS slippage exceeds limit (${MAX_SLIPPAGE_BPS} BPS).`,
    };
  }

  // 3. Rate limits
  if (RATE_LIMITED_TOOLS.includes(toolName)) {
    const now = Date.now();
    const history = (callTimestamps.get(toolName) || []).filter((ts) => now - ts < 60000);
    if (history.length >= 60) {
      return {
        allowed: false,
        reason: `RATE_LIMITED: '${toolName}' exceeded 60 req/min.`,
      };
    }
    history.push(now);
    callTimestamps.set(toolName, history);
  }

  return { allowed: true };
}
