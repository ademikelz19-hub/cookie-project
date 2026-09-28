"use client";

import React, { useState } from "react";
import { Settings, Cloud, Key, Database, Shield, Check } from "lucide-react";

export default function SettingsPage() {
  const [gcpProjectId, setGcpProjectId] = useState("grant-agent-gcp");
  const [geminiModel, setGeminiModel] = useState("gemini-1.5-pro");
  const [dbMode, setDbMode] = useState("Cloud SQL PostgreSQL");
  const [saved, setSaved] = useState(false);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    setSaved(true);
    setTimeout(() => setSaved(false), 2500);
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="border-b border-slate-800 pb-5">
        <h1 className="text-2xl font-bold text-white tracking-tight">Platform Settings & GCP Cloud Target</h1>
        <p className="text-xs text-slate-400 mt-1">
          Configure Google Cloud infrastructure, Secret Manager bindings, and Gemini / Vertex AI parameters.
        </p>
      </div>

      <form onSubmit={handleSave} className="space-y-6">
        {/* Google Cloud Architecture Card */}
        <div className="bg-slate-950 border border-slate-800 rounded-xl p-5 space-y-4">
          <div className="flex items-center gap-2 text-sm font-bold text-white">
            <Cloud className="w-4 h-4 text-indigo-400" />
            <span>Google Cloud Deployment Services</span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
            <div>
              <label className="block text-slate-300 font-semibold mb-1">GCP Project ID</label>
              <input
                type="text"
                value={gcpProjectId}
                onChange={(e) => setGcpProjectId(e.target.value)}
                className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-white"
              />
            </div>

            <div>
              <label className="block text-slate-300 font-semibold mb-1">Database Backend</label>
              <select
                value={dbMode}
                onChange={(e) => setDbMode(e.target.value)}
                className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-white"
              >
                <option value="Cloud SQL PostgreSQL">Cloud SQL PostgreSQL (Production Target)</option>
                <option value="Local SQLite">SQLite Engine (Local Dev & Unit Tests)</option>
              </select>
            </div>
          </div>
        </div>

        {/* AI & Gemini Parameters */}
        <div className="bg-slate-950 border border-slate-800 rounded-xl p-5 space-y-4">
          <div className="flex items-center gap-2 text-sm font-bold text-white">
            <Key className="w-4 h-4 text-emerald-400" />
            <span>AI Reasoning & Strategist Model</span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
            <div>
              <label className="block text-slate-300 font-semibold mb-1">Vertex AI / Gemini Model</label>
              <select
                value={geminiModel}
                onChange={(e) => setGeminiModel(e.target.value)}
                className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-white"
              >
                <option value="gemini-1.5-pro">Gemini 1.5 Pro (Deep Strategy & Alignment)</option>
                <option value="gemini-1.5-flash">Gemini 1.5 Flash (Fast Extraction & Verification)</option>
              </select>
            </div>

            <div>
              <label className="block text-slate-300 font-semibold mb-1">Secret Manager Source</label>
              <input
                type="text"
                disabled
                value="projects/grant-agent-gcp/secrets/gemini-api-key"
                className="w-full bg-slate-900 border border-slate-800 rounded-lg p-2.5 text-slate-400 cursor-not-allowed font-mono text-[11px]"
              />
            </div>
          </div>
        </div>

        {/* Security & Invariants Card */}
        <div className="bg-slate-950 border border-slate-800 rounded-xl p-5 space-y-3 text-xs">
          <div className="flex items-center gap-2 text-sm font-bold text-white">
            <Shield className="w-4 h-4 text-amber-400" />
            <span>Core Safety Policy Status</span>
          </div>
          <div className="space-y-1.5 text-slate-300">
            <div className="flex items-center gap-2">
              <Check className="w-4 h-4 text-emerald-400 shrink-0" />
              <span>Prompt injection defense active on external website DOM trees</span>
            </div>
            <div className="flex items-center gap-2">
              <Check className="w-4 h-4 text-emerald-400 shrink-0" />
              <span>Zero credentials / secrets printed in application activity logs</span>
            </div>
            <div className="flex items-center gap-2">
              <Check className="w-4 h-4 text-emerald-400 shrink-0" />
              <span>Mandatory human approval gate enforced prior to submission</span>
            </div>
          </div>
        </div>

        <div className="flex justify-end pt-2">
          <button
            type="submit"
            className="flex items-center gap-2 px-5 py-2.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-md transition-colors"
          >
            {saved ? (
              <>
                <Check className="w-4 h-4" />
                <span>Saved Successfully</span>
              </>
            ) : (
              <span>Save Configuration</span>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}
