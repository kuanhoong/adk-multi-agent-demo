"""
tests/test_t08_qa_agent.py — T08: QA Supervisor Agent

Verifies static configuration without making API calls:
  - Agent is an LlmAgent instance
  - Correct name, output_key, model prefix
  - Exactly one tool attached: issue_qa_disposition
  - Instruction references all four upstream reports
  - Instruction contains PASS / FAIL / MRB disposition options
"""
from google.adk.agents import LlmAgent

from agent import qa_supervisor_agent


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


def test_qa_agent_is_llm_agent():
    assert isinstance(qa_supervisor_agent, LlmAgent)


def test_qa_agent_name():
    assert qa_supervisor_agent.name == "qa_supervisor_agent"


def test_qa_agent_output_key():
    assert qa_supervisor_agent.output_key == "disposition"


def test_qa_agent_model_is_gemini():
    model = qa_supervisor_agent.model
    model_str = model if isinstance(model, str) else getattr(model, "model_name", str(model))
    assert "gemini" in model_str.lower()


def test_qa_agent_has_exactly_one_tool():
    assert len(qa_supervisor_agent.tools) == 1


def test_qa_agent_tool_is_issue_qa_disposition():
    names = _tool_names(qa_supervisor_agent)
    assert "issue_qa_disposition" in names, f"Expected 'issue_qa_disposition' in tool names, got: {names}"


def test_qa_agent_instruction_references_all_four_reports():
    instr = qa_supervisor_agent.instruction
    for key in ("{aoi_report}", "{metrology_report}", "{yield_report}", "{fa_report}"):
        assert key in instr, f"Instruction missing upstream context reference: {key}"


def test_qa_agent_instruction_contains_all_disposition_options():
    instr = qa_supervisor_agent.instruction
    for disposition in ("PASS", "FAIL", "MRB"):
        assert disposition in instr, f"Instruction missing disposition option: {disposition}"


def test_qa_agent_has_description():
    assert qa_supervisor_agent.description
    assert len(qa_supervisor_agent.description) > 10
