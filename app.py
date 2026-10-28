


from __future__ import annotations

import io
import math
from typing import Iterable

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

st.set_page_config(
    page_title="MechLab Studio | Spring Designer",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Shared styling and helpers ----------
st.markdown(
    """
    <style>
      .block-container {padding-top: 1.25rem; padding-bottom: 2rem; max-width: 1200px;}
      .hero { padding: 1.35rem 1.4rem; border-radius: 18px; margin-bottom: 1rem;
              background: linear-gradient(120deg, rgba(30,88,140,.18), rgba(31,158,137,.10));
              border: 1px solid rgba(120,140,160,.28); }
      .hero h1 { margin: 0 0 .35rem 0; }
      .hero p { margin: 0; font-size: 1rem; opacity: .88; }
      .module-card { padding: 1rem; border: 1px solid rgba(120,140,160,.3); border-radius: 14px;
                     min-height: 112px; margin-bottom: .35rem; }
      .module-card h3 { margin: 0 0 .45rem 0; font-size: 1.08rem; }
      .module-card p { margin: 0; opacity: .82; font-size: .93rem; }
      [data-testid="stMetric"] { border: 1px solid rgba(120,140,160,.22); padding: .7rem .8rem;
                                  border-radius: 12px; }
      @media (max-width: 640px) {
        .block-container { padding-left: .8rem; padding-right: .8rem; padding-top: .8rem; }
        .hero { padding: 1rem; }
      }
    </style>
    """,
    unsafe_allow_html=True,
)

MODULES = {
    "Spring Design": ("🌀", "Spring calculations, load–deflection curve, and a 3D helical spring view."),
    "Gear & Machine Design": ("⚙️", "Ideal spur-gear ratio, speed, torque, pitch circles, and report exports."),
    "Thermal & Welding": ("🌡️", "Explore an illustrative 2D heat field and center-point trend."),
    "Robotics & Kinematics": ("🦾", "Visualize a two-link planar robot arm and calculate its end position."),
    "Materials & Stress–Strain": ("📈", "Explore an idealized tensile stress–strain curve."),
    "AI Engineering Tutor": ("🤖", "Ask the existing online Groq-powered mechanical engineering tutor."),
}


def page_header(title: str, subtitle: str) -> None:
    st.markdown(f"## {title}")
    st.caption(subtitle)
    st.divider()


def metric_row(items: list[tuple[str, str, str]]) -> None:
    cols = st.columns(len(items))
    for col, (label, value, help_text) in zip(cols, items):
        col.metric(label, value, help=help_text)


def chart_layout(fig: go.Figure, height: int = 420) -> go.Figure:
    fig.update_layout(
        autosize=True,
        height=height,
        margin=dict(l=12, r=12, t=58, b=12),
        font=dict(size=12),
        title=dict(x=0.02, xanchor="left", y=0.97),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def _make_pdf(title: str, lines: Iterable[str]) -> bytes | None:
    """Create a compact PDF report when ReportLab is installed; otherwise return None."""
    try:
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_LEFT
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

        output = io.BytesIO()
        doc = SimpleDocTemplate(
            output, pagesize=letter,
            rightMargin=0.65 * inch, leftMargin=0.65 * inch,
            topMargin=0.65 * inch, bottomMargin=0.65 * inch,
        )
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name="ReportBody", parent=styles["BodyText"], alignment=TA_LEFT,
                                  leading=15, spaceAfter=7, textColor=colors.HexColor("#243244")))
        story = [Paragraph(title, styles["Title"]), Spacer(1, 12)]
        for line in lines:
            safe = (str(line).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
            story.append(Paragraph(safe, styles["ReportBody"]))
        doc.build(story)
        return output.getvalue()
    except ImportError:
        return None


def downloads(filename: str, df: pd.DataFrame, report_title: str, report_lines: list[str]) -> None:
    left, right = st.columns(2)
    with left:
        st.download_button(
            "⬇️ Download CSV data", data=df.to_csv(index=False).encode("utf-8"),
            file_name=f"{filename}.csv", mime="text/csv", use_container_width=True,
        )
    pdf_bytes = _make_pdf(report_title, report_lines)
    with right:
        if pdf_bytes:
            st.download_button(
                "⬇️ Download PDF report", data=pdf_bytes,
                file_name=f"{filename}_report.pdf", mime="application/pdf", use_container_width=True,
            )
        else:
            st.caption("PDF export requires ReportLab. CSV export is available now.")


# ---------- Spring design ----------
def spring_module() -> None:
    page_header("🌀 Spring Design & 3D Simulation",
                "Helical compression spring estimates with one shared applied-load value across the metrics and graphs.")
    with st.expander("Spring geometry and material inputs", expanded=True):
        a, b, c = st.columns(3)
        wire_d = a.number_input("Wire diameter d (mm)", min_value=0.5, max_value=30.0, value=4.0, step=0.5, key="sp_d")
        mean_d = b.number_input("Mean coil diameter D (mm)", min_value=2.0, max_value=300.0, value=25.0, step=1.0, key="sp_D")
        active_n = c.number_input("Active coils n", min_value=1.0, max_value=100.0, value=8.0, step=1.0, key="sp_n")
        shear_g = a.number_input("Shear modulus G (MPa)", min_value=1000.0, max_value=150000.0, value=79300.0, step=1000.0, key="sp_G")
        load_range = b.number_input("Maximum load shown on graph (N)", min_value=100.0, max_value=10000.0, value=1000.0, step=100.0, key="sp_max_load")
        st.caption("Educational estimate for a round-wire helical spring. Check fatigue, buckling, solid height, material limits and applicable standards before real design use.")

    if mean_d <= wire_d:
        st.error("Mean coil diameter must be greater than the wire diameter. Increase D before using the results.")
        return

    spring_index = mean_d / wire_d
    if spring_index <= 1.0:
        st.error("Spring index must be greater than 1. Check the geometry inputs.")
        return

    # Single source of truth for the selected load. This exact value drives every metric and marker below.
    applied_load = st.slider(
        "Applied load (N)", min_value=0.0, max_value=float(load_range),
        value=min(100.0, float(load_range)), step=max(1.0, float(load_range) / 1000.0), key="spring_applied_load",
    )

    stiffness = (shear_g * wire_d ** 4) / (8.0 * mean_d ** 3 * active_n)  # N/mm
    deflection = applied_load / stiffness if stiffness > 0 else 0.0
    wahl = ((4.0 * spring_index - 1.0) / (4.0 * spring_index - 4.0)) + (0.615 / spring_index)
    shear_stress = wahl * (8.0 * applied_load * mean_d) / (math.pi * wire_d ** 3)  # MPa
    free_length_est = max(wire_d * (active_n + 2.0), 1.2 * active_n * wire_d)

    metric_row([
        ("Spring rate", f"{stiffness:.3f} N/mm", "k = G d⁴ / (8 D³ n)"),
        ("Deflection", f"{deflection:.2f} mm", f"At selected load {applied_load:.1f} N"),
        ("Corrected shear stress", f"{shear_stress:.1f} MPa", "Includes Wahl factor"),
        ("Spring index", f"{spring_index:.2f}", "C = D / d"),
    ])
    st.caption(f"Wahl factor: {wahl:.3f} · Illustrative free-length estimate: {free_length_est:.1f} mm · Applied load: {applied_load:.1f} N")

    tab_curve, tab_3d = st.tabs(["Load–deflection curve", "3D spring view"])
    with tab_curve:
        loads = np.linspace(0.0, float(load_range), 151)
        deflections = loads / stiffness
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=deflections, y=loads, mode="lines", name="Linear spring response", line=dict(width=3)))
        fig.add_trace(go.Scatter(x=[deflection], y=[applied_load], mode="markers", name="Selected load",
                                 marker=dict(size=13, symbol="diamond", line=dict(width=1))))
        fig.update_layout(title="Load vs. deflection", xaxis_title="Deflection (mm)", yaxis_title="Load (N)",
                          xaxis=dict(rangemode="tozero"), yaxis=dict(range=[0, float(load_range) * 1.04]))
        st.plotly_chart(chart_layout(fig, 390), use_container_width=True,
                         config={"responsive": True, "displayModeBar": False, "scrollZoom": False})
        st.caption("The diamond and the deflection metric use the same selected-load control above.")
    with tab_3d:
        turns = max(3.0, float(active_n) + 1.0)
        theta = np.linspace(0.0, 2.0 * math.pi * turns, 700)
        pitch = free_length_est / turns
        radius = mean_d / 2.0
        x = radius * np.cos(theta)
        y = radius * np.sin(theta)
        z = (pitch / (2.0 * math.pi)) * theta
        spring_fig = go.Figure(go.Scatter3d(x=x, y=y, z=z, mode="lines", line=dict(width=7), name="Helical spring"))
        spring_fig.update_layout(
            title="Helical spring geometry (schematic)",
            scene=dict(xaxis_title="X (mm)", yaxis_title="Y (mm)", zaxis_title="Height (mm)",
                       aspectmode="data", camera=dict(eye=dict(x=1.7, y=1.8, z=1.25))),
            margin=dict(l=0, r=0, t=50, b=0), height=460,
        )
        st.plotly_chart(spring_fig, use_container_width=True,
                         config={"responsive": True, "displayModeBar": True, "scrollZoom": False})
        st.caption("Schematic geometry only; the coil shape is not a deformation/contact simulation.")

    loads_export = np.linspace(0.0, float(load_range), 151)
    df = pd.DataFrame({
        "load_N": loads_export,
        "deflection_mm": loads_export / stiffness,
        "wire_diameter_mm": wire_d,
        "mean_coil_diameter_mm": mean_d,
        "active_coils": active_n,
        "shear_modulus_MPa": shear_g,
    })
    downloads("spring_design", df, "Spring Design Report", [
        "MechLab Studio — Spring Design Report",
        f"Wire diameter: {wire_d:.3f} mm",
        f"Mean coil diameter: {mean_d:.3f} mm",
        f"Active coils: {active_n:.2f}",
        f"Shear modulus: {shear_g:.2f} MPa",
        f"Spring index: {spring_index:.4f}",
        f"Spring rate: {stiffness:.5f} N/mm",
        f"Applied load: {applied_load:.3f} N",
        f"Estimated deflection at applied load: {deflection:.4f} mm",
        f"Wahl factor: {wahl:.5f}",
        f"Corrected shear stress estimate: {shear_stress:.3f} MPa",
        "Educational preliminary calculation; fatigue, buckling, solid height, end conditions and material allowable stress are not verified.",
    ])
    st.warning("This preliminary model assumes linear elastic behavior. It does not certify a real spring design or check fatigue, buckling, coil clash or manufacturing limits.")


