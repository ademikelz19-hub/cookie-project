import {
  Organisation, DocumentItem, Grant, GrantMatch, ApplicationItem,
  ApplicationReviewSummary, BrowserSession, DashboardSummary,
  VerificationStatus, DocumentApprovalStatus
} from "../types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

async function request<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE}${endpoint}`;
  try {
    const res = await fetch(url, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options?.headers,
      },
      cache: "no-store"
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Request failed" }));
      throw new Error(err.detail || `HTTP Error ${res.status}`);
    }
    return await res.json();
  } catch (error: any) {
    console.error(`API Error on ${endpoint}:`, error.message);
    throw error;
  }
}

export const api = {
  // Dashboard
  getDashboard: () => request<DashboardSummary>("/dashboard"),

  // Organisations
  getOrganisations: () => request<Organisation[]>("/organisations"),
  getOrganisation: (id: string) => request<Organisation>(`/organisations/${id}`),
  createOrganisation: (data: Partial<Organisation>) =>
    request<Organisation>("/organisations", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  updateOrganisationVerification: (id: string, section_name: string, status: VerificationStatus) =>
    request<Organisation>(`/organisations/${id}/verification`, {
      method: "POST",
      body: JSON.stringify({ section_name, status }),
    }),

  // Documents
  getDocuments: (orgId?: string) =>
    request<DocumentItem[]>(`/documents${orgId ? `?organisation_id=${orgId}` : ""}`),
  updateDocumentApproval: (id: string, approval_status: DocumentApprovalStatus) =>
    request<DocumentItem>(`/documents/${id}/approval`, {
      method: "PATCH",
      body: JSON.stringify({ approval_status }),
    }),
  uploadDocument: async (orgId: string, category: string, file: File, description?: string) => {
    const formData = new FormData();
    formData.append("organisation_id", orgId);
    formData.append("category", category);
    formData.append("file", file);
    if (description) formData.append("description", description);
    formData.append("approved_for_application_use", "true");

    const res = await fetch(`${API_BASE}/documents/upload`, {
      method: "POST",
      body: formData,
    });
    if (!res.ok) throw new Error("Upload failed");
    return res.json();
  },

  // Grants
  getGrants: (params?: {
    sector?: string;
    no_mvp_only?: boolean;
    idea_stage_only?: boolean;
    min_amount?: number;
    search_query?: string;
  }) => {
    const q = new URLSearchParams();
    if (params?.sector) q.append("sector", params.sector);
    if (params?.no_mvp_only) q.append("no_mvp_only", "true");
    if (params?.idea_stage_only) q.append("idea_stage_only", "true");
    if (params?.min_amount) q.append("min_amount", params.min_amount.toString());
    if (params?.search_query) q.append("search_query", params.search_query);
    return request<Grant[]>(`/grants?${q.toString()}`);
  },
  getGrant: (id: string) => request<Grant>(`/grants/${id}`),
  pasteGrantUrl: (url: string, organisationId?: string, exactUrlMode = false) =>
    request<Grant>("/grants/paste-url", {
      method: "POST",
      body: JSON.stringify({ url, organisation_id: organisationId, exact_url_mode: exactUrlMode }),
    }),
  verifyGrant: (id: string) =>
    request<Grant>(`/grants/${id}/verify`, { method: "POST" }),

  // Matching
  analyseMatch: (organisationId: string, grantId: string) =>
    request<GrantMatch>("/matching/analyse", {
      method: "POST",
      body: JSON.stringify({ organisation_id: organisationId, grant_id: grantId }),
    }),
  getMatches: (orgId: string) => request<GrantMatch[]>(`/matching/${orgId}`),

  // Applications
  getApplications: (statusFilter?: string) =>
    request<ApplicationItem[]>(`/applications${statusFilter ? `?status_filter=${statusFilter}` : ""}`),
  getApplication: (id: string) => request<ApplicationItem>(`/applications/${id}`),
  prepareApplication: (organisationId: string, grantId: string) =>
    request<ApplicationItem>("/applications/prepare", {
      method: "POST",
      body: JSON.stringify({ organisation_id: organisationId, grant_id: grantId }),
    }),
  updateAnswer: (appId: string, questionId: string, answerText: string, approved?: boolean) =>
    request<any>(`/applications/${appId}/answers/${questionId}`, {
      method: "PUT",
      body: JSON.stringify({ answer_text: answerText, approved_status: approved }),
    }),
  getApplicationReview: (appId: string) =>
    request<ApplicationReviewSummary>(`/applications/${appId}/review`),
  approveApplication: (appId: string, approved: boolean, allowAutoSubmit = true) =>
    request<ApplicationItem>(`/applications/${appId}/approve`, {
      method: "POST",
      body: JSON.stringify({ approved, allow_auto_submit: allowAutoSubmit }),
    }),
  submitApplication: (appId: string) =>
    request<ApplicationItem>(`/applications/${appId}/submit`, { method: "POST" }),

  // Browser Automation
  startBrowserSession: (appId: string, targetUrl?: string) =>
    request<BrowserSession>("/browser/start", {
      method: "POST",
      body: JSON.stringify({ application_id: appId, target_url: targetUrl }),
    }),
  getBrowserSession: (sessionId: string) =>
    request<BrowserSession>(`/browser/${sessionId}`),
  sendBrowserCommand: (sessionId: string, action: string, data?: any) =>
    request<BrowserSession>(`/browser/${sessionId}/command`, {
      method: "POST",
      body: JSON.stringify({ action, intervention_data: data }),
    }),

  // Audit
  getAuditLogs: () => request<any[]>("/audit"),

  // Notifications
  getNotifications: () => request<any[]>("/notifications"),
  markNotificationRead: (id: string) =>
    request<any>(`/notifications/${id}/read`, { method: "PATCH" }),

  // Automation rules
  getAutomationProfiles: () => request<any[]>("/automation/profiles"),
};
