"""
tests/test_t04_optical_agent.py — T04: Optical Inspection Agent (AOI)

Verifies static configuration without making API calls:
  - Agent is an LlmAgent instance
  - Correct name, output_key, model prefix
  - Exactly one tool attached: run_aoi_scan
  - Instruction contains AOI role keywords
"""
import pytest
from google.adk.agents import LlmAgent

from agent import optical_inspection_agent
from tools import run_aoi_scan


def _tool_names(agent) -> list:
    """Extract tool names from an agent's tools list regardless of ADK wrapper type."""
    names = []
    for tool in agent.tools:
        if hasattr(tool, "name"):
            names.append(tool.name)
        elif hasattr(tool, "__name__"):
            names.append(tool.__name__)
        elif hasattr(tool, "func") and hasattr(tool.func, "__name__"):
            names.append(tool.func.__name__)
    return names


def test_optical_agent_is_llm_agent():
    assert isinstance(optical_inspection_agent, LlmAgent)


def test_optical_agent_name():
    assert optical_inspection_agent.name == "optical_inspection_agent"


def test_optical_agent_output_key():
    assert optical_inspection_agent.output_key == "aoi_report"


def test_optical_agent_model_is_gemini():
    model = optical_inspection_agent.model
    model_str = model if isinstance(model, str) else getattr(model, "model_name", str(model))
    assert "gemini" in model_str.lower()


def test_optical_agent_has_exactly_one_tool():
    assert len(optical_inspection_agent.tools) == 1


def test_optical_agent_tool_is_run_aoi_scan():
    names = _tool_names(optical_inspection_agent)
    assert "run_aoi_scan" in names, f"Expected 'run_aoi_scan' in tool names, got: {names}"


def test_optical_agent_instruction_contains_aoi_keywords():
    instr = optical_inspection_agent.instruction.lower()
    for keyword in ("aoi", "defect", "surface", "solder"):
        assert keyword in instr, f"Instruction missing keyword: '{keyword}'"


def test_optical_agent_has_description():
    assert optical_inspection_agent.description
    assert len(optical_inspection_agent.description) > 10
