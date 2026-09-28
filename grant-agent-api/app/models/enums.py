import enum

class VerificationStatus(str, enum.Enum):
    VERIFIED = "VERIFIED"
    UNVERIFIED = "UNVERIFIED"
    DO_NOT_USE = "DO NOT USE"

class GrantStageClassification(str, enum.Enum):
    GREEN_IDEA = "GREEN — IDEA STAGE"
    YELLOW_VALIDATION = "YELLOW — VALIDATION STAGE"
    ORANGE_MVP = "ORANGE — MVP REQUIRED"
    RED_TRACTION = "RED — TRACTION REQUIRED"

class GrantApplicationStatus(str, enum.Enum):
    OPEN = "OPEN"
    UPCOMING = "UPCOMING"
    CLOSED = "CLOSED"
    ROLLING = "ROLLING"
    INVITATION_ONLY = "INVITATION ONLY"
    UNCONFIRMED = "UNCONFIRMED"

class GrantVerificationStatus(str, enum.Enum):
    OFFICIAL_VERIFIED = "OFFICIAL VERIFIED"
    PARTIALLY_VERIFIED = "PARTIALLY VERIFIED"
    UNCONFIRMED = "UNCONFIRMED"
    FLAGGED = "FLAGGED"

class EligibilityMatchStatus(str, enum.Enum):
    ELIGIBLE = "ELIGIBLE"
    LIKELY_ELIGIBLE = "LIKELY ELIGIBLE"
    ELIGIBILITY_UNCLEAR = "ELIGIBILITY UNCLEAR"
    NOT_ELIGIBLE = "NOT ELIGIBLE"

class ApplicationStatus(str, enum.Enum):
    DISCOVERED = "Discovered"
    SAVED = "Saved"
    ANALYSING = "Analysing"
    PREPARING = "Preparing"
    READY_TO_APPLY = "Ready to Apply"
    APPLICATION_STARTED = "Application Started"
    WAITING_FOR_USER = "Waiting for User"
    APPLICATION_COMPLETE = "Application Complete"
    READY_FOR_REVIEW = "Ready for Review"
    SUBMITTED = "Submitted"
    UNDER_REVIEW = "Under Review"
    SHORTLISTED = "Shortlisted"
    INTERVIEW = "Interview"
    AWARDED = "Awarded"
    REJECTED = "Rejected"
    WITHDRAWN = "Withdrawn"

class DocumentCategory(str, enum.Enum):
    CERTIFICATE_OF_INCORPORATION = "Certificate of incorporation"
    ORGANISATION_PROFILE = "Organisation profile"
    PITCH_DECK = "Pitch deck"
    FOUNDER_CV = "Founder CV"
    TEAM_CV = "Team CV"
    RECOMMENDATION_LETTERS = "Recommendation letters"
    FINANCIAL_STATEMENTS = "Financial statements"
    BANK_DETAILS = "Bank details"
    SAFEGUARDING_POLICY = "Safeguarding policy"
    GENDER_POLICY = "Gender policy"
    PROCUREMENT_POLICY = "Procurement policy"
    GOVERNANCE_POLICY = "Governance policy"
    ANTI_FRAUD_POLICY = "Anti-fraud policy"
    MONITORING_AND_EVALUATION = "Monitoring and Evaluation documents"
    IMPACT_REPORTS = "Impact reports"
    PREVIOUS_GRANT_APPLICATIONS = "Previous grant applications"
    PROJECT_BUDGETS = "Project budgets"
    THEORY_OF_CHANGE = "Theory of Change"
    LOGICAL_FRAMEWORK = "Logical Framework"
    REFERENCES = "References"
    PARTNERSHIP_LETTERS = "Partnership letters"
    PRODUCT_SCREENSHOTS = "Product screenshots"
    REGISTRATION_DOCUMENTS = "Registration documents"
    TAX_DOCUMENTS = "Tax documents"
    OTHER_SUPPORTING_EVIDENCE = "Other supporting evidence"

class DocumentApprovalStatus(str, enum.Enum):
    APPROVED_FOR_APPLICATION_USE = "APPROVED FOR APPLICATION USE"
    PENDING_REVIEW = "PENDING REVIEW"
    NOT_APPROVED = "NOT APPROVED"

class BrowserSessionStatus(str, enum.Enum):
    IDLE = "IDLE"
    INITIALIZING = "INITIALIZING"
    NAVIGATING = "NAVIGATING"
    DETECTING_FIELDS = "DETECTING_FIELDS"
    FILLING_ANSWERS = "FILLING_ANSWERS"
    UPLOADING_DOCS = "UPLOADING_DOCS"
    WAITING_FOR_USER = "WAITING_FOR_USER"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

class InterventionType(str, enum.Enum):
    NONE = "NONE"
    EMAIL_VERIFICATION = "EMAIL_VERIFICATION"
    OTP = "OTP"
    CAPTCHA = "CAPTCHA"
    IDENTITY_VERIFICATION = "IDENTITY_VERIFICATION"
    LEGAL_DECLARATIONS = "LEGAL_DECLARATIONS"
    TERMS_AGREEMENT = "TERMS_AGREEMENT"
    MANUAL_TAKEOVER = "MANUAL_TAKEOVER"

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    MEMBER = "member"
    VIEWER = "viewer"

class AITaskStatus(str, enum.Enum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    RETRYING = "RETRYING"
    COMPLETED = "COMPLETED"
    WAITING_FOR_USER = "WAITING_FOR_USER"
    RETRYABLE_FAILED = "RETRYABLE_FAILED"
    PERMANENTLY_FAILED = "PERMANENTLY_FAILED"