# ---------- Gear & machine design ----------
def gear_module() -> None:
    page_header("⚙️ Gear & Machine Design", "A focused workspace for external spur-gear pairs and ideal gear-train calculations.")
    with st.expander("Gear inputs", expanded=True):
        a, b, c = st.columns(3)
        z1 = a.number_input("Driver teeth", 8, 300, 20, key="g_z1")
        z2 = b.number_input("Driven teeth", 8, 600, 60, key="g_z2")
        rpm = a.number_input("Driver speed (rpm)", 1.0, 100000.0, 1200.0, key="g_rpm")
        module_mm = c.number_input("Module (mm)", 0.25, 50.0, 2.0, key="g_mod")
        power = b.number_input("Input power (kW)", 0.01, 10000.0, 2.0, key="g_power")
        eff = c.number_input("Estimated efficiency (%)", 1.0, 100.0, 95.0, key="g_eff")
    ratio = z2 / z1
    out_rpm = rpm / ratio
    out_power = power * eff / 100.0
    tin = 9550.0 * power / rpm
    tout = 9550.0 * out_power / out_rpm
    d1, d2 = module_mm * z1, module_mm * z2
    center = (d1 + d2) / 2.0
    metric_row([
        ("Gear ratio", f"{ratio:.3f}:1", "Driven teeth / driver teeth"),
        ("Output speed", f"{out_rpm:.1f} rpm", "Ideal speed ratio"),
        ("Output torque", f"{tout:.2f} N·m", "Includes assumed efficiency"),
        ("Centre distance", f"{center:.2f} mm", "Standard external spur gears"),
    ])
    st.caption(f"Driver pitch diameter: {d1:.2f} mm · Driven pitch diameter: {d2:.2f} mm · Input torque: {tin:.2f} N·m")
    t = np.linspace(0, 2 * np.pi, 160)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=d1 / 2 * np.cos(t), y=d1 / 2 * np.sin(t), mode="lines", name=f"Driver ({z1} teeth)"))
    fig.add_trace(go.Scatter(x=center + d2 / 2 * np.cos(t), y=d2 / 2 * np.sin(t), mode="lines", name=f"Driven ({z2} teeth)"))
    fig.update_layout(title="Pitch-circle layout (schematic)", xaxis_title="X (mm)", yaxis_title="Y (mm)",
                      yaxis=dict(scaleanchor="x", scaleratio=1))
    st.plotly_chart(chart_layout(fig, 390), use_container_width=True, config={"responsive": True, "displayModeBar": False})
    df = pd.DataFrame([{"driver_teeth": z1, "driven_teeth": z2, "gear_ratio": ratio,
                        "input_speed_rpm": rpm, "output_speed_rpm": out_rpm, "input_power_kW": power,
                        "assumed_efficiency_pct": eff, "output_power_kW": out_power, "input_torque_Nm": tin,
                        "output_torque_Nm": tout, "module_mm": module_mm, "driver_pitch_diameter_mm": d1,
                        "driven_pitch_diameter_mm": d2, "centre_distance_mm": center}])
    downloads("gear_analysis", df, "Gear Pair Analysis Report", [
        f"Driver teeth: {z1}", f"Driven teeth: {z2}", f"Ratio: {ratio:.4f}:1",
        f"Input speed: {rpm:.2f} rpm", f"Output speed: {out_rpm:.2f} rpm",
        f"Input power: {power:.3f} kW", f"Assumed efficiency: {eff:.2f}%",
        f"Output torque: {tout:.3f} N·m", f"Centre distance: {center:.3f} mm",
        "Schematic pitch circles only; tooth profile/contact ratio/bending and pitting strength are not analysed.",
    ])
    st.warning("Preliminary ideal gear-pair tool. Tooth strength, contact ratio, backlash, lubrication, bearing loads and applicable standards are not assessed.")


