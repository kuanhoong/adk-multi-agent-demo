"""
tests/test_t01_scaffold.py — T01: Project Scaffold

Verifies:
  - All required project files exist
  - tests/ directory and conftest.py are present
  - .env defines GOOGLE_API_KEY
  - requirements.txt lists all required packages
  - Local Python modules (agent, tools, app) are importable
  - Third-party packages are installed
"""
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent


# ── File existence ─────────────────────────────────────────────────────────────

def test_required_root_files_exist():
    required = [".env", "requirements.txt", "agent.py", "tools.py", "__init__.py", "app.py", "pytest.ini"]
    missing = [f for f in required if not (ROOT / f).exists()]
    assert not missing, f"Missing required files: {missing}"


def test_tests_directory_structure():
    assert (ROOT / "tests").is_dir(), "tests/ directory must exist"
    assert (ROOT / "tests" / "__init__.py").exists(), "tests/__init__.py must exist"
    assert (ROOT / "tests" / "conftest.py").exists(), "tests/conftest.py must exist"


# ── .env content ───────────────────────────────────────────────────────────────

def test_env_defines_google_api_key():
    content = (ROOT / ".env").read_text()
    assert "GOOGLE_API_KEY" in content, ".env must define GOOGLE_API_KEY"


def test_env_defines_gemini_model():
    content = (ROOT / ".env").read_text()
    assert "GEMINI_MODEL" in content, ".env must define GEMINI_MODEL"


# ── requirements.txt content ───────────────────────────────────────────────────

def test_requirements_lists_core_packages():
    content = (ROOT / "requirements.txt").read_text().lower()
    required = ["google-adk", "streamlit", "python-dotenv", "pillow", "pytest"]
    missing = [pkg for pkg in required if pkg not in content]
    assert not missing, f"requirements.txt missing packages: {missing}"


# ── Local module imports ────────────────────────────────────────────────────────

def test_tools_module_importable():
    import tools
    expected_functions = [
        "run_aoi_scan",
        "run_metrology_check",
        "analyze_yield_impact",
        "perform_failure_analysis",
        "issue_qa_disposition",
    ]
    missing = [fn for fn in expected_functions if not callable(getattr(tools, fn, None))]
    assert not missing, f"tools.py missing callables: {missing}"


def test_agent_module_importable():
    import agent  # noqa: F401


def test_app_module_importable():
    import app  # noqa: F401


# ── Third-party packages ───────────────────────────────────────────────────────

def test_google_adk_installed():
    pytest.importorskip(
        "google.adk.agents",
        reason="google-adk not installed — run: pip install -r requirements.txt",
    )


def test_google_genai_installed():
    pytest.importorskip(
        "google.genai",
        reason="google-genai not installed — run: pip install -r requirements.txt",
    )


def test_streamlit_installed():
    pytest.importorskip(
        "streamlit",
        reason="streamlit not installed — run: pip install -r requirements.txt",
    )


def test_pillow_installed():
    pytest.importorskip(
        "PIL",
        reason="Pillow not installed — run: pip install -r requirements.txt",
    )
