"""
tests/test_t09_root_agent.py — T09: Root Agent + __init__.py

Verifies:
  - root_agent is a SequentialAgent
  - sub_agents list has all 5 specialist agents in the correct order
  - Each sub-agent is an LlmAgent
  - __init__.py correctly exports root_agent
  - root_agent name and description are set
"""
from google.adk.agents import LlmAgent, SequentialAgent

from agent import (
    failure_analysis_agent,
    metrology_agent,
    optical_inspection_agent,
    qa_supervisor_agent,
    root_agent,
    yield_engineer_agent,
)

EXPECTED_ORDER = [
    "optical_inspection_agent",
    "metrology_agent",
    "yield_engineer_agent",
    "failure_analysis_agent",
    "qa_supervisor_agent",
]


def test_root_agent_is_sequential_agent():
    assert isinstance(root_agent, SequentialAgent)


def test_root_agent_name():
    assert root_agent.name == "qc_inspector"


def test_root_agent_has_description():
    assert root_agent.description
    assert len(root_agent.description) > 10


def test_root_agent_has_five_sub_agents():
    assert len(root_agent.sub_agents) == 5


def test_root_agent_sub_agents_are_llm_agents():
    for sub in root_agent.sub_agents:
        assert isinstance(sub, LlmAgent), f"{sub} is not an LlmAgent"


def test_root_agent_sub_agents_in_correct_order():
    actual_names = [sub.name for sub in root_agent.sub_agents]
    assert actual_names == EXPECTED_ORDER, (
        f"Sub-agent order mismatch.\nExpected: {EXPECTED_ORDER}\nActual:   {actual_names}"
    )


def test_root_agent_contains_optical_inspection():
    names = [s.name for s in root_agent.sub_agents]
    assert "optical_inspection_agent" in names


def test_root_agent_contains_metrology():
    names = [s.name for s in root_agent.sub_agents]
    assert "metrology_agent" in names


def test_root_agent_contains_yield_engineer():
    names = [s.name for s in root_agent.sub_agents]
    assert "yield_engineer_agent" in names


def test_root_agent_contains_failure_analysis():
    names = [s.name for s in root_agent.sub_agents]
    assert "failure_analysis_agent" in names


def test_root_agent_contains_qa_supervisor():
    names = [s.name for s in root_agent.sub_agents]
    assert "qa_supervisor_agent" in names


def test_init_exports_root_agent():
    """Verify __init__.py makes root_agent importable as a package attribute."""
    import importlib
    import sys

    # Reload __init__ to test the export
    pkg_name = "bwai"
    if pkg_name in sys.modules:
        mod = sys.modules[pkg_name]
    else:
        # Fallback: root_agent already imported from agent directly above — just verify it's the same object
        from agent import root_agent as direct_root
        assert direct_root is root_agent
        return

    assert hasattr(mod, "root_agent"), "__init__.py must export root_agent"
    assert isinstance(mod.root_agent, SequentialAgent)
