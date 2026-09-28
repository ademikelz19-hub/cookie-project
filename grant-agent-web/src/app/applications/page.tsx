"use client";

export const dynamic = "force-dynamic";

import React, { useState, useEffect } from "react";
import { useSearchParams } from "next/navigation";
import {
  FileText, CheckCircle2, AlertTriangle, AlertCircle, Clock,
  ArrowRight, ShieldCheck, ExternalLink, Bot, Check, Edit3, X
} from "lucide-react";
import { api } from "../../lib/api";
import { ApplicationItem, ApplicationReviewSummary, ApplicationStatus } from "../../types";

function ApplicationsContent() {
  const searchParams = useSearchParams();
  const [applications, setApplications] = useState<ApplicationItem[]>([]);
  const [selectedApp, setSelectedApp] = useState<ApplicationItem | null>(null);
  const [reviewSummary, setReviewSummary] = useState<ApplicationReviewSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [editingQuestionId, setEditingQuestionId] = useState<string | null>(null);
  const [editText, setEditText] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const loadApplications = () => {
    setLoading(true);
    api.getApplications()
      .then((apps) => {
        setApplications(apps);
        const activeParam = searchParams.get("active");
        if (activeParam) {
          const found = apps.find(a => a.id === activeParam);
          if (found) {
            setSelectedApp(found);
            api.getApplicationReview(found.id).then(r => setReviewSummary(r));
          }
        } else if (apps.length > 0 && !selectedApp) {
          setSelectedApp(apps[0]);
          api.getApplicationReview(apps[0].id).then(r => setReviewSummary(r));
        }
      })
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadApplications();
  }, [searchParams]);

  const handleSelectApp = (app: ApplicationItem) => {
    setSelectedApp(app);
    api.getApplicationReview(app.id)
      .then((r) => setReviewSummary(r))
      .catch((err) => console.error(err));
  };

  const handleSaveAnswer = async (qId: string) => {
    if (!selectedApp) return;
    try {
      await api.updateAnswer(selectedApp.id, qId, editText, true);
      setEditingQuestionId(null);
      // Reload application
      const updated = await api.getApplication(selectedApp.id);
      setSelectedApp(updated);
      const rev = await api.getApplicationReview(selectedApp.id);
      setReviewSummary(rev);
    } catch (err: any) {
      alert("Error saving answer: " + err.message);
    }
  };

  const handleApprove = async () => {
    if (!selectedApp) return;
    try {
      const updated = await api.approveApplication(selectedApp.id, true, true);
      setSelectedApp(updated);
      const rev = await api.getApplicationReview(selectedApp.id);
      setReviewSummary(rev);
      alert("Application approved by user! Ready for browser automation or final submission.");
    } catch (err: any) {
      alert("Approval error: " + err.message);
    }
  };

  const handleSubmit = async () => {
    if (!selectedApp) return;
    setSubmitting(true);
    try {
      const submitted = await api.submitApplication(selectedApp.id);
      setSelectedApp(submitted);
      loadApplications();
      alert(`Application officially submitted! Reference: ${submitted.application_reference}`);
    } catch (err: any) {
      alert("Submission error: " + err.message);
    } finally {
      setSubmitting(false);
    }
  };

  const statuses: ApplicationStatus[] = [
    "Preparing", "Ready to Apply", "Application Started", "Waiting for User",
    "Ready for Review", "Submitted", "Under Review", "Awarded"
  ];

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 border-b border-slate-800 pb-5">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Applications & Review Gates</h1>
          <p className="text-xs text-slate-400 mt-1">
            End-to-end grant proposal preparation, factual consistency validation, and human approval gates.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Application Tracker List */}
        <div className="space-y-3">
          <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider px-1">
            Applications Tracker ({applications.length})
          </h3>

          <div className="space-y-2">
            {applications.map((app) => {
              const isSelected = selectedApp?.id === app.id;
              return (
                <div
                  key={app.id}
                  onClick={() => handleSelectApp(app)}
                  className={`p-4 rounded-xl border cursor-pointer transition-all ${
                    isSelected
                      ? "bg-slate-950 border-indigo-500 shadow-md ring-1 ring-indigo-500"
                      : "bg-slate-950/60 border-slate-800 hover:border-slate-700"
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                      {app.status}
                    </span>
                    <span className="text-xs font-bold text-slate-400">{app.completion_percentage}% Done</span>
                  </div>

                  <h4 className="text-xs font-bold text-white mb-1 line-clamp-1">{app.project_title || "Grant Project"}</h4>
                  <div className="w-full bg-slate-900 rounded-full h-1.5 overflow-hidden mt-3">
                    <div
                      className="bg-indigo-500 h-1.5 rounded-full"
                      style={{ width: `${app.completion_percentage}%` }}
                    />
                  </div>

                  {app.application_reference && (
                    <div className="mt-2 text-[10px] font-mono text-emerald-400 font-semibold">
                      Ref: {app.application_reference}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* Right: APPLICATION REVIEW SCREEN (Section 16) */}
        <div className="lg:col-span-2 space-y-6">
          {selectedApp && reviewSummary ? (
            <div className="bg-slate-950 border border-slate-800 rounded-xl p-6 shadow-sm space-y-6">
              {/* Review Header Banner */}
              <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 pb-5 border-b border-slate-850">
                <div>
                  <span className="text-[11px] font-bold text-indigo-400 uppercase tracking-wider block mb-1">
                    Application Review Screen
                  </span>
                  <h2 className="text-xl font-black text-white">{reviewSummary.grant_name}</h2>
                  <p className="text-xs text-slate-400 mt-0.5">
                    Applicant: <strong className="text-white">{reviewSummary.organisation_name}</strong> | Deadline: {reviewSummary.deadline}
                  </p>
                </div>

                <div className="text-right">
                  <span className="text-xs text-slate-400 block mb-1">Completion Readiness</span>
                  <div className="text-2xl font-black text-indigo-400">{reviewSummary.completion_percentage}%</div>
                </div>
              </div>

              {/* Progress & Validation Stats Grid */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
                <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
                  <span className="text-[11px] text-slate-400 block">Questions Completed</span>
                  <span className="text-base font-bold text-emerald-400">
                    {reviewSummary.questions_completed} / {reviewSummary.questions_total}
                  </span>
                </div>

                <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
                  <span className="text-[11px] text-slate-400 block">Documents Uploaded</span>
                  <span className="text-base font-bold text-emerald-400">
                    {reviewSummary.documents_uploaded} / {reviewSummary.documents_total_required}
                  </span>
                </div>

                <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
                  <span className="text-[11px] text-slate-400 block">Limit Violations</span>
                  <span className={`text-base font-bold ${
                    reviewSummary.word_limit_violations.length > 0 ? "text-rose-400" : "text-emerald-400"
                  }`}>
                    {reviewSummary.word_limit_violations.length}
                  </span>
                </div>

                <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
                  <span className="text-[11px] text-slate-400 block">Human Approval</span>
                  <span className={`text-base font-bold ${selectedApp.human_approved ? "text-emerald-400" : "text-amber-400"}`}>
                    {selectedApp.human_approved ? "Granted" : "Pending Gate"}
                  </span>
                </div>
              </div>

              {/* Warnings & Potential Contradictions (Consistency Checker) */}
              {(reviewSummary.warnings.length > 0 || reviewSummary.potential_errors.length > 0 || reviewSummary.word_limit_violations.length > 0) && (
                <div className="p-4 rounded-xl bg-amber-950/20 border border-amber-500/30 space-y-2 text-xs">
                  <div className="font-bold text-amber-400 flex items-center gap-1.5">
                    <AlertTriangle className="w-4 h-4" />
                    <span>Application Consistency Checker Audits</span>
                  </div>
                  {reviewSummary.potential_errors.map((err, i) => (
                    <div key={i} className="text-rose-300 flex items-start gap-2">
                      <span className="text-rose-500">•</span>
                      <span>{err}</span>
                    </div>
                  ))}
                  {reviewSummary.warnings.map((w, i) => (
                    <div key={i} className="text-amber-200/90 flex items-start gap-2">
                      <span className="text-amber-400">•</span>
                      <span>{w}</span>
                    </div>
                  ))}
                  {reviewSummary.word_limit_violations.map((v, i) => (
                    <div key={i} className="text-rose-300 flex items-start gap-2">
                      <span className="text-rose-500">•</span>
                      <span>Word Limit Violation: {v}</span>
                    </div>
                  ))}
                </div>
              )}

              {/* Draft Questions and Answers Preview */}
              <div className="space-y-4">
                <h3 className="text-sm font-bold text-white">Application Questions & Draft Answers</h3>
                <div className="space-y-3">
                  {selectedApp.questions.map((q, idx) => (
                    <div key={q.id} className="p-4 rounded-lg bg-slate-900 border border-slate-800 space-y-2">
                      <div className="flex justify-between items-start gap-2">
                        <span className="text-xs font-bold text-white">
                          {idx + 1}. {q.question_text}
                        </span>
                        <div className="flex items-center gap-2 shrink-0">
                          <span className="text-[10px] text-slate-400">
                            {q.answer ? `${q.answer.word_count} words` : "No answer"}
                          </span>
                          <button
                            onClick={() => {
                              setEditingQuestionId(q.id);
                              setEditText(q.answer?.answer_text || "");
                            }}
                            className="p-1 text-slate-400 hover:text-white"
                          >
                            <Edit3 className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      </div>

                      {editingQuestionId === q.id ? (
                        <div className="space-y-2 pt-2">
                          <textarea
                            value={editText}
                            onChange={(e) => setEditText(e.target.value)}
                            rows={4}
                            className="w-full bg-slate-950 border border-slate-700 rounded-lg p-3 text-xs text-white"
                          />
                          <div className="flex justify-end gap-2">
                            <button
                              onClick={() => setEditingQuestionId(null)}
                              className="px-2.5 py-1 text-xs text-slate-400 hover:bg-slate-800 rounded"
                            >
                              Cancel
                            </button>
                            <button
                              onClick={() => handleSaveAnswer(q.id)}
                              className="px-3 py-1 text-xs font-semibold bg-indigo-600 hover:bg-indigo-500 text-white rounded"
                            >
                              Save Answer
                            </button>
                          </div>
                        </div>
                      ) : (
                        <p className="text-xs text-slate-300 leading-relaxed bg-slate-950/60 p-3 rounded-md border border-slate-850">
                          {q.answer?.answer_text || <span className="text-rose-400">[REQUIRED FROM APPLICANT]</span>}
                        </p>
                      )}

                      {q.answer?.source_information_used && q.answer.source_information_used.length > 0 && (
                        <div className="text-[10px] text-slate-500 flex items-center gap-1.5 pt-1">
                          <ShieldCheck className="w-3 h-3 text-emerald-400" />
                          <span>Sources: {q.answer.source_information_used.join(", ")}</span>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>

              {/* Review Screen Action Bar (Section 16) */}
              <div className="pt-6 border-t border-slate-850 flex flex-wrap items-center justify-between gap-3">
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => {
                      if (selectedApp.questions.length > 0) {
                        setEditingQuestionId(selectedApp.questions[0].id);
                        setEditText(selectedApp.questions[0].answer?.answer_text || "");
                      }
                    }}
                    className="px-3.5 py-2 rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-200 text-xs font-semibold border border-slate-700"
                  >
                    EDIT APPLICATION
                  </button>

                  <button
                    onClick={() => window.open("/mock-portal", "_blank")}
                    className="px-3.5 py-2 rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-300 text-xs font-semibold border border-slate-800 flex items-center gap-1.5"
                  >
                    <span>OPEN APPLICATION WEBSITE</span>
                    <ExternalLink className="w-3.5 h-3.5" />
                  </button>

                  <button
                    onClick={() => window.location.href = `/automation?appId=${selectedApp.id}`}
                    className="px-3.5 py-2 rounded-lg bg-indigo-900/40 hover:bg-indigo-900/60 text-indigo-300 text-xs font-semibold border border-indigo-700/50 flex items-center gap-1.5"
                  >
                    <Bot className="w-3.5 h-3.5" />
                    <span>CONTINUE AUTOMATION</span>
                  </button>
                </div>

                <div className="flex items-center gap-3">
                  {!selectedApp.human_approved ? (
                    <button
                      onClick={handleApprove}
                      className="px-5 py-2.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold shadow-md flex items-center gap-1.5"
                    >
                      <Check className="w-4 h-4 stroke-[3]" />
                      <span>APPROVE APPLICATION</span>
                    </button>
                  ) : (
                    <button
                      onClick={handleSubmit}
                      disabled={submitting || selectedApp.status === "Submitted"}
                      className="px-5 py-2.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white text-xs font-bold shadow-md flex items-center gap-1.5"
                    >
                      <ArrowRight className="w-4 h-4" />
                      <span>{selectedApp.status === "Submitted" ? "OFFICIALLY SUBMITTED" : "APPROVE AND SUBMIT"}</span>
                    </button>
                  )}
                </div>
              </div>
            </div>
          ) : (
            <div className="bg-slate-950 border border-slate-800 rounded-xl p-12 text-center text-slate-400 text-xs">
              Select an application on the left or discover a new grant to prepare.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default function ApplicationsPage() {
  return (
    <React.Suspense fallback={<div className="p-8 text-center text-xs text-slate-500">Loading applications...</div>}>
      <ApplicationsContent />
    </React.Suspense>
  );
}
