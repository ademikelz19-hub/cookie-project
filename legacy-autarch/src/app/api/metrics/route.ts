import { NextResponse } from 'next/server';

export async function GET() {
  return NextResponse.json({
    cookPriceUsd: 0.142,
    bCookApy: 7.8,
    cookieboxClmmApy: 22.4,
    grailPotJackpotCook: 125000,
    grailPotTicketCostCook: 5,
    tvlCook: 1850.25,
    totalTransactionsExecuted: 4290,
  });
}
