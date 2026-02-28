#!/usr/bin/env bash
# deploy_cloudrun.sh
#
# Builds the container image locally and deploys the Lufthansa Travel Buddy
# Streamlit app to GCP Cloud Run.
#
# Prerequisites:
#   - gcloud CLI authenticated: gcloud auth login && gcloud auth configure-docker <REGION>-docker.pkg.dev
#   - Artifact Registry repository already created
#   - Required APIs enabled (run.googleapis.com, artifactregistry.googleapis.com, cloudbuild.googleapis.com)
#
# Usage:
#   export PROJECT_ID=your-gcp-project-id
#   export REGION=us-central1                          # optional, defaults below
#   export REPOSITORY=travel-buddy                     # optional, defaults below
#   export SERVICE_NAME=lufthansa-travel-buddy         # optional, defaults below
#   bash deployment/deploy_cloudrun.sh

set -euo pipefail

# ── Configuration ──────────────────────────────────────────────────────────────
PROJECT_ID="${PROJECT_ID:?Please set PROJECT_ID environment variable}"
REGION="${REGION:-us-central1}"
REPOSITORY="${REPOSITORY:-travel-buddy}"
SERVICE_NAME="${SERVICE_NAME:-lufthansa-travel-buddy}"
IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/${SERVICE_NAME}"

# Derive the script's directory so the script works from any CWD
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="$(dirname "${SCRIPT_DIR}")"   # lufthansa-travel-buddy/

echo "🚀 Deploying ${SERVICE_NAME} to Cloud Run"
echo "   Project : ${PROJECT_ID}"
echo "   Region  : ${REGION}"
echo "   Image   : ${IMAGE}"
echo ""

# ── Step 1: Create Artifact Registry repository (idempotent) ──────────────────
echo "📦 Ensuring Artifact Registry repository exists..."
gcloud artifacts repositories describe "${REPOSITORY}" \
    --project="${PROJECT_ID}" \
    --location="${REGION}" &>/dev/null \
  || gcloud artifacts repositories create "${REPOSITORY}" \
        --project="${PROJECT_ID}" \
        --repository-format=docker \
        --location="${REGION}" \
        --description="Container images for Travel Buddy"

# ── Step 2: Build & push the Docker image ─────────────────────────────────────
echo "🐳 Building Docker image..."
gcloud builds submit "${APP_DIR}" \
    --project="${PROJECT_ID}" \
    --tag="${IMAGE}:latest"

# ── Step 3: Deploy to Cloud Run ───────────────────────────────────────────────
echo "☁️  Deploying to Cloud Run..."
gcloud run deploy "${SERVICE_NAME}" \
    --project="${PROJECT_ID}" \
    --image="${IMAGE}:latest" \
    --region="${REGION}" \
    --platform=managed \
    --allow-unauthenticated \
    --port=8080 \
    --memory=1Gi \
    --cpu=1 \
    --min-instances=0 \
    --max-instances=10 \
    --set-env-vars="GOOGLE_CLOUD_PROJECT=${PROJECT_ID},GOOGLE_CLOUD_LOCATION=${REGION},GOOGLE_GENAI_USE_VERTEXAI=1" \
    --update-secrets="GOOGLE_API_KEY=google-api-key:latest,AVIATIONSTACK_API_KEY=aviationstack-api-key:latest"

echo ""
echo "✅ Deployment complete!"
echo "   Service URL: $(gcloud run services describe "${SERVICE_NAME}" \
    --project="${PROJECT_ID}" \
    --region="${REGION}" \
    --format='value(status.url)')"
