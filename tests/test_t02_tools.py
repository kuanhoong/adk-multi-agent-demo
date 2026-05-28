"""
tests/test_t02_tools.py — T02: Tools Layer

Each tool is tested for:
  - Valid inputs return a dict with all required schema keys
  - Return value types are correct (bool, int, float, list, str)
  - Invalid enum values raise ValueError with a descriptive message
  - Boundary values are handled correctly
"""
import pytest

from tools import (
    analyze_yield_impact,
    issue_qa_disposition,
    perform_failure_analysis,
    run_aoi_scan,
    run_metrology_check,
)


# ── run_aoi_scan ───────────────────────────────────────────────────────────────

class TestRunAoiScan:
    REQUIRED_KEYS = {
        "component_type", "part_family", "defects",
        "defect_count", "severity_level", "solder_quality", "contamination_found",
    }

    def _valid_args(self):
        return dict(
            component_type="IC Chip",
            part_family="Microcontroller",
            defects=[{"type": "crack", "location": "top-left", "severity": "minor", "description": "hairline"}],
            defect_count=1,
            severity_level="minor",
            solder_quality="good",
            contamination_found=False,
        )

    def test_returns_all_required_keys(self):
        result = run_aoi_scan(**self._valid_args())
        assert self.REQUIRED_KEYS == set(result.keys())

    def test_defect_count_derived_from_defects_list(self):
        args = self._valid_args()
        args["defect_count"] = 99
        result = run_aoi_scan(**args)
        assert result["defect_count"] == 1

    def test_no_defects_valid(self):
        args = self._valid_args()
        args["defects"] = []
        args["defect_count"] = 0
        args["severity_level"] = "none"
        result = run_aoi_scan(**args)
        assert result["defect_count"] == 0
        assert result["severity_level"] == "none"

    def test_all_valid_severity_levels(self):
        for level in ("none", "minor", "major", "critical"):
            args = self._valid_args()
            args["severity_level"] = level
            args["defects"] = [] if level == "none" else args["defects"]
            result = run_aoi_scan(**args)
            assert result["severity_level"] == level

    def test_all_valid_solder_quality_values(self):
        for quality in ("good", "acceptable", "poor", "N/A"):
            args = self._valid_args()
            args["solder_quality"] = quality
            result = run_aoi_scan(**args)
            assert result["solder_quality"] == quality

    def test_invalid_severity_raises_value_error(self):
        args = self._valid_args()
        args["severity_level"] = "catastrophic"
        with pytest.raises(ValueError, match="severity_level"):
            run_aoi_scan(**args)

    def test_invalid_solder_quality_raises_value_error(self):
        args = self._valid_args()
        args["solder_quality"] = "excellent"
        with pytest.raises(ValueError, match="solder_quality"):
            run_aoi_scan(**args)

    def test_contamination_found_is_bool(self):
        result = run_aoi_scan(**self._valid_args())
        assert isinstance(result["contamination_found"], bool)

    def test_defects_is_list(self):
        result = run_aoi_scan(**self._valid_args())
        assert isinstance(result["defects"], list)


# ── run_metrology_check ────────────────────────────────────────────────────────

class TestRunMetrologyCheck:
    REQUIRED_KEYS = {
        "placement_accurate", "orientation_correct", "symmetry_score",
        "dimensional_anomalies", "warpage_detected", "notes",
    }

    def _valid_args(self):
        return dict(
            placement_accurate=True,
            orientation_correct=True,
            symmetry_score=0.95,
            dimensional_anomalies=[],
            warpage_detected=False,
            notes="Within tolerance",
        )

    def test_returns_all_required_keys(self):
        result = run_metrology_check(**self._valid_args())
        assert self.REQUIRED_KEYS == set(result.keys())

    def test_symmetry_score_is_rounded_to_3dp(self):
        args = self._valid_args()
        args["symmetry_score"] = 0.123456789
        result = run_metrology_check(**args)
        assert result["symmetry_score"] == round(0.123456789, 3)

    def test_symmetry_score_boundary_zero(self):
        args = self._valid_args()
        args["symmetry_score"] = 0.0
        result = run_metrology_check(**args)
        assert result["symmetry_score"] == 0.0

    def test_symmetry_score_boundary_one(self):
        args = self._valid_args()
        args["symmetry_score"] = 1.0
        result = run_metrology_check(**args)
        assert result["symmetry_score"] == 1.0

    def test_symmetry_score_below_zero_raises(self):
        args = self._valid_args()
        args["symmetry_score"] = -0.01
        with pytest.raises(ValueError, match="symmetry_score"):
            run_metrology_check(**args)

    def test_symmetry_score_above_one_raises(self):
        args = self._valid_args()
        args["symmetry_score"] = 1.01
        with pytest.raises(ValueError, match="symmetry_score"):
            run_metrology_check(**args)

    def test_booleans_are_bool_type(self):
        result = run_metrology_check(**self._valid_args())
        assert isinstance(result["placement_accurate"], bool)
        assert isinstance(result["orientation_correct"], bool)
        assert isinstance(result["warpage_detected"], bool)

    def test_dimensional_anomalies_is_list(self):
        result = run_metrology_check(**self._valid_args())
        assert isinstance(result["dimensional_anomalies"], list)


# ── analyze_yield_impact ───────────────────────────────────────────────────────