# ---------- Thermal & welding ----------
def thermal_module() -> None:
    page_header("🌡️ Thermal & Welding Heat Simulation", "A simplified heat-source visualization for learning, not a welding procedure predictor.")
    a, b, c = st.columns(3)
    q = a.number_input("Heat input power (W)", 10.0, 100000.0, 1200.0, key="th_q")
    alpha = b.number_input("Thermal diffusivity (mm²/s)", 0.01, 200.0, 12.0, key="th_a")
    duration = c.number_input("Heating time (s)", 1.0, 3600.0, 60.0, key="th_t")
    eta = st.slider("Effective heat fraction", 0.1, 1.0, 0.75, 0.05, key="th_eta")
    xlim = st.slider("Field half-width (mm)", 10, 200, 60, key="th_x")
    xs = np.linspace(-xlim, xlim, 81)
    ys = np.linspace(-xlim, xlim, 81)
    X, Y = np.meshgrid(xs, ys)
    r2 = X ** 2 + Y ** 2
    spread = max(2.0, math.sqrt(4.0 * alpha * duration))
    amp = q * eta / (4.0 * math.pi * max(alpha, 0.01) * duration)
    temp = 20.0 + amp * np.exp(-r2 / (spread ** 2)) * duration / 100.0
    peak = float(temp.max())
    metric_row([
        ("Peak illustrative temperature", f"{peak:.1f} °C", "Model-dependent estimate"),
        ("Diffusion length scale", f"{spread:.2f} mm", "sqrt(4 α t)"),
        ("Effective heat input", f"{q * eta:.1f} W", "Power × heat fraction"),
    ])
    fig = go.Figure(go.Contour(x=xs, y=ys, z=temp, colorscale="Inferno", colorbar=dict(title="°C"),
                               contours=dict(showlabels=True)))
    fig.update_layout(title="Illustrative 2D heat field", xaxis_title="Distance x (mm)", yaxis_title="Distance y (mm)")
    st.plotly_chart(chart_layout(fig, 430), use_container_width=True, config={"responsive": True, "displayModeBar": False})
    times = np.linspace(1.0, duration, 80)
    center_t = 20.0 + (q * eta / (4.0 * math.pi * alpha * times)) * times / 100.0
    ft = go.Figure(go.Scatter(x=times, y=center_t, mode="lines", name="Center-point trend"))
    ft.update_layout(title="Simplified center-point trend", xaxis_title="Time (s)", yaxis_title="Illustrative temperature (°C)")
    st.plotly_chart(chart_layout(ft, 320), use_container_width=True, config={"responsive": True, "displayModeBar": False})
    df = pd.DataFrame({"x_mm": X.ravel(), "y_mm": Y.ravel(), "illustrative_temperature_C": temp.ravel()})
    downloads("thermal_simulation", df, "Thermal Simulation Report", [
        f"Input power: {q:.2f} W", f"Effective heat fraction: {eta:.3f}",
        f"Thermal diffusivity: {alpha:.4f} mm²/s", f"Heating time: {duration:.2f} s",
        f"Illustrative peak temperature: {peak:.3f} °C",
        "The Gaussian field is a teaching visualization, not a validated weld heat-transfer model.",
    ])
    st.warning("This simplified Gaussian visualization is not calibrated to a real weld, boundary conditions, material properties or process. Do not use it to select welding parameters or certify safety.")


