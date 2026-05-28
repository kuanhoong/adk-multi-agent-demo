"""
tests/test_t12_display.py — T12: Results Display + Verdict Banner

Tests pure formatting functions in app.py without starting Streamlit.
  - format_confidence_float: correct percentage strings
  - get_severity_color: correct hex per severity level
  - summarise_defects: correct summary for empty / single / multiple defects
  - format_bool_indicator: correct labels
  - format_corrective_actions: correct bulleted output
  - build_json_report: valid JSON output with all expected keys
  - render_verdict_banner logic: correct colours and labels for all dispositions
"""
import json

import pytest

from app import (
    SEVERITY_COLORS,
    VERDICT_COLORS,
    VERDICT_LABELS,
    build_json_report,
    format_bool_indicator,
    format_confidence_float,
    format_corrective_actions,
    get_severity_color,
    get_verdict_color,
    get_verdict_label,
    summarise_defects,
)


# ── format_confidence_float ────────────────────────────────────────────────────

def test_format_confidence_float_zero():
    assert format_confidence_float(0.0) == "0.0%"


def test_format_confidence_float_one():
    assert format_confidence_float(1.0) == "100.0%"


def test_format_confidence_float_midpoint():
    assert format_confidence_float(0.85) == "85.0%"


def test_format_confidence_float_rounds_to_one_decimal():
    assert format_confidence_float(0.856) == "85.6%"


def test_format_confidence_float_low():
    assert format_confidence_float(0.1) == "10.0%"


# ── get_severity_color ─────────────────────────────────────────────────────────

def test_severity_color_none_is_green():
    assert get_severity_color("none") == SEVERITY_COLORS["none"]


def test_severity_color_minor_is_amber():
    assert get_severity_color("minor") == SEVERITY_COLORS["minor"]


def test_severity_color_major():
    assert get_severity_color("major") == SEVERITY_COLORS["major"]


def test_severity_color_critical_is_red():
    assert get_severity_color("critical") == SEVERITY_COLORS["critical"]


def test_severity_color_unknown_returns_fallback():
    color = get_severity_color("unknown_level")
    assert color.startswith("#")


def test_severity_color_case_insensitive():
    assert get_severity_color("CRITICAL") == get_severity_color("critical")
    assert get_severity_color("MINOR")    == get_severity_color("minor")


# ── summarise_defects ──────────────────────────────────────────────────────────

def test_summarise_defects_empty_list():
    assert summarise_defects([]) == "No defects detected"


def test_summarise_defects_single():
    defects = [{"type": "crack", "severity": "minor", "location": "top"}]
    result = summarise_defects(defects)
    assert "1 defect" in result
    assert "minor" in result


def test_summarise_defects_multiple():
    defects = [
        {"type": "crack",   "severity": "minor",    "location": "top"},
        {"type": "void",    "severity": "major",    "location": "center"},
        {"type": "scratch", "severity": "critical", "location": "edge"},
    ]
    result = summarise_defects(defects)
    assert "3 defects" in result
    assert "critical" in result


def test_summarise_defects_worst_severity_is_highest():
    defects = [
        {"type": "a", "severity": "none"},
        {"type": "b", "severity": "minor"},
        {"type": "c", "severity": "major"},
    ]
    result = summarise_defects(defects)
    assert "major" in result
    assert "minor" not in result or "worst" in result


# ── format_bool_indicator ──────────────────────────────────────────────────────

def test_format_bool_indicator_true_default():
    assert format_bool_indicator(True) == "Yes"


def test_format_bool_indicator_false_default():
    assert format_bool_indicator(False) == "No"


def test_format_bool_indicator_custom_labels():
    assert format_bool_indicator(True,  "Pass", "Fail") == "Pass"
    assert format_bool_indicator(False, "Pass", "Fail") == "Fail"


# ── format_corrective_actions ──────────────────────────────────────────────────

def test_format_corrective_actions_empty():
    assert format_corrective_actions([]) == "None"


def test_format_corrective_actions_single():
    result = format_corrective_actions(["Retrain operators"])
    assert "Retrain operators" in result
    assert result.startswith("•")


def test_format_corrective_actions_multiple():
    actions = ["Action A", "Action B", "Action C"]
    result = format_corrective_actions(actions)
    assert result.count("•") == 3
    assert "Action A" in result
    assert "Action C" in result


# ── build_json_report ──────────────────────────────────────────────────────────

def test_build_json_report_returns_valid_json(mock_full_session_state):
    result = build_json_report(mock_full_session_state)
    parsed = json.loads(result)
    assert isinstance(parsed, dict)


def test_build_json_report_contains_all_keys(mock_full_session_state):
    result = build_json_report(mock_full_session_state)
    parsed = json.loads(result)
    expected_keys = {"aoi_report", "metrology_report", "yield_report", "fa_report", "disposition"}
    assert expected_keys == set(parsed.keys())


def test_build_json_report_is_pretty_printed(mock_full_session_state):
    result = build_json_report(mock_full_session_state)
    assert "\n" in result  # indented JSON has newlines


def test_build_json_report_disposition_preserved(mock_full_session_state):
    result = build_json_report(mock_full_session_state)
    parsed = json.loads(result)
    assert parsed["disposition"]["disposition"] in {"PASS", "FAIL", "MRB"}


# ── get_verdict_color / get_verdict_label (T12 display usage) ─────────────────

def test_verdict_banner_color_pass():
    assert get_verdict_color("PASS") == VERDICT_COLORS["PASS"]


def test_verdict_banner_color_fail():
    assert get_verdict_color("FAIL") == VERDICT_COLORS["FAIL"]


def test_verdict_banner_color_mrb():
    assert get_verdict_color("MRB") == VERDICT_COLORS["MRB"]


def test_verdict_banner_label_contains_pass():
    assert "PASS" in get_verdict_label("PASS")


def test_verdict_banner_label_contains_fail():
    assert "FAIL" in get_verdict_label("FAIL")


def test_verdict_banner_label_contains_mrb():
    assert "MRB" in get_verdict_label("MRB")


def test_all_dispositions_have_distinct_colors():
    colors = [get_verdict_color(d) for d in ("PASS", "FAIL", "MRB")]
    assert len(set(colors)) == 3, "Each disposition must have a unique colour"


def test_all_dispositions_have_distinct_labels():
    labels = [get_verdict_label(d) for d in ("PASS", "FAIL", "MRB")]
    assert len(set(labels)) == 3, "Each disposition must have a unique label"
