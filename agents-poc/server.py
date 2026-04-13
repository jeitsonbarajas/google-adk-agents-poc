import asyncio
import os
from google import genai
import uvicorn
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic
from fastapi import FastAPI, Query, Request
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()
OPENAI_CLIENT = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
CLAUDE_CLIENT = AsyncAnthropic(api_key=os.getenv("CLAUDE_API_KEY"))

# Configure Google Genai with API key
GEMINI_CLIENT = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

@app.post("/v1/chat/completions")
async def proxy_model(request: Request, model: str = Query("gpt-4o-mini")):
    data = await request.json()
    messages = data.get("messages", [])

    print("  peticion " + model + " con mensaje: "+ str(messages)  )

    # --- Routing según el modelo ---
    if model.startswith("gpt"):  # OpenAI
        # async con acreate() para no bloquear event loop
        resp = await OPENAI_CLIENT.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )
        content = resp.choices[0].message.content

    elif model.startswith("claude"):  # Anthropic

        resp = await CLAUDE_CLIENT.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1000,
            messages=messages 
        )

        content = resp.content[0].text


    elif model.startswith("gemini"):  # Google Gemini
        
        ultimo_mensaje = messages[-1]["content"] if messages else ""

        resp = await GEMINI_CLIENT.aio.generate_content_async(ultimo_mensaje)
        content = resp.text

    else:
        return {"error": f"Modelo {model} no soportado"}

    return {"choices": [{"message": {"role": "assistant", "content": content}}]}

if __name__ == "__main__":
    from config.settings import PORT
    uvicorn.run(app, host="0.0.0.0", port=PORT)