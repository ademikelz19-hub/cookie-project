/**
 * Autarch Strategy Rules Engine
 * Implements multi-vector yield allocation, Grail Pot break-even NFT arbitrage, and CLMM fee compounding.
 */

export interface AllocationPlan {
  bCookStakePct: number;
  cookieboxClmmPct: number;
  bakedBazaarGrailPotPct: number;
  totalCookCapital: number;
}

export interface ArbitrageOpportunity {
  collection: string;
  floorPriceCook: number;
  targetBidCook: number;
  marketplaceFeePct: number;
  estimatedTickets: number;
}

export class StrategyRules {
  private static readonly BAKED_BAZAAR_FEE_PCT = 0.005; // 0.5% marketplace fee diverted to Grail Pot
  private static readonly COOK_PER_GRAIL_TICKET = 5; // 1 ticket per 5 $COOK volume

  /**
   * Calculates optimal break-even bid for Grail Pot NFT farming
   * Bid slightly below floor such that Floor * (1 - Fee) >= Bid, neutralizing price risk
   */
  public static calculateGrailPotArbitrage(floorPriceCook: number): ArbitrageOpportunity {
    const netProceeds = floorPriceCook * (1 - this.BAKED_BAZAAR_FEE_PCT);
    // Target bid at 98% of net proceeds to absorb gas/SVM execution fees and guarantee break-even
    const targetBidCook = Number((netProceeds * 0.985).toFixed(2));
    const estimatedTickets = Math.floor(targetBidCook / this.COOK_PER_GRAIL_TICKET);

    return {
      collection: 'Sesamian',
      floorPriceCook,
      targetBidCook,
      marketplaceFeePct: this.BAKED_BAZAAR_FEE_PCT,
      estimatedTickets,
    };
  }

  /**
   * Deconstructs a high-level intent into fractional capital allocations
   */
  public static parseIntentAllocations(intentText: string, totalCapital: number = 100): AllocationPlan {
    const lower = intentText.toLowerCase();

    let bCook = 0.35;
    let clmm = 0.45;
    let grailPot = 0.20;

    if (lower.includes('grail') || lower.includes('pot') || lower.includes('jackpot') || lower.includes('nft')) {
      grailPot = 0.40;
      clmm = 0.30;
      bCook = 0.30;
    }

    if (lower.includes('conservative') || lower.includes('staking only') || lower.includes('pure')) {
      bCook = 0.80;
      clmm = 0.20;
      grailPot = 0.0;
    }

    if (lower.includes('clmm') || lower.includes('cookiebox') || lower.includes('fee')) {
      clmm = 0.60;
      bCook = 0.25;
      grailPot = 0.15;
    }

    return {
      bCookStakePct: bCook,
      cookieboxClmmPct: clmm,
      bakedBazaarGrailPotPct: grailPot,
      totalCookCapital: totalCapital,
    };
  }
}
