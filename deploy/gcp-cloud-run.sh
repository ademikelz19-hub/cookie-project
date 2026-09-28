#!/usr/bin/env bash
set -e

# ==============================================================================
# Google Cloud Run Deployment Script for Grant Agent Platform
# Services: grant-agent-api, grant-agent-web, grant-agent-worker
# ==============================================================================

PROJECT_ID="grant-agent-gcp"
REGION="us-central1"
AR_REPO="grant-agent-repo"

echo "=== 1. Setting Active GCP Project ==="
gcloud config set project ${PROJECT_ID}

echo "=== 2. Creating Artifact Registry Repository ==="
gcloud artifacts repositories create ${AR_REPO} \
    --repository-format=docker \
    --location=${REGION} \
    --description="Docker repository for Grant Agent containers" || true

echo "=== 3. Building and Submitting Container Images ==="
# Build API
gcloud builds submit --tag ${REGION}-docker.pkg.dev/${PROJECT_ID}/${AR_REPO}/grant-agent-api:latest \
    -f deploy/Dockerfile.api .

# Build Browser Automation Worker
gcloud builds submit --tag ${REGION}-docker.pkg.dev/${PROJECT_ID}/${AR_REPO}/grant-agent-worker:latest \
    -f deploy/Dockerfile.worker .

# Build Next.js Web Frontend
gcloud builds submit --tag ${REGION}-docker.pkg.dev/${PROJECT_ID}/${AR_REPO}/grant-agent-web:latest \
    -f deploy/Dockerfile.web .

echo "=== 4. Deploying Main Backend API to Cloud Run ==="
gcloud run deploy grant-agent-api \
    --image=${REGION}-docker.pkg.dev/${PROJECT_ID}/${AR_REPO}/grant-agent-api:latest \
    --region=${REGION} \
    --platform=managed \
    --allow-unauthenticated \
    --cpu=2 \
    --memory=2Gi \
    --min-instances=1 \
    --max-instances=10 \
    --set-env-vars="ENVIRONMENT=production,DEBUG=False" \
    --set-secrets="DATABASE_URL=grant-agent-db-url:latest,SECRET_KEY=grant-agent-jwt-secret:latest,GEMINI_API_KEY=grant-agent-gemini-key:latest"

API_URL=$(gcloud run services describe grant-agent-api --region=${REGION} --format="value(status.url)")

echo "=== 5. Deploying Isolated Browser Worker to Cloud Run ==="
# Note: Increased memory and execution timeout (15 mins) for headless Chromium browser workers
gcloud run deploy grant-agent-worker \
    --image=${REGION}-docker.pkg.dev/${PROJECT_ID}/${AR_REPO}/grant-agent-worker:latest \
    --region=${REGION} \
    --platform=managed \
    --no-allow-unauthenticated \
    --cpu=4 \
    --memory=4Gi \
    --timeout=900 \
    --min-instances=0 \
    --max-instances=5 \
    --set-secrets="DATABASE_URL=grant-agent-db-url:latest,SECRET_KEY=grant-agent-jwt-secret:latest"

echo "=== 6. Deploying Next.js Web Application to Cloud Run ==="
gcloud run deploy grant-agent-web \
    --image=${REGION}-docker.pkg.dev/${PROJECT_ID}/${AR_REPO}/grant-agent-web:latest \
    --region=${REGION} \
    --platform=managed \
    --allow-unauthenticated \
    --cpu=1 \
    --memory=1Gi \
    --min-instances=1 \
    --max-instances=10 \
    --set-env-vars="NEXT_PUBLIC_API_URL=${API_URL}/api/v1"

WEB_URL=$(gcloud run services describe grant-agent-web --region=${REGION} --format="value(status.url)")

echo "=== 7. Configuring Cloud Scheduler for Automated Grant Discovery ==="
gcloud scheduler jobs create http grant-agent-daily-scout \
    --schedule="0 2 * * *" \
    --uri="${API_URL}/api/v1/automation/scout-run" \
    --http-method=POST \
    --time-zone="Etc/UTC" \
    --location=${REGION} \
    --project=${PROJECT_ID} || echo "Cloud Scheduler job already exists or scheduled."

echo "=== 8. Verifying Cloud Logging Sink ==="
gcloud logging sinks describe grant-agent-logs-sink --project=${PROJECT_ID} 2>/dev/null || \
    echo "Cloud Logging standard telemetry enabled on Cloud Run services."

echo "=============================================================================="
echo "Deployment Complete!"
echo "API Service URL:       ${API_URL}"
echo "Web Platform URL:      ${WEB_URL}"
echo "=============================================================================="