# ---------- Robotics ----------
def robotics_module() -> None:
    page_header("🦾 Robotics & Kinematics", "Two-link planar robot arm: endpoint position from joint angles, with pose export.")
    a, b, c = st.columns(3)
    L1 = a.number_input("Link 1 length (mm)", 10.0, 2000.0, 300.0, key="r_l1")
    L2 = b.number_input("Link 2 length (mm)", 10.0, 2000.0, 220.0, key="r_l2")
    t1 = c.slider("Joint 1 angle (°)", -180, 180, 35, key="r_t1")
    t2 = st.slider("Joint 2 relative angle (°)", -180, 180, 55, key="r_t2")
    r1, r2 = math.radians(t1), math.radians(t1 + t2)
    x1, y1 = L1 * math.cos(r1), L1 * math.sin(r1)
    x2, y2 = x1 + L2 * math.cos(r2), y1 + L2 * math.sin(r2)
    reach = math.hypot(x2, y2)
    metric_row([
        ("End-effector X", f"{x2:.2f} mm", "Base origin at (0, 0)"),
        ("End-effector Y", f"{y2:.2f} mm", "Planar vertical coordinate"),
        ("Reach from base", f"{reach:.2f} mm", "Endpoint distance"),
    ])
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[0, x1, x2], y=[0, y1, y2], mode="lines+markers+text",
                             text=["Base", "Joint 1", "Tool tip"], textposition="top center",
                             line=dict(width=7), marker=dict(size=11), name="Robot arm"))
    fig.add_shape(type="circle", x0=-(L1 + L2), y0=-(L1 + L2), x1=L1 + L2, y1=L1 + L2,
                  line=dict(dash="dot", color="gray"))
    fig.update_layout(title="Planar robot arm pose", xaxis_title="X (mm)", yaxis_title="Y (mm)",
                      xaxis=dict(range=[-(L1 + L2) * 1.1, (L1 + L2) * 1.1]),
                      yaxis=dict(range=[-(L1 + L2) * 1.1, (L1 + L2) * 1.1], scaleanchor="x", scaleratio=1))
    st.plotly_chart(chart_layout(fig, 430), use_container_width=True, config={"responsive": True, "displayModeBar": False})
    df = pd.DataFrame([{"link1_mm": L1, "link2_mm": L2, "joint1_deg": t1,
                        "joint2_relative_deg": t2, "joint2_absolute_deg": t1 + t2,
                        "end_effector_x_mm": x2, "end_effector_y_mm": y2, "reach_mm": reach}])
    downloads("robot_kinematics", df, "Robot Kinematics Report", [
        f"Link 1: {L1:.3f} mm", f"Link 2: {L2:.3f} mm", f"Joint 1 angle: {t1} degrees",
        f"Joint 2 relative angle: {t2} degrees", f"End effector X: {x2:.3f} mm",
        f"End effector Y: {y2:.3f} mm", f"Reach: {reach:.3f} mm",
        "Planar forward kinematics only; dynamics, collision and inverse-kinematics constraints are not included.",
    ])
    st.info("Uses planar forward kinematics. Joint limits, collision detection, dynamics and actuator sizing are not included.")


