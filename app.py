

import io
import numpy as np
import streamlit as st
import plotly.graph_objects as go
import requests
from reportlab.pdfgen import canvas

st.set_page_config(
    page_title="AI-Assisted Spring Designer",
    page_icon="⚙️",
    layout="wide",
)

st.title("AI-Assisted Spring Designer")
st.caption("Mechanical engineering design, visualization, and learning")
st.write(
    "Calculate spring parameters, explore load–deflection behavior, "
    "and visualize a helical compression spring in interactive 3D."
)

# -------------------------------------------------------------------
# 1. Inputs
# -------------------------------------------------------------------
st.subheader("1. Spring Design Inputs")

col1, col2 = st.columns(2)
with col1:
    wire_d = st.number_input(
        "Wire diameter (mm)", min_value=0.1, max_value=100.0,
        value=5.0, step=0.5
    )
    mean_d = st.number_input(
        "Mean coil diameter (mm)", min_value=0.2, max_value=2000.0,
        value=40.0, step=1.0
    )
    coils = st.number_input(
        "Number of active coils", min_value=1.0, max_value=100.0,
        value=8.0, step=1.0
    )
with col2:
    load = st.number_input(
        "Applied load (N)", min_value=0.0, max_value=1_000_000.0,
        value=100.0, step=10.0
    )
    shear_modulus = st.number_input(
        "Shear modulus (GPa)", min_value=1.0, max_value=300.0,
        value=79.3, step=1.0
    )

valid_design = mean_d > wire_d and wire_d > 0 and coils > 0 and shear_modulus > 0

if not valid_design:
    st.error("Enter valid values. Mean coil diameter must be greater than wire diameter.")
    st.stop()

# Calculations use SI units internally.
d = wire_d / 1000.0
D = mean_d / 1000.0
G = shear_modulus * 1e9
spring_index = D / d

if spring_index <= 1.0:
    st.error("Spring index must be greater than 1.")
    st.stop()

stiffness_n_m = G * d**4 / (8.0 * D**3 * coils)
deflection_mm = (load / stiffness_n_m) * 1000.0
wahl_factor = ((4.0 * spring_index - 1.0) / (4.0 * spring_index - 4.0)) + 0.615 / spring_index
shear_stress_mpa = (
    wahl_factor * 8.0 * load * D / (np.pi * d**3)
) / 1e6
stiffness_n_mm = stiffness_n_m / 1000.0

# A simple geometry-based free length estimate is used for visualization only.
# It is not a manufacturing recommendation.
estimated_free_length_mm = max(coils * wire_d * 2.2, coils * wire_d + 10.0)
estimated_solid_height_mm = coils * wire_d
available_travel_mm = max(0.0, estimated_free_length_mm - estimated_solid_height_mm)
visual_deflection_mm = min(deflection_mm, available_travel_mm)
estimated_loaded_length_mm = max(
    estimated_solid_height_mm,
    estimated_free_length_mm - visual_deflection_mm
)

# -------------------------------------------------------------------
# 2. Results
# -------------------------------------------------------------------
st.subheader("2. Calculated Results")
a, b, c = st.columns(3)
a.metric("Spring stiffness", f"{stiffness_n_mm:.3f} N/mm")
b.metric("Deflection at applied load", f"{deflection_mm:.3f} mm")
c.metric("Spring index", f"{spring_index:.2f}")

a, b = st.columns(2)
a.metric("Wahl factor", f"{wahl_factor:.3f}")
b.metric("Estimated shear stress", f"{shear_stress_mpa:.2f} MPa")

if spring_index < 4.0 or spring_index > 12.0:
    st.warning(
        "Spring index is outside the commonly used preliminary range of 4 to 12. "
        "Review the design against a suitable engineering reference."
    )
if deflection_mm > available_travel_mm:
    st.warning(
        "The calculated deflection exceeds the travel available in the illustrative "
        "spring geometry. The 3D display is capped at the estimated solid height; "
        "this is a visualization limit, not a validated solid-height calculation."
    )

st.info(
    "Educational preliminary model. The estimated free length and solid height used "
    "for visualization are assumptions. Fatigue, buckling, end effects, tolerances, "
    "material strength, surge, and allowable stress are not fully checked. Verify "
    "designs against a trusted engineering reference before manufacture or use."
)

# -------------------------------------------------------------------
# 3. Improved load–deflection graph
# -------------------------------------------------------------------
st.subheader("3. Load–Deflection Graph")
st.caption(
    "The marker identifies your selected applied load and calculated deflection. "
    "Guide lines help you read the coordinates."
)

max_graph_load = max(load * 1.25, 100.0)
loads = np.linspace(0.0, max_graph_load, 160)
deflections = loads / stiffness_n_mm

