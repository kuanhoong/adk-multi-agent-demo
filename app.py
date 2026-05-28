"""
Agentic QC Inspector — Streamlit UI

Layout:   T10
Runner:   T11 (runner.py)
Display:  T12 (result cards + verdict banner)
"""
import io
import json

import streamlit as st
from PIL import Image

# ── Constants ──────────────────────────────────────────────────────────────────

ACCEPTED_EXTENSIONS = {"jpg", "jpeg", "png", "bmp"}

VERDICT_COLORS = {
    "PASS": "#00C851",
    "FAIL": "#ff4444",
    "MRB":  "#ffbb33",
}

VERDICT_LABELS = {
    "PASS": "PASS — Ship As-Is",
    "FAIL": "FAIL — Scrap / Rework",
    "MRB":  "MRB — Material Review Board Hold",
}

AGENT_STATUS_ICONS = {
    "queued":  "⏳",
    "running": "🔄",
    "done":    "✅",
    "error":   "❌",
}

AGENT_DISPLAY_NAMES = {
    "optical_inspection_agent": "① Optical Inspection Agent  (AOI)",
    "metrology_agent":          "② Metrology Agent  (CMM)",
    "yield_engineer_agent":     "③ Yield Engineer Agent",
    "failure_analysis_agent":   "④ Failure Analysis Agent  (FA Lab)",
    "qa_supervisor_agent":      "⑤ QA Supervisor Agent",
}

AGENT_ORDER = [
    "optical_inspection_agent",
    "metrology_agent",
    "yield_engineer_agent",
    "failure_analysis_agent",
    "qa_supervisor_agent",
]

SEVERITY_COLORS = {
    "none":     "#00C851",
    "minor":    "#ffbb33",
    "major":    "#FF8800",
    "critical": "#ff4444",
}


# ── Pure utility functions — T10 (layout) ─────────────────────────────────────

def get_verdict_color(disposition: str) -> str:
    """Return hex colour string for a QA disposition value."""
    return VERDICT_COLORS.get(disposition, "#888888")


def get_verdict_label(disposition: str) -> str:
    """Return human-readable label for a QA disposition value."""
    return VERDICT_LABELS.get(disposition, disposition)


def get_agent_status_icon(status: str) -> str:
    """Return emoji icon for an agent pipeline status."""
    return AGENT_STATUS_ICONS.get(status, "⏳")


def validate_image_extension(filename: str) -> bool:
    """Return True if the filename has an accepted image extension."""
    if "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[-1].lower()
    return ext in ACCEPTED_EXTENSIONS


def image_bytes_to_pil(data: bytes) -> Image.Image:
    """Convert raw image bytes to a PIL Image."""
    return Image.open(io.BytesIO(data))


def build_initial_statuses() -> dict:
    """Return the initial pipeline status dict with all agents queued."""
    return {agent_id: "queued" for agent_id in AGENT_ORDER}


# ── Pure utility functions — T12 (display) ────────────────────────────────────

def format_confidence_float(value: float) -> str:
    """Format a 0.0–1.0 confidence float as a percentage string, e.g. '85.0%'."""
    return f"{float(value) * 100:.1f}%"


def get_severity_color(severity: str) -> str:
    """Return a hex colour for a defect severity level."""
    return SEVERITY_COLORS.get(severity.lower(), "#888888")


def summarise_defects(defects: list) -> str:
    """Return a short human-readable summary of a defect list."""
    if not defects:
        return "No defects detected"
    count = len(defects)
    severity_rank = ["none", "minor", "major", "critical"]
    noun = "defect" if count == 1 else "defects"
    # Support dict defects (test fixtures) and string defects (live API format)
    dict_severities = [
        d.get("severity", "none") for d in defects if isinstance(d, dict)
    ]
    if dict_severities:
        worst = max(
            dict_severities,
            key=lambda s: severity_rank.index(s.lower()) if s.lower() in severity_rank else 0,
        )
        return f"{count} {noun} — worst severity: {worst}"
    return f"{count} {noun} detected"


def format_bool_indicator(value: bool, true_label: str = "Yes", false_label: str = "No") -> str:
    """Format a boolean as a labelled string."""
    return true_label if value else false_label


def format_corrective_actions(actions: list) -> str:
    """Format a list of corrective actions as a bulleted string."""
    if not actions:
        return "None"
    return "\n".join(f"• {a}" for a in actions)


def build_json_report(session_state: dict) -> str:
    """Serialise full session state results to a formatted JSON string."""
    return json.dumps(session_state, indent=2, default=str)


# ── Streamlit rendering functions — T10 ───────────────────────────────────────

def render_header():
    st.markdown(
        """
        <h1 style='margin-bottom:0'>🔬 Agentic QC Inspector</h1>
        <p style='color:#888;margin-top:4px'>
        Powered by <strong>Google ADK</strong> + <strong>Gemini</strong> &nbsp;|&nbsp;
        Multi-Agent Manufacturing Quality Control &nbsp;|&nbsp;
        Manufacturing Quality Demo
        </p>
        <hr style='margin-top:8px;margin-bottom:16px'>
        """,
        unsafe_allow_html=True,
    )


