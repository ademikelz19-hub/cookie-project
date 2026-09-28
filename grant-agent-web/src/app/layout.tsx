import type { Metadata } from "next";
import "./globals.css";
import { Navigation } from "../components/Navigation";

export const metadata: Metadata = {
  title: "Grant Agent — Cloud Grant Discovery, Strategy & Automation",
  description: "AI-Powered Grant Discovery, Research, Strategy, and Browser Automation Platform",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-slate-900 text-slate-100 antialiased selection:bg-indigo-500 selection:text-white">
        <Navigation>{children}</Navigation>
      </body>
    </html>
  );
}