# ---------- Materials ----------
def materials_module() -> None:
    page_header("📈 Materials & Stress–Strain", "An idealized tensile stress–strain curve with elastic modulus and an illustrative post-yield response.")
    a, b, c = st.columns(3)
    E = a.number_input("Young's modulus (GPa)", 1.0, 500.0, 200.0, key="m_E")
    ys = b.number_input("Yield strength (MPa)", 1.0, 3000.0, 250.0, key="m_yield")
    uts = c.number_input("Ultimate strength (MPa)", 1.0, 5000.0, 450.0, key="m_uts")
    elong = st.slider("Illustrative strain range (%)", 0.2, 30.0, 5.0, 0.2, key="m_strain")
    if uts < ys:
        st.warning("Ultimate strength is below yield strength. Adjust the inputs for a typical ductile-metal illustration.")
    strain = np.linspace(0.0, elong / 100.0, 250)
    e_mpa = E * 1000.0
    ey = ys / e_mpa
    stress = np.where(strain <= ey, e_mpa * strain,
                      ys + (uts - ys) * np.minimum((strain - ey) / max(float(strain.max() - ey), 1e-9), 1.0))
    sel_pct = st.slider("Selected engineering strain (%)", 0.0, float(elong), min(float(elong), 1.0), 0.1, key="m_selstrain")
    sel = sel_pct / 100.0
    selected_stress = float(np.interp(sel, strain, stress))
    metric_row([
        ("Young's modulus", f"{E:.2f} GPa", "Elastic slope"),
        ("Yield strain estimate", f"{ey * 100:.3f}%", "Yield strength / modulus"),
        ("Selected stress", f"{selected_stress:.2f} MPa", f"At {sel_pct:.2f}% strain"),
    ])
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=strain * 100, y=stress, mode="lines", name="Idealized material curve", line=dict(width=3)))
    fig.add_trace(go.Scatter(x=[sel_pct], y=[selected_stress], mode="markers", name="Selected strain",
                             marker=dict(size=12, symbol="diamond")))
    fig.add_vline(x=ey * 100, line_dash="dash", annotation_text="Estimated yield strain")
    fig.update_layout(title="Engineering stress–strain curve (idealized)", xaxis_title="Engineering strain (%)",
                      yaxis_title="Engineering stress (MPa)", xaxis=dict(range=[0, float(elong)]))
    st.plotly_chart(chart_layout(fig, 410), use_container_width=True, config={"responsive": True, "displayModeBar": False})
    df = pd.DataFrame({"engineering_strain_fraction": strain, "engineering_strain_pct": strain * 100,
                       "illustrative_stress_MPa": stress})
    downloads("materials_stress_strain", df, "Materials Stress Strain Report", [
        f"Young's modulus: {E:.3f} GPa", f"Yield strength: {ys:.3f} MPa",
        f"Ultimate strength input: {uts:.3f} MPa", f"Estimated yield strain: {ey * 100:.5f}%",
        f"Selected strain: {sel_pct:.4f}%", f"Illustrative selected stress: {selected_stress:.3f} MPa",
        "Curve is a simplified teaching approximation, not experimental material data or a constitutive law.",
    ])
    st.warning("The post-yield curve is an illustrative interpolation, not a validated material model. Use certified material data for engineering design.")


