"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import {
  Compass, Lightbulb, Clock, AlertTriangle, DollarSign,
  ArrowRight, CheckCircle2, ChevronRight, Sparkles, Building
} from "lucide-react";
import { api } from "../../lib/api";
import { DashboardSummary } from "../../types";

export default function DashboardPage() {
  const [data, setData] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getDashboard()
      .then((res) => setData(res))
      .catch((err) => console.error("Error loading dashboard:", err))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto space-y-8">
      {/* Top Welcome Banner */}
      <div className="bg-gradient-to-r from-indigo-950/80 via-slate-900 to-slate-950 border border-indigo-500/20 rounded-2xl p-6 shadow-lg flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-semibold px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-400 border border-indigo-500/30">
              Active Strategy Engine
            </span>
          </div>
          <h1 className="text-2xl font-extrabold text-white tracking-tight">
            Grant Operations & Strategic Dispatch
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            AI-powered discovery, stage-matching, answer preparation, and Playwright browser automation.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Link
            href="/discover?idea_stage_only=true"
            className="flex items-center gap-1.5 px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold shadow-md transition-colors"
          >
            <Sparkles className="w-4 h-4" />
            <span>Idea-Stage Grants Only</span>
          </Link>
          <Link
            href="/discover"
            className="flex items-center gap-1.5 px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 transition-colors"
          >
            <span>Explore All Opportunities</span>
            <ChevronRight className="w-4 h-4" />
          </Link>
        </div>
      </div>

      {/* Primary KPI Metrics Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        {/* Open Grants */}
        <div className="bg-slate-950 border border-slate-800 rounded-xl p-4">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-medium">Open Grants</span>
            <Compass className="w-4 h-4 text-indigo-400" />
          </div>
          <div className="text-2xl font-bold text-white">{data?.open_grants || 0}</div>
          <span className="text-[11px] text-emerald-400 font-medium">Authoritative verified</span>
        </div>

        {/* Idea-Stage Grants */}
        <div className="bg-slate-950 border border-slate-800 rounded-xl p-4">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-medium">Idea-Stage Grants</span>
            <Lightbulb className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-bold text-white">{data?.idea_stage_grants || 0}</div>
          <span className="text-[11px] text-emerald-400 font-medium">No MVP required to apply</span>
        </div>

        {/* Applications in Progress */}
        <div className="bg-slate-950 border border-slate-800 rounded-xl p-4">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-medium">In Progress</span>
            <Clock className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-2xl font-bold text-white">{data?.applications_in_progress || 0}</div>
          <span className="text-[11px] text-slate-400">Preparing / In automation</span>
        </div>

        {/* Requires Attention */}
        <div className="bg-slate-950 border border-slate-800 rounded-xl p-4">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-medium">Requires Attention</span>
            <AlertTriangle className="w-4 h-4 text-rose-400" />
          </div>
          <div className="text-2xl font-bold text-white">{data?.applications_requiring_attention || 0}</div>
          <span className="text-[11px] text-rose-400 font-medium">Approval or OTP gate active</span>
        </div>

        {/* Funding Potential */}
        <div className="bg-slate-950 border border-slate-800 rounded-xl p-4">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-medium">Funding Potential</span>
            <DollarSign className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-bold text-white">
            ${((data?.funding_potential_usd || 0) / 1000).toFixed(0)}k
          </div>
          <span className="text-[11px] text-slate-400">Available funding pool</span>
        </div>
      </div>

      {/* Two Column Layout: Deadlines & Recent Submissions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Upcoming Deadlines */}
        <div className="bg-slate-950 border border-slate-800 rounded-xl p-5 shadow-sm">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-sm font-bold text-white flex items-center gap-2">
              <Clock className="w-4 h-4 text-amber-400" />
              <span>Upcoming Funder Deadlines</span>
            </h2>
            <Link href="/discover" className="text-xs text-indigo-400 hover:underline">
              View Calendar &rarr;
            </Link>
          </div>

          <div className="space-y-3">
            {data?.upcoming_deadlines?.map((grant) => (
              <div
                key={grant.id}
                className="flex items-center justify-between p-3 rounded-lg bg-slate-900 border border-slate-800 hover:border-slate-700 transition-colors"
              >
                <div>
                  <h4 className="text-xs font-semibold text-white">{grant.grant_name}</h4>
                  <p className="text-[11px] text-slate-400">{grant.funder}</p>
                </div>
                <div className="text-right">
                  <span className="text-xs font-mono font-bold text-amber-400 block">{grant.deadline}</span>
                  <span className="text-[10px] text-slate-400">Up to ${grant.amount_max.toLocaleString()}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Recent Submissions */}
        <div className="bg-slate-950 border border-slate-800 rounded-xl p-5 shadow-sm">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-sm font-bold text-white flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <span>Recently Submitted Applications</span>
            </h2>
            <Link href="/applications" className="text-xs text-indigo-400 hover:underline">
              Application Tracker &rarr;
            </Link>
          </div>

          {data?.recent_submissions && data.recent_submissions.length > 0 ? (
            <div className="space-y-3">
              {data.recent_submissions.map((sub) => (
                <div
                  key={sub.id}
                  className="flex items-center justify-between p-3 rounded-lg bg-slate-900 border border-slate-800"
                >
                  <div>
                    <h4 className="text-xs font-semibold text-white">{sub.grant_name}</h4>
                    <p className="text-[11px] text-slate-400">Org: {sub.organisation_name}</p>
                  </div>
                  <div className="text-right">
                    <span className="text-xs font-mono font-bold text-emerald-400 block">{sub.reference}</span>
                    <span className="text-[10px] text-slate-400">{sub.status}</span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-slate-500 text-xs">
              No applications submitted yet. Ready to prepare your first grant application.
            </div>
          )}
        </div>
      </div>

      {/* Recently Discovered Grants */}
      <div className="bg-slate-950 border border-slate-800 rounded-xl p-5 shadow-sm">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-sm font-bold text-white flex items-center gap-2">
            <Compass className="w-4 h-4 text-indigo-400" />
            <span>Recently Discovered Opportunities</span>
          </h2>
          <Link href="/discover" className="text-xs text-indigo-400 hover:underline">
            All Grants &rarr;
          </Link>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {data?.recent_grants?.map((g) => (
            <div key={g.id} className="p-4 rounded-lg bg-slate-900 border border-slate-800 hover:border-slate-700 transition-colors flex flex-col justify-between">
              <div>
                <span className="text-[10px] font-semibold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20 inline-block mb-2">
                  {g.stage}
                </span>
                <h4 className="text-xs font-bold text-white line-clamp-1 mb-1">{g.grant_name}</h4>
                <p className="text-[11px] text-slate-400">{g.funder}</p>
              </div>

              <div className="pt-4 border-t border-slate-800 mt-3 flex items-center justify-between">
                <span className="text-xs font-bold text-white">${g.amount_max.toLocaleString()}</span>
                <Link
                  href={`/grants/${g.id}`}
                  className="text-xs text-indigo-400 font-semibold hover:underline flex items-center gap-1"
                >
                  <span>Analyse</span>
                  <ArrowRight className="w-3 h-3" />
                </Link>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
