"""
tools.py — Tool functions for the Agentic QC Inspector

Each tool is called by an LLM agent to record its structured analysis findings.
The LLM performs visual reasoning on the image; the tool validates and formats
the output into a typed schema that downstream agents can consume.
"""
from typing import List

VALID_SEVERITY_LEVELS = {"none", "minor", "major", "critical"}
VALID_SOLDER_QUALITY = {"good", "acceptable", "poor", "N/A"}
VALID_DISPOSITIONS = {"PASS", "FAIL", "MRB"}
VALID_PROCESS_STAGES = {
    "SMT", "reflow", "assembly", "handling", "incoming", "storage", "unknown"
}
VALID_YIELD_IMPACTS = {"low", "medium", "high"}


def run_aoi_scan(
    component_type: str,
    part_family: str,
    defects: List[str],
    defect_count: int,
    severity_level: str,
    solder_quality: str,
    contamination_found: bool,
) -> dict:
    """
    Record Automated Optical Inspection (AOI) findings for a manufacturing component.
    Call this tool after visually analysing the component image.

    Args:
        component_type: Type of component, e.g. 'IC Chip', 'PCB', 'Connector', 'Capacitor'
        part_family: Component sub-family, e.g. 'Microcontroller', 'MOSFET', 'BGA package'
        defects: List of defect description strings. Each string must follow the format:
                 "<type> at <location> [<severity>]: <description>"
                 Example: "hairline crack at top-left corner [major]: stress fracture visible"
        defect_count: Total number of defects found
        severity_level: Overall worst-case severity — one of: none, minor, major, critical
        solder_quality: Solder joint assessment — one of: good, acceptable, poor, N/A
        contamination_found: True if foreign material or contamination is visible

    Returns:
        Structured AOI inspection record dict
    """
    if severity_level not in VALID_SEVERITY_LEVELS:
        raise ValueError(
            f"severity_level must be one of {VALID_SEVERITY_LEVELS}, got '{severity_level}'"
        )
    if solder_quality not in VALID_SOLDER_QUALITY:
        raise ValueError(
            f"solder_quality must be one of {VALID_SOLDER_QUALITY}, got '{solder_quality}'"
        )

    return {
        "component_type": str(component_type),
        "part_family": str(part_family),
        "defects": list(defects),
        "defect_count": len(defects),
        "severity_level": severity_level,
        "solder_quality": solder_quality,
        "contamination_found": bool(contamination_found),
    }


def run_metrology_check(
    placement_accurate: bool,
    orientation_correct: bool,
    symmetry_score: float,
    dimensional_anomalies: List[str],
    warpage_detected: bool,
    notes: str,
) -> dict:
    """
    Record dimensional verification and metrology findings for a manufacturing component.
    Call this tool after assessing the geometric properties of the component image.

    Args:
        placement_accurate: True if component placement appears within acceptable tolerance
        orientation_correct: True if component is correctly oriented (no rotation/flip errors)
        symmetry_score: Visual symmetry score between 0.0 (asymmetric) and 1.0 (perfect)
        dimensional_anomalies: List of observed dimensional issues, e.g. ['pin misalignment']
        warpage_detected: True if board or component warpage is visible
        notes: Additional metrology observations or measurement notes

    Returns:
        Structured metrology inspection record dict
    """
    if not (0.0 <= float(symmetry_score) <= 1.0):
        raise ValueError(
            f"symmetry_score must be between 0.0 and 1.0, got {symmetry_score}"
        )

    return {
        "placement_accurate": bool(placement_accurate),
        "orientation_correct": bool(orientation_correct),
        "symmetry_score": round(float(symmetry_score), 3),
        "dimensional_anomalies": list(dimensional_anomalies),
        "warpage_detected": bool(warpage_detected),
        "notes": str(notes),
    }


