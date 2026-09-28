#!/usr/bin/env bash
set -e

# ==============================================================================
# Google Cloud SQL (PostgreSQL 16) Provisioning Script for Grant Agent Platform
# ==============================================================================

PROJECT_ID=${GCP_PROJECT_ID:-"grant-agent-gcp"}
REGION=${GCP_REGION:-"us-central1"}
INSTANCE_NAME="grant-agent-postgres"
DATABASE_NAME="grant_agent"
DB_USER="grant_agent_user"
# In production, DB_PASSWORD should be provided via environment or generated securely
DB_PASSWORD=${DB_PASSWORD:-$(openssl rand -base64 24 | tr -dc 'a-zA-Z0-9' | head -c 20)}

echo "=== 1. Enabling Cloud SQL Admin API ==="
gcloud services enable sqladmin.googleapis.com --project=${PROJECT_ID}

echo "=== 2. Creating Cloud SQL PostgreSQL Instance ==="
# Enterprise tier PostgreSQL 16 with automatic backups and point-in-time recovery
gcloud sql instances create ${INSTANCE_NAME} \
    --database-version=POSTGRES_16 \
    --tier=db-custom-2-7680 \
    --region=${REGION} \
    --storage-size=50GB \
    --storage-type=SSD \
    --storage-auto-increase \
    --backup-start-time=03:00 \
    --enable-point-in-time-recovery \
    --database-flags=autovacuum=on,max_connections=200 \
    --availability-type=REGIONAL \
    --project=${PROJECT_ID} || echo "Instance ${INSTANCE_NAME} already exists or creation in progress."

echo "=== 3. Creating Production Database ==="
gcloud sql databases create ${DATABASE_NAME} \
    --instance=${INSTANCE_NAME} \
    --project=${PROJECT_ID} || echo "Database ${DATABASE_NAME} already exists."

echo "=== 4. Creating Database User ==="
gcloud sql users create ${DB_USER} \
    --instance=${INSTANCE_NAME} \
    --password="${DB_PASSWORD}" \
    --project=${PROJECT_ID} || echo "User ${DB_USER} already exists."

CONNECTION_NAME=$(gcloud sql instances describe ${INSTANCE_NAME} --project=${PROJECT_ID} --format="value(connectionName)")

echo "=============================================================================="
echo "Cloud SQL Instance Provisioned Successfully!"
echo "Connection Name: ${CONNECTION_NAME}"
echo "Database Name:   ${DATABASE_NAME}"
echo "Database User:   ${DB_USER}"
echo ""
echo "Constructed SQLAlchemy / Cloud SQL Connection URL format:"
echo "postgresql+psycopg2://${DB_USER}:${DB_PASSWORD}@/${DATABASE_NAME}?host=/cloudsql/${CONNECTION_NAME}"
echo "=============================================================================="
