#!/usr/bin/env bash
# =============================================================================
# setup-gcp.sh
# One-time GCP setup: enables APIs, creates Artifact Registry repo,
# Service Account, and Workload Identity Federation for GitHub Actions.
#
# Usage:
#   chmod +x setup-gcp.sh
#   ./setup-gcp.sh
#
# Requirements:
#   - gcloud CLI installed and authenticated (gcloud auth login)
#   - Owner or Editor role on the GCP project
# =============================================================================

set -euo pipefail

# ---------------------------------------------------------------------------
# CONFIGURATION — edit these if needed
# ---------------------------------------------------------------------------
PROJECT_ID="careful-aleph-493015-f6"
REGION="us-east1"
REGISTRY_NAME="google-adk-agents"
SERVICE_NAME="google-adk-agents-poc"
SA_NAME="github-actions-sa"
WIF_POOL="github-pool"
WIF_PROVIDER="github-provider"
GITHUB_REPO="jeitsonbarajas/google-adk-agents-poc"
# ---------------------------------------------------------------------------

SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

echo ""
echo "======================================================================"
echo "  GCP Setup for: ${PROJECT_ID}"
echo "  GitHub Repo  : ${GITHUB_REPO}"
echo "======================================================================"
echo ""

# --- Set active project ---
echo ">> Setting active project..."
gcloud config set project "${PROJECT_ID}"

# --- Get project number (needed for WIF) ---
PROJECT_NUMBER=$(gcloud projects describe "${PROJECT_ID}" --format="value(projectNumber)")
echo "   Project Number: ${PROJECT_NUMBER}"

# ---------------------------------------------------------------------------
# 1. Enable required APIs
# ---------------------------------------------------------------------------
echo ""
echo ">> [1/6] Enabling required APIs..."
gcloud services enable \
  artifactregistry.googleapis.com \
  run.googleapis.com \
  iam.googleapis.com \
  iamcredentials.googleapis.com \
  cloudbuild.googleapis.com

echo "   APIs enabled."

# ---------------------------------------------------------------------------
# 2. Create Artifact Registry repository
# ---------------------------------------------------------------------------
echo ""
echo ">> [2/6] Creating Artifact Registry repository: ${REGISTRY_NAME} in ${REGION}..."
if gcloud artifacts repositories describe "${REGISTRY_NAME}" \
     --location="${REGION}" --project="${PROJECT_ID}" &>/dev/null; then
  echo "   Repository already exists, skipping."
else
  gcloud artifacts repositories create "${REGISTRY_NAME}" \
    --repository-format=docker \
    --location="${REGION}" \
    --description="Docker images for ${SERVICE_NAME}"
  echo "   Repository created."
fi

# ---------------------------------------------------------------------------
# 3. Create Service Account
# ---------------------------------------------------------------------------
echo ""
echo ">> [3/6] Creating Service Account: ${SA_NAME}..."
if gcloud iam service-accounts describe "${SA_EMAIL}" --project="${PROJECT_ID}" &>/dev/null; then
  echo "   Service account already exists, skipping."
else
  gcloud iam service-accounts create "${SA_NAME}" \
    --display-name="GitHub Actions SA for ${SERVICE_NAME}" \
    --project="${PROJECT_ID}"
  echo "   Service account created: ${SA_EMAIL}"
fi

# ---------------------------------------------------------------------------
# 4. Assign IAM roles to the Service Account
# ---------------------------------------------------------------------------
echo ""
echo ">> [4/6] Assigning IAM roles to ${SA_EMAIL}..."

for ROLE in \
  "roles/artifactregistry.writer" \
  "roles/run.admin" \
  "roles/iam.serviceAccountUser"; do
  gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="${ROLE}" \
    --condition=None \
    --quiet
  echo "   Assigned: ${ROLE}"
done

# ---------------------------------------------------------------------------
# 5. Create Workload Identity Pool
# ---------------------------------------------------------------------------
echo ""
echo ">> [5/6] Creating Workload Identity Pool: ${WIF_POOL}..."
if gcloud iam workload-identity-pools describe "${WIF_POOL}" \
     --location=global --project="${PROJECT_ID}" &>/dev/null; then
  echo "   WIF Pool already exists, skipping."
else
  gcloud iam workload-identity-pools create "${WIF_POOL}" \
    --location=global \
    --display-name="GitHub Actions Pool" \
    --project="${PROJECT_ID}"
  echo "   WIF Pool created."
fi

# Create OIDC Provider inside the pool
echo "   Creating OIDC Provider: ${WIF_PROVIDER}..."
if gcloud iam workload-identity-pools providers describe "${WIF_PROVIDER}" \
     --workload-identity-pool="${WIF_POOL}" \
     --location=global \
     --project="${PROJECT_ID}" &>/dev/null; then
  echo "   OIDC Provider already exists, skipping."
else
  gcloud iam workload-identity-pools providers create-oidc "${WIF_PROVIDER}" \
    --workload-identity-pool="${WIF_POOL}" \
    --location=global \
    --issuer-uri="https://token.actions.githubusercontent.com" \
    --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository,attribute.actor=assertion.actor" \
    --attribute-condition="attribute.repository=='${GITHUB_REPO}'" \
    --project="${PROJECT_ID}"
  echo "   OIDC Provider created."
fi

# ---------------------------------------------------------------------------
# 6. Bind Service Account to Workload Identity Pool
# ---------------------------------------------------------------------------
echo ""
echo ">> [6/6] Binding Service Account to Workload Identity Pool..."
WIF_MEMBER="principalSet://iam.googleapis.com/projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/${WIF_POOL}/attribute.repository/${GITHUB_REPO}"

gcloud iam service-accounts add-iam-policy-binding "${SA_EMAIL}" \
  --project="${PROJECT_ID}" \
  --role="roles/iam.workloadIdentityUser" \
  --member="${WIF_MEMBER}" \
  --condition=None \
  --quiet

echo "   Binding complete."

# ---------------------------------------------------------------------------
# OUTPUT: GitHub Secrets values
# ---------------------------------------------------------------------------
WIF_PROVIDER_FULL="projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/${WIF_POOL}/providers/${WIF_PROVIDER}"

echo ""
echo "======================================================================"
echo "  SETUP COMPLETE"
echo "======================================================================"
echo ""
echo "  Add these secrets to GitHub:"
echo "  Settings > Secrets and variables > Actions > New repository secret"
echo ""
echo "  GCP_WORKLOAD_IDENTITY_PROVIDER:"
echo "  ${WIF_PROVIDER_FULL}"
echo ""
echo "  GCP_SERVICE_ACCOUNT:"
echo "  ${SA_EMAIL}"
echo ""
echo "  Also add your API keys:"
echo "    OPENAI_API_KEY"
echo "    GOOGLE_API_KEY"
echo "    CLAUDE_API_KEY"
echo ""
echo "  Image will be published to:"
echo "  ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REGISTRY_NAME}/${SERVICE_NAME}"
echo ""
echo "  Once secrets are set, push to main to trigger the first deployment."
echo "======================================================================"
