"""
runner.py — ADK Runner integration for the Agentic QC Inspector

Handles session creation, pipeline execution, event streaming,
and progress tracking for the Streamlit UI.
"""
import asyncio
import io
import json
import sys
from contextlib import contextmanager
from typing import Callable, Optional

from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from agent import root_agent

load_dotenv()

APP_NAME = "qc_inspector"

# Noise patterns printed directly to stdout by google-genai when the model
# returns thinking tokens (thought_signature).  These are informational only
# and safe to suppress in a Streamlit context.
_SUPPRESS_SUBSTRINGS = (
    "non-text parts in the response",
    "thought_signature",
    "returning concatenated text result",
    "Check the full candidates",
)


@contextmanager
def _suppress_genai_noise():
    """Redirect stdout/stderr lines matching known google-genai noise patterns."""
    class _Filter(io.TextIOWrapper):
        def __init__(self, wrapped):
            self._wrapped = wrapped

        def write(self, s):
            if not any(sub in s for sub in _SUPPRESS_SUBSTRINGS):
                self._wrapped.write(s)
            return len(s)

        def flush(self):
            self._wrapped.flush()

        def __getattr__(self, name):
            return getattr(self._wrapped, name)

    old_out, old_err = sys.stdout, sys.stderr
    sys.stdout = _Filter(old_out)
    sys.stderr = _Filter(old_err)
    try:
        yield
    finally:
        sys.stdout, sys.stderr = old_out, old_err
USER_ID  = "demo_user"

AGENT_PIPELINE_ORDER = [
    "optical_inspection_agent",
    "metrology_agent",
    "yield_engineer_agent",
    "failure_analysis_agent",
    "qa_supervisor_agent",
]

EXPECTED_STATE_KEYS = {
    "aoi_report",
    "metrology_report",
    "yield_report",
    "fa_report",
    "disposition",
}


# ── Pure utility functions (tested in test_t11_runner.py) ─────────────────────

def build_runner(session_service: InMemorySessionService) -> Runner:
    """Create an ADK Runner for the qc_inspector pipeline."""
    return Runner(
        agent=root_agent,
        app_name=APP_NAME,
        session_service=session_service,
    )


def build_inspection_content(image_bytes: bytes, mime_type: str = "image/jpeg") -> types.Content:
    """Construct a multimodal user message containing the component image."""
    return types.Content(
        role="user",
        parts=[
            types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
            types.Part.from_text(
                text=(
                    "You are inspecting a manufacturing component. "
                    "Perform your specialist analysis on this image."
                )
            ),
        ],
    )


def detect_agent_from_event(event) -> Optional[str]:
    """
    Return the agent_id if the event is a completed final response from a known pipeline agent.
    Returns None for orchestrator events, intermediate events, or unknown agents.
    """
    if not hasattr(event, "author"):
        return None
    if event.author not in AGENT_PIPELINE_ORDER:
        return None
    if not event.is_final_response():
        return None
    return event.author


def extract_state_keys(session_state: dict) -> dict:
    """Extract only the five expected QC report keys from raw session state.
    String values are JSON-parsed into dicts (agents write JSON text via output_key).
    """
    result = {}
    for k, v in session_state.items():
        if k not in EXPECTED_STATE_KEYS:
            continue
        if isinstance(v, str):
            try:
                result[k] = json.loads(v)
            except (json.JSONDecodeError, ValueError):
                result[k] = v
        else:
            result[k] = v
    return result


def get_mime_type(filename: str) -> str:
    """Infer MIME type from image filename extension."""
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return {
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
        "bmp": "image/bmp",
    }.get(ext, "image/jpeg")


# ── Async pipeline runner ─────────────────────────────────────────────────────

async def run_inspection_async(
    image_bytes: bytes,
    mime_type: str = "image/jpeg",
    progress_callback: Optional[Callable[[str, str], None]] = None,
) -> dict:
    """
    Execute the full 5-agent QC inspection pipeline.

    Args:
        image_bytes:       Raw bytes of the component image
        mime_type:         MIME type of the image (default: image/jpeg)
        progress_callback: Optional callback(agent_id, status) fired as each agent
                           transitions. status is one of: 'running', 'done', 'error'

    Returns:
        dict with keys: aoi_report, metrology_report, yield_report, fa_report, disposition
    """
    session_service = InMemorySessionService()
    runner = build_runner(session_service)

    session = await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
    )
    session_id = session.id
    content = build_inspection_content(image_bytes, mime_type)

    # Signal first agent as running before pipeline starts
    if progress_callback and AGENT_PIPELINE_ORDER:
        progress_callback(AGENT_PIPELINE_ORDER[0], "running")

    try:
        with _suppress_genai_noise():
            async for event in runner.run_async(
                user_id=USER_ID,
                session_id=session_id,
                new_message=content,
            ):
                completed = detect_agent_from_event(event)
                if completed and progress_callback:
                    progress_callback(completed, "done")
                    idx = AGENT_PIPELINE_ORDER.index(completed)
                    if idx + 1 < len(AGENT_PIPELINE_ORDER):
                        progress_callback(AGENT_PIPELINE_ORDER[idx + 1], "running")
    except Exception as exc:
        if progress_callback:
            for agent_id in AGENT_PIPELINE_ORDER:
                progress_callback(agent_id, "error")
        raise RuntimeError(f"Inspection pipeline failed: {exc}") from exc

    final_session = await session_service.get_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=session_id,
    )
    return extract_state_keys(dict(final_session.state))


def run_inspection(
    image_bytes: bytes,
    mime_type: str = "image/jpeg",
    progress_callback: Optional[Callable[[str, str], None]] = None,
) -> dict:
    """Synchronous wrapper around run_inspection_async — for use in Streamlit."""
    return asyncio.run(run_inspection_async(image_bytes, mime_type, progress_callback))
