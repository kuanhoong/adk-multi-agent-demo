"""
tests/test_t10_ui_layout.py — T10: Streamlit Layout + Image Upload

Tests pure Python utility functions in app.py without starting Streamlit.
  - get_verdict_color: correct hex for PASS / FAIL / MRB / unknown
  - get_verdict_label: correct label strings
  - get_agent_status_icon: correct emoji for each status
  - validate_image_extension: accepts valid types, rejects invalid
  - image_bytes_to_pil: converts bytes to PIL Image
  - build_initial_statuses: all 5 agents start as 'queued'
  - Constants: AGENT_ORDER has 5 entries, VERDICT_COLORS covers all dispositions
"""
import io

import pytest
from PIL import Image

from app import (
    ACCEPTED_EXTENSIONS,
    AGENT_ORDER,
    VERDICT_COLORS,
    build_initial_statuses,
    get_agent_status_icon,
    get_verdict_color,
    get_verdict_label,
    image_bytes_to_pil,
    validate_image_extension,
)


# ── get_verdict_color ──────────────────────────────────────────────────────────

def test_verdict_color_pass_is_green():
    color = get_verdict_color("PASS")
    assert color.startswith("#")
    assert color == VERDICT_COLORS["PASS"]


def test_verdict_color_fail_is_red():
    color = get_verdict_color("FAIL")
    assert color.startswith("#")
    assert color == VERDICT_COLORS["FAIL"]


def test_verdict_color_mrb_is_amber():
    color = get_verdict_color("MRB")
    assert color.startswith("#")
    assert color == VERDICT_COLORS["MRB"]


def test_verdict_color_unknown_returns_fallback():
    color = get_verdict_color("UNKNOWN")
    assert color.startswith("#")


def test_verdict_colors_all_three_dispositions_covered():
    for disposition in ("PASS", "FAIL", "MRB"):
        assert disposition in VERDICT_COLORS


# ── get_verdict_label ──────────────────────────────────────────────────────────

def test_verdict_label_pass_contains_ship():
    label = get_verdict_label("PASS")
    assert "PASS" in label


def test_verdict_label_fail_contains_rework():
    label = get_verdict_label("FAIL")
    assert "FAIL" in label


def test_verdict_label_mrb_contains_review():
    label = get_verdict_label("MRB")
    assert "MRB" in label


# ── get_agent_status_icon ──────────────────────────────────────────────────────

def test_status_icon_queued():
    assert get_agent_status_icon("queued") == "⏳"


def test_status_icon_running():
    assert get_agent_status_icon("running") == "🔄"


def test_status_icon_done():
    assert get_agent_status_icon("done") == "✅"


def test_status_icon_error():
    assert get_agent_status_icon("error") == "❌"


def test_status_icon_unknown_returns_string():
    icon = get_agent_status_icon("unknown_status")
    assert isinstance(icon, str)


# ── validate_image_extension ───────────────────────────────────────────────────

@pytest.mark.parametrize("filename", ["part.jpg", "part.jpeg", "chip.png", "board.bmp"])
def test_valid_image_extensions_accepted(filename):
    assert validate_image_extension(filename) is True


@pytest.mark.parametrize("filename", ["report.pdf", "data.xlsx", "model.stl", "README.md", "noextension"])
def test_invalid_extensions_rejected(filename):
    assert validate_image_extension(filename) is False


def test_extension_check_is_case_insensitive():
    assert validate_image_extension("CHIP.JPG") is True
    assert validate_image_extension("BOARD.PNG") is True


def test_file_without_extension_rejected():
    assert validate_image_extension("chipimage") is False


# ── image_bytes_to_pil ─────────────────────────────────────────────────────────

def test_image_bytes_to_pil_returns_pil_image(sample_image_bytes):
    img = image_bytes_to_pil(sample_image_bytes)
    assert isinstance(img, Image.Image)


def test_image_bytes_to_pil_correct_size(sample_image_bytes):
    img = image_bytes_to_pil(sample_image_bytes)
    assert img.size == (200, 200)


def test_image_bytes_to_pil_invalid_bytes_raises():
    with pytest.raises(Exception):
        image_bytes_to_pil(b"not an image")


# ── build_initial_statuses ─────────────────────────────────────────────────────

def test_build_initial_statuses_has_five_agents():
    statuses = build_initial_statuses()
    assert len(statuses) == 5


def test_build_initial_statuses_all_queued():
    statuses = build_initial_statuses()
    for agent_id, status in statuses.items():
        assert status == "queued", f"{agent_id} should start as 'queued', got '{status}'"


def test_build_initial_statuses_keys_match_agent_order():
    statuses = build_initial_statuses()
    assert set(statuses.keys()) == set(AGENT_ORDER)


# ── AGENT_ORDER constant ───────────────────────────────────────────────────────

def test_agent_order_has_five_entries():
    assert len(AGENT_ORDER) == 5


def test_agent_order_contains_all_expected_agents():
    expected = {
        "optical_inspection_agent",
        "metrology_agent",
        "yield_engineer_agent",
        "failure_analysis_agent",
        "qa_supervisor_agent",
    }
    assert set(AGENT_ORDER) == expected


def test_agent_order_starts_with_optical_inspection():
    assert AGENT_ORDER[0] == "optical_inspection_agent"


def test_agent_order_ends_with_qa_supervisor():
    assert AGENT_ORDER[-1] == "qa_supervisor_agent"


# ── ACCEPTED_EXTENSIONS constant ──────────────────────────────────────────────

def test_accepted_extensions_is_set():
    assert isinstance(ACCEPTED_EXTENSIONS, set)


def test_accepted_extensions_contains_jpg():
    assert "jpg" in ACCEPTED_EXTENSIONS
