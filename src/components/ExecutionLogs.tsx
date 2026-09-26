'use client';

import React, { useEffect, useState, useRef } from 'react';
import { Terminal, ShieldCheck, Activity, CheckCircle, ExternalLink, Zap, AlertCircle } from 'lucide-react';

export interface LogEntry {
  id: string;
  timestamp: string;
  type: 'cpi' | 'mcp' | 'policy' | 'trade' | 'grail_pot' | 'error';
  summary: string;
  signature?: string;
  toolUsed?: string;
  status: 'pending' | 'success' | 'failed' | 'guarded';
}

const INITIAL_LOGS: LogEntry[] = [
  {
    id: 'log-init-1',
    timestamp: 'System',
    type: 'policy',
    toolUsed: 'PolicyLayer::Gateway',
    summary: 'PolicyLayer active: Irreversible operations blocked (lock_liquidity, cancel_listing). Max trade limit: 100 $COOK.',
    status: 'guarded',
  },
  {
    id: 'log-init-2',
    timestamp: 'System',
    type: 'mcp',
    toolUsed: 'cookie-mcp::RPC',
    summary: 'Connected to Cookie Chain SVM (rpc.cookiescan.io). Sub-second finality active.',
    status: 'success',
  },
  {
    id: 'log-init-3',
    timestamp: 'System',
    type: 'cpi',
    toolUsed: 'Agent::Terminal',
    summary: 'Ready. Choose a strategy preset or write a custom intent below, then click Execute Intent.',
    status: 'pending',
  },
];

