import { NextResponse } from 'next/server';

export async function GET() {
  return NextResponse.json({
    status: 'ok',
    protocol: 'Autarch Protocol',
    network: 'Cookie Chain SVM',
    rpc: 'https://rpc.cookiescan.io',
    policyLayer: 'Active — docs/policy.json enforced',
  });
}
