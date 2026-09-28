"use client";

import React, { useState, useEffect } from "react";
import { useSearchParams } from "next/navigation";
import { Search, Filter, Sparkles, Plus, Check } from "lucide-react";
import { api } from "../../lib/api";
import { Grant } from "../../types";
import { GrantCard } from "../../components/GrantCard";

function DiscoverContent() {
  const searchParams = useSearchParams();
  const [grants, setGrants] = useState<Grant[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedSector, setSelectedSector] = useState("All");
  
  // Specific filters required in Section 7
  const [noMvpOnly, setNoMvpOnly] = useState(false);
  const [ideaStageOnly, setIdeaStageOnly] = useState(false);

  // Check URL query parameters
  useEffect(() => {
    if (searchParams.get("idea_stage_only") === "true") {
      setIdeaStageOnly(true);
      setNoMvpOnly(true);
    }
  }, [searchParams]);

  const loadGrants = () => {
    setLoading(true);
    api.getGrants({
      sector: selectedSector !== "All" ? selectedSector : undefined,
      no_mvp_only: noMvpOnly,
      idea_stage_only: ideaStageOnly,
      search_query: searchQuery || undefined,
    })
      .then((data) => setGrants(data))
      .catch((err) => console.error("Error fetching grants:", err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadGrants();
  }, [selectedSector, noMvpOnly, ideaStageOnly]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    loadGrants();
  };

  const sectors = ["All", "Technology", "Web3 / Blockchain", "Social Impact", "Education", "Climate & Sustainability", "Health"];

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-slate-800 pb-5">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Discover Grants & Capital</h1>
          <p className="text-xs text-slate-400 mt-1">
            Scouting official government, philanthropic, tech ecosystem, and foundation opportunities.
          </p>
        </div>

        {/* Essential Filter Toggles */}
        <div className="flex flex-wrap items-center gap-3">
          <button
            onClick={() => {
              const next = !ideaStageOnly;
              setIdeaStageOnly(next);
              if (next) setNoMvpOnly(true);
            }}
            className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-semibold border transition-all ${
              ideaStageOnly
                ? "bg-emerald-500/20 text-emerald-300 border-emerald-500/40 shadow-sm"
                : "bg-slate-950 text-slate-400 border-slate-800 hover:border-slate-700"
            }`}
          >
            <div className={`w-3.5 h-3.5 rounded flex items-center justify-center border ${ideaStageOnly ? "bg-emerald-500 border-emerald-500 text-slate-950" : "border-slate-600"}`}>
              {ideaStageOnly && <Check className="w-2.5 h-2.5 stroke-[3]" />}
            </div>
            <span>Show Idea-Stage Grants Only</span>
          </button>

          <button
            onClick={() => {
              setNoMvpOnly(!noMvpOnly);
              if (ideaStageOnly && noMvpOnly) setIdeaStageOnly(false);
            }}
            className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-semibold border transition-all ${
              noMvpOnly
                ? "bg-indigo-500/20 text-indigo-300 border-indigo-500/40 shadow-sm"
                : "bg-slate-950 text-slate-400 border-slate-800 hover:border-slate-700"
            }`}
          >
            <div className={`w-3.5 h-3.5 rounded flex items-center justify-center border ${noMvpOnly ? "bg-indigo-500 border-indigo-500 text-slate-950" : "border-slate-600"}`}>
              {noMvpOnly && <Check className="w-2.5 h-2.5 stroke-[3]" />}
            </div>
            <span>Show Grants That Do Not Require an MVP</span>
          </button>
        </div>
      </div>

      {/* Search and Filters Bar */}
      <div className="bg-slate-950 border border-slate-800 rounded-xl p-4 flex flex-col md:flex-row items-center gap-4">
        <form onSubmit={handleSearchSubmit} className="flex-1 w-full relative">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
          <input
            type="text"
            placeholder="Search by grant name, funder, keyword, or sector..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-slate-900 border border-slate-700 rounded-lg pl-9 pr-4 py-2 text-xs text-white focus:outline-none focus:border-indigo-500"
          />
        </form>

        <div className="flex items-center gap-2 w-full md:w-auto overflow-x-auto pb-1 md:pb-0">
          <Filter className="w-4 h-4 text-slate-400 shrink-0" />
          {sectors.map((sec) => (
            <button
              key={sec}
              onClick={() => setSelectedSector(sec)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap transition-colors ${
                selectedSector === sec
                  ? "bg-indigo-600 text-white"
                  : "bg-slate-900 text-slate-400 hover:text-slate-200 border border-slate-800"
              }`}
            >
              {sec}
            </button>
          ))}
        </div>
      </div>

      {/* Grant Cards Grid */}
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
        </div>
      ) : grants.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {grants.map((grant) => (
            <GrantCard
              key={grant.id}
              grant={grant}
              onPrepare={async (id) => {
                const orgId = localStorage.getItem("grant_agent_active_org");
                if (!orgId) {
                  alert("Please select or configure an active organisation vault first.");
                  return;
                }
                try {
                  const app = await api.prepareApplication(orgId, id);
                  window.location.href = `/applications?active=${app.id}`;
                } catch (err: any) {
                  alert("Error preparing application: " + err.message);
                }
              }}
            />
          ))}
        </div>
      ) : (
        <div className="bg-slate-950 border border-slate-800 rounded-xl p-12 text-center">
          <p className="text-sm font-semibold text-slate-300 mb-1">No grants matching current filters</p>
          <p className="text-xs text-slate-500 mb-4">Try clearing stage filters or pasting an official grant URL above.</p>
          <button
            onClick={() => {
              setNoMvpOnly(false);
              setIdeaStageOnly(false);
              setSelectedSector("All");
              setSearchQuery("");
            }}
            className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold"
          >
            Reset All Filters
          </button>
        </div>
      )}
    </div>
  );
}

export default function DiscoverPage() {
  return (
    <React.Suspense fallback={<div className="p-8 text-center text-xs text-slate-500">Loading grants...</div>}>
      <DiscoverContent />
    </React.Suspense>
  );
}
