#!/usr/bin/env bash
set -e

# ==============================================================================
# Google Cloud Storage (GCS) Provisioning Script for Grant Agent Platform
# Buckets:
# 1. Documents Vault Bucket (Encrypted, versioned applicant documents)
# 2. Browser Automation Screenshots Bucket (Temporary artifacts with lifecycle retention)
# ==============================================================================

PROJECT_ID=${GCP_PROJECT_ID:-"grant-agent-gcp"}
REGION=${GCP_REGION:-"us-central1"}
DOCUMENTS_BUCKET="${PROJECT_ID}-grant-documents-vault"
SCREENSHOTS_BUCKET="${PROJECT_ID}-grant-browser-artifacts"

echo "=== 1. Enabling Cloud Storage APIs ==="
gcloud services enable storage.googleapis.com --project=${PROJECT_ID}

echo "=== 2. Creating Documents Vault Bucket ==="
# Uniform bucket-level access and object versioning for security and auditing
gcloud storage buckets create gs://${DOCUMENTS_BUCKET} \
    --project=${PROJECT_ID} \
    --location=${REGION} \
    --uniform-bucket-level-access \
    --pap=enforced || echo "Bucket ${DOCUMENTS_BUCKET} already exists."

echo "Enabling Object Versioning on Documents Vault..."
gcloud storage buckets update gs://${DOCUMENTS_BUCKET} --versioning

echo "=== 3. Creating Browser Automation Artifacts Bucket ==="
gcloud storage buckets create gs://${SCREENSHOTS_BUCKET} \
    --project=${PROJECT_ID} \
    --location=${REGION} \
    --uniform-bucket-level-access || echo "Bucket ${SCREENSHOTS_BUCKET} already exists."

echo "Configuring 30-day Lifecycle Auto-Deletion for Browser Screenshots..."
cat <<EOF > /tmp/gcs-screenshots-lifecycle.json
{
  "rule": [
    {
      "action": {"type": "Delete"},
      "condition": {"age": 30}
    }
  ]
}
EOF

gcloud storage buckets update gs://${SCREENSHOTS_BUCKET} --lifecycle-file=/tmp/gcs-screenshots-lifecycle.json
rm -f /tmp/gcs-screenshots-lifecycle.json

echo "=== 4. Setting CORS Configuration for Document Uploads ==="
cat <<EOF > /tmp/gcs-cors.json
[
  {
    "origin": ["*"],
    "responseHeader": ["Content-Type", "x-goog-resumable"],
    "method": ["GET", "PUT", "POST", "HEAD"],
    "maxAgeSeconds": 3600
  }
]
EOF

gcloud storage buckets update gs://${DOCUMENTS_BUCKET} --cors-file=/tmp/gcs-cors.json
rm -f /tmp/gcs-cors.json

echo "=============================================================================="
echo "GCS Storage Buckets Created Successfully!"
echo "Vault Bucket:       gs://${DOCUMENTS_BUCKET}"
echo "Screenshots Bucket: gs://${SCREENSHOTS_BUCKET}"
echo "=============================================================================="
