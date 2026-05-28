"""
tests/conftest.py — Shared test fixtures for the Agentic QC Inspector

Provides:
  - sample_image_bytes      : minimal valid JPEG for vision agent tests
  - mock_aoi_report         : fixture output from optical_inspection_agent
  - mock_metrology_report   : fixture output from metrology_agent
  - mock_yield_report       : fixture output from yield_engineer_agent
  - mock_fa_report          : fixture output from failure_analysis_agent
  - mock_disposition        : fixture output from qa_supervisor_agent
  - mock_full_session_state : complete session.state after all agents run
"""
import io

import pytest
from PIL import Image


@pytest.fixture
def sample_image_bytes() -> bytes:
    """Generate a minimal valid JPEG image for testing (200x200 grey square)."""
    img = Image.new("RGB", (200, 200), color=(180, 180, 180))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


@pytest.fixture
def mock_aoi_report() -> dict:
    return {
        "component_type": "IC Chip",
        "part_family": "Microcontroller",
        "defects": [
            "hairline crack at top-left corner [minor]: Small surface crack, not penetrating substrate"
        ],
        "defect_count": 1,
        "severity_level": "minor",
        "solder_quality": "good",
        "contamination_found": False,
    }


@pytest.fixture
def mock_metrology_report() -> dict:
    return {
        "placement_accurate": True,
        "orientation_correct": True,
        "symmetry_score": 0.92,
        "dimensional_anomalies": [],
        "warpage_detected": False,
        "notes": "Component within acceptable dimensional tolerances.",
    }


@pytest.fixture
def mock_yield_report() -> dict:
    return {
        "defect_type": "hairline crack",
        "process_stage": "handling",
        "systemic_risk": False,
        "yield_impact_estimate": "low",
        "corrective_actions": [
            "Review handling procedures at inspection station",
            "Add anti-static padding to component trays",
        ],
    }


@pytest.fixture
def mock_fa_report() -> dict:
    return {
        "failure_mode": "mechanical stress fracture",
        "root_cause": "Excessive pressure applied during manual handling",
        "confidence": 0.78,
        "latent_risk": False,
        "recommended_actions": [
            "Implement handling force limits",
            "Retrain operators on ESD-safe handling procedures",
        ],
    }


@pytest.fixture
def mock_disposition() -> dict:
    return {
        "disposition": "MRB",
        "confidence_pct": 72,
        "critical_findings": ["Hairline crack detected on IC package body"],
        "mandatory_action": "Hold for engineering review before shipment",
        "disposition_rationale": (
            "Single minor crack present. Component is functional but crack poses "
            "a potential latent reliability risk. MRB review required."
        ),
    }


@pytest.fixture
def mock_full_session_state(
    mock_aoi_report,
    mock_metrology_report,
    mock_yield_report,
    mock_fa_report,
    mock_disposition,
) -> dict:
    """Complete session.state as it appears after all 5 agents have run."""
    return {
        "aoi_report": mock_aoi_report,
        "metrology_report": mock_metrology_report,
        "yield_report": mock_yield_report,
        "fa_report": mock_fa_report,
        "disposition": mock_disposition,
    }
