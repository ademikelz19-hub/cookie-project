"use client";

import React, { useState, useEffect } from "react";
import {
  Building2, CheckCircle2, AlertCircle, ShieldAlert,
  Users, Layers, Award, TrendingUp, DollarSign, Heart, Cpu
} from "lucide-react";
import { api } from "../../lib/api";
import { Organisation, VerificationStatus } from "../../types";
import { VerificationBadge } from "../../components/VerificationBadge";

export default function OrganisationsPage() {
  const [organisations, setOrganisations] = useState<Organisation[]>([]);
  const [selectedOrg, setSelectedOrg] = useState<Organisation | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getOrganisations()
      .then((orgs) => {
        setOrganisations(orgs);
        if (orgs.length > 0) {
          const activeId = localStorage.getItem("grant_agent_active_org");
          const found = orgs.find(o => o.id === activeId) || orgs[0];
          setSelectedOrg(found);
        }
      })
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  const handleUpdateStatus = async (section: string, status: VerificationStatus) => {
    if (!selectedOrg) return;
    try {
      const updated = await api.updateOrganisationVerification(selectedOrg.id, section, status);
      setSelectedOrg(updated);
      setOrganisations(organisations.map(o => o.id === updated.id ? updated : o));
    } catch (err: any) {
      alert("Error updating verification: " + err.message);
    }
  };

  if (loading || !selectedOrg) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  const sections = [
    {
      id: "basic_details",
      title: "Basic Details",
      status: selectedOrg.basic_details_status,
      icon: Building2,
      fields: [
        { label: "Organisation Name", val: selectedOrg.organisation_name },
        { label: "Project Name", val: selectedOrg.project_name },
        { label: "Registration Status", val: `${selectedOrg.registration_status} (${selectedOrg.registration_number || 'N/A'})` },
        { label: "Operating Countries", val: selectedOrg.operating_countries?.join(", ") },
        { label: "Official Email", val: selectedOrg.email },
        { label: "Website", val: selectedOrg.website },
      ]
    },
    {
      id: "description",
      title: "Mission, Vision & Description",
      status: selectedOrg.description_status,
      icon: Layers,
      fields: [
        { label: "Short Description", val: selectedOrg.short_description },
        { label: "Mission Statement", val: selectedOrg.mission },
        { label: "Vision", val: selectedOrg.vision },
      ]
    },
    {
      id: "problem",
      title: "Problem Statement & Audience",
      status: selectedOrg.problem_status,
      icon: AlertCircle,
      fields: [
        { label: "Core Problems Addressed", val: selectedOrg.problems_addressed },
        { label: "Target Audience", val: selectedOrg.target_audience },
        { label: "Target Geographies", val: selectedOrg.geography },
        { label: "Underserved Groups", val: selectedOrg.underserved_groups },
      ]
    },
    {
      id: "solution",
      title: "Solution, Products & Programmes",
      status: selectedOrg.solution_status,
      icon: Cpu,
      fields: [
        { label: "Core Products", val: selectedOrg.products },
        { label: "Programmes", val: selectedOrg.programmes },
        { label: "Technical Solution", val: selectedOrg.technology_solution },
      ]
    },
    {
      id: "stage",
      title: "Development Stage",
      status: selectedOrg.stage_status,
      icon: Award,
      fields: [
        { label: "Current Lifecycle Stage", val: selectedOrg.stage.toUpperCase() },
      ]
    },
    {
      id: "traction",
      title: "Traction & Verification Metrics",
      status: selectedOrg.traction_status,
      icon: TrendingUp,
      fields: [
        { label: "Active Users", val: selectedOrg.users_count.toLocaleString() },
        { label: "Verified Beneficiaries", val: selectedOrg.beneficiaries_count.toLocaleString() },
        { label: "Annual Revenue", val: `$${selectedOrg.revenue_amount.toLocaleString()}` },
        { label: "Pilots & Deployments", val: selectedOrg.pilots_description },
        { label: "Partnerships", val: selectedOrg.partnerships_description },
      ]
    },
    {
      id: "funding",
      title: "Previous Funding & Capital",
      status: selectedOrg.funding_status,
      icon: DollarSign,
      fields: [
        { label: "Founder Funding", val: selectedOrg.founder_funding },
        { label: "Previous Grants", val: selectedOrg.previous_grants },
        { label: "Current Target", val: selectedOrg.current_fundraising },
      ]
    },
    {
      id: "impact",
      title: "Impact, Gender & SDGs",
      status: selectedOrg.impact_status,
      icon: Heart,
      fields: [
        { label: "Gender Representation", val: selectedOrg.gender_representation },
        { label: "Employment Created", val: `${selectedOrg.employment_created} Jobs` },
        { label: "SDG Alignment", val: selectedOrg.sdgs?.join("; ") },
        { label: "Measurable Impact", val: selectedOrg.measurable_social_impact },
      ]
    },
    {
      id: "financial",
      title: "Financial History & Project Budgets",
      status: selectedOrg.financial_status,
      icon: DollarSign,
      fields: [
        { label: "Annual Operating Budget", val: `$${selectedOrg.annual_budget.toLocaleString()}` },
        { label: "Financial History", val: selectedOrg.financial_history },
      ]
    }
  ];

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 border-b border-slate-800 pb-5">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Organisation Profile Vault</h1>
          <p className="text-xs text-slate-400 mt-1">
            Maintain verified applicant facts. AI writers are strictly restricted to <strong>VERIFIED</strong> data.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <select
            value={selectedOrg.id}
            onChange={(e) => {
              const found = organisations.find(o => o.id === e.target.value);
              if (found) {
                setSelectedOrg(found);
                localStorage.setItem("grant_agent_active_org", found.id);
              }
            }}
            className="bg-slate-950 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-white"
          >
            {organisations.map((org) => (
              <option key={org.id} value={org.id}>{org.organisation_name}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Verification Mandate Alert */}
      <div className="p-4 rounded-xl bg-indigo-950/40 border border-indigo-500/30 flex items-start gap-3 text-xs">
        <ShieldAlert className="w-5 h-5 text-indigo-400 shrink-0 mt-0.5" />
        <div className="text-slate-300 leading-relaxed">
          <strong className="text-white block font-semibold mb-0.5">Strict Factual Guarantee Protocol:</strong>
          Any section marked as <span className="text-slate-400 font-semibold">UNVERIFIED</span> or <span className="text-rose-400 font-semibold">DO NOT USE</span> will trigger an explicit <code className="text-indigo-300 font-mono">[REQUIRED FROM APPLICANT]</code> review checkpoint and will never be fabricated in grant applications.
        </div>
      </div>

      {/* Sections List */}
      <div className="space-y-4">
        {sections.map((sec) => {
          const Icon = sec.icon;
          return (
            <div key={sec.id} className="bg-slate-950 border border-slate-800 rounded-xl p-5 shadow-sm">
              <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 pb-4 border-b border-slate-850">
                <div className="flex items-center gap-2.5">
                  <div className="w-8 h-8 rounded-lg bg-indigo-600/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400">
                    <Icon className="w-4 h-4" />
                  </div>
                  <div>
                    <h3 className="text-sm font-bold text-white">{sec.title}</h3>
                    <div className="mt-0.5">
                      <VerificationBadge status={sec.status} />
                    </div>
                  </div>
                </div>

                {/* Granular Verification Controls */}
                <div className="flex items-center gap-1.5 bg-slate-900 p-1 rounded-lg border border-slate-800">
                  <button
                    onClick={() => handleUpdateStatus(sec.id, "VERIFIED")}
                    className={`px-2.5 py-1 rounded text-[11px] font-bold transition-colors ${
                      sec.status === "VERIFIED"
                        ? "bg-emerald-600 text-white"
                        : "text-slate-400 hover:text-white"
                    }`}
                  >
                    VERIFIED
                  </button>
                  <button
                    onClick={() => handleUpdateStatus(sec.id, "UNVERIFIED")}
                    className={`px-2.5 py-1 rounded text-[11px] font-bold transition-colors ${
                      sec.status === "UNVERIFIED"
                        ? "bg-slate-700 text-white"
                        : "text-slate-400 hover:text-white"
                    }`}
                  >
                    UNVERIFIED
                  </button>
                  <button
                    onClick={() => handleUpdateStatus(sec.id, "DO NOT USE")}
                    className={`px-2.5 py-1 rounded text-[11px] font-bold transition-colors ${
                      sec.status === "DO NOT USE"
                        ? "bg-rose-600 text-white"
                        : "text-slate-400 hover:text-white"
                    }`}
                  >
                    DO NOT USE
                  </button>
                </div>
              </div>

              {/* Field Entries Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-4 text-xs">
                {sec.fields.map((f, i) => (
                  <div key={i} className="p-3 rounded-lg bg-slate-900 border border-slate-800/80">
                    <span className="text-[11px] text-slate-400 font-medium block mb-0.5">{f.label}</span>
                    <span className="text-white font-semibold block break-words">
                      {f.val || <span className="text-slate-600 font-normal">Not provided</span>}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