# ---------- Existing online AI tutor ----------
def tutor_module() -> None:
    page_header("🤖 AI Engineering Tutor", "Existing online Groq chatbot. The API key is read securely from Streamlit Secrets.")
    question = st.text_area("Your engineering question",
                            placeholder="e.g., Explain Hooke's law and show a worked example.", height=130,
                            key="tutor_question")
    if st.button("Ask AI tutor", type="primary", use_container_width=True):
        if not question.strip():
            st.warning("Enter a question first.")
        else:
            try:
                key = st.secrets["GROQ_API_KEY"]
                response = requests.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                    json={"model": "openai/gpt-oss-120b", "messages": [
                        {"role": "system", "content": (
                            "You are a careful mechanical engineering tutor. Explain clearly, show equations and units, "
                            "state assumptions, and warn when results require validation against a trusted engineering "
                            "standard. Do not claim a preliminary model certifies a real design.")},
                        {"role": "user", "content": question},
                    ], "temperature": 0.3},
                    timeout=60,
                )
                response.raise_for_status()
                st.session_state.chat_answer = response.json()["choices"][0]["message"]["content"]
            except KeyError:
                st.error("GROQ_API_KEY is missing from Streamlit Secrets. Add it in the app's Secrets settings; never paste the key into this code.")
            except requests.HTTPError as exc:
                status = exc.response.status_code if exc.response is not None else "unknown"
                st.error(f"Groq returned HTTP {status}. Check provider/model availability and try again.")
            except requests.RequestException:
                st.error("Could not connect to Groq. Check connectivity or provider availability and try again.")
            except (ValueError, TypeError, IndexError, KeyError):
                st.error("The AI response had an unexpected format. Please try again.")
    answer = st.session_state.get("chat_answer", "")
    if answer:
        st.markdown("### Answer")
        st.markdown(answer)
    st.caption("This module uses the configured online API; it is not a local model. Use is subject to provider availability and limits.")


