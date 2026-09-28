#!/usr/bin/env bash
set -e

# ==============================================================================
# Google Cloud Secret Manager Provisioning Script for Grant Agent Platform
# ==============================================================================

PROJECT_ID=${GCP_PROJECT_ID:-"grant-agent-gcp"}
PROJECT_NUMBER=$(gcloud projects describe ${PROJECT_ID} --format="value(projectNumber)")
CLOUDRUN_SA="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

echo "=== 1. Enabling Secret Manager API ==="
gcloud services enable secretmanager.googleapis.com --project=${PROJECT_ID}

create_secret_if_absent() {
    local SECRET_NAME=$1
    local SECRET_VALUE=$2

    if ! gcloud secrets describe ${SECRET_NAME} --project=${PROJECT_ID} > /dev/null 2>&1; then
        echo "Creating secret: ${SECRET_NAME}..."
        gcloud secrets create ${SECRET_NAME} \
            --replication-policy="automatic" \
            --project=${PROJECT_ID}
        
        echo -n "${SECRET_VALUE}" | gcloud secrets versions add ${SECRET_NAME} \
            --data-file=- \
            --project=${PROJECT_ID}
    else
        echo "Secret ${SECRET_NAME} already exists."
    fi
}

echo "=== 2. Creating Application Secrets ==="
# JWT Secret Key
create_secret_if_absent "grant-agent-jwt-secret" "$(openssl rand -base64 32)"

# Gemini API Key (Placeholder if not set in environment)
create_secret_if_absent "grant-agent-gemini-key" "${GEMINI_API_KEY:-"ENTER_YOUR_GEMINI_API_KEY_HERE"}"

# Vault Field-Level Encryption Key (AES-256)
create_secret_if_absent "grant-agent-vault-encryption-key" "$(openssl rand -base64 32)"

# Database URL (Default placeholder or parameterized)
create_secret_if_absent "grant-agent-db-url" "${DATABASE_URL:-"postgresql+psycopg2://grant_agent_user:password@/grant_agent?host=/cloudsql/${PROJECT_ID}:us-central1:grant-agent-postgres"}"

echo "=== 3. Granting Secret Access to Cloud Run Service Account ==="
for SECRET in "grant-agent-jwt-secret" "grant-agent-gemini-key" "grant-agent-vault-encryption-key" "grant-agent-db-url"; do
    gcloud secrets add-iam-policy-binding ${SECRET} \
        --member="serviceAccount:${CLOUDRUN_SA}" \
        --role="roles/secretmanager.secretAccessor" \
        --project=${PROJECT_ID}
done

echo "=============================================================================="
echo "Secret Manager Configuration Complete!"
echo "Cloud Run SA (${CLOUDRUN_SA}) granted secretAccessor on all platform secrets."
echo "=============================================================================="
