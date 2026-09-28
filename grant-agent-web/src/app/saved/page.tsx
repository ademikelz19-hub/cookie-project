"use client";

import React, { useState, useEffect } from "react";
import { Bookmark, Compass } from "lucide-react";
import Link from "next/link";
import { api } from "../../lib/api";
import { Grant } from "../../types";
import { GrantCard } from "../../components/GrantCard";

export default function SavedGrantsPage() {
  const [grants, setGrants] = useState<Grant[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // For demo/prototype, show first 2 grants as bookmarked
    api.getGrants()
      .then((data) => setGrants(data.slice(0, 2)))
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      <div className="border-b border-slate-800 pb-5 flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Saved Funding Opportunities</h1>
          <p className="text-xs text-slate-400 mt-1">Bookmarked grants shortlisted for review and positioning.</p>
        </div>
      </div>

      {loading ? (
        <div className="flex items-center justify-center h-48">
          <div className="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
        </div>
      ) : grants.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {grants.map((grant) => (
            <GrantCard key={grant.id} grant={grant} isSaved={true} />
          ))}
        </div>
      ) : (
        <div className="bg-slate-950 border border-slate-800 rounded-xl p-12 text-center">
          <Bookmark className="w-8 h-8 text-slate-600 mx-auto mb-3" />
          <p className="text-sm font-semibold text-slate-300 mb-1">No saved grants yet</p>
          <p className="text-xs text-slate-500 mb-4">Explore open opportunities and bookmark relevant grants.</p>
          <Link
            href="/discover"
            className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-indigo-600 text-white text-xs font-semibold hover:bg-indigo-500"
          >
            <Compass className="w-4 h-4" />
            <span>Discover Grants</span>
          </Link>
        </div>
      )}
    </div>
  );
}
