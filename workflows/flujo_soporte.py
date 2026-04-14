import uuid
from config.settings import APP_NAME, USER_ID, SESSION_SERVICE
from agents.orquestador import orquestador
from agents.agente_redactor import agente_redactor
from google.adk.runners import Runner
from google.genai import types

def construir_mensaje(texto: str) -> types.Content:
    return types.Content(role="user", parts=[types.Part(text=texto)])

async def ejecutar_con_runner(agente, mensaje: str, session_id: str) -> str:
    await SESSION_SERVICE.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=session_id)
    runner = Runner(agent=agente, app_name=APP_NAME, session_service=SESSION_SERVICE)
    ultima_respuesta = None

    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=session_id,
        new_message=construir_mensaje(mensaje)
    ):
        if event.is_final_response() and event.content and event.content.parts:
            partes_texto = [p.text for p in event.content.parts if hasattr(p, "text") and p.text]
            if partes_texto:
                ultima_respuesta = "\n".join(partes_texto)
                if hasattr(event, "author") and event.author:
                    preview = ultima_respuesta[:80]
                    sufijo = f"... (+{len(ultima_respuesta)-80} chars)" if len(ultima_respuesta) > 80 else ""
                    print(f"   💬 [{event.author}]: {preview}{sufijo}")

    return ultima_respuesta or "Sin respuesta."

# ═══════════════════════════════════════════════════════
# FLUJO PRINCIPAL
# Los agentes se coordinan entre sí vía el orquestador.
# Python solo gestiona el HITL y la entrada/salida.
# ═══════════════════════════════════════════════════════

async def ejecutar_flujo_soporte(ticket_usuario: str) -> str:
    # session_id único por ticket para evitar colisiones
    ticket_id = str(uuid.uuid4())[:8]

    # ─────────────────────────────────────────
    # FASE 1: RESOLUCIÓN
    # Orquestador → AgenteResolutor → Gemini (via tool)
    # Los agentes hablan entre sí dentro de esta fase.
    # ─────────────────────────────────────────
    print("\n[FASE 1] Orquestador coordinando resolución del ticket...")
    print(f"         session_id: {ticket_id}_resolucion\n")

    solucion = await ejecutar_con_runner(
        agente=orquestador,
        mensaje=f"Resuelve este ticket de soporte: {ticket_usuario}",
        session_id=f"{ticket_id}_resolucion"
    )

    # ─────────────────────────────────────────
    # FASE 2: HUMAN-IN-THE-LOOP
    # Python gestiona la auditoría humana.
    # El humano puede aprobar, editar o rechazar.
    # ─────────────────────────────────────────
    print("\n" + "=" * 55)
    print("  AUDITORÍA HUMANA")
    print("=" * 55)
    print(solucion)
    print("=" * 55)

    decision = input("\n¿Aprobar respuesta? (si/editar/rechazar): ").lower().strip()

    if decision == "rechazar":
        print("[INFO] Flujo cancelado por el auditor.")
        return "Flujo cancelado por el auditor."

    solucion_aprobada = input("Ingrese corrección: ") if decision == "editar" else solucion

    # ─────────────────────────────────────────
    # FASE 3: REDACCIÓN FINAL
    # Orquestador → AgenteRedactor
    # Recibe la solución validada y produce respuesta para el cliente.
    # ─────────────────────────────────────────
    print("\n[FASE 3] Orquestador coordinando redacción final...\n")

    respuesta_final = await ejecutar_con_runner(
        agente=agente_redactor,  # ← directo
        mensaje=solucion_aprobada,
        session_id=f"{ticket_id}_redaccion"
    )

    return respuesta_final


# ═══════════════════════════════════════════════════════
# VERSIÓN HTTP (sin input): dividida en 2 fases para Cloud Run
# ═══════════════════════════════════════════════════════

async def ejecutar_fase1_resolucion(ticket_usuario: str) -> tuple[str, str]:
    """Fase 1: resuelve el ticket. Devuelve (solucion, ticket_id)."""
    ticket_id = str(uuid.uuid4())[:8]
    print(f"\n[FASE 1] session_id: {ticket_id}_resolucion")
    solucion = await ejecutar_con_runner(
        agente=orquestador,
        mensaje=f"Resuelve este ticket de soporte: {ticket_usuario}",
        session_id=f"{ticket_id}_resolucion"
    )
    return solucion, ticket_id


async def ejecutar_fase3_redaccion(solucion_aprobada: str, ticket_id: str) -> str:
    """Fase 3: redacta la respuesta final a partir de la solución aprobada."""
    print(f"\n[FASE 3] session_id: {ticket_id}_redaccion")
    return await ejecutar_con_runner(
        agente=orquestador,
        mensaje=f"La solución fue validada por el auditor. Redacta la respuesta final para el cliente: {solucion_aprobada}",
        session_id=f"{ticket_id}_redaccion"
    )
