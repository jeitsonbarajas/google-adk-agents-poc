# 📦 Artefactos de Despliegue - Google ADK Agents

Lista completa de archivos creados para despliegue en Railway y Google Cloud Run.

## 🐳 Containerización

| Archivo | Descripción | Uso |
|---------|-------------|-----|
| `Dockerfile` | Imagen Docker optimizada para producción | Railway, GCP, desarrollo local |
| `docker-compose.yml` | Orquestación para desarrollo local | Desarrollo con Docker |
| `.dockerignore` | Archivos excluidos del build | Optimización de imagen |

## ⚡ Railway

| Archivo | Descripción | Configuración |
|---------|-------------|---------------|
| `railway.toml` | Configuración de Railway | Build, deploy, variables |
| `deploy-railway.sh` | Script automatizado de despliegue | CLI de Railway |

**Variables requeridas en Railway Dashboard:**
- `OPENAI_API_KEY`
- `GOOGLE_API_KEY` (opcional)
- `CLAUDE_API_KEY` (opcional)

## ☁️ Google Cloud Run

| Archivo | Descripción | Propósito |
|---------|-------------|-----------|
| `cloudbuild.yaml` | Configuración de Cloud Build | CI/CD automático |
| `deploy-gcp.sh` | Script automatizado de despliegue | gcloud CLI |

**Recursos GCP creados:**
- Container Registry images
- Cloud Run service
- Secret Manager secrets
- Service Account con permisos mínimos

## 🚀 Aplicación de Producción

| Archivo | Descripción | Funcionalidad |
|---------|-------------|---------------|
| `agents-poc/production_start.py` | Punto de entrada para producción | Servidor optimizado |
| `requirements.txt` | Dependencias actualizadas | Versiones específicas |

**Características de producción:**
- Health checks automáticos
- Gestión de variables de entorno
- Múltiples interfaces (API + Web)
- Logs estructurados

## ⚙️ Configuración

| Archivo | Descripción | Uso |
|---------|-------------|-----|
| `.env.example` | Template de variables de entorno | Configuración local |
| `setup.sh` | Script de configuración inicial (Unix) | Instalación automatizada |
| `setup.bat` | Script de configuración inicial (Windows) | Instalación automatizada |

## 📖 Documentación

| Archivo | Descripción | Contenido |
|---------|-------------|-----------|
| `DEPLOYMENT.md` | Guía completa de despliegue | Pasos detallados para ambas plataformas |
| `DEPLOYMENT_ARTIFACTS.md` | Este archivo | Lista de artefactos |

## 🔄 Workflows Sugeridos

### Para GitHub Actions (Railway):
```yaml
name: Deploy to Railway
on: [push]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: railway deploy
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
```

### Para GitHub Actions (GCP):
```yaml
name: Deploy to Cloud Run
on: [push]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: google-github-actions/setup-gcloud@v0
      - run: gcloud builds submit --config cloudbuild.yaml .
```

## 🧪 Testing Local

```bash
# Configuración inicial
./setup.sh  # Unix
setup.bat   # Windows

# Docker local
docker-compose up --build

# Verificar funcionamiento
curl http://localhost:8000/health
```

## 📊 URLs de Producción

### Railway:
- **App**: `https://tu-proyecto.up.railway.app`
- **Health**: `https://tu-proyecto.up.railway.app/health`
- **API**: `https://tu-proyecto.up.railway.app/api/docs`

### Google Cloud Run:
- **App**: `https://google-adk-agents-xyz-uc.a.run.app`
- **Health**: `https://google-adk-agents-xyz-uc.a.run.app/health`
- **API**: `https://google-adk-agents-xyz-uc.a.run.app/api/docs`

## 🔧 Comandos Útiles

```bash
# Railway
railway login
railway link
railway logs --follow
railway variables

# Google Cloud
gcloud auth login
gcloud config set project PROJECT_ID
gcloud run services list
gcloud logs tail --follow

# Docker
docker build -t google-adk-agents .
docker run -p 8000:8000 google-adk-agents
docker-compose up --build
```

## 💡 Próximos Pasos

- [ ] Configurar CI/CD con GitHub Actions
- [ ] Implementar métricas y monitoreo
- [ ] Configurar backup automático
- [ ] Optimizar para escalabilidad
- [ ] Implementar tests automatizados

---

**¡Todo listo para desplegar en producción! 🚀**