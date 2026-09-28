export type VerificationStatus = "VERIFIED" | "UNVERIFIED" | "DO NOT USE";

export type GrantStageClassification =
  | "GREEN — IDEA STAGE"
  | "YELLOW — VALIDATION STAGE"
  | "ORANGE — MVP REQUIRED"
  | "RED — TRACTION REQUIRED";

export type GrantApplicationStatus =
  | "OPEN"
  | "UPCOMING"
  | "CLOSED"
  | "ROLLING"
  | "INVITATION ONLY"
  | "UNCONFIRMED";

export type GrantVerificationStatus =
  | "OFFICIAL VERIFIED"
  | "PARTIALLY VERIFIED"
  | "UNCONFIRMED"
  | "FLAGGED";

export type EligibilityMatchStatus =
  | "ELIGIBLE"
  | "LIKELY ELIGIBLE"
  | "ELIGIBILITY UNCLEAR"
  | "NOT ELIGIBLE";

export type ApplicationStatus =
  | "Discovered"
  | "Saved"
  | "Analysing"
  | "Preparing"
  | "Ready to Apply"
  | "Application Started"
  | "Waiting for User"
  | "Application Complete"
  | "Ready for Review"
  | "Submitted"
  | "Under Review"
  | "Shortlisted"
  | "Interview"
  | "Awarded"
  | "Rejected"
  | "Withdrawn";

export type DocumentApprovalStatus =
  | "APPROVED FOR APPLICATION USE"
  | "PENDING REVIEW"
  | "NOT APPROVED";

export interface Founder {
  id?: string;
  name: string;
  role: string;
  biography?: string;
  age?: number;
  education?: string;
  relevant_experience?: string;
  verification_status: VerificationStatus;
}

export interface TeamMember {
  id?: string;
  name: string;
  role: string;
  biography?: string;
  skills: string[];
  verification_status: VerificationStatus;
}

export interface Organisation {
  id: string;
  owner_id: string;
  organisation_name: string;
  project_name?: string;
  organisation_type: string;
  registration_status: string;
  registration_number?: string;
  registration_country?: string;
  date_founded?: string;
  website?: string;
  email?: string;
  phone?: string;
  address?: string;
  operating_countries: string[];
  basic_details_status: VerificationStatus;

  short_description?: string;
  long_description?: string;
  mission?: string;
  vision?: string;
  objectives?: string;
  description_status: VerificationStatus;

  problems_addressed?: string;
  target_audience?: string;
  geography?: string;
  underserved_groups?: string;
  problem_status: VerificationStatus;

  products?: string;
  services?: string;
  programmes?: string;
  technology_solution?: string;
  solution_status: VerificationStatus;

  stage: string;
  stage_status: VerificationStatus;

  users_count: number;
  beneficiaries_count: number;
  customers_count: number;
  revenue_amount: number;
  pilots_description?: string;
  partnerships_description?: string;
  testimonials?: string;
  impact_metrics?: Record<string, any>;
  traction_status: VerificationStatus;

  previous_grants?: string;
  investment?: string;
  founder_funding?: string;
  current_fundraising?: string;
  funding_status: VerificationStatus;

  gender_representation?: string;
  employment_created: number;
  programme_outcomes?: string;
  sdgs: string[];
  measurable_social_impact?: string;
  impact_status: VerificationStatus;

  tech_stack: string[];
  platform?: string;
  intellectual_property?: string;
  technical_capabilities?: string;
  technology_status: VerificationStatus;

  annual_budget: number;
  annual_revenue: number;
  project_budgets?: string;
  financial_history?: string;
  financial_status: VerificationStatus;

  pref_min_amount: number;
  pref_max_amount: number;
  pref_countries: string[];
  pref_sectors: string[];
  pref_stages: string[];
  pref_funding_types: string[];
  grant_preferences_status: VerificationStatus;

  founders: Founder[];
  team_members: TeamMember[];
}

export interface DocumentItem {
  id: string;
  organisation_id: string;
  filename: string;
  storage_path: string;
  file_size_bytes: number;
  mime_type: string;
  category: string;
  description?: string;
  upload_date: string;
  approval_status: DocumentApprovalStatus;
  extracted_metadata?: Record<string, any>;
  extracted_text?: string;
}

export interface GrantQuestion {
  id: string;
  question_text: string;
  character_limit?: number;
  word_limit?: number;
  is_required: boolean;
  guidance?: string;
}