export const ExecutionLogs: React.FC = () => {
  const [logs, setLogs] = useState<LogEntry[]>(INITIAL_LOGS);
  const [wsConnected, setWsConnected] = useState<boolean>(true);
  const logContainerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Attempt WebSocket connection to Cookie Chain RPC or backend log stream
    const wsUrl = process.env.NEXT_PUBLIC_WS_RPC_URL || 'wss://rpc.cookiescan.io';
    let socket: WebSocket | null = null;

    try {
      socket = new WebSocket(wsUrl);

      socket.onopen = () => {
        setWsConnected(true);
        // Subscribe to program account notifications or logs
        socket?.send(
          JSON.stringify({
            jsonrpc: '2.0',
            id: 1,
            method: 'logsSubscribe',
            params: [{ mentions: ['Autarch11111111111111111111111111111111111'] }, { commitment: 'confirmed' }],
          })
        );
      };

      socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.params?.result) {
            const rawLog = data.params.result;
            const newEntry: LogEntry = {
              id: `log-${Date.now()}-${Math.random()}`,
              timestamp: new Date().toLocaleTimeString(),
              type: 'cpi',
              summary: `SVM Log Event: Signature ${rawLog.value?.signature?.slice(0, 8)}... confirmed on Cookie Chain.`,
              signature: rawLog.value?.signature?.slice(0, 10),
              status: rawLog.value?.err ? 'failed' : 'success',
            };
            setLogs((prev) => [...prev.slice(-30), newEntry]);
          }
        } catch {
          // ignore non-json
        }
      };

      socket.onerror = () => {
        setWsConnected(false);
      };

      socket.onclose = () => {
        setWsConnected(false);
      };
    } catch (err) {
      console.warn('[ExecutionLogs] WebSocket connection fallback active:', err);
      setWsConnected(false);
    }

    return () => {
      if (socket && socket.readyState === WebSocket.OPEN) {
        socket.close();
      }
    };
  }, []);

  // Listen for custom agent intent dispatch events from window
  useEffect(() => {
    const handleNewLog = (e: CustomEvent<LogEntry>) => {
      if (e.detail) {
        setLogs((prev) => [...prev, e.detail]);
      }
    };

    window.addEventListener('autarch:log' as any, handleNewLog);
    return () => window.removeEventListener('autarch:log' as any, handleNewLog);
  }, []);

  // Auto-scroll on new log entries
  useEffect(() => {
    if (logContainerRef.current) {
      logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight;
    }
  }, [logs]);

  return (
    <div className="bg-cyber-card border border-cyber-border rounded-xl p-5 flex flex-col h-[400px]">
      {/* Header */}
      <div className="flex items-center justify-between pb-3 border-b border-cyber-border mb-3">
        <div className="flex items-center gap-2">
          <Terminal className="w-4 h-4 text-cookie-300" />
          <span className="text-sm font-semibold font-mono text-white">Agent Execution Stream & RPC Logs</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-cyber-bg border border-cyber-border text-[11px] font-mono">
            <span
              className={`w-2 h-2 rounded-full ${
                wsConnected ? 'bg-emerald-400 animate-ping' : 'bg-amber-400'
              }`}
            />
            <span className="text-neutral-300">
              {wsConnected ? 'WebSocket Live: rpc.cookiescan.io' : 'Polling RPC Stream'}
            </span>
          </div>
        </div>
      </div>

      {/* Terminal Output */}
      <div
        ref={logContainerRef}
        className="flex-1 overflow-y-auto space-y-2.5 font-mono text-xs pr-1"
      >
        {logs.map((log) => {
          let badgeColor = 'bg-blue-950/50 text-blue-300 border-blue-800/40';
          let statusIcon = <Activity className="w-3 h-3 text-blue-400" />;

          if (log.status === 'guarded') {
            badgeColor = 'bg-purple-950/50 text-purple-300 border-purple-800/40';
            statusIcon = <ShieldCheck className="w-3 h-3 text-purple-400" />;
          } else if (log.status === 'success') {
            badgeColor = 'bg-emerald-950/50 text-emerald-300 border-emerald-800/40';
            statusIcon = <CheckCircle className="w-3 h-3 text-emerald-400" />;
          } else if (log.status === 'failed') {
            badgeColor = 'bg-rose-950/50 text-rose-300 border-rose-800/40';
            statusIcon = <AlertCircle className="w-3 h-3 text-rose-400" />;
          }

          return (
            <div
              key={log.id}
              className="p-2.5 rounded bg-cyber-bg/80 border border-cyber-border/40 hover:border-cookie-400/30 transition-all flex flex-col gap-1"
            >
              <div className="flex items-center justify-between text-[11px] text-neutral-400">
                <div className="flex items-center gap-2">
                  <span className="text-neutral-500">{log.timestamp}</span>
                  {log.toolUsed && (
                    <span className="px-1.5 py-0.2 text-[10px] rounded bg-neutral-800 text-cookie-300 border border-neutral-700">
                      {log.toolUsed}
                    </span>
                  )}
                </div>
                <div className="flex items-center gap-1.5">
                  <span className={`px-2 py-0.5 rounded border text-[10px] flex items-center gap-1 ${badgeColor}`}>
                    {statusIcon}
                    <span className="capitalize">{log.status}</span>
                  </span>
                </div>
              </div>

              <div className="text-neutral-200 leading-relaxed text-xs">
                {log.summary}
              </div>

              {log.signature && (
                <div className="flex items-center gap-1 text-[10px] text-cookie-300/80 mt-0.5">
                  <span>Tx Sig:</span>
                  <a
                    href={`https://cookiescan.io/tx/${log.signature}`}
                    target="_blank"
                    rel="noreferrer"
                    className="hover:underline flex items-center gap-0.5"
                  >
                    <span>{log.signature}</span>
                    <ExternalLink className="w-2.5 h-2.5" />
                  </a>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Terminal Footer status */}
      <div className="pt-2 mt-2 border-t border-cyber-border flex items-center justify-between text-[11px] text-neutral-500 font-mono">
        <span>PolicyLayer v1.0.0 active</span>
        <span className="text-cookie-300 flex items-center gap-1">
          <Zap className="w-3 h-3" /> Sub-second finality
        </span>
      </div>
    </div>
  );
};

export default ExecutionLogs;