class TestAnalyzeYieldImpact:
    REQUIRED_KEYS = {
        "defect_type", "process_stage", "systemic_risk",
        "yield_impact_estimate", "corrective_actions",
    }

    def _valid_args(self):
        return dict(
            defect_type="hairline crack",
            process_stage="handling",
            systemic_risk=False,
            yield_impact_estimate="low",
            corrective_actions=["Review handling procedures"],
        )

    def test_returns_all_required_keys(self):
        result = analyze_yield_impact(**self._valid_args())
        assert self.REQUIRED_KEYS == set(result.keys())

    def test_all_valid_process_stages(self):
        for stage in ("SMT", "reflow", "assembly", "handling", "incoming", "storage", "unknown"):
            args = self._valid_args()
            args["process_stage"] = stage
            result = analyze_yield_impact(**args)
            assert result["process_stage"] == stage

    def test_all_valid_yield_impact_estimates(self):
        for impact in ("low", "medium", "high"):
            args = self._valid_args()
            args["yield_impact_estimate"] = impact
            result = analyze_yield_impact(**args)
            assert result["yield_impact_estimate"] == impact

    def test_invalid_process_stage_raises(self):
        args = self._valid_args()
        args["process_stage"] = "shipping"
        with pytest.raises(ValueError, match="process_stage"):
            analyze_yield_impact(**args)

    def test_invalid_yield_impact_raises(self):
        args = self._valid_args()
        args["yield_impact_estimate"] = "critical"
        with pytest.raises(ValueError, match="yield_impact_estimate"):
            analyze_yield_impact(**args)

    def test_systemic_risk_is_bool(self):
        result = analyze_yield_impact(**self._valid_args())
        assert isinstance(result["systemic_risk"], bool)

    def test_corrective_actions_is_list(self):
        result = analyze_yield_impact(**self._valid_args())
        assert isinstance(result["corrective_actions"], list)


# ── perform_failure_analysis ───────────────────────────────────────────────────

class TestPerformFailureAnalysis:
    REQUIRED_KEYS = {
        "failure_mode", "root_cause", "confidence",
        "latent_risk", "recommended_actions",
    }

    def _valid_args(self):
        return dict(
            failure_mode="mechanical stress fracture",
            root_cause="Excessive pressure during handling",
            confidence=0.85,
            latent_risk=False,
            recommended_actions=["Retrain operators"],
        )

    def test_returns_all_required_keys(self):
        result = perform_failure_analysis(**self._valid_args())
        assert self.REQUIRED_KEYS == set(result.keys())

    def test_confidence_is_rounded_to_3dp(self):
        args = self._valid_args()
        args["confidence"] = 0.856789
        result = perform_failure_analysis(**args)
        assert result["confidence"] == round(0.856789, 3)

    def test_confidence_boundary_zero(self):
        args = self._valid_args()
        args["confidence"] = 0.0
        result = perform_failure_analysis(**args)
        assert result["confidence"] == 0.0

    def test_confidence_boundary_one(self):
        args = self._valid_args()
        args["confidence"] = 1.0
        result = perform_failure_analysis(**args)
        assert result["confidence"] == 1.0

    def test_confidence_below_zero_raises(self):
        args = self._valid_args()
        args["confidence"] = -0.01
        with pytest.raises(ValueError, match="confidence"):
            perform_failure_analysis(**args)

    def test_confidence_above_one_raises(self):
        args = self._valid_args()
        args["confidence"] = 1.01
        with pytest.raises(ValueError, match="confidence"):
            perform_failure_analysis(**args)

    def test_latent_risk_is_bool(self):
        result = perform_failure_analysis(**self._valid_args())
        assert isinstance(result["latent_risk"], bool)

    def test_recommended_actions_is_list(self):
        result = perform_failure_analysis(**self._valid_args())
        assert isinstance(result["recommended_actions"], list)


# ── issue_qa_disposition ───────────────────────────────────────────────────────

class TestIssueQaDisposition:
    REQUIRED_KEYS = {
        "disposition", "confidence_pct", "critical_findings",
        "mandatory_action", "disposition_rationale",
    }

    def _valid_args(self):
        return dict(
            disposition="PASS",
            confidence_pct=90,
            critical_findings=[],
            mandatory_action="Ship to customer",
            disposition_rationale="No defects found. Component meets all QA criteria.",
        )

    def test_returns_all_required_keys(self):
        result = issue_qa_disposition(**self._valid_args())
        assert self.REQUIRED_KEYS == set(result.keys())

    def test_all_three_dispositions_valid(self):
        for disposition in ("PASS", "FAIL", "MRB"):
            args = self._valid_args()
            args["disposition"] = disposition
            result = issue_qa_disposition(**args)
            assert result["disposition"] == disposition

    def test_invalid_disposition_raises(self):
        args = self._valid_args()
        args["disposition"] = "REVIEW"
        with pytest.raises(ValueError, match="disposition"):
            issue_qa_disposition(**args)

    def test_confidence_pct_boundary_zero(self):
        args = self._valid_args()
        args["confidence_pct"] = 0
        result = issue_qa_disposition(**args)
        assert result["confidence_pct"] == 0

    def test_confidence_pct_boundary_100(self):
        args = self._valid_args()
        args["confidence_pct"] = 100
        result = issue_qa_disposition(**args)
        assert result["confidence_pct"] == 100

    def test_confidence_pct_above_100_raises(self):
        args = self._valid_args()
        args["confidence_pct"] = 101
        with pytest.raises(ValueError, match="confidence_pct"):
            issue_qa_disposition(**args)

    def test_confidence_pct_below_zero_raises(self):
        args = self._valid_args()
        args["confidence_pct"] = -1
        with pytest.raises(ValueError, match="confidence_pct"):
            issue_qa_disposition(**args)

    def test_confidence_pct_is_int(self):
        result = issue_qa_disposition(**self._valid_args())
        assert isinstance(result["confidence_pct"], int)

    def test_critical_findings_is_list(self):
        result = issue_qa_disposition(**self._valid_args())
        assert isinstance(result["critical_findings"], list)
