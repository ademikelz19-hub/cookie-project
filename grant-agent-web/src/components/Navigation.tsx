"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard, Compass, Bookmark, Building2, FileText,
  FolderLock, Bot, Bell, Settings, Plus, ExternalLink
} from "lucide-react";
import { api } from "../lib/api";
import { Organisation } from "../types";

export function Navigation({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const [organisations, setOrganisations] = useState<Organisation[]>([]);
  const [selectedOrgId, setSelectedOrgId] = useState<string>("");
  const [urlModalOpen, setUrlModalOpen] = useState(false);
  const [pasteUrlInput, setPasteUrlInput] = useState("");
  const [isScraping, setIsScraping] = useState(false);

  useEffect(() => {
    api.getOrganisations()
      .then((orgs) => {
        setOrganisations(orgs);
        if (orgs.length > 0) {
          const stored = localStorage.getItem("grant_agent_active_org");
          if (stored && orgs.some(o => o.id === stored)) {
            setSelectedOrgId(stored);
          } else {
            setSelectedOrgId(orgs[0].id);
            localStorage.setItem("grant_agent_active_org", orgs[0].id);
          }
        }
      })
      .catch((err) => console.error("Error loading organisations:", err));
  }, []);

  const handleOrgChange = (id: string) => {
    setSelectedOrgId(id);
    localStorage.setItem("grant_agent_active_org", id);
    window.dispatchEvent(new Event("orgChanged"));
  };

  const handlePasteUrlSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!pasteUrlInput) return;
    setIsScraping(true);
    try {
      const grant = await api.pasteGrantUrl(pasteUrlInput, selectedOrgId);
      setUrlModalOpen(false);
      setPasteUrlInput("");
      window.location.href = `/grants/${grant.id}`;
    } catch (err: any) {
      alert("Error discovering grant from URL: " + err.message);
    } finally {
      setIsScraping(false);
    }
  };

  const navItems = [
    { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
    { name: "Discover Grants", href: "/discover", icon: Compass },
    { name: "Saved Grants", href: "/saved", icon: Bookmark },
    { name: "Organisations", href: "/organisations", icon: Building2 },
    { name: "Applications", href: "/applications", icon: FileText },
    { name: "Documents", href: "/documents", icon: FolderLock },
    { name: "Automation", href: "/automation", icon: Bot },
    { name: "Notifications", href: "/notifications", icon: Bell },
    { name: "Settings", href: "/settings", icon: Settings },
  ];

  return (
    <div className="flex h-screen bg-slate-900 text-slate-100 font-sans overflow-hidden">
      {/* Sidebar */}
      <aside className="w-64 bg-slate-950 border-r border-slate-800 flex flex-col justify-between shrink-0">
        <div>
          {/* Logo */}
          <div className="p-6 border-b border-slate-800/80 flex items-center justify-between">
            <Link href="/dashboard" className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center font-bold text-white shadow-lg shadow-indigo-500/30">
                G
              </div>
              <div>
                <span className="font-bold text-base tracking-tight text-white block">Grant Agent</span>
                <span className="text-[10px] text-indigo-400 font-medium tracking-wider uppercase block">Cloud Platform</span>
              </div>
            </Link>
          </div>

          {/* Organisation Profile Selector */}
          <div className="p-4 border-b border-slate-800/60 bg-slate-900/40">
            <label className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block mb-1.5">
              Active Organisation Vault
            </label>
            <select
              value={selectedOrgId}
              onChange={(e) => handleOrgChange(e.target.value)}
              className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none focus:border-indigo-500"
            >
              {organisations.map((org) => (
                <option key={org.id} value={org.id}>
                  {org.organisation_name} ({org.stage.toUpperCase()})
                </option>
              ))}
            </select>
          </div>

          {/* Navigation Links */}
          <nav className="p-3 space-y-1 overflow-y-auto">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = pathname === item.href || pathname.startsWith(`${item.href}/`);
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={`flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-xs font-semibold transition-colors ${
                    isActive
                      ? "bg-indigo-600 text-white shadow-sm"
                      : "text-slate-400 hover:text-slate-200 hover:bg-slate-900"
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span>{item.name}</span>
                </Link>
              );
            })}
          </nav>
        </div>

        {/* Bottom Quick Action: PASTE GRANT URL */}
        <div className="p-4 border-t border-slate-800">
          <button
            onClick={() => setUrlModalOpen(true)}
            className="w-full flex items-center justify-center gap-2 bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 text-white font-semibold py-2.5 px-3 rounded-lg text-xs shadow-md shadow-indigo-600/20 transition-all"
          >
            <Plus className="w-4 h-4" />
            <span>PASTE GRANT URL</span>
          </button>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 bg-slate-900 overflow-hidden">
        {/* Top Header */}
        <header className="h-14 border-b border-slate-800 px-8 flex items-center justify-between bg-slate-950/40 shrink-0">
          <div className="flex items-center gap-3">
            <span className="text-xs font-medium text-slate-400">Environment:</span>
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded text-[11px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
              Google Cloud Production Target
            </span>
          </div>

          <div className="flex items-center gap-4">
            <button
              onClick={() => setUrlModalOpen(true)}
              className="text-xs bg-slate-800 hover:bg-slate-700 text-slate-200 px-3 py-1.5 rounded-md border border-slate-700 flex items-center gap-1.5"
            >
              <span>Paste Official URL</span>
              <ExternalLink className="w-3.5 h-3.5" />
            </button>
            <Link href="/notifications" className="relative p-1.5 text-slate-400 hover:text-white">
              <Bell className="w-4 h-4" />
              <span className="absolute top-1 right-1 w-2 h-2 rounded-full bg-indigo-500 ring-2 ring-slate-900" />
            </Link>
            <div className="flex items-center gap-2 pl-3 border-l border-slate-800">
              <div className="w-7 h-7 rounded-full bg-indigo-700 flex items-center justify-center text-xs font-bold text-white">
                GO
              </div>
              <span className="text-xs font-medium text-slate-200">Grant Officer</span>
            </div>
          </div>
        </header>

        {/* Content Body */}
        <main className="flex-1 overflow-y-auto p-8">{children}</main>
      </div>

      {/* PASTE GRANT URL MODAL */}
      {urlModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-xl max-w-lg w-full p-6 shadow-2xl">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-base font-bold text-white">Paste Official Grant URL</h3>
              <button onClick={() => setUrlModalOpen(false)} className="text-slate-400 hover:text-white text-sm">✕</button>
            </div>
            <p className="text-xs text-slate-400 mb-4">
              Enter any official grant portal or funder call-for-proposals link. The Grant Scout Agent will verify the source, extract criteria, determine eligibility stage (Green/Yellow/Orange/Red), and set up your application.
            </p>
            <form onSubmit={handlePasteUrlSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Official Grant / Application URL</label>
                <input
                  type="url"
                  required
                  placeholder="https://funder.org/grants/application"
                  value={pasteUrlInput}
                  onChange={(e) => setPasteUrlInput(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-indigo-500"
                />
              </div>
              <div className="flex items-center justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setUrlModalOpen(false)}
                  className="px-3 py-1.5 rounded-lg text-xs font-medium text-slate-400 hover:bg-slate-800"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isScraping}
                  className="px-4 py-2 rounded-lg text-xs font-semibold bg-indigo-600 hover:bg-indigo-500 text-white flex items-center gap-1.5 shadow"
                >
                  {isScraping ? "Scouting & Verifying..." : "Discover & Extract Grant"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
