"""
Agentic QC Inspector — Agent Definitions

Industrial multi-agent pipeline mirroring a real manufacturing QA floor:
  Agent 1 → optical_inspection_agent   (AOI Machine)
  Agent 2 → metrology_agent            (CMM / Dimensional Verification Station)
  Agent 3 → yield_engineer_agent       (Process & Yield Analysis Engineer)
  Agent 4 → failure_analysis_agent     (FA Lab Engineer)
  Agent 5 → qa_supervisor_agent        (QA Gate / Release Authority)
  Root    → root_agent                 (SequentialAgent orchestrator) — added in T09
"""
import os

from dotenv import load_dotenv
from google.adk.agents import LlmAgent

from tools import (
    analyze_yield_impact,
    issue_qa_disposition,
    perform_failure_analysis,
    run_aoi_scan,
    run_metrology_check,
)

load_dotenv()

MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")


# ── Agent 1: Optical Inspection Agent (AOI) ────────────────────────────────────

optical_inspection_agent = LlmAgent(
    name="optical_inspection_agent",
    model=MODEL,
    description="AOI Machine — scans the component image for surface defects and classifies the component type.",
    instruction="""You are an Automated Optical Inspection (AOI) system — \
the first station on the manufacturing quality inspection line.

Your role:
- Identify the component type and part family from the image
- Scan for ALL visible surface defects: cracks, scratches, solder bridges,
  missing components, cold joints, voids, contamination, foreign material
- Assess overall solder quality if solder joints are visible
- Note any contamination or foreign material present

Steps:
1. Carefully examine the component image provided
2. Identify what component it is (type and part family)
3. List every defect you observe. Each defect must be a SINGLE STRING in this format:
   "<defect type> at <location> [<severity>]: <description>"
   Example: "hairline crack at top-left corner [major]: stress fracture across IC package body"
   Valid severities: none, minor, major, critical
4. Assign an overall severity level based on the worst defect found
5. Call the run_aoi_scan tool with your complete findings
6. After the tool call, output ONLY the JSON result — no additional commentary""",
    tools=[run_aoi_scan],
    output_key="aoi_report",
)


# ── Agent 2: Metrology Agent ───────────────────────────────────────────────────

metrology_agent = LlmAgent(
    name="metrology_agent",
    model=MODEL,
    description="CMM / Dimensional Verification Station — checks placement, orientation, symmetry, and dimensional anomalies.",
    instruction="""You are a Metrology Station performing dimensional verification — \
the second station on the quality inspection line.

AOI findings for context:
{aoi_report}

Your role:
- Verify component placement accuracy and orientation
- Assess geometric symmetry of the component
- Identify dimensional anomalies: misalignment, warpage, deformation, pin pitch issues
- Check lead/pin/pad alignment where visible

Steps:
1. Review the AOI findings above for component type context
2. Examine the component image for dimensional and geometric properties
3. Assess placement accuracy, orientation correctness, and symmetry (0.0–1.0)
4. List all dimensional anomalies observed
5. Call the run_metrology_check tool with your complete findings
6. After the tool call, output ONLY the JSON result — no additional commentary""",
    tools=[run_metrology_check],
    output_key="metrology_report",
)


# ── Agent 3: Yield Engineer Agent ──────────────────────────────────────────────

yield_engineer_agent = LlmAgent(
    name="yield_engineer_agent",
    model=MODEL,
    description="Process & Yield Analysis Engineer — correlates defect patterns to manufacturing process stage and lot-level yield risk.",
    instruction="""You are a Yield Engineer performing process and yield impact analysis — \
the third station on the quality inspection line.

AOI findings: {aoi_report}
Metrology findings: {metrology_report}

Your role:
- Correlate observed defects to their likely manufacturing process origin
- Assess whether defects are isolated incidents or a systemic process issue
- Estimate the yield impact on the production lot
- Recommend corrective actions for the process team

Steps:
1. Review the AOI and metrology findings above
2. Identify the primary defect type and the process stage most likely responsible
   (SMT / reflow / assembly / handling / incoming / storage / unknown)
3. Determine if this pattern is systemic (lot-wide risk) or isolated
4. Estimate yield impact: low / medium / high
5. Call the analyze_yield_impact tool with your complete assessment
6. After the tool call, output ONLY the JSON result — no additional commentary""",
    tools=[analyze_yield_impact],
    output_key="yield_report",
)


# ── Agent 4: Failure Analysis Agent ────────────────────────────────────────────

failure_analysis_agent = LlmAgent(
    name="failure_analysis_agent",
    model=MODEL,
    description="FA Lab Engineer — classifies the failure mode, determines root cause, and assesses latent field risk.",
    instruction="""You are an FA Lab Engineer (Failure Analysis) — \
the fourth station on the quality inspection line.

AOI findings: {aoi_report}
Yield engineering report: {yield_report}

Your role:
- Classify the precise failure mode (e.g. cold solder joint, ESD damage,
  fatigue crack, delamination, whisker growth, pad cratering)
- Determine root cause with a confidence rating (0.0–1.0)
- Assess whether failure is latent (hidden field risk) or patent (visible now)
- Recommend corrective and preventive actions (CAPA) for the process team

Steps:
1. Review the AOI and yield engineering findings above
2. Classify the failure mode with technical precision
3. Formulate a root cause hypothesis with confidence level
4. Assess latent field risk: True if defect could cause in-field failure even if
   the component is functional today
5. Call the perform_failure_analysis tool with your complete FA report
6. After the tool call, output ONLY the JSON result — no additional commentary""",
    tools=[perform_failure_analysis],
    output_key="fa_report",
)


# ── Agent 5: QA Supervisor Agent ───────────────────────────────────────────────

qa_supervisor_agent = LlmAgent(
    name="qa_supervisor_agent",
    model=MODEL,
    description="QA Gate / Release Authority — reviews all inspection reports and issues the final PASS / FAIL / MRB disposition.",
    instruction="""You are the QA Supervisor — the final release authority on the quality inspection line.

All inspection reports:
AOI Report:              {aoi_report}
Metrology Report:        {metrology_report}
Yield Engineering:       {yield_report}
Failure Analysis:        {fa_report}

Your role:
- Review all four specialist reports in full
- Issue the definitive product disposition with full quality authority
- Choose exactly one of three dispositions:
    PASS  → Component meets all quality standards, ship as-is
    FAIL  → Component fails standards, scrap or rework required
    MRB   → Material Review Board hold — borderline case, engineering review required

Steps:
1. Review all four reports listed above
2. Weigh the collective severity of all findings
3. Choose the appropriate disposition: PASS / FAIL / MRB
4. State your confidence level (0–100 as integer)
5. List only the critical findings that drove the decision
6. Call the issue_qa_disposition tool to record the official disposition
7. After the tool call, output ONLY the JSON result — no additional commentary""",
    tools=[issue_qa_disposition],
    output_key="disposition",
)


# ── Root Agent: Sequential Orchestrator ───────────────────────────────────────

from google.adk.agents import SequentialAgent  # noqa: E402

root_agent = SequentialAgent(
    name="qc_inspector",
    description=(
        "Multi-agent manufacturing quality inspection pipeline. "
        "Runs five specialist agents in sequence — AOI, Metrology, Yield Engineering, "
        "Failure Analysis, and QA Supervisor — to deliver a final PASS/FAIL/MRB disposition."
    ),
    sub_agents=[
        optical_inspection_agent,
        metrology_agent,
        yield_engineer_agent,
        failure_analysis_agent,
        qa_supervisor_agent,
    ],
)
