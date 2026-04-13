# Imagen base oficial de Python slim
FROM python:3.11-slim

# Evitar archivos .pyc y buffering de logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instalar dependencias primero (capa cacheada)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código
COPY . .

# Cloud Run inyecta PORT automáticamente; uvicorn lo lee desde settings.py
EXPOSE 8080

CMD ["python", "server.py"]
