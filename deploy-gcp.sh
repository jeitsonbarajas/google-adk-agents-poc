#!/bin/bash
# Script para desplegar en Google Cloud Run

set -e

PROJECT_ID="your-gcp-project-id"
SERVICE_NAME="google-adk-agents"
REGION="us-central1"

echo "🚀 Desplegando Google ADK Agents en Google Cloud Run..."

# Verificar que gcloud esté instalado
if ! command -v gcloud &> /dev/null; then
    echo "❌ Google Cloud SDK no está instalado"
    echo "💡 Instalar desde: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Verificar autenticación
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q "@"; then
    echo "🔐 Autenticándose en Google Cloud..."
    gcloud auth login
fi

# Configurar proyecto
echo "📋 Configurando proyecto GCP..."
echo "Project ID actual: $(gcloud config get-value project)"
read -p "¿Usar proyecto '$PROJECT_ID'? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    gcloud config set project $PROJECT_ID
else
    read -p "Ingresa tu Project ID: " PROJECT_ID
    gcloud config set project $PROJECT_ID
fi

# Habilitar APIs necesarias
echo "⚙️  Habilitando APIs de GCP..."
gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    containerregistry.googleapis.com

# Crear service account
echo "🔐 Creando service account..."
gcloud iam service-accounts create google-adk-agents-sa \
    --display-name="Google ADK Agents Service Account" \
    --description="Service account for Google ADK Agents" \
    || echo "Service account ya existe"

# Asignar roles
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:google-adk-agents-sa@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/run.invoker"

# Configurar secrets (API Keys)
echo "🔑 Configurando secrets..."
echo "Por favor configura los siguientes secrets en Secret Manager:"
echo "1. GOOGLE_API_KEY"

read -p "¿Deseas configurar el secret ahora? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    read -s -p "Ingresa tu GOOGLE_API_KEY: " GOOGLE_KEY
    echo
    echo "$GOOGLE_KEY" | gcloud secrets create google-api-key --data-file=-
fi

# Construir y deployar usando Cloud Build
echo "🏗️  Iniciando build y deploy..."
gcloud builds submit --config cloudbuild.yaml .

# Configurar variables de entorno en Cloud Run
echo "⚙️  Configurando Cloud Run..."
gcloud run services update $SERVICE_NAME \
    --region=$REGION \
    --update-env-vars="ENVIRONMENT=gcp,PYTHONPATH=/app" \
    --update-secrets="GOOGLE_API_KEY=google-api-key:latest" \
    || echo "Configuración aplicada parcialmente"

# Obtener URL del servicio
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)")

echo "✅ Despliegue completado!"
echo "🌐 URL: $SERVICE_URL"
echo "💚 Health check: $SERVICE_URL/health"
echo "📖 API Docs: $SERVICE_URL/api/docs"