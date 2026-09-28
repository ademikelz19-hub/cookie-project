"use client";

import React, { useState, useEffect } from "react";
import { FolderLock, Upload, FileText, CheckCircle2, XCircle, Search, ShieldCheck } from "lucide-react";
import { api } from "../../lib/api";
import { DocumentItem, DocumentApprovalStatus } from "../../types";

export default function DocumentsPage() {
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploadModalOpen, setUploadModalOpen] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [selectedCategory, setSelectedCategory] = useState("Certificate of incorporation");
  const [fileDescription, setFileDescription] = useState("");
  const [uploading, setUploading] = useState(false);

  const categories = [
    "Certificate of incorporation", "Organisation profile", "Pitch deck",
    "Founder CV", "Team CV", "Recommendation letters", "Financial statements",
    "Bank details", "Safeguarding policy", "Gender policy", "Procurement policy",
    "Governance policy", "Anti-fraud policy", "Monitoring and Evaluation documents",
    "Impact reports", "Previous grant applications", "Project budgets",
    "Theory of Change", "Logical Framework", "References", "Partnership letters",
    "Product screenshots", "Registration documents", "Tax documents", "Other supporting evidence"
  ];

  const loadDocuments = () => {
    setLoading(true);
    const orgId = localStorage.getItem("grant_agent_active_org");
    api.getDocuments(orgId || undefined)
      .then((docs) => setDocuments(docs))
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadDocuments();
    window.addEventListener("orgChanged", loadDocuments);
    return () => window.removeEventListener("orgChanged", loadDocuments);
  }, []);

  const handleToggleApproval = async (doc: DocumentItem) => {
    const nextStatus: DocumentApprovalStatus =
      doc.approval_status === "APPROVED FOR APPLICATION USE"
        ? "NOT APPROVED"
        : "APPROVED FOR APPLICATION USE";
    try {
      const updated = await api.updateDocumentApproval(doc.id, nextStatus);
      setDocuments(documents.map(d => d.id === updated.id ? updated : d));
    } catch (err: any) {
      alert("Error updating document approval: " + err.message);
    }
  };

  const handleUploadSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) return;
    const orgId = localStorage.getItem("grant_agent_active_org");
    if (!orgId) {
      alert("No active organisation selected");
      return;
    }

    setUploading(true);
    try {
      await api.uploadDocument(orgId, selectedCategory, selectedFile, fileDescription);
      setUploadModalOpen(false);
      setSelectedFile(null);
      setFileDescription("");
      loadDocuments();
    } catch (err: any) {
      alert("Upload error: " + err.message);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 border-b border-slate-800 pb-5">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Document Vault</h1>
          <p className="text-xs text-slate-400 mt-1">
            Secure reusable document repository. Only files marked <strong>APPROVED FOR APPLICATION USE</strong> will be uploaded by the browser worker.
          </p>
        </div>

        <button
          onClick={() => setUploadModalOpen(true)}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-md transition-colors"
        >
          <Upload className="w-4 h-4" />
          <span>Upload Document</span>
        </button>
      </div>

      {/* Safety Notice */}
      <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 flex items-center justify-between text-xs">
        <div className="flex items-center gap-2.5 text-slate-300">
          <ShieldCheck className="w-4 h-4 text-emerald-400 shrink-0" />
          <span>Strict Upload Invariant: Browser automation workers will abort file upload if document approval is revoked.</span>
        </div>
        <span className="text-[11px] font-semibold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
          Active Security Gate
        </span>
      </div>

      {/* Document List */}
      {loading ? (
        <div className="flex items-center justify-center h-48">
          <div className="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
        </div>
      ) : documents.length > 0 ? (
        <div className="bg-slate-950 border border-slate-800 rounded-xl overflow-hidden shadow-sm">
          <div className="divide-y divide-slate-850">
            {documents.map((doc) => {
              const isApproved = doc.approval_status === "APPROVED FOR APPLICATION USE";
              return (
                <div key={doc.id} className="p-4 flex flex-col md:flex-row justify-between items-start md:items-center gap-4 hover:bg-slate-900/50 transition-colors">
                  <div className="flex items-start gap-3">
                    <div className="w-10 h-10 rounded-lg bg-slate-900 border border-slate-800 flex items-center justify-center text-indigo-400 shrink-0 mt-0.5">
                      <FileText className="w-5 h-5" />
                    </div>
                    <div>
                      <h4 className="text-xs font-bold text-white">{doc.filename}</h4>
                      <p className="text-[11px] text-indigo-400 font-medium">{doc.category}</p>
                      {doc.description && <p className="text-[11px] text-slate-400 mt-0.5">{doc.description}</p>}
                      <span className="text-[10px] text-slate-500 mt-1 block">
                        {(doc.file_size_bytes / 1024).toFixed(0)} KB · Uploaded {new Date(doc.upload_date).toLocaleDateString()}
                      </span>
                    </div>
                  </div>

                  <div className="flex items-center gap-3 w-full md:w-auto justify-between md:justify-end">
                    <span className={`text-[11px] font-bold px-2.5 py-1 rounded-full border ${
                      isApproved
                        ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/30"
                        : "bg-slate-800 text-slate-400 border-slate-700"
                    }`}>
                      {doc.approval_status}
                    </span>

                    <button
                      onClick={() => handleToggleApproval(doc)}
                      className={`text-xs px-3 py-1.5 rounded-lg font-semibold transition-colors ${
                        isApproved
                          ? "bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 border border-rose-500/30"
                          : "bg-emerald-600 hover:bg-emerald-500 text-white shadow-sm"
                      }`}
                    >
                      {isApproved ? "Revoke Approval" : "Approve for Upload"}
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      ) : (
        <div className="bg-slate-950 border border-slate-800 rounded-xl p-12 text-center">
          <FolderLock className="w-8 h-8 text-slate-600 mx-auto mb-3" />
          <p className="text-sm font-semibold text-slate-300 mb-1">No documents in vault</p>
          <p className="text-xs text-slate-500 mb-4">Upload incorporation documents, project budgets, and pitch decks.</p>
          <button
            onClick={() => setUploadModalOpen(true)}
            className="px-4 py-2 rounded-lg bg-indigo-600 text-white text-xs font-semibold"
          >
            Upload First Document
          </button>
        </div>
      )}

      {/* Upload Modal */}
      {uploadModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-xl max-w-lg w-full p-6 shadow-2xl">
            <h3 className="text-base font-bold text-white mb-4">Upload to Document Vault</h3>
            <form onSubmit={handleUploadSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Document Category *</label>
                <select
                  value={selectedCategory}
                  onChange={(e) => setSelectedCategory(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white"
                >
                  {categories.map((c) => (
                    <option key={c} value={c}>{c}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Description / Notes</label>
                <input
                  type="text"
                  placeholder="e.g. Audited financials for 2024"
                  value={fileDescription}
                  onChange={(e) => setFileDescription(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Select File (PDF, DOCX, PNG) *</label>
                <input
                  type="file"
                  required
                  onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
                  className="w-full text-xs text-slate-400 file:mr-4 file:py-1.5 file:px-3 file:rounded-md file:border-0 file:text-xs file:font-semibold file:bg-indigo-600 file:text-white hover:file:bg-indigo-500"
                />
              </div>

              <div className="flex items-center justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setUploadModalOpen(false)}
                  className="px-3 py-1.5 rounded-lg text-xs font-medium text-slate-400 hover:bg-slate-800"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={uploading}
                  className="px-4 py-2 rounded-lg text-xs font-semibold bg-indigo-600 hover:bg-indigo-500 text-white"
                >
                  {uploading ? "Uploading..." : "Save to Vault"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
