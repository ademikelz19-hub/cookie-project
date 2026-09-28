import React from "react";
import Link from "next/link";
import { Calendar, Globe, DollarSign, Building, ArrowRight, Bookmark } from "lucide-react";
import { Grant } from "../types";
import { StageBadge } from "./StageBadge";

interface GrantCardProps {
  grant: Grant;
  onPrepare?: (grantId: string) => void;
  onSave?: (grantId: string) => void;
  isSaved?: boolean;
}

export function GrantCard({ grant, onPrepare, onSave, isSaved }: GrantCardProps) {
  return (
    <div className="bg-slate-950 border border-slate-800 rounded-xl p-5 hover:border-slate-700 transition-all flex flex-col justify-between shadow-sm">
      <div>
        {/* Top Badges */}
        <div className="flex flex-wrap items-center justify-between gap-2 mb-3">
          <StageBadge stage={grant.stage_classification} />
          <div className="flex items-center gap-1.5">
            <span className="text-[10px] font-semibold uppercase px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
              {grant.application_status}
            </span>
            {grant.eligible_countries.includes("Nigeria") && (
              <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-800">
                Nigeria Eligible
              </span>
            )}
          </div>
        </div>

        {/* Grant Title & Funder */}
        <h3 className="text-base font-bold text-white mb-1 leading-snug line-clamp-2">
          {grant.grant_name}
        </h3>
        <p className="text-xs text-indigo-400 font-medium mb-4 flex items-center gap-1.5">
          <Building className="w-3.5 h-3.5" />
          {grant.funder}
        </p>

        {/* Metrics Grid */}
        <div className="grid grid-cols-2 gap-2.5 py-3 border-y border-slate-850 text-xs mb-4">
          <div className="flex items-center gap-2 text-slate-300">
            <DollarSign className="w-4 h-4 text-emerald-400 shrink-0" />
            <div>
              <span className="text-[10px] text-slate-400 block">Funding Cap</span>
              <span className="font-semibold text-white">
                ${grant.funding_amount_max.toLocaleString()} {grant.currency}
              </span>
            </div>
          </div>

          <div className="flex items-center gap-2 text-slate-300">
            <Calendar className="w-4 h-4 text-amber-400 shrink-0" />
            <div>
              <span className="text-[10px] text-slate-400 block">Deadline</span>
              <span className="font-semibold text-white">{grant.deadline || "Rolling"}</span>
            </div>
          </div>

          <div className="flex items-center gap-2 text-slate-300">
            <Globe className="w-4 h-4 text-blue-400 shrink-0" />
            <div>
              <span className="text-[10px] text-slate-400 block">Geographies</span>
              <span className="font-semibold text-white truncate max-w-[120px] block">
                {grant.eligible_countries.join(", ")}
              </span>
            </div>
          </div>

          <div className="flex items-center gap-2 text-slate-300">
            <span className="w-4 h-4 rounded bg-purple-500/20 text-purple-400 font-bold flex items-center justify-center text-[10px]">
              S
            </span>
            <div>
              <span className="text-[10px] text-slate-400 block">Sector</span>
              <span className="font-semibold text-white truncate max-w-[120px] block">
                {grant.sector}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex items-center gap-2 pt-2">
        <Link
          href={`/grants/${grant.id}`}
          className="flex-1 text-center py-2 px-3 rounded-lg border border-slate-700 hover:bg-slate-850 text-slate-200 text-xs font-semibold transition-colors"
        >
          VIEW
        </Link>
        <button
          onClick={() => onSave && onSave(grant.id)}
          className={`p-2 rounded-lg border text-xs font-semibold transition-colors ${
            isSaved
              ? "border-amber-500/40 bg-amber-500/10 text-amber-400"
              : "border-slate-700 hover:bg-slate-850 text-slate-300"
          }`}
          title="Save grant"
        >
          <Bookmark className="w-3.5 h-3.5" />
        </button>
        <button
          onClick={() => onPrepare && onPrepare(grant.id)}
          className="flex-[1.5] flex items-center justify-center gap-1.5 py-2 px-3 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-sm transition-colors"
        >
          <span>PREPARE APPLICATION</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </button>
      </div>
    </div>
  );
}