def analyze_yield_impact(
    defect_type: str,
    process_stage: str,
    systemic_risk: bool,
    yield_impact_estimate: str,
    corrective_actions: List[str],
) -> dict:
    """
    Record yield engineering analysis — assess the production impact of observed defects.
    Call this tool after correlating defect patterns to process yield implications.

    Args:
        defect_type: Primary defect category observed, e.g. 'solder void', 'hairline crack'
        process_stage: Manufacturing stage where defect likely originated —
                       one of: SMT, reflow, assembly, handling, incoming, storage, unknown
        systemic_risk: True if defect pattern suggests a lot-wide or process-wide issue
        yield_impact_estimate: Estimated yield impact — one of: low, medium, high
        corrective_actions: List of recommended process corrective actions

    Returns:
        Structured yield impact analysis dict
    """
    if process_stage not in VALID_PROCESS_STAGES:
        raise ValueError(
            f"process_stage must be one of {VALID_PROCESS_STAGES}, got '{process_stage}'"
        )
    if yield_impact_estimate not in VALID_YIELD_IMPACTS:
        raise ValueError(
            f"yield_impact_estimate must be one of {VALID_YIELD_IMPACTS}, got '{yield_impact_estimate}'"
        )

    return {
        "defect_type": str(defect_type),
        "process_stage": process_stage,
        "systemic_risk": bool(systemic_risk),
        "yield_impact_estimate": yield_impact_estimate,
        "corrective_actions": list(corrective_actions),
    }


def perform_failure_analysis(
    failure_mode: str,
    root_cause: str,
    confidence: float,
    latent_risk: bool,
    recommended_actions: List[str],
) -> dict:
    """
    Record failure analysis findings — classify the failure mode and root cause.
    Call this tool after determining the failure mechanism and its origin.

    Args:
        failure_mode: Specific failure mode, e.g. 'cold solder joint', 'ESD damage',
                      'fatigue crack', 'delamination', 'whisker growth'
        root_cause: Root cause hypothesis, e.g. 'insufficient reflow temperature'
        confidence: Confidence in the root cause hypothesis, between 0.0 and 1.0
        latent_risk: True if the defect poses a latent field failure risk
        recommended_actions: List of corrective and preventive actions for the process team

    Returns:
        Structured failure analysis report dict
    """
    if not (0.0 <= float(confidence) <= 1.0):
        raise ValueError(
            f"confidence must be between 0.0 and 1.0, got {confidence}"
        )

    return {
        "failure_mode": str(failure_mode),
        "root_cause": str(root_cause),
        "confidence": round(float(confidence), 3),
        "latent_risk": bool(latent_risk),
        "recommended_actions": list(recommended_actions),
    }


def issue_qa_disposition(
    disposition: str,
    confidence_pct: int,
    critical_findings: List[str],
    mandatory_action: str,
    disposition_rationale: str,
) -> dict:
    """
    Issue the final QA disposition for the inspected component.
    Call this tool after reviewing all prior inspection reports to render the quality verdict.

    Args:
        disposition: Final quality decision — one of:
                     PASS  → use as-is, meets all quality standards
                     FAIL  → scrap or rework required, do not ship
                     MRB   → Material Review Board hold, engineering review required
        confidence_pct: Confidence in the disposition, as an integer percentage 0–100
        critical_findings: List of the most critical issues driving the disposition
        mandatory_action: The single mandatory next step, e.g. 'Ship to customer'
        disposition_rationale: Brief explanation of the disposition decision

    Returns:
        Structured QA disposition record dict
    """
    if disposition not in VALID_DISPOSITIONS:
        raise ValueError(
            f"disposition must be one of {VALID_DISPOSITIONS}, got '{disposition}'"
        )
    if not (0 <= int(confidence_pct) <= 100):
        raise ValueError(
            f"confidence_pct must be between 0 and 100, got {confidence_pct}"
        )

    return {
        "disposition": disposition,
        "confidence_pct": int(confidence_pct),
        "critical_findings": list(critical_findings),
        "mandatory_action": str(mandatory_action),
        "disposition_rationale": str(disposition_rationale),
    }
