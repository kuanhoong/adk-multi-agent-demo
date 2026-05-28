"""
tests/test_t05_metrology_agent.py — T05: Metrology Agent

Verifies static configuration without making API calls:
  - Agent is an LlmAgent instance
  - Correct name, output_key, model prefix
  - Exactly one tool attached: run_metrology_check
  - Instruction references upstream AOI context and metrology keywords
"""
from google.adk.agents import LlmAgent

from agent import metrology_agent


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


def test_metrology_agent_is_llm_agent():
    assert isinstance(metrology_agent, LlmAgent)


def test_metrology_agent_name():
    assert metrology_agent.name == "metrology_agent"


def test_metrology_agent_output_key():
    assert metrology_agent.output_key == "metrology_report"


def test_metrology_agent_model_is_gemini():
    model = metrology_agent.model
    model_str = model if isinstance(model, str) else getattr(model, "model_name", str(model))
    assert "gemini" in model_str.lower()


def test_metrology_agent_has_exactly_one_tool():
    assert len(metrology_agent.tools) == 1


def test_metrology_agent_tool_is_run_metrology_check():
    names = _tool_names(metrology_agent)
    assert "run_metrology_check" in names, f"Expected 'run_metrology_check' in tool names, got: {names}"


def test_metrology_agent_instruction_references_aoi_context():
    assert "{aoi_report}" in metrology_agent.instruction


def test_metrology_agent_instruction_contains_metrology_keywords():
    instr = metrology_agent.instruction.lower()
    for keyword in ("placement", "orientation", "symmetry", "dimensional"):
        assert keyword in instr, f"Instruction missing keyword: '{keyword}'"


def test_metrology_agent_has_description():
    assert metrology_agent.description
    assert len(metrology_agent.description) > 10
