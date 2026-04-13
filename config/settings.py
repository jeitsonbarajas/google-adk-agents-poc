import os
from dotenv import load_dotenv
from google.adk.sessions import InMemorySessionService

load_dotenv()

APP_NAME = "google-adk-agents-poc"
USER_ID = "usuario_123"
SESSION_SERVICE = InMemorySessionService()
PORT = int(os.getenv("PORT", 8080))

# Vertex AI config for ADK/Gemini usage in serverless environments.
USE_VERTEX_AI = os.getenv("USE_VERTEX_AI", "false").lower() == "true"
GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("GCP_PROJECT")
GOOGLE_CLOUD_LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")

if USE_VERTEX_AI:
	os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "true")
	if GOOGLE_CLOUD_PROJECT:
		os.environ.setdefault("GOOGLE_CLOUD_PROJECT", GOOGLE_CLOUD_PROJECT)
	os.environ.setdefault("GOOGLE_CLOUD_LOCATION", GOOGLE_CLOUD_LOCATION)