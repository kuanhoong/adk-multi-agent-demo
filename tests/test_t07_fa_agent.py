"""
tests/test_t07_fa_agent.py — T07: Failure Analysis Agent

Verifies static configuration without making API calls:
  - Agent is an LlmAgent instance
  - Correct name, output_key, model prefix
  - Exactly one tool attached: perform_failure_analysis
  - Instruction references AOI and yield upstream context + FA keywords
"""
from google.adk.agents import LlmAgent

from agent import failure_analysis_agent


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


def test_fa_agent_is_llm_agent():
    assert isinstance(failure_analysis_agent, LlmAgent)


def test_fa_agent_name():
    assert failure_analysis_agent.name == "failure_analysis_agent"


def test_fa_agent_output_key():
    assert failure_analysis_agent.output_key == "fa_report"


def test_fa_agent_model_is_gemini():
    model = failure_analysis_agent.model
    model_str = model if isinstance(model, str) else getattr(model, "model_name", str(model))
    assert "gemini" in model_str.lower()


def test_fa_agent_has_exactly_one_tool():
    assert len(failure_analysis_agent.tools) == 1


def test_fa_agent_tool_is_perform_failure_analysis():
    names = _tool_names(failure_analysis_agent)
    assert "perform_failure_analysis" in names, f"Expected 'perform_failure_analysis' in tool names, got: {names}"


def test_fa_agent_instruction_references_aoi_and_yield_context():
    instr = failure_analysis_agent.instruction
    assert "{aoi_report}" in instr
    assert "{yield_report}" in instr


def test_fa_agent_instruction_contains_fa_keywords():
    instr = failure_analysis_agent.instruction.lower()
    for keyword in ("failure mode", "root cause", "latent", "confidence"):
        assert keyword in instr, f"Instruction missing keyword: '{keyword}'"


def test_fa_agent_has_description():
    assert failure_analysis_agent.description
    assert len(failure_analysis_agent.description) > 10
