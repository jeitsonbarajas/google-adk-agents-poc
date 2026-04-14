# 🚀 Guía de Despliegue - Google ADK Agents

Esta guía te ayudará a desplegar el sistema de soporte inteligente en **Google Cloud Run**.

## 📋 Prerequisitos

### Para ambas plataformas:
- **Git** instalado
- **Docker** instalado (para desarrollo local)
- **API Keys** configuradas:
  - `GOOGLE_API_KEY` (requerido) — obtener en [Google AI Studio](https://aistudio.google.com/app/apikey)

---

## ☁️ Despliegue en Google Cloud Run

### 1. Preparación

```bash
# Instalar Google Cloud SDK
# https://cloud.google.com/sdk/docs/install

# Autenticarse
gcloud auth login

# Configurar proyecto
gcloud config set project YOUR_PROJECT_ID

# Habilitar APIs
gcloud services enable cloudbuild.googleapis.com run.googleapis.com
```

### 2. Configuración de Secrets

```bash
# Crear secret para API key
echo "AI-tu-google-key" | gcloud secrets create google-api-key --data-file=-
```

### 3. Despliegue Automático

```bash
# Usando script automatizado
chmod +x deploy-gcp.sh
./deploy-gcp.sh

# O manualmente
gcloud builds submit --config cloudbuild.yaml .
```

### 4. Configuración de Cloud Run

```bash
# El script automático hace esto, pero puedes hacerlo manualmente:
gcloud run services update google-adk-agents \
  --region=us-central1 \
  --update-secrets="GOOGLE_API_KEY=google-api-key:latest" \
  --update-env-vars="ENVIRONMENT=gcp"
```

### 5. Verificación

```bash
# Obtener URL del servicio
gcloud run services describe google-adk-agents \
  --region=us-central1 --format="value(status.url)"
```

---

## 🐳 Desarrollo Local con Docker

### Opción 1: Docker Compose

```bash
# Crear archivo .env
cp .env.example .env
# Editar .env con tus API keys

# Ejecutar
docker-compose up --build

# URLs locales:
# - App: http://localhost:8000
# - Health: http://localhost:8000/health
# - API: http://localhost:8000/api/docs
```

### Opción 2: Docker directo

```bash
# Build
docker build -t google-adk-agents .

# Run
docker run -p 8080:8080 \
  -e GOOGLE_API_KEY=AI-xxxxx \
  -e ENVIRONMENT=docker \
  google-adk-agents
```

---

## 📊 Monitoreo y Troubleshooting

### Health Checks

Todas las plataformas incluyen health checks automáticos:

```bash
# Verificar salud del servicio
curl https://tu-app.com/health

# Respuesta esperada:
{
  "status": "healthy",
  "environment": "gcp|docker"
}
```

### Logs

#### Google Cloud Run:
```bash
gcloud logs tail --follow \
  --filter="resource.type=cloud_run_revision AND resource.labels.service_name=google-adk-agents"
```

#### Docker:
```bash
docker logs -f <container-id>
```

### Troubleshooting Común

#### Error: "Missing API Key"
```bash
# Verificar variables de entorno
gcloud secrets versions list google-api-key  # GCP
docker exec <container> env | grep API_KEY   # Docker
```

#### Error: "Port binding failed"
```bash
# GCP: Cloud Run maneja puertos automáticamente  
# Docker: Verificar que el puerto no esté ocupado
```

#### Error: "Module not found"
```bash
# Verificar que el PYTHONPATH esté configurado
# El Dockerfile ya incluye: ENV PYTHONPATH=/app
```

---

## 🔒 Configuración de Seguridad

### Variables de Entorno Seguras

**Google Cloud Run:**
- Usar Secret Manager para API keys
- IAM roles específicos por servicio

**Docker Local:**
- Usar archivo `.env` (no commitear)
- Considerar Docker secrets para production

### Service Account (GCP)

```bash
# Crear service account con permisos mínimos
gcloud iam service-accounts create google-adk-agents-sa \
  --display-name="Google ADK Agents"

# Asignar solo roles necesarios
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:google-adk-agents-sa@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/run.invoker"
```

---

## 📈 Configuración de Escalabilidad

### Google Cloud Run:
```bash
# Configurar escalado
gcloud run services update google-adk-agents \
  --region=us-central1 \
  --min-instances=1 \
  --max-instances=10 \
  --cpu=2 \
  --memory=2Gi
```

---

## 💰 Estimación de Costos

### Google Cloud Run:
- **Free Tier**: 2M requests/mes
- **Pay-per-use**: ~$0.40/million requests
- + costos de Container Registry
- + costos de API calls

### APIs:
- **Google Gemini**: Gratis hasta límite — ver [precios](https://ai.google.dev/pricing)
- **Vertex AI Gemini**: Pay-per-use — ver [precios](https://cloud.google.com/vertex-ai/pricing)

---

## 🔄 CI/CD Pipeline

### GitHub Actions (GCP)

```yaml
# .github/workflows/gcp-deploy.yml
name: Deploy to Cloud Run
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: google-github-actions/setup-gcloud@v0
      - run: gcloud builds submit --config cloudbuild.yaml .
```

---

## ✅ Checklist de Despliegue

- [ ] API Keys configuradas
- [ ] Variables de entorno establecidas
- [ ] Docker build exitoso localmente
- [ ] Health check respondiendo
- [ ] SSL/HTTPS habilitado
- [ ] Logs configurados
- [ ] Escalabilidad configurada
- [ ] Monitoreo establecido
- [ ] Backup de configuración

---

## 🆘 Soporte


**Problemas de GCP:**
- [Cloud Run Docs](https://cloud.google.com/run/docs)
- [GCP Support](https://cloud.google.com/support)

**Problemas del código:**
- GitHub Issues del repositorio
- Documentación del README principal