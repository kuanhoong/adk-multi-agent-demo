"""
tests/test_t06_yield_agent.py — T06: Yield Engineer Agent

Verifies static configuration without making API calls:
  - Agent is an LlmAgent instance
  - Correct name, output_key, model prefix
  - Exactly one tool attached: analyze_yield_impact
  - Instruction references both AOI and metrology upstream context
"""
from google.adk.agents import LlmAgent

from agent import yield_engineer_agent


def _tool_names(agent) -> list:
    names = []
    for tool in agent.tools:
        if hasattr(tool, "name"):
            names.append(tool.name)
        elif hasattr(tool, "__name__"):
            names.append(tool.__name__)
        elif hasattr(tool, "func") and hasattr(tool.func, "__name__"):
            names.append(tool.func.__name__)
    return names


def test_yield_agent_is_llm_agent():
    assert isinstance(yield_engineer_agent, LlmAgent)


def test_yield_agent_name():
    assert yield_engineer_agent.name == "yield_engineer_agent"


def test_yield_agent_output_key():
    assert yield_engineer_agent.output_key == "yield_report"


def test_yield_agent_model_is_gemini():
    model = yield_engineer_agent.model
    model_str = model if isinstance(model, str) else getattr(model, "model_name", str(model))
    assert "gemini" in model_str.lower()


def test_yield_agent_has_exactly_one_tool():
    assert len(yield_engineer_agent.tools) == 1


def test_yield_agent_tool_is_analyze_yield_impact():
    names = _tool_names(yield_engineer_agent)
    assert "analyze_yield_impact" in names, f"Expected 'analyze_yield_impact' in tool names, got: {names}"


def test_yield_agent_instruction_references_both_upstream_reports():
    instr = yield_engineer_agent.instruction
    assert "{aoi_report}" in instr
    assert "{metrology_report}" in instr


def test_yield_agent_instruction_contains_yield_keywords():
    instr = yield_engineer_agent.instruction.lower()
    for keyword in ("yield", "process", "systemic", "corrective"):
        assert keyword in instr, f"Instruction missing keyword: '{keyword}'"


def test_yield_agent_has_description():
    assert yield_engineer_agent.description
    assert len(yield_engineer_agent.description) > 10
