"""
tests/test_t03_fixtures.py — T03: Test Fixtures

Verifies that all conftest.py fixtures are well-formed:
  - sample_image_bytes is a valid readable JPEG
  - Each mock report dict contains all required schema keys
  - Values have correct types and are within valid ranges
  - mock_full_session_state contains all 5 agent output keys
"""
import io

from PIL import Image


# ── sample_image_bytes ─────────────────────────────────────────────────────────

def test_sample_image_bytes_is_bytes(sample_image_bytes):
    assert isinstance(sample_image_bytes, bytes)


def test_sample_image_bytes_is_non_empty(sample_image_bytes):
    assert len(sample_image_bytes) > 0


def test_sample_image_bytes_is_valid_jpeg(sample_image_bytes):
    img = Image.open(io.BytesIO(sample_image_bytes))
    assert img.format == "JPEG"


def test_sample_image_bytes_has_correct_dimensions(sample_image_bytes):
    img = Image.open(io.BytesIO(sample_image_bytes))
    assert img.size == (200, 200)


# ── mock_aoi_report ────────────────────────────────────────────────────────────

def test_mock_aoi_report_has_all_keys(mock_aoi_report):
    required = {
        "component_type", "part_family", "defects",
        "defect_count", "severity_level", "solder_quality", "contamination_found",
    }
    assert required.issubset(mock_aoi_report.keys())


def test_mock_aoi_report_defects_is_list(mock_aoi_report):
    assert isinstance(mock_aoi_report["defects"], list)


def test_mock_aoi_report_severity_level_valid(mock_aoi_report):
    assert mock_aoi_report["severity_level"] in {"none", "minor", "major", "critical"}


def test_mock_aoi_report_contamination_is_bool(mock_aoi_report):
    assert isinstance(mock_aoi_report["contamination_found"], bool)


# ── mock_metrology_report ──────────────────────────────────────────────────────

def test_mock_metrology_report_has_all_keys(mock_metrology_report):
    required = {
        "placement_accurate", "orientation_correct", "symmetry_score",
        "dimensional_anomalies", "warpage_detected", "notes",
    }
    assert required.issubset(mock_metrology_report.keys())


def test_mock_metrology_report_symmetry_score_in_range(mock_metrology_report):
    score = mock_metrology_report["symmetry_score"]
    assert 0.0 <= score <= 1.0


def test_mock_metrology_report_booleans(mock_metrology_report):
    assert isinstance(mock_metrology_report["placement_accurate"], bool)
    assert isinstance(mock_metrology_report["orientation_correct"], bool)
    assert isinstance(mock_metrology_report["warpage_detected"], bool)


# ── mock_yield_report ──────────────────────────────────────────────────────────

def test_mock_yield_report_has_all_keys(mock_yield_report):
    required = {
        "defect_type", "process_stage", "systemic_risk",
        "yield_impact_estimate", "corrective_actions",
    }
    assert required.issubset(mock_yield_report.keys())


def test_mock_yield_report_yield_impact_valid(mock_yield_report):
    assert mock_yield_report["yield_impact_estimate"] in {"low", "medium", "high"}


def test_mock_yield_report_corrective_actions_is_list(mock_yield_report):
    assert isinstance(mock_yield_report["corrective_actions"], list)


# ── mock_fa_report ─────────────────────────────────────────────────────────────

def test_mock_fa_report_has_all_keys(mock_fa_report):
    required = {
        "failure_mode", "root_cause", "confidence",
        "latent_risk", "recommended_actions",
    }
    assert required.issubset(mock_fa_report.keys())


def test_mock_fa_report_confidence_in_range(mock_fa_report):
    assert 0.0 <= mock_fa_report["confidence"] <= 1.0


def test_mock_fa_report_latent_risk_is_bool(mock_fa_report):
    assert isinstance(mock_fa_report["latent_risk"], bool)


# ── mock_disposition ───────────────────────────────────────────────────────────

def test_mock_disposition_has_all_keys(mock_disposition):
    required = {
        "disposition", "confidence_pct", "critical_findings",
        "mandatory_action", "disposition_rationale",
    }
    assert required.issubset(mock_disposition.keys())


def test_mock_disposition_value_valid(mock_disposition):
    assert mock_disposition["disposition"] in {"PASS", "FAIL", "MRB"}


def test_mock_disposition_confidence_pct_in_range(mock_disposition):
    assert 0 <= mock_disposition["confidence_pct"] <= 100


def test_mock_disposition_critical_findings_is_list(mock_disposition):
    assert isinstance(mock_disposition["critical_findings"], list)


# ── mock_full_session_state ────────────────────────────────────────────────────

def test_mock_full_session_state_has_all_agent_keys(mock_full_session_state):
    expected = {"aoi_report", "metrology_report", "yield_report", "fa_report", "disposition"}
    assert expected == set(mock_full_session_state.keys())


def test_mock_full_session_state_values_are_dicts(mock_full_session_state):
    for key, value in mock_full_session_state.items():
        assert isinstance(value, dict), f"session_state['{key}'] must be a dict"
