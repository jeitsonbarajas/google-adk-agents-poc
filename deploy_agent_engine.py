"""
deploy_agent_engine.py — Deploys the orquestador to Vertex AI Agent Engine.
"""
import os

import vertexai
from vertexai.preview import reasoning_engines

PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "careful-aleph-493015-f6")
LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-east1")
STAGING_BUCKET = f"gs://{PROJECT_ID}-agent-engine-staging"
DISPLAY_NAME = "google-adk-agents-poc"

AGENT_REQUIREMENTS = [
    "google-adk>=1.0.0",
    "google-cloud-aiplatform>=1.87.0",
    "httpx>=0.25.0",
    "python-dotenv>=1.0.0",
    "pydantic>=2.0.0",
]

EXTRA_PACKAGES = ["./agents", "./tools", "./config", "./workflows"]

os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "true"
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", PROJECT_ID)
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", LOCATION)

from agents.orquestador import orquestador  # noqa: E402


class VertexAdkApp(reasoning_engines.AdkApp):
    def __init__(self, project_id: str, location: str, **kwargs):
        self._project_id = project_id
        self._location = location
        super().__init__(**kwargs)

    def set_up(self):
        import os
        os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "true")
        os.environ.setdefault("GOOGLE_CLOUD_PROJECT", self._project_id)
        os.environ.setdefault("GOOGLE_CLOUD_LOCATION", self._location)
        super().set_up()


def build_app():
    return VertexAdkApp(project_id=PROJECT_ID, location=LOCATION, agent=orquestador, enable_tracing=True)


def deploy_new():
    print(f"  Project  : {PROJECT_ID}")
    print(f"  Location : {LOCATION}")
    print(f"  Bucket   : {STAGING_BUCKET}")
    print("")
    print("Uploading agent to Vertex AI Agent Engine (this may take ~5 min)...")
    return reasoning_engines.ReasoningEngine.create(
        build_app(),
        requirements=AGENT_REQUIREMENTS,
        display_name=DISPLAY_NAME,
        description="Multi-agent customer support system with HITL pattern.",
        extra_packages=EXTRA_PACKAGES,
    )


def main():
    vertexai.init(project=PROJECT_ID, location=LOCATION, staging_bucket=STAGING_BUCKET)

    remote_agent = deploy_new()

    resource_name = remote_agent.resource_name
    print("")
    print("=" * 70)
    print("  DEPLOYMENT COMPLETE")
    print(f"  Resource name : {resource_name}")
    print("=" * 70)

    output_file = os.environ.get("AGENT_ENGINE_RESOURCE_FILE", "agent_engine_resource.txt")
    with open(output_file, "w") as f:
        f.write(resource_name)
    print(f"\n  Resource name saved to: {output_file}")


if __name__ == "__main__":
    main()
