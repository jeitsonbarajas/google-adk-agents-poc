@echo off
REM Script de configuración inicial para Google ADK Agents (Windows)

echo 🤖 Google ADK Agents - Configuración Inicial
echo ==============================================

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python no está instalado
    exit /b 1
)

REM Verificar pip
pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pip no está instalado
    exit /b 1
)

echo ✅ Dependencias básicas verificadas

REM Crear entorno virtual
echo 🐍 Creando entorno virtual...
if exist venv (
    echo ⚠️  venv ya existe, saltando...
) else (
    python -m venv venv
    echo ✅ Entorno virtual creado
)

REM Activar entorno virtual
echo 🔌 Activando entorno virtual...
call venv\Scripts\activate.bat

REM Instalar dependencias
echo 📦 Instalando dependencias...
python -m pip install --upgrade pip
pip install -r requirements.txt
echo ✅ Dependencias instaladas

REM Configurar archivo .env
echo ⚙️  Configurando variables de entorno...
if not exist .env (
    copy .env.example .env
    echo 📝 Archivo .env creado desde template
    echo 🔑 IMPORTANTE: Edita .env con tus API keys antes de continuar
    echo.
    echo    Necesitas configurar:
    echo    - OPENAI_API_KEY=sk-xxxxx
    echo    - GOOGLE_API_KEY=AIxxxxx (opcional)
    echo    - CLAUDE_API_KEY=sk-antxxxxx (opcional)
) else (
    echo ⚠️  .env ya existe, saltando...
)

REM Verificar estructura del proyecto
echo 📂 Verificando estructura del proyecto...
if exist agents-poc (
    echo ✅ Directorio agents-poc encontrado
) else (
    echo ❌ Directorio agents-poc no encontrado
    echo 💡 Asegúrate de estar en el directorio correcto
    exit /b 1
)

REM Test básico
echo 🧪 Ejecutando test básico...
cd agents-poc
python -c "try: import google.adk, openai, fastapi; print('✅ Importaciones básicas funcionan')" 2>nul || echo ❌ Error en importaciones

echo.
echo 🎉 ¡Configuración inicial completada!
echo.
echo 📋 Próximos pasos:
echo 1. Editar .env con tus API keys
echo 2. Desarrollo local:
echo    cd agents-poc ^&^& python main.py
echo 3. Interfaz web:
echo    cd agents-poc ^&^& python start.py --adk-web
echo 4. Despliegue:
echo    deploy-railway.sh   # para Railway
echo    deploy-gcp.sh       # para Google Cloud Run
echo.
echo 📖 Ver DEPLOYMENT.md para más detalles

pause