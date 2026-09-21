import { NextResponse } from 'next/server';
import { runOrchestrator } from '@/lib/orchestrator';

export async function POST(request: Request) {
  try {
    const { intent, userWallet } = await request.json();
    if (!intent) {
      return NextResponse.json({ error: 'Missing intent' }, { status: 400 });
    }

    const logs = await runOrchestrator(intent, userWallet || 'UnknownVaultPDA');

    return NextResponse.json({
      intent,
      userWallet,
      status: 'completed',
      logs,
    });
  } catch (err: any) {
    return NextResponse.json({ error: err.message || 'Internal error' }, { status: 500 });
  }
}
