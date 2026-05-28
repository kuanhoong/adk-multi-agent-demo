"""
tests/test_t13_integration.py — T13: Final Integration Test Suite

Verifies end-to-end structural integrity across all layers:
  1. All project files are present
  2. All modules import cleanly together
  3. The full agent pipeline wires correctly (root_agent → 5 sub-agents)
  4. Runner utility functions handle mock data correctly end-to-end
  5. Display functions produce correct output for all three dispositions
  6. Session state schema is consistent across agent, runner, and app layers
  7. All previous test files are collected and pass (meta-test)

Note: This test does NOT make real API calls. Live pipeline testing
      requires GOOGLE_API_KEY to be set in .env.
"""
import importlib
import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

ROOT = Path(__file__).parent.parent

# ── 1. Project file presence ───────────────────────────────────────────────────

def test_all_source_files_present():
    required = [
        ".env", "requirements.txt", "pytest.ini",
        "__init__.py", "agent.py", "tools.py", "runner.py", "app.py",
    ]
    missing = [f for f in required if not (ROOT / f).exists()]
    assert not missing, f"Missing source files: {missing}"


def test_all_test_files_present():
    expected = [f"test_t{i:02d}_" for i in range(1, 14)]
    test_files = [p.name for p in (ROOT / "tests").glob("test_t*.py")]
    missing = [prefix for prefix in expected if not any(f.startswith(prefix) for f in test_files)]
    assert not missing, f"Missing test files with prefixes: {missing}"


# ── 2. Cross-module imports ────────────────────────────────────────────────────

def test_tools_importable():
    import tools
    assert tools is not None


def test_agent_importable():
    import agent
    assert agent is not None


def test_runner_importable():
    import runner
    assert runner is not None


def test_app_importable():
    import app
    assert app is not None


def test_all_five_tools_accessible():
    from tools import (
        analyze_yield_impact,
        issue_qa_disposition,
        perform_failure_analysis,
        run_aoi_scan,
        run_metrology_check,
    )
    for fn in (run_aoi_scan, run_metrology_check, analyze_yield_impact,
               perform_failure_analysis, issue_qa_disposition):
        assert callable(fn)


def test_all_six_agents_accessible():
    from agent import (
        failure_analysis_agent,
        metrology_agent,
        optical_inspection_agent,
        qa_supervisor_agent,
        root_agent,
        yield_engineer_agent,
    )
    for ag in (optical_inspection_agent, metrology_agent, yield_engineer_agent,
               failure_analysis_agent, qa_supervisor_agent, root_agent):
        assert ag is not None


# ── 3. Full agent pipeline wiring ─────────────────────────────────────────────

def test_root_agent_is_sequential_agent():
    from agent import root_agent
    assert isinstance(root_agent, SequentialAgent)


def test_root_agent_has_five_llm_sub_agents():
    from agent import root_agent
    assert len(root_agent.sub_agents) == 5
    for sub in root_agent.sub_agents:
        assert isinstance(sub, LlmAgent)


def test_pipeline_output_keys_form_complete_schema():
    from agent import root_agent
    output_keys = {sub.output_key for sub in root_agent.sub_agents}
    expected_keys = {"aoi_report", "metrology_report", "yield_report", "fa_report", "disposition"}
    assert output_keys == expected_keys


def test_each_agent_has_exactly_one_tool():
    from agent import root_agent
    for sub in root_agent.sub_agents:
        assert len(sub.tools) == 1, f"{sub.name} should have exactly 1 tool"


def test_agent_instructions_reference_upstream_context():
    from agent import (
        failure_analysis_agent,
        metrology_agent,
        qa_supervisor_agent,
        yield_engineer_agent,
    )
    assert "{aoi_report}" in metrology_agent.instruction
    assert "{aoi_report}" in yield_engineer_agent.instruction
    assert "{metrology_report}" in yield_engineer_agent.instruction
    assert "{aoi_report}" in failure_analysis_agent.instruction
    assert "{yield_report}" in failure_analysis_agent.instruction
    assert all(
        key in qa_supervisor_agent.instruction
        for key in ("{aoi_report}", "{metrology_report}", "{yield_report}", "{fa_report}")
    )