fig_graph = go.Figure()
fig_graph.add_trace(
    go.Scatter(
        x=deflections,
        y=loads,
        mode="lines",
        name="Ideal linear response",
        line=dict(width=3),
        hovertemplate="Deflection: %{x:.3f} mm<br>Load: %{y:.2f} N<extra></extra>",
    )
)
fig_graph.add_trace(
    go.Scatter(
        x=[deflection_mm],
        y=[load],
        mode="markers",
        name="Selected operating point",
        marker=dict(size=13, symbol="circle"),
        hovertemplate=(
            "Selected point<br>Deflection: %{x:.3f} mm"
            "<br>Load: %{y:.2f} N<extra></extra>"
        ),
    )
)
fig_graph.add_trace(
    go.Scatter(
        x=[deflection_mm, deflection_mm],
        y=[0, load],
        mode="lines",
        name="Deflection guide",
        line=dict(dash="dash", width=1.5),
        hoverinfo="skip",
    )
)
fig_graph.add_trace(
    go.Scatter(
        x=[0, deflection_mm],
        y=[load, load],
        mode="lines",
        name="Load guide",
        line=dict(dash="dash", width=1.5),
        hoverinfo="skip",
    )
)
fig_graph.update_layout(
    title="Spring Response at the Selected Load",
    xaxis_title="Deflection (mm)",
    yaxis_title="Load (N)",
    hovermode="closest",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
    margin=dict(l=20, r=20, t=80, b=20),
    height=480,
)
fig_graph.update_xaxes(showgrid=True, zeroline=True)
fig_graph.update_yaxes(showgrid=True, zeroline=True)
st.plotly_chart(fig_graph, use_container_width=True)

g1, g2, g3 = st.columns(3)
g1.metric("Selected load", f"{load:.2f} N")
g2.metric("Corresponding deflection", f"{deflection_mm:.3f} mm")
g3.metric("Stiffness", f"{stiffness_n_mm:.3f} N/mm")

with st.expander("Understand this graph"):
    st.write(
        "For the ideal linear spring model, load = stiffness × deflection. "
        "The slope of the load-versus-deflection curve is the spring stiffness. "
        "The graph is linear because this calculation assumes constant stiffness; "
        "it does not model nonlinear material behavior, coil contact, or plastic deformation."
    )

# -------------------------------------------------------------------
# 4. Interactive 3D spring visualization and simulation
# -------------------------------------------------------------------
st.subheader("4. Interactive 3D Spring Simulation")
st.write(
    "Use the slider to explore the spring at different loads. Drag to rotate the "
    "3D view and use the controls to zoom. This is a geometry-based visualization "
    "driven by the ideal spring calculation, not a finite-element simulation."
)

sim_load = st.slider(
    "Simulation load (N)",
    min_value=0.0,
    max_value=float(max(1000.0, load * 2.0)),
    value=float(min(load, max(1000.0, load * 2.0))),
    step=max(1.0, float(max(1000.0, load * 2.0)) / 100.0),
    key="simulation_load",
)

sim_deflection_mm = (sim_load / stiffness_n_mm) if stiffness_n_mm > 0 else 0.0
sim_visual_deflection_mm = min(sim_deflection_mm, available_travel_mm)
sim_length_mm = max(
    estimated_solid_height_mm,
    estimated_free_length_mm - sim_visual_deflection_mm,
)

# Generate a helical centreline, then plot it as a 3D tube-like line.
theta = np.linspace(0.0, 2.0 * np.pi * coils, max(500, int(coils * 100)))
radius_mm = mean_d / 2.0
pitch_mm = sim_length_mm / coils
x = radius_mm * np.cos(theta)
y = radius_mm * np.sin(theta)
z = (theta / (2.0 * np.pi * coils)) * sim_length_mm

fig_3d = go.Figure()
fig_3d.add_trace(
    go.Scatter3d(
        x=x, y=y, z=z,
        mode="lines",
        name="Spring wire centreline",
        line=dict(width=8),
        hovertemplate="X: %{x:.2f} mm<br>Y: %{y:.2f} mm<br>Z: %{z:.2f} mm<extra></extra>",
    )
)
# End reference circles improve the visual sense of the spring's extent.
circle_t = np.linspace(0, 2 * np.pi, 100)
for z_end, label in [(0.0, "Lower reference"), (sim_length_mm, "Upper reference")]:
    fig_3d.add_trace(
        go.Scatter3d(
            x=radius_mm * np.cos(circle_t),
            y=radius_mm * np.sin(circle_t),
            z=np.full_like(circle_t, z_end),
            mode="lines",
            name=label,
            line=dict(width=3, dash="dash"),
            hoverinfo="skip",
            showlegend=True,
        )
    )

fig_3d.update_layout(
    title=f"Helical Spring — simulated load {sim_load:.1f} N",
    scene=dict(
        xaxis_title="X (mm)",
        yaxis_title="Y (mm)",
        zaxis_title="Height (mm)",
        aspectmode="data",
        camera=dict(eye=dict(x=1.6, y=1.6, z=1.2)),
    ),
    margin=dict(l=0, r=0, t=60, b=0),
    height=600,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
)
st.plotly_chart(fig_3d, use_container_width=True)

