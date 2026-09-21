import express, { Request, Response } from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import { agentOrchestrator } from './agent/orchestrator';
import { mcpClient } from './mcp-client/client';
import { policyGuard } from './mcp-client/policyGuard';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 4000;

app.use(cors());
app.use(express.json());

// Health & System Info
app.get('/api/health', (req: Request, res: Response) => {
  res.json({
    status: 'ok',
    protocol: 'Autarch Protocol',
    network: 'Cookie Chain SVM',
    rpc: process.env.COOKIE_RPC_URL || 'https://rpc.cookiescan.io',
    policyLayer: 'Enforcing docs/policy.json',
  });
});

// Process Autonomous Intent
app.post('/api/intent', async (req: Request, res: Response) => {
  try {
    const { intent, userWallet } = req.body;
    if (!intent) {
      return res.status(400).json({ error: 'Missing intent string in request body' });
    }

    const result = await agentOrchestrator.executeIntent(
      intent,
      userWallet || '11111111111111111111111111111111'
    );

    return res.json(result);
  } catch (error: any) {
    console.error('[Autarch API] Intent execution error:', error);
    return res.status(500).json({ error: error.message || 'Internal Agent Execution Error' });
  }
});

// Query Protocol Metrics
app.get('/api/metrics', (req: Request, res: Response) => {
  res.json({
    cookPriceUsd: 0.142,
    bCookApy: 7.8,
    cookieboxClmmApy: 22.4,
    grailPotJackpotCook: 125000,
    grailPotTicketCostCook: 5,
    tvlCook: 1850.25,
    totalTransactionsExecuted: 4290,
  });
});

// Query Tools & PolicyLayer Status
app.get('/api/tools', (req: Request, res: Response) => {
  const toolsWithPolicy = mcpClient.tools.map((t) => ({
    name: t.name,
    category: t.category,
    description: t.description,
    isAllowed: policyGuard.evaluate(t.name).allowed,
  }));

  res.json({
    totalTools: toolsWithPolicy.length,
    tools: toolsWithPolicy,
  });
});

app.listen(PORT, () => {
  console.log(`=======================================================`);
  console.log(`🍪 Autarch Protocol Backend Agent running on port ${PORT}`);
  console.log(`⚡ Connected to Cookie Chain SVM: ${process.env.COOKIE_RPC_URL || 'https://rpc.cookiescan.io'}`);
  console.log(`🛡️ PolicyLayer active: Destructive operations permanently BLOCKED`);
  console.log(`=======================================================`);
});
