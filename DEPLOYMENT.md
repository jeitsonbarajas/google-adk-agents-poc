# 🚀 Guía de Despliegue - Google ADK Agents

Esta guía te ayudará a desplegar el sistema de soporte inteligente en **Railway** y **Google Cloud Run**.

## 📋 Prerequisitos

### Para ambas plataformas:
- **Git** instalado
- **Docker** instalado (para desarrollo local)
- **API Keys** configuradas:
  - `OPENAI_API_KEY` (requerido)
  - `GOOGLE_API_KEY` (opcional, para Gemini)
  - `CLAUDE_API_KEY` (opcional, para Claude)

---

## 🚄 Opción A: Despliegue en Railway

### 1. Preparación

```bash
# Instalar Railway CLI
npm install -g @railway/cli

# Autenticarse
railway login

# Clonar repositorio
git clone <tu-repo>
cd google-adk-agents-poc
```

### 2. Configuración de Variables

1. Ir a [Railway Dashboard](https://railway.app/dashboard)
2. Crear nuevo proyecto
3. Conectar con GitHub repository
4. Configurar variables de entorno:

```
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
GOOGLE_API_KEY=AIxxxxxxxxxxxxxxxxxxxxxxxxxxxx
CLAUDE_API_KEY=sk-antxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 3. Despliegue Automático

```bash
# Usando script automatizado
chmod +x deploy-railway.sh
./deploy-railway.sh

# O manualmente
railway project
railway up
```

### 4. Verificación

- **URL Principal**: `https://tu-app.up.railway.app`
- **Health Check**: `https://tu-app.up.railway.app/health`
- **API Docs**: `https://tu-app.up.railway.app/api/docs`

### ⚙️ Configuración Avanzada Railway

```toml
# railway.toml (ya incluido)
[deploy]
healthcheckPath = "/health"
healthcheckTimeout = 300
restartPolicyType = "always"

[[services]]
name = "google-adk-agents"
```

---

## ☁️ Opción B: Despliegue en Google Cloud Run

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
# Crear secrets para API keys
echo "sk-tu-openai-key" | gcloud secrets create openai-api-key --data-file=-
echo "AI-tu-google-key" | gcloud secrets create google-api-key --data-file=-
echo "sk-ant-tu-claude-key" | gcloud secrets create claude-api-key --data-file=-
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
  --update-secrets="OPENAI_API_KEY=openai-api-key:latest" \
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
docker run -p 8000:8000 \
  -e OPENAI_API_KEY=sk-xxxxx \
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
  "environment": "railway|gcp|docker"
}
```

### Logs

#### Railway:
```bash
railway logs --follow
```

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
railway variables  # Railway
gcloud secrets versions list openai-api-key  # GCP
docker exec <container> env | grep API_KEY  # Docker
```

#### Error: "Port binding failed"
```bash
# Railway: El puerto se asigna automáticamente
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

**Railway:**
- Variables encriptadas automáticamente
- Acceso via Railway Dashboard

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

### Railway:
- Escalado automático disponible
- Configurar en Railway Dashboard

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

### Railway:
- **Hobby Plan**: $5/mes
- **Pro Plan**: $20/mes
- + costos de API calls (OpenAI, etc.)

### Google Cloud Run:
- **Free Tier**: 2M requests/mes
- **Pay-per-use**: ~$0.40/million requests
- + costos de Container Registry
- + costos de API calls

### APIs Externas:
- **OpenAI GPT-4**: ~$30/1M tokens
- **Google Gemini**: Gratis hasta límite
- **Anthropic Claude**: ~$15/1M tokens

---

## 🔄 CI/CD Pipeline

### GitHub Actions (Railway)

```yaml
# .github/workflows/railway-deploy.yml
name: Deploy to Railway
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: railway deploy
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
```

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

**Problemas de Railway:**
- [Railway Discord](https://discord.gg/railway)
- [Railway Docs](https://docs.railway.app/)

**Problemas de GCP:**
- [Cloud Run Docs](https://cloud.google.com/run/docs)
- [GCP Support](https://cloud.google.com/support)

**Problemas del código:**
- GitHub Issues del repositorio
- Documentación del README principal