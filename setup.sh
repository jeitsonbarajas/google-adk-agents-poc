#!/bin/bash
# Script de configuración inicial para Google ADK Agents

set -e

echo "🤖 Google ADK Agents - Configuración Inicial"
echo "=============================================="

# Verificar Git
if ! command -v git &> /dev/null; then
    echo "❌ Git no está instalado"
    exit 1
fi

# Verificar Python
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "❌ Python no está instalado"
    exit 1
fi

# Verificar pip
if ! command -v pip &> /dev/null && ! command -v pip3 &> /dev/null; then
    echo "❌ pip no está instalado"
    exit 1
fi

echo "✅ Dependencias básicas verificadas"

# Crear entorno virtual
echo "🐍 Creando entorno virtual..."
if [ -d "venv" ]; then
    echo "⚠️  venv ya existe, saltando..."
else
    python -m venv venv
    echo "✅ Entorno virtual creado"
fi

# Activar entorno virtual
echo "🔌 Activando entorno virtual..."
source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null || echo "⚠️  No se pudo activar automáticamente"

# Instalar dependencias
echo "📦 Instalando dependencias..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Dependencias instaladas"

# Configurar archivo .env
echo "⚙️  Configurando variables de entorno..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "📝 Archivo .env creado desde template"
    echo "🔑 IMPORTANTE: Edita .env con tus API keys antes de continuar"
    echo ""
    echo "   Necesitas configurar:"
    echo "   - OPENAI_API_KEY=sk-xxxxx"
    echo "   - GOOGLE_API_KEY=AIxxxxx (opcional)"
    echo "   - CLAUDE_API_KEY=sk-antxxxxx (opcional)"
else
    echo "⚠️  .env ya existe, saltando..."
fi

# Verificar estructura del proyecto
echo "📂 Verificando estructura del proyecto..."
if [ -d "agents-poc" ]; then
    echo "✅ Directorio agents-poc encontrado"
else
    echo "❌ Directorio agents-poc no encontrado"
    echo "💡 Asegúrate de estar en el directorio correcto"
    exit 1
fi

# Test básico
echo "🧪 Ejecutando test básico..."
cd agents-poc
python -c "
try:
    import google.adk
    import openai
    import fastapi
    print('✅ Importaciones básicas funcionan')
except ImportError as e:
    print(f'❌ Error de importación: {e}')
    exit(1)
"

echo ""
echo "🎉 ¡Configuración inicial completada!"
echo ""
echo "📋 Próximos pasos:"
echo "1. Editar .env con tus API keys"
echo "2. Desarrollo local:"
echo "   cd agents-poc && python main.py"
echo "3. Interfaz web:"
echo "   cd agents-poc && python start.py --adk-web"
echo "4. Despliegue:"
echo "   ./deploy-railway.sh  # para Railway"
echo "   ./deploy-gcp.sh      # para Google Cloud Run"
echo ""
echo "📖 Ver DEPLOYMENT.md para más detalles"