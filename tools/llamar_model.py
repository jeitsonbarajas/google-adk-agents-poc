import os

from google import genai

_gemini_client = None


def _get_client() -> genai.Client:
    """Lazy-initialize the Gemini client.

    Inside Vertex AI Agent Engine, GOOGLE_GENAI_USE_VERTEXAI=true and ADC
    provides credentials automatically — no API key required.
    Locally, falls back to GOOGLE_API_KEY.
    """
    global _gemini_client
    if _gemini_client is None:
        use_vertex = os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "false").lower() == "true"
        if use_vertex:
            _gemini_client = genai.Client(
                vertexai=True,
                project=os.getenv("GOOGLE_CLOUD_PROJECT"),
                location=os.getenv("GOOGLE_CLOUD_LOCATION", "us-east1"),
            )
        else:
            _gemini_client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
    return _gemini_client


def generar_respuesta(analisis: str):
    client = _get_client()
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=analisis
    )
    return response.candidates[0].content.parts[0].text