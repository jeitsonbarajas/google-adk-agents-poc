from google.adk.agents import LlmAgent
from agents.agente_resolutor import agente_resolutor
from agents.agente_redactor import agente_redactor
# ═══════════════════════════════════════════════════════
# AGENTES
# ═══════════════════════════════════════════════════════

# --- Orquestador principal ---
# El cerebro del flujo. Coordina a los sub-agentes,
# les habla y les pasa contexto directamente.
orquestador = LlmAgent(
    name="Orquestador",
    model="gemini-3-flash-preview",
    sub_agents=[agente_resolutor, agente_redactor],
    instruction="""
Eres el coordinador del sistema de soporte de Glosas IG Services.

REGLAS ESTRICTAS:
- NUNCA resumas, acortes ni parafrasees las respuestas de los sub-agentes.
- Siempre devuelve el texto COMPLETO tal como lo entrego el sub-agente.
- No agregues frases como "Le informaremos..." ni comentarios propios al final.

Tu flujo de trabajo es:
1. Recibe el ticket del cliente.
2. Transfiere el ticket completo al AgenteResolutor.
3. Recibe la respuesta COMPLETA del AgenteResolutor, sin modificarla ni agregar nada.
4. Envia respuesta COMPLETA al AgenteRedactor.

"""
)