def render_agent_pipeline(statuses: dict):
    """Render the live agent pipeline status panel."""
    st.subheader("Agent Pipeline")
    for agent_id in AGENT_ORDER:
        status = statuses.get(agent_id, "queued")
        icon = get_agent_status_icon(status)
        label = AGENT_DISPLAY_NAMES.get(agent_id, agent_id)
        color = "#00C851" if status == "done" else ("#ff4444" if status == "error" else "#ccc")
        st.markdown(
            f"<div style='padding:6px 0;color:{color}'>{icon} &nbsp; {label}</div>",
            unsafe_allow_html=True,
        )


def render_verdict_banner(disposition_data: dict):
    """Render the colour-coded final disposition banner."""
    disposition = disposition_data.get("disposition", "MRB")
    color = get_verdict_color(disposition)
    label = get_verdict_label(disposition)
    confidence = disposition_data.get("confidence_pct", 0)
    action = disposition_data.get("mandatory_action", "")
    rationale = disposition_data.get("disposition_rationale", "")

    st.markdown(
        f"""
        <div style='background:{color};padding:24px;border-radius:12px;text-align:center;margin:16px 0'>
            <h2 style='color:white;margin:0;font-size:1.8em'>{label}</h2>
            <p style='color:white;margin:8px 0 0;font-size:1.1em'>Confidence: <strong>{confidence}%</strong></p>
            <p style='color:white;margin:6px 0 0'>{action}</p>
            <p style='color:rgba(255,255,255,0.85);margin:4px 0 0;font-size:0.9em'>{rationale}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    findings = disposition_data.get("critical_findings", [])
    if findings:
        st.markdown("**Critical Findings:**")
        for f in findings:
            st.markdown(f"- {f}")


# ── Streamlit rendering functions — T12 ───────────────────────────────────────

def render_aoi_card(aoi: dict):
    """Render an expandable card for AOI inspection results."""
    defect_summary = summarise_defects(aoi.get("defects", []))
    severity = aoi.get("severity_level", "none")
    sev_color = get_severity_color(severity)

    with st.expander(f"① AOI Report — {aoi.get('component_type', 'Component')} | {defect_summary}", expanded=True):
        c1, c2, c3 = st.columns(3)
        c1.metric("Component Type", aoi.get("component_type", "—"))
        c2.metric("Part Family",    aoi.get("part_family", "—"))
        c3.metric("Defects Found",  aoi.get("defect_count", 0))

        c4, c5 = st.columns(2)
        c4.metric("Solder Quality", aoi.get("solder_quality", "—"))
        c5.metric("Contamination",  format_bool_indicator(aoi.get("contamination_found", False)))

        st.markdown(
            f"<span style='background:{sev_color};color:white;padding:2px 10px;"
            f"border-radius:12px;font-size:0.85em'>Overall Severity: {severity.upper()}</span>",
            unsafe_allow_html=True,
        )

        defects = aoi.get("defects", [])
        if defects:
            st.markdown("**Defects:**")
            for d in defects:
                if isinstance(d, dict):
                    st.markdown(
                        f"- **{d.get('type', '?')}** at {d.get('location', '?')} "
                        f"[{d.get('severity', '?')}] — {d.get('description', '')}"
                    )
                else:
                    st.markdown(f"- {d}")


def render_metrology_card(met: dict):
    """Render an expandable card for Metrology results."""
    status = "OK" if met.get("placement_accurate") and met.get("orientation_correct") else "ISSUES FOUND"
    with st.expander(f"② Metrology Report — {status}", expanded=False):
        c1, c2, c3 = st.columns(3)
        c1.metric("Placement Accurate",  format_bool_indicator(met.get("placement_accurate", False)))
        c2.metric("Orientation Correct", format_bool_indicator(met.get("orientation_correct", False)))
        c3.metric("Warpage Detected",    format_bool_indicator(met.get("warpage_detected", False), "Yes ⚠️", "No ✓"))

        sym = met.get("symmetry_score", 0.0)
        st.metric("Symmetry Score", f"{sym:.3f} / 1.000")

        anomalies = met.get("dimensional_anomalies", [])
        if anomalies:
            st.markdown("**Dimensional Anomalies:**")
            for a in anomalies:
                st.markdown(f"- {a}")
        else:
            st.success("No dimensional anomalies detected")

        if met.get("notes"):
            st.caption(met["notes"])


def render_yield_card(yld: dict):
    """Render an expandable card for Yield Engineering results."""
    impact = yld.get("yield_impact_estimate", "unknown")
    systemic = yld.get("systemic_risk", False)
    badge = "🔴 SYSTEMIC RISK" if systemic else "🟢 Isolated"
    with st.expander(f"③ Yield Engineering — Impact: {impact.upper()} | {badge}", expanded=False):
        c1, c2 = st.columns(2)
        c1.metric("Primary Defect Type", yld.get("defect_type", "—"))
        c2.metric("Process Stage",       yld.get("process_stage", "—"))

        c3, c4 = st.columns(2)
        c3.metric("Yield Impact",   impact.upper())
        c4.metric("Systemic Risk",  format_bool_indicator(systemic, "Yes — lot-wide", "No — isolated"))

        actions = yld.get("corrective_actions", [])
        if actions:
            st.markdown("**Corrective Actions:**")
            for a in actions:
                st.markdown(f"- {a}")


def render_fa_card(fa: dict):
    """Render an expandable card for Failure Analysis results."""
    mode = fa.get("failure_mode", "—")
    conf = format_confidence_float(fa.get("confidence", 0.0))
    with st.expander(f"④ Failure Analysis — {mode} | Confidence: {conf}", expanded=False):
        st.metric("Failure Mode", mode)
        st.metric("Confidence",   conf)
        st.markdown(f"**Root Cause:** {fa.get('root_cause', '—')}")
        st.metric(
            "Latent Field Risk",
            format_bool_indicator(fa.get("latent_risk", False), "Yes ⚠️ — field failure risk", "No ✓"),
        )
        actions = fa.get("recommended_actions", [])
        if actions:
            st.markdown("**CAPA Recommendations:**")
            for a in actions:
                st.markdown(f"- {a}")


def render_results_cards(session_state: dict):
    """Render all five agent result cards from session state."""
    if "aoi_report" in session_state:
        render_aoi_card(session_state["aoi_report"])
    if "metrology_report" in session_state:
        render_metrology_card(session_state["metrology_report"])
    if "yield_report" in session_state:
        render_yield_card(session_state["yield_report"])
    if "fa_report" in session_state:
        render_fa_card(session_state["fa_report"])


def render_placeholder_results():
    """Placeholder shown before analysis runs."""
    st.info("Upload a component image and click **▶ Run Analysis** to start the inspection pipeline.")


# ── Main app entry point ───────────────────────────────────────────────────────

def main():
    st.set_page_config(
        page_title="Agentic QC Inspector",
        page_icon="🔬",
        layout="wide",
    )

    render_header()

    left, right = st.columns([1, 2])

    # ── Left panel: upload + controls ─────────────────────────────────────────
    with left:
        st.subheader("Component Image")
        uploaded = st.file_uploader(
            "Upload a manufacturing component image",
            type=list(ACCEPTED_EXTENSIONS),
            help="Accepted formats: JPG, PNG, BMP",
        )

        if uploaded is not None:
            if not validate_image_extension(uploaded.name):
                st.error(f"Unsupported file type. Accepted: {', '.join(ACCEPTED_EXTENSIONS)}")
            else:
                image_bytes = uploaded.read()
                st.image(image_bytes, caption=uploaded.name, width="stretch")
                st.session_state["image_bytes"] = image_bytes
                st.session_state["image_name"] = uploaded.name
                st.session_state.pop("session_state_result", None)  # clear stale results

        run_disabled = "image_bytes" not in st.session_state
        if st.button("▶  Run Analysis", disabled=run_disabled, width="stretch", type="primary"):
            st.session_state["run_requested"] = True
            st.session_state["agent_statuses"] = build_initial_statuses()

    # ── Right panel: pipeline status + results ────────────────────────────────
    with right:
        statuses_placeholder = st.empty()
        results_placeholder  = st.empty()

        # Render current statuses
        with statuses_placeholder.container():
            render_agent_pipeline(st.session_state.get("agent_statuses", build_initial_statuses()))

        st.divider()

        # Run the pipeline if requested
        if st.session_state.pop("run_requested", False):
            from runner import get_mime_type, run_inspection  # late import to avoid startup cost

            image_bytes = st.session_state["image_bytes"]
            image_name  = st.session_state.get("image_name", "component.jpg")
            mime_type   = get_mime_type(image_name)

            def on_progress(agent_id: str, status: str):
                st.session_state["agent_statuses"][agent_id] = status
                with statuses_placeholder.container():
                    render_agent_pipeline(st.session_state["agent_statuses"])

            with st.spinner("Running QC inspection pipeline…"):
                try:
                    result = run_inspection(image_bytes, mime_type=mime_type, progress_callback=on_progress)
                    st.session_state["session_state_result"] = result
                    # Mark any remaining agents as done (in case events were missed)
                    for agent_id in AGENT_ORDER:
                        if st.session_state["agent_statuses"].get(agent_id) != "error":
                            st.session_state["agent_statuses"][agent_id] = "done"
                except RuntimeError as exc:
                    st.error(f"Pipeline error: {exc}")

            with statuses_placeholder.container():
                render_agent_pipeline(st.session_state.get("agent_statuses", build_initial_statuses()))

        # Render results if available
        result = st.session_state.get("session_state_result")
        if result:
            if "disposition" in result:
                render_verdict_banner(result["disposition"])

            render_results_cards(result)

            st.divider()
            report_json = build_json_report(result)
            st.download_button(
                label="⬇  Download Full QC Report (JSON)",
                data=report_json,
                file_name=f"qc_report_{st.session_state.get('image_name', 'report')}.json",
                mime="application/json",
                width="stretch",
            )
        else:
            render_placeholder_results()


if __name__ == "__main__":
    main()
