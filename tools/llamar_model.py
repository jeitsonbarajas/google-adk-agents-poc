import os

from google import genai

_gemini_client = None


def _get_client() -> genai.Client:
    """Lazy-initialize the Gemini client.

    Priority:
    1. GOOGLE_API_KEY is set → use it directly (local dev, CI, Cloud Run)
    2. Otherwise → Vertex AI with ADC (Agent Engine sandbox, GCP environments)
    """
    global _gemini_client
    if _gemini_client is None:
        api_key = os.getenv("GOOGLE_API_KEY")
        if api_key:
            _gemini_client = genai.Client(api_key=api_key)
        else:
            _gemini_client = genai.Client(
                vertexai=True,
                project=os.getenv("GOOGLE_CLOUD_PROJECT"),
                location=os.getenv("GOOGLE_CLOUD_LOCATION", "us-east1"),
            )
    return _gemini_client


def generar_respuesta(analisis: str):
    client = _get_client()
    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=analisis
    )
    return response.candidates[0].content.parts[0].text