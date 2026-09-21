'use client';

import React, {
  createContext,
  useContext,
  useMemo,
  useCallback,
  useEffect,
  useState,
  ReactNode,
} from 'react';
import {
  ConnectionProvider,
  WalletProvider,
  useWallet,
} from '@solana/wallet-adapter-react';
import { WalletModalProvider } from '@solana/wallet-adapter-react-ui';
import { Connection, clusterApiUrl } from '@solana/web3.js';

// Default Styles for Solana Wallet Adapter UI
import '@solana/wallet-adapter-react-ui/styles.css';

// Cookie Chain SVM Constants
export const COOKIE_CHAIN_RPC =
  process.env.NEXT_PUBLIC_RPC_URL || 'https://rpc.cookiescan.io';
export const COOKIE_CHAIN_WS_RPC =
  process.env.NEXT_PUBLIC_WS_RPC_URL || 'wss://rpc.cookiescan.io';
export const COOKIE_CHAIN_GENESIS_HASH =
  process.env.NEXT_PUBLIC_COOKIE_GENESIS_HASH ||
  'cookie_chain_svm_mainnet'; // Custom SVM Genesis Identifier

// Type definition for injected Nightly Wallet Solana API
declare global {
  interface Window {
    nightly?: {
      solana?: {
        connect: (options?: { onlyIfTrusted?: boolean }) => Promise<{ publicKey: { toString: () => string } }>;
        disconnect: () => Promise<void>;
        changeNetwork?: (networkUrlOrId: string) => Promise<void>;
        network?: string;
        publicKey?: { toString: () => string };
      };
    };
  }
}

interface CookieNetworkContextState {
  isNightlyInstalled: boolean;
  isCookieChainNetwork: boolean;
  currentNetwork: string | null;
  switchToCookieChain: () => Promise<boolean>;
  rpcEndpoint: string;
}

const CookieNetworkContext = createContext<CookieNetworkContextState>({
  isNightlyInstalled: false,
  isCookieChainNetwork: false,
  currentNetwork: null,
  switchToCookieChain: async () => false,
  rpcEndpoint: COOKIE_CHAIN_RPC,
});

export const useCookieNetwork = () => useContext(CookieNetworkContext);

interface SolanaProviderProps {
  children: ReactNode;
}

/**
 * Inner component to manage Nightly-specific network detection and switching
 */
function CookieNetworkInnerProvider({ children }: { children: ReactNode }) {
  const { connected, wallet } = useWallet();
  const [isNightlyInstalled, setIsNightlyInstalled] = useState<boolean>(false);
  const [isCookieChainNetwork, setIsCookieChainNetwork] = useState<boolean>(false);
  const [currentNetwork, setCurrentNetwork] = useState<string | null>(null);

  // Check if Nightly is injected and inspect current network
  const checkNightlyState = useCallback(() => {
    if (typeof window !== 'undefined' && window.nightly?.solana) {
      setIsNightlyInstalled(true);
      const network = window.nightly.solana.network || 'unknown';
      setCurrentNetwork(network);

      const isCookie =
        network.toLowerCase().includes('cookie') ||
        network === COOKIE_CHAIN_GENESIS_HASH ||
        network === COOKIE_CHAIN_RPC;

      setIsCookieChainNetwork(isCookie);
    } else {
      setIsNightlyInstalled(false);
      setIsCookieChainNetwork(false);
    }
  }, []);

  useEffect(() => {
    checkNightlyState();

    // Re-check periodically or on window focus
    const interval = setInterval(checkNightlyState, 3000);
    window.addEventListener('focus', checkNightlyState);

    return () => {
      clearInterval(interval);
      window.removeEventListener('focus', checkNightlyState);
    };
  }, [checkNightlyState, connected, wallet]);

  /**
   * Programmatically prompts Nightly to switch network to Cookie Chain SVM
   */
  const switchToCookieChain = useCallback(async (): Promise<boolean> => {
    if (typeof window === 'undefined' || !window.nightly?.solana) {
      console.warn('[Autarch] Nightly Wallet extension not detected.');
      return false;
    }

    try {
      if (typeof window.nightly.solana.changeNetwork === 'function') {
        console.log('[Autarch] Prompting Nightly to switch to Cookie Chain RPC...');
        await window.nightly.solana.changeNetwork(COOKIE_CHAIN_RPC);
        checkNightlyState();
        return true;
      } else {
        console.warn('[Autarch] changeNetwork method not available on window.nightly.solana');
        return false;
      }
    } catch (error) {
      console.error('[Autarch] Failed to switch Nightly network to Cookie Chain:', error);
      return false;
    }
  }, [checkNightlyState]);

  return (
    <CookieNetworkContext.Provider
      value={{
        isNightlyInstalled,
        isCookieChainNetwork,
        currentNetwork,
        switchToCookieChain,
        rpcEndpoint: COOKIE_CHAIN_RPC,
      }}
    >
      {children}
    </CookieNetworkContext.Provider>
  );
}

/**
 * Core SolanaProvider for Autarch Protocol.
 *
 * CRITICAL ARCHITECTURAL CONSTRAINTS:
 * 1. Points dynamically to https://rpc.cookiescan.io.
 * 2. Strict Standard Wallet Discovery: initializes with wallets={[]} to allow standard-compliant
 *    extensions like Nightly to auto-connect cleanly without legacy adapter bundle bloat.
 * 3. Enforces window.nightly.solana.changeNetwork() verification for Cookie Chain SVM.
 */
export function SolanaProvider({ children }: SolanaProviderProps) {
  // Direct RPC Connection to Cookie Chain SVM with WebSocket commitment
  const endpoint = useMemo(() => COOKIE_CHAIN_RPC, []);

  // Standard wallet discovery: empty array delegates purely to @solana/wallet-standard
  // No legacy PhantomWalletAdapter, UnsafeBurnerWalletAdapter, or WalletConnect v1
  const wallets = useMemo(() => [], []);

  const SafeConnectionProvider = ConnectionProvider as unknown as React.FC<any>;
  const SafeWalletProvider = WalletProvider as unknown as React.FC<any>;
  const SafeWalletModalProvider = WalletModalProvider as unknown as React.FC<any>;

  return (
    <SafeConnectionProvider
      endpoint={endpoint}
      config={{
        commitment: 'confirmed',
        wsEndpoint: COOKIE_CHAIN_WS_RPC,
      }}
    >
      <SafeWalletProvider wallets={wallets} autoConnect>
        <SafeWalletModalProvider>
          <CookieNetworkInnerProvider>{children}</CookieNetworkInnerProvider>
        </SafeWalletModalProvider>
      </SafeWalletProvider>
    </SafeConnectionProvider>
  );
}

export default SolanaProvider;
