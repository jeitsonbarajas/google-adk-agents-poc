from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from tools.resolver_problema_tecnico import resolver_problema_tecnico
from tools.resolver_problema_facturacion import resolver_problema_facturacion
# ═══════════════════════════════════════════════════════
# AGENTES
# ═══════════════════════════════════════════════════════
# --- Agente Resolutor (sub-agente con tools) ---
# Recibe el ticket ya clasificado y decide qué tool usar.
# Habla con Gemini a través de las tools sin intervención de Python.
agente_resolutor = LlmAgent(
    name="AgenteResolutor",
    model="gemini-3-flash-preview",
    tools=[
        FunctionTool(resolver_problema_tecnico),
        FunctionTool(resolver_problema_facturacion),
    ],
    instruction="""
Eres un agente resolutor de tickets de soporte especializado.

Cuando recibas un ticket:
1. Analiza si es un problema TECNICO o de FACTURACION.
2. Usa la herramienta correspondiente para obtener la solución:
   - Problemas técnicos (errores, APIs, infraestructura, conexiones) → resolver_problema_tecnico
   - Problemas de facturación (cobros, pagos, disputas) → resolver_problema_facturacion
3. Devuelve la solución completa obtenida de la herramienta al agente Orquestador.

IMPORTANTE: Siempre usa una herramienta. No respondas sin consultarlas.
"""
)