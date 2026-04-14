import asyncio
import os
from google import genai
import uvicorn
from fastapi import FastAPI, Query, Request
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

# Configure Google Genai with API key
GEMINI_CLIENT = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

@app.post("/v1/chat/completions")
async def proxy_model(request: Request, model: str = Query("gemini-2.5-flash")):
    data = await request.json()
    messages = data.get("messages", [])

    print("  peticion " + model + " con mensaje: " + str(messages))

    # --- Routing según el modelo ---
    if model.startswith("gemini"):  # Google Gemini
        ultimo_mensaje = messages[-1]["content"] if messages else ""
        resp = await GEMINI_CLIENT.aio.generate_content_async(ultimo_mensaje)
        content = resp.text
    else:
        return {"error": f"Modelo {model} no soportado. Solo se admiten modelos Gemini."}

    return {"choices": [{"message": {"role": "assistant", "content": content}}]}

if __name__ == "__main__":
    from config.settings import PORT
    uvicorn.run(app, host="0.0.0.0", port=PORT)