# ---------- Navigation ----------
def set_module(module_name: str) -> None:
    # Called as a Streamlit callback before the next full rerun.
    st.session_state.active_module = module_name
    st.session_state.nav_radio = module_name


st.session_state.setdefault("active_module", "Home")
st.session_state.setdefault("chat_answer", "")
st.session_state.setdefault("nav_radio", "Home")

with st.sidebar:
    st.markdown("# ⚙️ MechLab Studio")
    st.caption("Mechanical engineering workbench")
    choices = ["Home"] + list(MODULES.keys())
    if st.session_state.active_module not in choices:
        st.session_state.active_module = "Home"
    if st.session_state.nav_radio not in choices:
        st.session_state.nav_radio = st.session_state.active_module
    selected = st.radio(
        "Navigation", choices,
        index=choices.index(st.session_state.active_module),
        format_func=lambda x: "🏠  Home" if x == "Home" else f"{MODULES[x][0]}  {x}",
        key="nav_radio",
    )
    st.session_state.active_module = selected
    st.divider()
    st.caption("Built with Python · Streamlit · Plotly")

active = st.session_state.active_module
if active == "Home":
    st.markdown(
        '<div class="hero"><h1>MechLab Studio</h1><p>One engineering module at a time. Calculate, simulate, inspect results, and export your readings.</p></div>',
        unsafe_allow_html=True,
    )
    st.markdown("### Choose a workspace")
    st.write("Select a module. Only that workspace opens, keeping its calculations, graphs, simulation and downloads together.")
    names = list(MODULES.keys())
    for start in range(0, len(names), 2):
        cols = st.columns(2, gap="large")
        for col, name in zip(cols, names[start:start + 2]):
            emoji, desc = MODULES[name]
            with col:
                st.markdown(f'<div class="module-card"><h3>{emoji} {name}</h3><p>{desc}</p></div>', unsafe_allow_html=True)
                st.button(
                    f"Open {name} →", key=f"open_{name}", use_container_width=True,
                    on_click=set_module, args=(name,),
                )
    st.divider()
    st.markdown("### Project notes")
    c1, c2, c3 = st.columns(3)
    c1.metric("Workspaces", "6", "One active workspace at a time")
    c2.metric("Export formats", "CSV + PDF", "PDF requires ReportLab")
    c3.metric("AI connection", "Groq API", "Key stored in Streamlit Secrets")
    st.caption("Engineering results are educational preliminary estimates. Validate against authoritative references and applicable standards before real-world use.")
elif active == "Spring Design":
    spring_module()
elif active == "Gear & Machine Design":
    gear_module()
elif active == "Thermal & Welding":
    thermal_module()
elif active == "Robotics & Kinematics":
    robotics_module()
elif active == "Materials & Stress–Strain":
    materials_module()
elif active == "AI Engineering Tutor":
    tutor_module()
