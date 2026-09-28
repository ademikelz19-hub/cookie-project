import type { Metadata } from 'next';
import './globals.css';
import { SolanaProvider } from '@/contexts/SolanaProvider';

export const metadata: Metadata = {
  title: 'Autarch Protocol | Intent-Centric Yield on Cookie Chain SVM',
  description:
    'Autonomous, AI-driven, intent-centric Smart Vault & Yield Terminal on Cookie Chain with Nightly Wallet Standard and PolicyLayer security.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-cyber-bg text-neutral-100 antialiased selection:bg-cookie-400 selection:text-neutral-900">
        <SolanaProvider>
          {children}
        </SolanaProvider>
      </body>
    </html>
  );
}