export interface Grant {
  id: string;
  grant_name: string;
  funder: string;
  official_url: string;
  application_url?: string;
  source_url?: string;

  funding_amount_min: number;
  funding_amount_max: number;
  currency: string;

  deadline?: string;
  opening_date?: string;
  country: string;
  eligible_countries: string[];
  eligible_regions: string[];
  sector: string;
  grant_type: string;
  organisation_types: string[];

  project_stage: string;
  stage_classification: GrantStageClassification;

  incorporation_required: boolean;
  mvp_required: boolean;
  traction_required: boolean;
  revenue_required: boolean;
  previous_funding_required: boolean;
  age_requirement: string;
  team_requirement: string;

  application_language: string;
  application_status: GrantApplicationStatus;
  application_process?: string;
  required_documents: string[];
  required_questions: string[];
  selection_criteria?: string;
  response_timeline: string;
  reapplication_allowed: boolean;
  matching_funds_required: boolean;
  equity_required: boolean;

  verification_status: GrantVerificationStatus;
  verification_confidence: number;
  verified_extracted_text?: string;
  website_last_checked: string;
  created_at: string;
  questions?: GrantQuestion[];
}

export interface GrantMatch {
  id?: string;
  grant_id: string;
  organisation_id: string;
  eligibility_status: EligibilityMatchStatus;
  relevance_score: number;
  strong_match_factors: string[];
  weak_match_factors: string[];
  missing_requirements: string[];
  disqualifying_requirements: string[];
  information_needed: string[];
}

export interface ApplicationAnswer {
  id: string;
  question_id: string;
  answer_text: string;
  character_count: number;
  word_count: number;
  source_information_used: string[];
  verification_status: VerificationStatus;
  approved_status: boolean;
  last_edited: string;
}

export interface ApplicationQuestionItem {
  id: string;
  application_id: string;
  question_text: string;
  character_limit?: number;
  word_limit?: number;
  is_required: boolean;
  answer?: ApplicationAnswer;
}

export interface ApplicationItem {
  id: string;
  organisation_id: string;
  grant_id: string;
  status: ApplicationStatus;
  completion_percentage: number;
  project_title?: string;
  project_summary?: string;
  submission_date?: string;
  application_reference?: string;
  confirmation_number?: string;
  human_approved: boolean;
  auto_submit_after_approval: boolean;
  created_at: string;
  updated_at: string;
  questions: ApplicationQuestionItem[];
}

export interface ApplicationReviewSummary {
  application_id: string;
  grant_name: string;
  organisation_name: string;
  deadline?: string;
  completion_percentage: number;
  questions_total: number;
  questions_completed: number;
  questions_missing: number;
  documents_total_required: number;
  documents_uploaded: number;
  documents_missing: number;
  declarations_pending: string[];
  warnings: string[];
  potential_errors: string[];
  word_limit_violations: string[];
  character_limit_violations: string[];
  eligibility_warnings: string[];
  ready_for_final_approval: boolean;
}

export interface BrowserEvent {
  id: string;
  event_type: string;
  description: string;
  screenshot_path?: string;
  metadata_json: Record<string, any>;
  created_at: string;
}

export interface BrowserSession {
  id: string;
  application_id: string;
  status: string;
  current_url?: string;
  current_task: string;
  current_step: string;
  latest_screenshot_path?: string;
  intervention_required: boolean;
  intervention_type: string;
  intervention_message?: string;
  completed_fields_count: number;
  total_fields_detected: number;
  error_message?: string;
  started_at: string;
  completed_at?: string;
  events: BrowserEvent[];
}

export interface DashboardSummary {
  open_grants: number;
  idea_stage_grants: number;
  applications_in_progress: number;
  applications_requiring_attention: number;
  funding_potential_usd: number;
  recent_grants: Array<{
    id: string;
    grant_name: string;
    funder: string;
    amount_max: number;
    stage: string;
    deadline?: string;
    status: string;
  }>;
  recent_submissions: Array<{
    id: string;
    grant_name: string;
    organisation_name: string;
    reference?: string;
    submission_date?: string;
    status: string;
  }>;
  upcoming_deadlines: Array<{
    id: string;
    grant_name: string;
    funder: string;
    deadline?: string;
    amount_max: number;
  }>;
}
