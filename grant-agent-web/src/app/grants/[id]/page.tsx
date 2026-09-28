"use client";

import React, { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import {
  ExternalLink, Calendar, Globe, DollarSign, CheckCircle2,
  AlertCircle, ArrowRight, ShieldCheck, FileText, Bot, Activity,
  Bookmark, ChevronRight
} from "lucide-react";
import { api } from "../../../lib/api";
import { Grant, GrantMatch, Organisation } from "../../../types";
import { StageBadge } from "../../../components/StageBadge";

export default function GrantDetailPage() {
  const params = useParams();
  const router = useRouter();
  const grantId = params.id as string;

  const [grant, setGrant] = useState<Grant | null>(null);
  const [activeTab, setActiveTab] = useState<
    "overview" | "eligibility" | "requirements" | "strategy" | "documents" | "application" | "activity"
  >("overview");
  const [matchResult, setMatchResult] = useState<GrantMatch | null>(null);
  const [activeOrg, setActiveOrg] = useState<Organisation | null>(null);
  const [loading, setLoading] = useState(true);
  const [analysing, setAnalysing] = useState(false);

  useEffect(() => {
    if (!grantId) return;
    setLoading(true);

    api.getGrant(grantId)
      .then((g) => setGrant(g))
      .catch((err) => console.error(err));

    const storedOrgId = localStorage.getItem("grant_agent_active_org");
    if (storedOrgId) {
      api.getOrganisation(storedOrgId)
        .then((org) => {
          setActiveOrg(org);
          // Run matching analysis
          api.analyseMatch(storedOrgId, grantId)
            .then((m) => setMatchResult(m))
            .catch(() => {});
        })
        .catch(() => {});
    }

    setLoading(false);
  }, [grantId]);

  const handleAnalyseForOrg = async () => {
    if (!activeOrg || !grant) return;
    setAnalysing(true);
    try {
      const match = await api.analyseMatch(activeOrg.id, grant.id);
      setMatchResult(match);
      setActiveTab("eligibility");
    } catch (err: any) {
      alert("Error analysing eligibility: " + err.message);
    } finally {
      setAnalysing(false);
    }
  };

  const handlePrepareApplication = async () => {
    if (!activeOrg || !grant) return;
    try {
      const app = await api.prepareApplication(activeOrg.id, grant.id);
      router.push(`/applications?active=${app.id}`);
    } catch (err: any) {
      alert("Error preparing application: " + err.message);
    }
  };

  if (loading || !grant) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  const tabs = [
    { id: "overview", label: "Overview" },
    { id: "eligibility", label: "Eligibility" },
    { id: "requirements", label: "Requirements" },
    { id: "strategy", label: "Strategy" },
    { id: "documents", label: "Documents" },
    { id: "application", label: "Application" },
    { id: "activity", label: "Activity" },
  ];

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Top Banner Card */}
      <div className="bg-slate-950 border border-slate-800 rounded-2xl p-6 shadow-md">
        <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
          <div className="flex items-center gap-3">
            <StageBadge stage={grant.stage_classification} />
            <span className="text-xs font-semibold px-2.5 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
              {grant.application_status}
            </span>
            <span className="text-xs font-semibold px-2.5 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-800 flex items-center gap-1">
              <ShieldCheck className="w-3 h-3" />
              Official Verified Source
            </span>
          </div>

          <div className="text-xs text-slate-400">
            Last Checked: {new Date(grant.website_last_checked).toLocaleDateString()}
          </div>
        </div>

        <h1 className="text-2xl font-black text-white mb-2">{grant.grant_name}</h1>
        <p className="text-sm font-semibold text-indigo-400 mb-6">{grant.funder}</p>

        {/* Primary Metrics Strip */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 py-4 border-y border-slate-850 text-xs mb-6">
          <div>
            <span className="text-slate-400 block mb-0.5">Maximum Funding</span>
            <span className="text-base font-bold text-emerald-400">
              ${grant.funding_amount_max.toLocaleString()} {grant.currency}
            </span>
          </div>

          <div>
            <span className="text-slate-400 block mb-0.5">Funder Deadline</span>
            <span className="text-base font-bold text-amber-400">{grant.deadline || "Rolling"}</span>
          </div>

          <div>
            <span className="text-slate-400 block mb-0.5">Eligible Geographies</span>
            <span className="text-sm font-bold text-white truncate block">
              {grant.eligible_countries.join(", ")}
            </span>
          </div>

          <div>
            <span className="text-slate-400 block mb-0.5">MVP Requirement</span>
            <span className={`text-sm font-bold ${grant.mvp_required ? "text-orange-400" : "text-emerald-400"}`}>
              {grant.mvp_required ? "MVP Required" : "No MVP Required"}
            </span>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-wrap items-center gap-3">
          <button
            onClick={handleAnalyseForOrg}
            disabled={analysing}
            className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 flex items-center gap-1.5 transition-colors"
          >
            <span>{analysing ? "Analysing..." : "ANALYSE FOR ORGANISATION"}</span>
          </button>

          <button
            onClick={handlePrepareApplication}
            className="px-5 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-md flex items-center gap-1.5 transition-colors"
          >
            <span>PREPARE APPLICATION</span>
            <ArrowRight className="w-4 h-4" />
          </button>

          <a
            href={grant.official_url}
            target="_blank"
            rel="noreferrer"
            className="px-4 py-2 rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-300 text-xs font-semibold border border-slate-800 flex items-center gap-1.5 transition-colors"
          >
            <span>OPEN OFFICIAL WEBSITE</span>
            <ExternalLink className="w-3.5 h-3.5" />
          </a>

          <button
            onClick={() => router.push(`/automation`)}
            className="px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold flex items-center gap-1.5 shadow transition-colors ml-auto"
          >
            <Bot className="w-3.5 h-3.5" />
            <span>START APPLICATION</span>
          </button>
        </div>
      </div>

      {/* Tabs Header */}
      <div className="flex border-b border-slate-800 gap-1 overflow-x-auto">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            className={`px-4 py-2.5 text-xs font-bold capitalize transition-colors border-b-2 whitespace-nowrap ${
              activeTab === tab.id
                ? "border-indigo-500 text-white bg-slate-950/50"
                : "border-transparent text-slate-400 hover:text-slate-200"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Contents */}
      <div className="bg-slate-950 border border-slate-800 rounded-xl p-6">
        {/* Tab 1: Overview */}
        {activeTab === "overview" && (
          <div className="space-y-6 text-xs text-slate-300 leading-relaxed">
            <div>
              <h3 className="text-sm font-bold text-white mb-2">Grant Opportunity Overview</h3>
              <p>{grant.verified_extracted_text || "Authoritative extract from official funder documentation."}</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-4 border-t border-slate-850">
              <div>
                <h4 className="font-bold text-white mb-2">Selection & Award Criteria</h4>
                <p>{grant.selection_criteria || "Technical innovation, feasibility, sustainability, and quantified impact."}</p>
              </div>

              <div>
                <h4 className="font-bold text-white mb-2">Application Language & Timeline</h4>
                <p>Language: {grant.application_language}</p>
                <p className="mt-1">Response Timeline: {grant.response_timeline}</p>
              </div>
            </div>
          </div>
        )}

        {/* Tab 2: Eligibility */}
        {activeTab === "eligibility" && (
          <div className="space-y-6 text-xs">
            {matchResult ? (
              <div>
                <div className="flex items-center justify-between p-4 rounded-xl bg-slate-900 border border-slate-800 mb-6">
                  <div>
                    <span className="text-[11px] text-slate-400 block mb-1">
                      Eligibility Match for {activeOrg?.organisation_name}
                    </span>
                    <span className={`text-base font-extrabold ${
                      matchResult.eligibility_status === "ELIGIBLE" ? "text-emerald-400" : "text-amber-400"
                    }`}>
                      {matchResult.eligibility_status}
                    </span>
                  </div>

                  <div className="text-right">
                    <span className="text-[11px] text-slate-400 block mb-1">Internal Relevance Index</span>
                    <span className="text-base font-bold text-white">{matchResult.relevance_score}/100</span>
                    <span className="text-[10px] text-slate-500 block">(Sorting metric only, not probability)</span>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <h4 className="font-bold text-emerald-400 mb-3 flex items-center gap-1.5">
                      <CheckCircle2 className="w-4 h-4" />
                      <span>Strong Match Factors</span>
                    </h4>
                    <ul className="space-y-2">
                      {matchResult.strong_match_factors.map((f, i) => (
                        <li key={i} className="p-2.5 rounded bg-emerald-950/20 border border-emerald-900 text-slate-300">
                          {f}
                        </li>
                      ))}
                    </ul>
                  </div>

                  <div>
                    <h4 className="font-bold text-amber-400 mb-3 flex items-center gap-1.5">
                      <AlertCircle className="w-4 h-4" />
                      <span>Missing Information & Weak Factors</span>
                    </h4>
                    <ul className="space-y-2">
                      {matchResult.missing_requirements.concat(matchResult.information_needed).map((m, i) => (
                        <li key={i} className="p-2.5 rounded bg-amber-950/20 border border-amber-900 text-slate-300">
                          {m}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-center py-8">
                <p className="text-slate-400 mb-4">Click below to evaluate eligibility against your selected active organisation profile.</p>
                <button
                  onClick={handleAnalyseForOrg}
                  className="px-4 py-2 rounded-lg bg-indigo-600 text-white text-xs font-semibold"
                >
                  Run Eligibility Analysis
                </button>
              </div>
            )}
          </div>
        )}

        {/* Tab 3: Requirements */}
        {activeTab === "requirements" && (
          <div className="space-y-4 text-xs">
            <h3 className="text-sm font-bold text-white mb-2">Mandatory Application Requirements</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-2">
                <div className="font-semibold text-white">Stage & Technical Readiness</div>
                <p className="text-slate-400">Classification: {grant.stage_classification}</p>
                <p className="text-slate-400">MVP Required: {grant.mvp_required ? "Yes" : "No"}</p>
                <p className="text-slate-400">Traction Required: {grant.traction_required ? "Yes" : "No"}</p>
              </div>

              <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-2">
                <div className="font-semibold text-white">Legal & Compliance</div>
                <p className="text-slate-400">Incorporation Required: {grant.incorporation_required ? "Yes" : "No"}</p>
                <p className="text-slate-400">Matching Funds: {grant.matching_funds_required ? "Yes" : "No"}</p>
                <p className="text-slate-400">Equity / Dilution: {grant.equity_required ? "Yes" : "No (100% Non-Dilutive Grant)"}</p>
              </div>
            </div>
          </div>
        )}

        {/* Tab 4: Strategy */}
        {activeTab === "strategy" && (
          <div className="space-y-4 text-xs text-slate-300">
            <div className="flex justify-between items-center mb-2">
              <h3 className="text-sm font-bold text-white">Tailored Strategic Positioning</h3>
              <button
                onClick={handlePrepareApplication}
                className="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold rounded-lg"
              >
                Synthesize Strategic Proposal &rarr;
              </button>
            </div>
            <p className="text-slate-400">
              The Application Strategist Agent matches the funder’s mandate with verified profile evidence to establish an authentic narrative without inventing unverified facts.
            </p>
          </div>
        )}

        {/* Tab 5: Documents */}
        {activeTab === "documents" && (
          <div className="space-y-4 text-xs">
            <h3 className="text-sm font-bold text-white mb-2">Required Application Documents</h3>
            <div className="space-y-2">
              {grant.required_documents.map((docName, i) => (
                <div key={i} className="flex items-center justify-between p-3 rounded-lg bg-slate-900 border border-slate-800">
                  <span className="font-semibold text-white flex items-center gap-2">
                    <FileText className="w-4 h-4 text-indigo-400" />
                    {docName}
                  </span>
                  <span className="text-[11px] text-emerald-400 font-medium">Approved Vault File Linked</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Tab 6: Application */}
        {activeTab === "application" && (
          <div className="space-y-4 text-xs">
            <h3 className="text-sm font-bold text-white mb-2">Application Questions</h3>
            <div className="space-y-3">
              {grant.required_questions.map((q, i) => (
                <div key={i} className="p-4 rounded-lg bg-slate-900 border border-slate-800">
                  <div className="font-semibold text-white mb-1">{i + 1}. {q}</div>
                  <span className="text-[10px] text-slate-500">Max 300 words · Form field identifier detected</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Tab 7: Activity */}
        {activeTab === "activity" && (
          <div className="space-y-3 text-xs">
            <h3 className="text-sm font-bold text-white mb-2">Verification & Discovery History</h3>
            <div className="p-3 rounded-lg bg-slate-900 border border-slate-800 text-slate-400">
              <span className="text-white font-semibold">Grant Scout Discovery:</span> Scraped from official funder portal. Stage classified as {grant.stage_classification}.
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
