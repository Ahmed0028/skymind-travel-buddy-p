# Deployment Guide

## Option 1 — GCP Cloud Run (Streamlit UI)

Runs the Streamlit front-end (`app.py`) as a fully-managed, auto-scaling
container on [Cloud Run](https://cloud.google.com/run).

### Prerequisites

```bash
# Install / update gcloud CLI
gcloud components update

# Authenticate
gcloud auth login
REGION=us-central1   # set to your preferred region
gcloud auth configure-docker ${REGION}-docker.pkg.dev

# Enable required APIs (one-time per project)
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  secretmanager.googleapis.com
```

### Store secrets in Secret Manager

API keys are injected into the container via Secret Manager (never bake them
into the image).

```bash
# Gemini / Google AI API key
echo -n "YOUR_GOOGLE_API_KEY" | \
  gcloud secrets create google-api-key --data-file=-

# Aviationstack API key
echo -n "YOUR_AVIATIONSTACK_API_KEY" | \
  gcloud secrets create aviationstack-api-key --data-file=-

# Grant the Cloud Run service account access
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')
gcloud secrets add-iam-policy-binding google-api-key \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
gcloud secrets add-iam-policy-binding aviationstack-api-key \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

### Manual deploy (one-command)

```bash
export PROJECT_ID=your-gcp-project-id
export REGION=us-central1          # optional
bash deployment/deploy_cloudrun.sh
```

The script will:
1. Create an Artifact Registry repository (if missing)
2. Build the Docker image with Cloud Build
3. Push the image to Artifact Registry
4. Deploy / update the Cloud Run service

### CI/CD with Cloud Build

Trigger automatic builds on every push to `main`:

```bash
# From repo root
gcloud builds triggers create github \
  --project=$PROJECT_ID \
  --region=$REGION \
  --repo-name=skymind-travel-buddy-p \
  --repo-owner=Ahmed0028 \
  --branch-pattern='^main$' \
  --build-config=lufthansa-travel-buddy/cloudbuild.yaml
```

The `cloudbuild.yaml` file at `lufthansa-travel-buddy/cloudbuild.yaml` builds,
pushes, and deploys the service automatically.

---

## Option 2 — Vertex AI Agent Engine

Deploys the ADK agent directly to
[Vertex AI Agent Engine](https://cloud.google.com/vertex-ai/docs/reasoning-engine/overview)
(no Streamlit UI required).

### Setup

```bash
pip install google-cloud-aiplatform
```

### Deploy

```bash
python deployment/deploy.py --create
```

### Test

```bash
python deployment/test_deployment.py --resource_id="projects/.../reasoningEngines/..."
```

### Manage

```bash
# List agents
python deployment/deploy.py --list

# Delete agent
python deployment/deploy.py --delete --resource_id="..."
```
