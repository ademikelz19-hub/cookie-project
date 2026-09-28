"use client";

import React, { useState, useEffect } from "react";
import { useSearchParams } from "next/navigation";
import {
  Bot, Pause, Play, Monitor, AlertTriangle, CheckCircle2,
  RefreshCw, ShieldAlert, ArrowRight, XCircle
} from "lucide-react";
import { api } from "../../lib/api";
import { BrowserSession, ApplicationItem } from "../../types";

function AutomationContent() {
  const searchParams = useSearchParams();
  const [session, setSession] = useState<BrowserSession | null>(null);
  const [applications, setApplications] = useState<ApplicationItem[]>([]);
  const [selectedAppId, setSelectedAppId] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [otpInput, setOtpInput] = useState("");

  useEffect(() => {
    api.getApplications()
      .then((apps) => {
        setApplications(apps);
        const urlAppId = searchParams.get("appId");
        if (urlAppId) {
          setSelectedAppId(urlAppId);
        } else if (apps.length > 0) {
          setSelectedAppId(apps[0].id);
        }
      })
      .catch((err) => console.error(err));
  }, [searchParams]);

  const handleStartAutomation = async () => {
    if (!selectedAppId) return;
    setLoading(true);
    try {
      const sess = await api.startBrowserSession(selectedAppId);
      setSession(sess);
    } catch (err: any) {
      alert("Error initiating browser worker: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleCommand = async (action: string, data?: any) => {
    if (!session) return;
    try {
      const updated = await api.sendBrowserCommand(session.id, action, data);
      setSession(updated);
    } catch (err: any) {
      alert(`Command error: ${err.message}`);
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 border-b border-slate-800 pb-5">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Playwright Browser Automation Worker</h1>
          <p className="text-xs text-slate-400 mt-1">
            Isolated headless Chromium container execution. Live state capture, human intervention gates, and takeover controls.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <select
            value={selectedAppId}
            onChange={(e) => setSelectedAppId(e.target.value)}
            className="bg-slate-950 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-white"
          >
            {applications.map((app) => (
              <option key={app.id} value={app.id}>
                {app.project_title || "Application"} ({app.status})
              </option>
            ))}
          </select>

          <button
            onClick={handleStartAutomation}
            disabled={loading}
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white text-xs font-semibold shadow-md transition-colors"
          >
            <Bot className="w-4 h-4" />
            <span>{loading ? "Starting Worker..." : "Start Browser Session"}</span>
          </button>
        </div>
      </div>

      {session ? (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Live View & Interactive Player */}
          <div className="lg:col-span-2 space-y-4">
            <div className="bg-slate-950 border border-slate-800 rounded-xl overflow-hidden shadow-sm">
              {/* Virtual Browser Top Frame */}
              <div className="bg-slate-900 border-b border-slate-800 px-4 py-2.5 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="flex gap-1.5">
                    <span className="w-2.5 h-2.5 rounded-full bg-rose-500/80" />
                    <span className="w-2.5 h-2.5 rounded-full bg-amber-500/80" />
                    <span className="w-2.5 h-2.5 rounded-full bg-emerald-500/80" />
                  </div>
                  <span className="text-[11px] font-mono text-slate-400 truncate max-w-md ml-2">
                    {session.current_url || "https://funder-portal.org/apply"}
                  </span>
                </div>

                <span className="text-[11px] font-bold px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                  {session.status}
                </span>
              </div>

              {/* Live Canvas / Screenshot Area */}
              <div className="aspect-video bg-slate-900/50 flex flex-col items-center justify-center relative p-6 text-center">
                {session.latest_screenshot_path ? (
                  <img
                    src={`/api/v1/browser/${session.id}/screenshot`}
                    alt="Live Browser Screenshot"
                    className="w-full h-full object-contain rounded"
                  />
                ) : (
                  <div className="space-y-3">
                    <Monitor className="w-12 h-12 text-slate-700 mx-auto animate-pulse" />
                    <div className="text-xs text-slate-400 font-medium">
                      Navigating official grant portal: <strong>{session.current_task}</strong>
                    </div>
                    <span className="text-[11px] text-slate-500 block">Step: {session.current_step}</span>
                  </div>
                )}

                {/* Human Intervention Overlay (Section 13 & 33) */}
                {session.intervention_required && (
                  <div className="absolute inset-0 bg-slate-950/85 backdrop-blur-sm flex items-center justify-center p-6 z-10">
                    <div className="max-w-md w-full bg-slate-900 border border-amber-500/40 rounded-xl p-5 text-center shadow-2xl space-y-4">
                      <div className="w-10 h-10 rounded-full bg-amber-500/20 text-amber-400 flex items-center justify-center mx-auto">
                        <AlertTriangle className="w-5 h-5" />
                      </div>
                      <h4 className="text-sm font-bold text-white">Human Gate: {session.intervention_type}</h4>
                      <p className="text-xs text-slate-300 leading-relaxed">
                        {session.intervention_message || "Human action required to continue automated submission."}
                      </p>

                      {session.intervention_type === "OTP" && (
                        <div className="space-y-3">
                          <input
                            type="text"
                            placeholder="Enter 6-Digit Passkey"
                            value={otpInput}
                            onChange={(e) => setOtpInput(e.target.value)}
                            className="w-full text-center tracking-widest text-lg font-mono bg-slate-950 border border-slate-700 rounded-lg p-2 text-white"
                          />
                          <button
                            onClick={() => handleCommand("submit_intervention", { otp_code: otpInput })}
                            className="w-full py-2 bg-amber-600 hover:bg-amber-500 text-white font-bold rounded-lg text-xs"
                          >
                            Submit Code to Automation
                          </button>
                        </div>
                      )}

                      {session.intervention_type !== "OTP" && (
                        <button
                          onClick={() => handleCommand("resume")}
                          className="w-full py-2 bg-indigo-600 hover:bg-indigo-500 text-white font-bold rounded-lg text-xs"
                        >
                          I Have Completed Verification · Resume
                        </button>
                      )}
                    </div>
                  </div>
                )}
              </div>

              {/* Worker Action Bar (Section 33) */}
              <div className="bg-slate-900 border-t border-slate-800 p-4 flex flex-wrap items-center justify-between gap-3">
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => handleCommand("pause")}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700"
                  >
                    <Pause className="w-3.5 h-3.5" />
                    <span>PAUSE</span>
                  </button>

                  <button
                    onClick={() => handleCommand("resume")}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700"
                  >
                    <Play className="w-3.5 h-3.5" />
                    <span>RESUME</span>
                  </button>

                  <button
                    onClick={() => handleCommand("take_control")}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-amber-950/40 hover:bg-amber-950/60 text-amber-300 text-xs font-semibold border border-amber-800/60"
                  >
                    <Monitor className="w-3.5 h-3.5" />
                    <span>TAKE CONTROL</span>
                  </button>
                </div>

                <button
                  onClick={() => handleCommand("cancel")}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-rose-950/30 hover:bg-rose-950/50 text-rose-300 text-xs font-semibold border border-rose-800/50"
                >
                  <XCircle className="w-3.5 h-3.5" />
                  <span>CANCEL SESSION</span>
                </button>
              </div>
            </div>
          </div>

          {/* Right: Activity Feed & Security Audits */}
          <div className="space-y-4">
            <div className="bg-slate-950 border border-slate-800 rounded-xl p-5 shadow-sm space-y-4">
              <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                Live Worker Activity Feed
              </h3>

              <div className="space-y-2 max-h-96 overflow-y-auto pr-1">
                {session.events && session.events.length > 0 ? (
                  session.events.map((ev, i) => (
                    <div key={i} className="p-3 rounded-lg bg-slate-900 border border-slate-850 text-xs space-y-1">
                      <div className="flex items-center justify-between">
                        <span className="font-semibold text-white capitalize">{ev.event_type}</span>
                        <span className="text-[10px] text-slate-500">
                          {new Date(ev.created_at).toLocaleTimeString()}
                        </span>
                      </div>
                      <p className="text-[11px] text-slate-300">{ev.description}</p>
                    </div>
                  ))
                ) : (
                  <div className="text-center py-6 text-slate-500 text-xs">
                    Session initialized. Awaiting next DOM action.
                  </div>
                )}
              </div>
            </div>

            {/* Prompt Injection Shield Status */}
            <div className="bg-slate-950 border border-slate-800 rounded-xl p-4 text-xs space-y-2">
              <div className="flex items-center gap-2 text-emerald-400 font-bold">
                <ShieldAlert className="w-4 h-4" />
                <span>Untrusted Content Guard</span>
              </div>
              <p className="text-slate-400 text-[11px]">
                Active DOM sanitization filters prevent webpage prompt injection and credential exfiltration attempts.
              </p>
            </div>
          </div>
        </div>
      ) : (
        <div className="bg-slate-950 border border-slate-800 rounded-xl p-12 text-center text-xs">
          <Bot className="w-10 h-10 text-slate-600 mx-auto mb-3" />
          <p className="text-sm font-semibold text-slate-300 mb-1">No Active Browser Session</p>
          <p className="text-xs text-slate-500 mb-6">Select an application and start the automated worker to view live progress.</p>
          <button
            onClick={handleStartAutomation}
            className="px-5 py-2.5 rounded-lg bg-indigo-600 text-white font-semibold shadow-md"
          >
            Launch Browser Automation Worker
          </button>
        </div>
      )}
    </div>
  );
}

export default function AutomationPage() {
  return (
    <React.Suspense fallback={<div className="p-8 text-center text-xs text-slate-500">Loading browser activity...</div>}>
      <AutomationContent />
    </React.Suspense>
  );
}
