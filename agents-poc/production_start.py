#!/usr/bin/env python3
"""
Punto de entrada para producción en Railway y Google Cloud Run
"""
import os
import sys
import asyncio
import uvicorn
from contextlib import asynccontextmanager

# Configuración para producción
PORT = int(os.getenv("PORT", 8000))
HOST = "0.0.0.0"
ENVIRONMENT = os.getenv("RAILWAY_ENVIRONMENT") or os.getenv("GOOGLE_CLOUD_PROJECT") or "development"

def setup_production_environment():
    """Configurar el entorno de producción"""
    # Verificar que las variables críticas estén configuradas
    required_vars = ["OPENAI_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"ERROR: Variables de entorno requeridas no configuradas: {missing_vars}")
        sys.exit(1)
    
    # Configurar variables por defecto para producción
    os.environ.setdefault("ADAPTER_SERVER_URL", f"http://localhost:{PORT}")
    
    print(f"🚀 Iniciando en modo producción:")
    print(f"   - Entorno: {ENVIRONMENT}")
    print(f"   - Puerto: {PORT}")
    print(f"   - Host: {HOST}")

def create_production_app():
    """Crear aplicación para producción con múltiples servicios"""
    from fastapi import FastAPI, Request
    from fastapi.responses import HTMLResponse, JSONResponse
    from fastapi.staticfiles import StaticFiles
    import httpx
    
    app = FastAPI(
        title="Google ADK Agents - Sistema de Soporte",
        description="Sistema de soporte inteligente con múltiples agentes",
        version="1.0.0"
    )
    
    # Health check para Railway/Cloud Run
    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "environment": ENVIRONMENT}
    
    # Endpoint principal - redirige a ADK Web
    @app.get("/", response_class=HTMLResponse)
    async def root():
        return """
        <html>
            <head>
                <title>Google ADK Agents</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; }
                    .container { max-width: 600px; margin: 0 auto; text-align: center; }
                    .btn { background: #4285f4; color: white; padding: 12px 24px; 
                           text-decoration: none; border-radius: 4px; margin: 8px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🤖 Sistema de Soporte Inteligente</h1>
                    <p>Google ADK Agents en producción</p>
                    <a href="/adk" class="btn">🌐 Interfaz ADK Web</a>
                    <a href="/api/docs" class="btn">📖 API Docs</a>
                    <a href="/health" class="btn">💚 Health Check</a>
                </div>
            </body>
        </html>
        """
    
    # API endpoints del proxy
    from server import app as server_app
    app.mount("/api", server_app)
    
    return app

async def start_adk_web_service():
    """Iniciar Google ADK Web en puerto separado"""
    try:
        import subprocess
        import time
        
        # Dar tiempo a que el servidor principal se inicie
        await asyncio.sleep(3)
        
        adk_port = PORT + 1
        print(f"🌟 Iniciando ADK Web en puerto {adk_port}")
        
        # Ejecutar ADK Web en proceso separado
        process = subprocess.Popen([
            "python", "-m", "uvicorn", 
            "adk_main:app",
            "--host", "0.0.0.0", 
            "--port", str(adk_port),
            "--log-level", "info"
        ])
        
        return process
        
    except Exception as e:
        print(f"⚠️  No se pudo iniciar ADK Web: {e}")
        return None

def main():
    """Función principal"""
    setup_production_environment()
    
    # Crear aplicación principal
    app = create_production_app()
    
    # Configurar uvicorn para producción
    config = uvicorn.Config(
        app,
        host=HOST,
        port=PORT,
        log_level="info",
        access_log=True,
        loop="asyncio"
    )
    
    server = uvicorn.Server(config)
    
    # Ejecutar servidor
    try:
        print(f"✅ Servidor iniciado en http://{HOST}:{PORT}")
        server.run()
    except KeyboardInterrupt:
        print("\n🛑 Servidor detenido")
    except Exception as e:
        print(f"❌ Error del servidor: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()