s1, s2, s3 = st.columns(3)
s1.metric("Simulation load", f"{sim_load:.1f} N")
s2.metric("Calculated deflection", f"{sim_deflection_mm:.3f} mm")
s3.metric("Displayed spring height", f"{sim_length_mm:.2f} mm")

if sim_deflection_mm > available_travel_mm:
    st.warning(
        "The theoretical deflection exceeds the visualization's estimated available "
        "travel. The displayed spring height is capped for visual clarity."
    )

# -------------------------------------------------------------------
# 5. Engineering interpretation
# -------------------------------------------------------------------
st.subheader("5. Engineering Interpretation")
st.write(
    f"At an applied load of {load:.2f} N, the ideal linear model predicts "
    f"{deflection_mm:.3f} mm deflection with stiffness {stiffness_n_mm:.3f} N/mm."
)
st.write(
    f"The estimated Wahl-corrected wire shear stress is {shear_stress_mpa:.2f} MPa. "
    "This value should be compared with an appropriate material-specific allowable "
    "stress before drawing any safety conclusion."
)

# -------------------------------------------------------------------
# 6. Existing online AI chatbot (Groq) — retained
# -------------------------------------------------------------------
st.divider()
st.subheader("6. Mechanical Engineering AI Assistant")
st.caption("Online AI powered by your configured Groq API key.")

question = st.text_area(
    "Ask a mechanical engineering question",
    placeholder="Example: Explain Hooke's law and give an example.",
    key="engineering_question",
)

if st.button("Ask Groq AI", type="primary"):
    if not question.strip():
        st.warning("Please enter a question first.")
    else:
        try:
            api_key = st.secrets["GROQ_API_KEY"]
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "openai/gpt-oss-120b",
                    "messages": [
                        {
                            "role": "system",
                            "content": (
                                "You are a helpful mechanical engineering tutor. "
                                "Explain concepts clearly, show equations where useful, "
                                "and mention when engineering calculations need verification."
                            ),
                        },
                        {"role": "user", "content": question},
                    ],
                    "temperature": 0.3,
                },
                timeout=60,
            )
            response.raise_for_status()
            answer = response.json()["choices"][0]["message"]["content"]
            st.markdown("### AI Answer")
            st.write(answer)
        except requests.HTTPError:
            status = response.status_code if "response" in locals() else "unknown"
            st.error(f"The AI provider returned an HTTP error (status: {status}). Please try again later.")
        except KeyError as error:
            if str(error) == "'GROQ_API_KEY'":
                st.error("GROQ_API_KEY is missing from Streamlit Secrets.")
            else:
                st.error("The AI response did not contain the expected fields.")
        except requests.RequestException:
            st.error("Could not reach the AI provider. Check the connection and try again.")
        except Exception:
            st.error("The AI request failed. Check your Streamlit Secrets and try again.")

# -------------------------------------------------------------------
# 7. PDF report download — retained and expanded with key results
# -------------------------------------------------------------------
def create_spring_pdf():
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer)
    pdf.setTitle("Spring Design Report")

    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(50, 790, "Spring Design Report")
    pdf.setFont("Helvetica", 11)
    report_lines = [
        "AI-Assisted Spring Designer",
        "",
        f"Wire diameter: {wire_d:.3f} mm",
        f"Mean coil diameter: {mean_d:.3f} mm",
        f"Active coils: {coils:.2f}",
        f"Applied load: {load:.3f} N",
        f"Shear modulus: {shear_modulus:.3f} GPa",
        "",
        f"Spring stiffness: {stiffness_n_mm:.5f} N/mm",
        f"Deflection: {deflection_mm:.5f} mm",
        f"Spring index: {spring_index:.5f}",
        f"Wahl factor: {wahl_factor:.5f}",
        f"Estimated corrected shear stress: {shear_stress_mpa:.5f} MPa",
        "",
        "Model assumptions and limitations:",
        "- Ideal linear spring stiffness model.",
        "- Visualization length is estimated, not a manufacturing specification.",
        "- Fatigue, buckling, end effects, tolerances and material allowable stress",
        "  are not fully evaluated.",
        "",
        "Verify all calculations and safety requirements against trusted engineering",
        "references before manufacturing or practical use.",
    ]
    y = 750
    for line in report_lines:
        if y < 60:
            pdf.showPage()
            pdf.setFont("Helvetica", 11)
            y = 790
        pdf.drawString(50, y, line)
        y -= 20
    pdf.save()
    buffer.seek(0)
    return buffer.getvalue()

st.subheader("7. Download PDF Report")
pdf_data = create_spring_pdf()
st.download_button(
    label="Download Spring Design Report (PDF)",
    data=pdf_data,
    file_name="spring_design_report.pdf",
    mime="application/pdf",
)
st.caption("Educational prototype. Verify engineering calculations before practical use.")