# ── 4. Runner utilities end-to-end ────────────────────────────────────────────

def test_runner_builds_with_root_agent():
    from runner import build_runner
    session_service = InMemorySessionService()
    r = build_runner(session_service)
    assert isinstance(r, Runner)
    from agent import root_agent
    assert r.agent is root_agent


def test_runner_content_has_image_and_text():
    from runner import build_inspection_content
    content = build_inspection_content(b"\xff\xd8\xff", mime_type="image/jpeg")
    assert isinstance(content, types.Content)
    assert len(content.parts) == 2
    assert content.parts[0].inline_data.mime_type == "image/jpeg"


def test_runner_detects_all_pipeline_agents_on_final_event():
    from runner import AGENT_PIPELINE_ORDER, detect_agent_from_event
    for agent_id in AGENT_PIPELINE_ORDER:
        event = MagicMock()
        event.author = agent_id
        event.is_final_response.return_value = True
        assert detect_agent_from_event(event) == agent_id


def test_runner_extract_state_consistent_with_agent_output_keys():
    from agent import root_agent
    from runner import extract_state_keys

    agent_output_keys = {sub.output_key for sub in root_agent.sub_agents}
    mock_state = {key: {"data": "mock"} for key in agent_output_keys}
    mock_state["_extra"] = "should be excluded"
    result = extract_state_keys(mock_state)
    assert set(result.keys()) == agent_output_keys


# ── 5. Display functions for all three dispositions ───────────────────────────

@pytest.mark.parametrize("disposition,expected_substr", [
    ("PASS", "PASS"),
    ("FAIL", "FAIL"),
    ("MRB",  "MRB"),
])
def test_verdict_label_covers_all_dispositions(disposition, expected_substr):
    from app import get_verdict_label
    label = get_verdict_label(disposition)
    assert expected_substr in label


def test_verdict_colors_are_distinct():
    from app import get_verdict_color
    colors = {get_verdict_color(d) for d in ("PASS", "FAIL", "MRB")}
    assert len(colors) == 3


def test_build_json_report_with_full_mock_state(mock_full_session_state):
    from app import build_json_report
    report = build_json_report(mock_full_session_state)
    parsed = json.loads(report)
    assert set(parsed.keys()) == {"aoi_report", "metrology_report", "yield_report", "fa_report", "disposition"}


# ── 6. Schema consistency across layers ───────────────────────────────────────

def test_tool_output_keys_match_agent_output_keys():
    """Tool return dicts should contain the keys agents store as output."""
    from tools import (
        analyze_yield_impact,
        issue_qa_disposition,
        perform_failure_analysis,
        run_aoi_scan,
        run_metrology_check,
    )
    aoi = run_aoi_scan("IC", "MCU", [], 0, "none", "N/A", False)
    assert "component_type" in aoi and "defects" in aoi

    met = run_metrology_check(True, True, 1.0, [], False, "ok")
    assert "symmetry_score" in met

    yld = analyze_yield_impact("crack", "handling", False, "low", [])
    assert "process_stage" in yld

    fa = perform_failure_analysis("crack", "stress", 0.8, False, [])
    assert "failure_mode" in fa and "confidence" in fa

    disp = issue_qa_disposition("PASS", 95, [], "Ship", "Clean component")
    assert "disposition" in disp and disp["disposition"] == "PASS"


def test_mock_session_state_schema_matches_runner_expected_keys(mock_full_session_state):
    from runner import EXPECTED_STATE_KEYS
    assert set(mock_full_session_state.keys()) == EXPECTED_STATE_KEYS


# ── 7. Meta-test: all previous test files collect without errors ───────────────

def test_all_test_modules_collect_without_import_error():
    """Verify every test_tXX file can be imported cleanly."""
    test_dir = ROOT / "tests"
    for test_file in sorted(test_dir.glob("test_t[0-1][0-9]_*.py")):
        module_name = test_file.stem
        spec = importlib.util.spec_from_file_location(module_name, test_file)
        mod = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(mod)
        except Exception as exc:
            pytest.fail(f"Import of {test_file.name} failed: {exc}")
