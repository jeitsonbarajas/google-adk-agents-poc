#!/bin/bash
# Script para desplegar en Railway

echo "🚀 Desplegando Google ADK Agents en Railway..."

# Verificar que Railway CLI esté instalado
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI no está instalado"
    echo "💡 Instalar con: npm install -g @railway/cli"
    exit 1
fi

# Verificar autenticación
if ! railway whoami &> /dev/null; then
    echo "🔐 Autenticándose en Railway..."
    railway login
fi

# Crear proyecto si no existe
echo "📋 Configurando proyecto..."
railway project

# Configurar variables de entorno
echo "⚙️  Configurando variables de entorno..."
echo "🔑 Por favor configura las siguientes variables en Railway Dashboard:"
echo "   OPENAI_API_KEY=sk-xxxxxx"
echo "   GOOGLE_API_KEY=AIxxxxxx (opcional)"
echo "   CLAUDE_API_KEY=sk-antxxxxx (opcional)"

read -p "¿Has configurado las API keys en Railway Dashboard? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Configura las API keys primero"
    exit 1
fi

# Hacer deploy
echo "🚀 Iniciando despliegue..."
railway up

echo "✅ Despliegue completado!"
echo "🌐 URL: https://google-adk-agents-production.up.railway.app"
echo "💚 Health check: https://google-adk-agents-production.up.railway.app/health"