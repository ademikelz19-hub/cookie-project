#!/usr/bin/env bash
set -e

# ==============================================================================
# Google Cloud Tasks Configuration Script for Grant Agent Platform
# Handles asynchronous queuing of browser automation jobs and grant research scans
# ==============================================================================

PROJECT_ID=${GCP_PROJECT_ID:-"grant-agent-gcp"}
REGION=${GCP_REGION:-"us-central1"}
QUEUE_NAME="grant-agent-browser-tasks"

echo "=== 1. Enabling Cloud Tasks API ==="
gcloud services enable cloudtasks.googleapis.com --project=${PROJECT_ID}

echo "=== 2. Creating Cloud Tasks Queue for Browser Automation Jobs ==="
# Browser automation jobs require controlled concurrency to prevent anti-bot IP blocks
# and sufficient execution window (up to 15 minutes)
gcloud tasks queues create ${QUEUE_NAME} \
    --location=${REGION} \
    --max-concurrent-dispatches=5 \
    --max-dispatches-per-second=2 \
    --max-attempts=3 \
    --min-backoff=10s \
    --max-backoff=300s \
    --project=${PROJECT_ID} || echo "Queue ${QUEUE_NAME} already exists."

echo "=============================================================================="
echo "Cloud Tasks Queue Ready: projects/${PROJECT_ID}/locations/${REGION}/queues/${QUEUE_NAME}"
echo "=============================================================================="
