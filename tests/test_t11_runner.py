"""
tests/test_t11_runner.py — T11: ADK Runner Integration

Tests pure utility functions without making real API calls:
  - build_runner creates a Runner backed by root_agent
  - build_inspection_content creates correct multimodal Content structure
  - detect_agent_from_event correctly maps events to agent IDs
  - extract_state_keys filters raw session state to expected report keys
  - get_mime_type infers correct MIME type from filenames
"""
from unittest.mock import MagicMock

import pytest
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from agent import root_agent
from runner import (
    AGENT_PIPELINE_ORDER,
    EXPECTED_STATE_KEYS,
    build_inspection_content,
    build_runner,
    detect_agent_from_event,
    extract_state_keys,
    get_mime_type,
)


# ── build_runner ───────────────────────────────────────────────────────────────

def test_build_runner_returns_runner_instance():
    session_service = InMemorySessionService()
    runner = build_runner(session_service)
    assert isinstance(runner, Runner)


def test_build_runner_uses_root_agent():
    session_service = InMemorySessionService()
    runner = build_runner(session_service)
    assert runner.agent is root_agent


# ── build_inspection_content ───────────────────────────────────────────────────

def test_build_content_returns_content_type():
    content = build_inspection_content(b"fake_bytes")
    assert isinstance(content, types.Content)


def test_build_content_role_is_user():
    content = build_inspection_content(b"fake_bytes")
    assert content.role == "user"


def test_build_content_has_two_parts():
    content = build_inspection_content(b"fake_bytes")
    assert len(content.parts) == 2


def test_build_content_first_part_is_image_bytes():
    content = build_inspection_content(b"fake_bytes", mime_type="image/jpeg")
    first = content.parts[0]
    assert first.inline_data is not None
    assert first.inline_data.mime_type == "image/jpeg"
    assert first.inline_data.data == b"fake_bytes"


def test_build_content_second_part_is_text():
    content = build_inspection_content(b"fake_bytes")
    second = content.parts[1]
    assert second.text is not None
    assert len(second.text) > 0


def test_build_content_png_mime_type():
    content = build_inspection_content(b"fake_bytes", mime_type="image/png")
    assert content.parts[0].inline_data.mime_type == "image/png"


def test_build_content_bmp_mime_type():
    content = build_inspection_content(b"fake_bytes", mime_type="image/bmp")
    assert content.parts[0].inline_data.mime_type == "image/bmp"


# ── detect_agent_from_event ────────────────────────────────────────────────────

def test_detect_known_agent_final_response():
    event = MagicMock()
    event.author = "optical_inspection_agent"
    event.is_final_response.return_value = True
    assert detect_agent_from_event(event) == "optical_inspection_agent"


def test_detect_known_agent_not_final_returns_none():
    event = MagicMock()
    event.author = "metrology_agent"
    event.is_final_response.return_value = False
    assert detect_agent_from_event(event) is None


def test_detect_unknown_author_returns_none():
    event = MagicMock()
    event.author = "some_other_agent"
    event.is_final_response.return_value = True
    assert detect_agent_from_event(event) is None


def test_detect_event_without_author_attr_returns_none():
    event = object()
    assert detect_agent_from_event(event) is None


def test_detect_orchestrator_author_returns_none():
    event = MagicMock()
    event.author = "qc_inspector"  # SequentialAgent, not a specialist
    event.is_final_response.return_value = True
    assert detect_agent_from_event(event) is None


@pytest.mark.parametrize("agent_id", AGENT_PIPELINE_ORDER)
def test_detect_all_pipeline_agents(agent_id):
    event = MagicMock()
    event.author = agent_id
    event.is_final_response.return_value = True
    assert detect_agent_from_event(event) == agent_id


# ── extract_state_keys ─────────────────────────────────────────────────────────

def test_extract_all_five_report_keys():
    state = {
        "aoi_report":       {"component_type": "IC"},
        "metrology_report": {"placement_accurate": True},
        "yield_report":     {"yield_impact_estimate": "low"},
        "fa_report":        {"failure_mode": "crack"},
        "disposition":      {"disposition": "PASS"},
        "_internal":        "excluded",
        "user_prompt":      "excluded",
    }
    result = extract_state_keys(state)
    assert set(result.keys()) == EXPECTED_STATE_KEYS


def test_extract_excludes_non_report_keys():
    state = {"_system": "data", "aoi_report": {"component_type": "PCB"}}
    result = extract_state_keys(state)
    assert "_system" not in result


def test_extract_partial_state():
    state = {"aoi_report": {"component_type": "PCB"}}
    result = extract_state_keys(state)
    assert result == {"aoi_report": {"component_type": "PCB"}}


def test_extract_empty_state_returns_empty():
    assert extract_state_keys({}) == {}


def test_extract_preserves_values():
    state = {"disposition": {"disposition": "MRB", "confidence_pct": 72}}
    result = extract_state_keys(state)
    assert result["disposition"]["confidence_pct"] == 72


# ── get_mime_type ──────────────────────────────────────────────────────────────

@pytest.mark.parametrize("filename,expected", [
    ("chip.jpg",  "image/jpeg"),
    ("chip.jpeg", "image/jpeg"),
    ("board.png", "image/png"),
    ("part.bmp",  "image/bmp"),
    ("CHIP.JPG",  "image/jpeg"),
])
def test_get_mime_type_known_extensions(filename, expected):
    assert get_mime_type(filename) == expected


def test_get_mime_type_unknown_extension_defaults_to_jpeg():
    assert get_mime_type("file.xyz") == "image/jpeg"


def test_get_mime_type_no_extension_defaults_to_jpeg():
    assert get_mime_type("noextension") == "image/jpeg"


# ── Constants ──────────────────────────────────────────────────────────────────

def test_agent_pipeline_order_has_five_entries():
    assert len(AGENT_PIPELINE_ORDER) == 5


def test_expected_state_keys_has_five_entries():
    assert len(EXPECTED_STATE_KEYS) == 5


def test_agent_pipeline_order_first_is_optical():
    assert AGENT_PIPELINE_ORDER[0] == "optical_inspection_agent"


def test_agent_pipeline_order_last_is_qa_supervisor():
    assert AGENT_PIPELINE_ORDER[-1] == "qa_supervisor_agent"
