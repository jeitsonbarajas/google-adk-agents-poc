"""
deploy_agent_engine.py
----------------------
Deploys the orquestador ADK agent to Vertex AI Agent Engine.

Usage:
    python deploy_agent_engine.py [--update RESOURCE_NAME]

    Without --update: creates a new Agent Engine deployment.
    With --update: updates an existing deployment (faster, keeps same endpoint).

Environment variables required:
    GOOGLE_CLOUD_PROJECT   GCP project ID
    GOOGLE_CLOUD_LOCATION  GCP region (e.g. us-east1)
    OPENAI_API_KEY         OpenAI key (injected as env var into the agent)
    CLAUDE_API_KEY         Anthropic key  (injected as env var into the agent)

Authentication:
    Runs via Application Default Credentials (ADC).
    In GitHub Actions this is handled by Workload Identity Federation.
    Locally: run `gcloud auth application-default login`.
"""

import argparse
import os
import sys

import vertexai
from vertexai.preview import reasoning_engines

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "careful-aleph-493015-f6")
LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-east1")
STAGING_BUCKET = f"gs://{PROJECT_ID}-agent-engine-staging"
DISPLAY_NAME = "google-adk-agents-poc"

# Agent requirements installed inside the Agent Engine sandbox
AGENT_REQUIREMENTS = [
    "google-adk>=1.0.0",
    "openai>=1.0.0",
    "anthropic>=0.25.0",
    "httpx>=0.25.0",
    "python-dotenv>=1.0.0",
    "pydantic>=2.0.0",
]

# ---------------------------------------------------------------------------
# Set Vertex AI backend for ADK (must be set before importing agents)
# ---------------------------------------------------------------------------
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "true"
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", PROJECT_ID)
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", LOCATION)

# ---------------------------------------------------------------------------
# Import agent (after env vars are set)
# ---------------------------------------------------------------------------
from agents.orquestador import orquestador  # noqa: E402


def build_app() -> reasoning_engines.AdkApp:
    """Wrap the orquestador in AdkApp for Agent Engine."""
    return reasoning_engines.AdkApp(
        agent=orquestador,
        enable_tracing=True,
    )


def _runtime_env_vars() -> dict:
    """Environment variables injected into the Agent Engine sandbox at runtime."""
    return {
        "GOOGLE_GENAI_USE_VERTEXAI": "true",
        "GOOGLE_CLOUD_PROJECT": PROJECT_ID,
        "GOOGLE_CLOUD_LOCATION": LOCATION,
    }


def deploy_new() -> reasoning_engines.ReasoningEngine:
    """Create a brand-new Agent Engine deployment."""
    print(f"  Project  : {PROJECT_ID}")
    print(f"  Location : {LOCATION}")
    print(f"  Bucket   : {STAGING_BUCKET}")
    print("")
    print("Uploading agent to Vertex AI Agent Engine (this may take ~5 min)...")

    remote_agent = reasoning_engines.ReasoningEngine.create(
        build_app(),
        requirements=AGENT_REQUIREMENTS,
        display_name=DISPLAY_NAME,
        description="Multi-agent customer support system with HITL pattern.",
        extra_packages=[],
        env_vars=_runtime_env_vars(),
    )
    return remote_agent


def deploy_update(resource_name: str) -> reasoning_engines.ReasoningEngine:
    """Update an existing Agent Engine deployment in-place."""
    print(f"Updating existing Agent Engine: {resource_name} ...")
    remote_agent = reasoning_engines.ReasoningEngine(resource_name)
    remote_agent.update(
        agent_engine=build_app(),
        requirements=AGENT_REQUIREMENTS,
        display_name=DISPLAY_NAME,
        env_vars=_runtime_env_vars(),
    )
    return remote_agent


def main() -> None:
    parser = argparse.ArgumentParser(description="Deploy ADK agent to Vertex AI Agent Engine")
    parser.add_argument(
        "--update",
        metavar="RESOURCE_NAME",
        help="Resource name of an existing deployment to update instead of creating new",
    )
    args = parser.parse_args()

    # Initialize Vertex AI SDK
    vertexai.init(project=PROJECT_ID, location=LOCATION, staging_bucket=STAGING_BUCKET)

    if args.update:
        remote_agent = deploy_update(args.update)
    else:
        remote_agent = deploy_new()

    resource_name = remote_agent.resource_name
    print("")
    print("=" * 70)
    print("  DEPLOYMENT COMPLETE")
    print("=" * 70)
    print(f"  Resource name : {resource_name}")
    print("")
    print("  Save the resource name above — use it with --update on future deploys.")
    print("")
    print("  To query the agent:")
    print(f"    from vertexai.preview import reasoning_engines")
    print(f"    agent = reasoning_engines.ReasoningEngine('{resource_name}')")
    print(f"    response = agent.query(input='Tengo un problema con mi factura')")
    print("=" * 70)

    # Write resource name to file so the CI pipeline can cache it
    output_file = os.environ.get("AGENT_ENGINE_RESOURCE_FILE", "agent_engine_resource.txt")
    with open(output_file, "w") as f:
        f.write(resource_name)
    print(f"\n  Resource name saved to: {output_file}")


if __name__ == "__main__":
    main()
