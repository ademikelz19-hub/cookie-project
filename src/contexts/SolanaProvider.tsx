'use client';

import React, {
  createContext,
  useContext,
  useCallback,
  useEffect,
  useState,
  ReactNode,
} from 'react';

// Cookie Chain SVM Constants
export const COOKIE_CHAIN_RPC =
  process.env.NEXT_PUBLIC_RPC_URL || 'https://rpc.cookiescan.io';
export const COOKIE_CHAIN_WS_RPC =
  process.env.NEXT_PUBLIC_WS_RPC_URL || 'wss://rpc.cookiescan.io';

// Nightly Wallet type declaration
declare global {
  interface Window {
    nightly?: {
      solana?: {
        connect: (options?: { onlyIfTrusted?: boolean }) => Promise<{ publicKey: { toString: () => string } }>;
        disconnect: () => Promise<void>;
        changeNetwork?: (rpcUrl: string) => Promise<void>;
        network?: string;
        publicKey?: { toString: () => string } | null;
        isConnected?: boolean;
      };
    };
  }
}

interface NightlyContextState {
  connected: boolean;
  publicKey: string | null;
  connecting: boolean;
  isNightlyInstalled: boolean;
  isCookieChainNetwork: boolean;
  connect: () => Promise<void>;
  disconnect: () => Promise<void>;
  switchToCookieChain: () => Promise<void>;
}

const NightlyContext = createContext<NightlyContextState>({
  connected: false,
  publicKey: null,
  connecting: false,
  isNightlyInstalled: false,
  isCookieChainNetwork: false,
  connect: async () => {},
  disconnect: async () => {},
  switchToCookieChain: async () => {},
});

export const useNightly = () => useContext(NightlyContext);

export function SolanaProvider({ children }: { children: ReactNode }) {
  const [connected, setConnected] = useState(false);
  const [publicKey, setPublicKey] = useState<string | null>(null);
  const [connecting, setConnecting] = useState(false);
  const [isNightlyInstalled, setIsNightlyInstalled] = useState(false);
  const [isCookieChainNetwork, setIsCookieChainNetwork] = useState(false);

  // Detect Nightly on mount and periodically
  useEffect(() => {
    const check = () => {
      if (typeof window !== 'undefined' && window.nightly?.solana) {
        setIsNightlyInstalled(true);
        const nightly = window.nightly.solana;

        // If already connected (e.g. user returns to page), restore state
        if (nightly.publicKey && nightly.isConnected) {
          const pk = nightly.publicKey.toString();
          setPublicKey(pk);
          setConnected(true);
        }

        // Check network
        const net = nightly.network || '';
        setIsCookieChainNetwork(
          net.includes('cookie') || net === COOKIE_CHAIN_RPC
        );
      } else {
        setIsNightlyInstalled(false);
      }
    };

    check();
    const interval = setInterval(check, 2000);
    window.addEventListener('focus', check);
    return () => {
      clearInterval(interval);
      window.removeEventListener('focus', check);
    };
  }, []);

  const connect = useCallback(async () => {
    if (typeof window === 'undefined') return;

    if (!window.nightly?.solana) {
      // Nightly not installed — open install page
      window.open('https://nightly.app', '_blank');
      return;
    }

    try {
      setConnecting(true);
      const res = await window.nightly.solana.connect();
      const pk = res?.publicKey?.toString() || window.nightly.solana.publicKey?.toString();
      if (pk) {
        setPublicKey(pk);
        setConnected(true);
      }
    } catch (err) {
      console.error('[Autarch] Nightly connect error:', err);
    } finally {
      setConnecting(false);
    }
  }, []);

  const disconnect = useCallback(async () => {
    try {
      await window.nightly?.solana?.disconnect();
    } catch {}
    setConnected(false);
    setPublicKey(null);
  }, []);

  const switchToCookieChain = useCallback(async () => {
    if (!window.nightly?.solana) return;
    try {
      if (typeof window.nightly.solana.changeNetwork === 'function') {
        await window.nightly.solana.changeNetwork(COOKIE_CHAIN_RPC);
        setIsCookieChainNetwork(true);
      }
    } catch (err) {
      console.error('[Autarch] switchToCookieChain error:', err);
    }
  }, []);

  return (
    <NightlyContext.Provider
      value={{
        connected,
        publicKey,
        connecting,
        isNightlyInstalled,
        isCookieChainNetwork,
        connect,
        disconnect,
        switchToCookieChain,
      }}
    >
      {children}
    </NightlyContext.Provider>
  );
}

export default SolanaProvider;
