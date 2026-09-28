# Grant Agent — Deployment & Operational Manual

Production-ready, modular cloud application for AI-powered grant discovery, research, strategy, drafting, and browser automation.

---

## Architecture Overview

```
                                 ┌─────────────────────────┐
                                 │   Next.js 14 Frontend   │
                                 │    (Cloud Run / Web)    │
                                 └────────────┬────────────┘
                                              │ REST / JSON
                                              ▼
┌──────────────────────┐         ┌─────────────────────────┐         ┌──────────────────────┐
│  Cloud SQL Postgres  │ ◄────── │       FastAPI API       │ ◄────── │    Secret Manager    │
│  (16 Relational DDL) │         │     (Agents & Core)     │         │   (Vault & Tokens)   │
└──────────────────────┘         └────────────┬────────────┘         └──────────────────────┘
                                              │ Cloud Tasks
                                              ▼
┌──────────────────────┐         ┌─────────────────────────┐         ┌──────────────────────┐
│  Cloud Storage (GCS) │ ◄────── │ Playwright Browser Agent│ ──────► │ External Grant Sites │
│ (Vault & Screenshots)│         │ (Isolated Headless Pod) │         │ (Human Gate Pauses)  │
└──────────────────────┘         └─────────────────────────┘         └──────────────────────┘
```

### Core Components
1. **`grant-agent-api/`**: FastAPI backend implementing all 22 relational models, authentication, and the 6 AI Agents (`Scout`, `Verifier`, `Matcher`, `Strategist`, `Writer`, `Validator`).
2. **`grant-agent-worker/`**: Asynchronous Playwright Chromium engine with DOM inspection, anti-injection sanitization, screenshot capture, document uploads, and human gate interruption.
3. **`grant-agent-web/`**: Next.js 14, Tailwind CSS, TypeScript web application with all 9 core interfaces (`/dashboard`, `/discover`, `/saved`, `/grants/[id]`, `/organisations`, `/documents`, `/applications`, `/automation`, `/notifications`, `/settings`).
4. **`mock_grant_portal/`**: Sandbox testing portal simulating multi-field grant applications, file uploads, OTP challenges, and CAPTCHA gates.
5. **`deploy/`**: Complete set of production container Dockerfiles, Docker Compose orchestrator, and Google Cloud Platform deployment shell scripts.

---

## Safety Invariants & Policy Enforcement

- **Strict Profile Truthfulness:** The application will never fabricate applicant metrics, traction, or revenue. Unverified items are strictly flagged `UNCONFIRMED` or `REQUIRED FROM APPLICANT`.
- **Approved Document Gate:** Only files marked `APPROVED FOR APPLICATION USE` can be attached or uploaded to external grant portals.
- **Human-in-the-Loop Interruption:** Automations automatically halt at CAPTCHA, 2FA/OTP, and electronic signature gates, requiring human intervention.
- **Untrusted DOM Sanitization:** Webpage content is filtered against prompt injection patterns prior to agent reasoning.
- **Mandatory Final Approval:** No application is submitted automatically without explicit human authorization on the review screen.

---

## Local Development & Testing

### 1. Prerequisites
- Python 3.11+
- Node.js 18+ and `npm`
- Google Chrome or Chromium (for Playwright)

### 2. Setup Virtual Environment
```bash
python -m venv .venv
# On Windows PowerShell:
.venv\Scripts\Activate.ps1
# On Linux / macOS:
source .venv/bin/activate

pip install -r grant-agent-api/requirements.txt
pip install -r grant-agent-worker/requirements.txt
playwright install chromium
```

### 3. Run Automated Tests
```bash
# Run API, Schema, Seed Data, and Agent Logic Tests:
pytest grant-agent-api/tests -v

# Run Playwright Browser Automation Worker & Mock Portal Tests:
pytest grant-agent-worker/worker_tests -v
```

### 4. Running the Stack Locally
```bash
# Terminal 1: Launch FastAPI Backend
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload --app-dir grant-agent-api

# Terminal 2: Launch Next.js Frontend
cd grant-agent-web
npm run dev

# Terminal 3: Launch Mock Grant Portal (Sandbox Testing)
python -m uvicorn mock_grant_portal.server:app --port 8088 --reload
```

---

## Local Containerized Deployment (Docker Compose)

To spin up PostgreSQL, the Backend API, Playwright Worker, Mock Portal, and Next.js Web Application in a single command:

```bash
docker compose -f deploy/docker-compose.yml up --build
```

Access points:
- Web Application: `http://localhost:3000`
- API Swagger Docs: `http://localhost:8000/docs`
- Mock Portal: `http://localhost:8088`

---

## Google Cloud Platform Production Deployment

Ensure you have authenticated with `gcloud auth login` and set your active project:
```bash
export GCP_PROJECT_ID="your-production-project-id"
export GCP_REGION="us-central1"
gcloud config set project $GCP_PROJECT_ID
```

Execute the provisioning scripts in sequential order:

### Step 1: Provision Secret Manager Keys
```bash
bash deploy/gcp-secret-manager.sh
```
*Creates `grant-agent-jwt-secret`, `grant-agent-gemini-key`, `grant-agent-vault-encryption-key`, and `grant-agent-db-url`.*

### Step 2: Provision Cloud SQL (PostgreSQL 16)
```bash
bash deploy/gcp-cloud-sql.sh
```
*Configures a regional PostgreSQL 16 instance with automated backups, SSD storage, and point-in-time recovery.*

### Step 3: Provision Google Cloud Storage Buckets
```bash
bash deploy/gcp-cloud-storage.sh
```
*Creates versioned, uniform-access buckets for applicant documents and screenshot artifacts with auto-expiring lifecycles.*

### Step 4: Provision Cloud Tasks Worker Queue
```bash
bash deploy/gcp-cloud-tasks.sh
```
*Sets up `grant-agent-browser-tasks` queue with controlled dispatch concurrency.*

### Step 5: Build & Deploy Container Images to Cloud Run
```bash
bash deploy/gcp-cloud-run.sh
```
*Builds container images using Cloud Build into Artifact Registry and deploys `grant-agent-api`, `grant-agent-worker`, and `grant-agent-web`.*
