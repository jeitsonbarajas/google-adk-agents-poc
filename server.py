import asyncio
import os
from typing import Literal
from google import genai
import uvicorn
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic
from fastapi import FastAPI, HTTPException, Query, Request
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from workflows.flujo_soporte import ejecutar_fase1_resolucion, ejecutar_fase3_redaccion

load_dotenv()
app = FastAPI(
    title="Google ADK Agents POC API",
    description=(
        "API de soporte con patrón Human-in-the-Loop (HITL).\n\n"
        "Flujo recomendado:\n"
        "1. Llamar a /soporte/resolver para obtener solución preliminar y ticket_id.\n"
        "2. Un auditor humano aprueba/edita/rechaza esa solución.\n"
        "3. Llamar a /soporte/aprobar con la decisión para generar respuesta final."
    ),
    version="1.0.0",
)

# Estado HITL en memoria (para POC). En producción usar Firestore o Redis.
_pendientes: dict[str, str] = {}
OPENAI_CLIENT = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
CLAUDE_CLIENT = AsyncAnthropic(api_key=os.getenv("CLAUDE_API_KEY"))

# Configure Google Genai with API key
GEMINI_CLIENT = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))


def _build_upstream_http_error(exc: Exception) -> HTTPException:
    message = str(exc)

    if "API_KEY_INVALID" in message or "API key not valid" in message:
        return HTTPException(
            status_code=502,
            detail="Fallo al llamar al proveedor Google Gemini: GOOGLE_API_KEY invalida.",
        )

    return HTTPException(
        status_code=502,
        detail=f"Fallo al llamar a un proveedor externo: {message}",
    )

@app.post("/v1/chat/completions")
async def proxy_model(request: Request, model: str = Query("gpt-4o-mini")):
    try:
        data = await request.json()
        messages = data.get("messages", [])

        print("  peticion " + model + " con mensaje: "+ str(messages)  )

        # --- Routing según el modelo ---
        if model.startswith("gpt"):  # OpenAI
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
            raise HTTPException(status_code=400, detail=f"Modelo {model} no soportado")

        return {"choices": [{"message": {"role": "assistant", "content": content}}]}
    except HTTPException:
        raise
    except Exception as exc:
        raise _build_upstream_http_error(exc) from exc

# ─────────────────────────────────────────
# Endpoints HITL (Human-in-the-Loop)
# ─────────────────────────────────────────

class TicketRequest(BaseModel):
    ticket: str = Field(
        ...,
        description="Texto del ticket del cliente.",
        examples=["No puedo descargar mi factura de enero"],
    )


class ResolverResponse(BaseModel):
    ticket_id: str = Field(..., description="Identificador del ticket en flujo HITL.")
    solucion: str = Field(..., description="Solución preliminar para revisión humana.")

class AprobacionRequest(BaseModel):
    ticket_id: str = Field(..., description="ticket_id devuelto por /soporte/resolver")
    decision: Literal["aprobar", "editar", "rechazar"] = Field(
        ...,
        description="Decisión del auditor humano sobre la solución preliminar.",
    )
    correccion: str = Field(
        default="",
        description="Texto corregido cuando decision es 'editar'.",
        examples=["Se valida ajuste manual de glosa y se notifica por correo."],
    )


class AprobarResponse(BaseModel):
    respuesta_final: str = Field(..., description="Respuesta final para el cliente.")


@app.post(
    "/soporte/resolver",
    response_model=ResolverResponse,
    tags=["Soporte HITL"],
    summary="Fase 1: Resolver ticket",
    description="Genera una solución preliminar y la deja pendiente para auditoría humana.",
)
async def resolver_ticket(body: TicketRequest):
    try:
        solucion, ticket_id = await ejecutar_fase1_resolucion(body.ticket)
        _pendientes[ticket_id] = solucion
        return {"ticket_id": ticket_id, "solucion": solucion}
    except Exception as exc:
        raise _build_upstream_http_error(exc) from exc


@app.post(
    "/soporte/aprobar",
    response_model=AprobarResponse,
    tags=["Soporte HITL"],
    summary="Fase 3: Aprobar/editar/rechazar",
    description=(
        "Recibe la decisión del auditor sobre una solución pendiente y devuelve la redacción final."
    ),
    responses={
        404: {
            "description": "ticket_id no encontrado o ya procesado",
            "content": {
                "application/json": {
                    "example": {"detail": "ticket_id no encontrado o ya procesado"}
                }
            },
        }
    },
)
async def aprobar_ticket(body: AprobacionRequest):
    try:
        solucion = _pendientes.pop(body.ticket_id, None)
        if solucion is None:
            raise HTTPException(status_code=404, detail="ticket_id no encontrado o ya procesado")

        if body.decision == "rechazar":
            return {"respuesta_final": "Flujo cancelado por el auditor."}

        solucion_aprobada = body.correccion if body.decision == "editar" else solucion
        respuesta_final = await ejecutar_fase3_redaccion(solucion_aprobada, body.ticket_id)
        return {"respuesta_final": respuesta_final}
    except HTTPException:
        raise
    except Exception as exc:
        raise _build_upstream_http_error(exc) from exc


if __name__ == "__main__":
    from config.settings import PORT
    uvicorn.run(app, host="0.0.0.0", port=PORT)