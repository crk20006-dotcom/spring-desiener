

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import requests

st.set_page_config(
    page_title="AI-Assisted Spring Designer",
    page_icon="⚙️",
    layout="wide"
)

st.title("AI-Assisted Spring Designer")
st.caption("Python for Scientific Computing in Mechanical Engineering")
st.write("Calculate spring stiffness, deflection, spring index, and estimated shear stress.")

st.subheader("1. Spring Design Inputs")

col1, col2 = st.columns(2)

with col1:
    wire_d = st.number_input(
        "Wire diameter (mm)", min_value=0.1, value=5.0, step=0.5
    )
    mean_d = st.number_input(
        "Mean coil diameter (mm)", min_value=0.2, value=40.0, step=1.0
    )
    coils = st.number_input(
        "Number of active coils", min_value=1.0, value=8.0, step=1.0
    )

with col2:
    load = st.number_input(
        "Applied load (N)", min_value=0.0, value=100.0, step=10.0
    )
    shear_modulus = st.number_input(
        "Shear modulus (GPa)", min_value=1.0, value=79.3, step=1.0
    )

if st.button("Calculate Spring Parameters", type="primary"):
    if mean_d <= wire_d:
        st.error("Mean coil diameter must be greater than wire diameter.")
    else:
        # Convert input values to SI units
        d = wire_d / 1000.0
        D = mean_d / 1000.0
        G = shear_modulus * 1e9

        # Calculate spring index
        C = D / d

        if C <= 1.0:
            st.error("Spring index must be greater than 1.")
        else:
            # Ideal spring stiffness (N/m)
            k = G * d**4 / (8.0 * D**3 * coils)

            # Deflection (m)
            deflection_m = load / k

            # Wahl correction factor
            Kw = ((4.0 * C - 1.0) / (4.0 * C - 4.0)) + 0.615 / C

            # Estimated corrected wire shear stress (Pa)
            tau_pa = Kw * 8.0 * load * D / (np.pi * d**3)

            deflection_mm = deflection_m * 1000.0
            tau_mpa = tau_pa / 1e6

            st.subheader("2. Calculated Results")
            a, b, c = st.columns(3)
            a.metric("Spring stiffness", f"{k:.2f} N/m")
            b.metric("Deflection", f"{deflection_mm:.3f} mm")
            c.metric("Spring index", f"{C:.2f}")

            a, b = st.columns(2)
            a.metric("Wahl factor", f"{Kw:.3f}")
            b.metric("Estimated shear stress", f"{tau_mpa:.2f} MPa")

            if C < 4.0 or C > 12.0:
                st.warning(
                    "Spring index is outside the commonly used preliminary "
                    "range of 4 to 12. Review the design."
                )

            st.subheader("3. Load–Deflection Graph")
            loads = np.linspace(0.0, max(load, 1.0), 100)
            deflections = (loads / k) * 1000.0

            fig, ax = plt.subplots(figsize=(8, 4))
            ax.plot(deflections, loads, linewidth=2)
            ax.set_xlabel("Deflection (mm)")
            ax.set_ylabel("Load (N)")
            ax.set_title("Ideal Spring Load–Deflection Curve")
            ax.grid(True, alpha=0.3)
            st.pyplot(fig)
            plt.close(fig)

            st.subheader("4. Engineering Interpretation")
            st.write(
                f"For an applied load of {load:.2f} N, the ideal model "
                f"predicts a deflection of {deflection_mm:.3f} mm."
            )
            st.write(
                f"The estimated corrected wire shear stress is {tau_mpa:.2f} MPa."
            )

            st.info(
                "Educational model only. Fatigue life, buckling, solid height, "
                "end effects, material strength, and allowable stress are not "
                "yet checked. Verify the design against an appropriate "
                "engineering reference before practical use."
            )

st.divider()
st.caption("Educational prototype | Local AI assistant will be added later.")


# Local AI Mechanical Engineering Assistant
st.divider()
st.subheader("5. Local AI Mechanical Engineering Assistant")
st.caption("Powered by Ollama and Qwen2.5-Coder 7B. Runs locally.")

question = st.text_area(
    "Ask a mechanical engineering question",
    placeholder="Example: Explain Hooke's law and give an example."
)

if st.button("Ask Groq AI"):
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
                    "model": "llama-3.3-70b-versatile",
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
            st.markdown("### Groq AI Answer")
            st.write(answer)

        except Exception as error:
            st.error(f"AI request failed: {error}")
st.write(response.text if "response" in locals() else "No response received.")
#6.spring simulation
st.subheader("6. Spring Simulation")

st.write("Adjust the applied load to see how the spring deflects.")

sim_load = st.slider(
    "Simulation Load (N)",
    min_value=0.0,
    max_value=1000.0,
    value=100.0,
    step=10.0
)

d = wire_d / 1000.0
D = mean_d / 1000.0
G = shear_modulus * 1e9

if mean_d > wire_d and D > 0 and d > 0 and coils > 0:
    sim_k = G * d**4 / (8.0 * D**3 * coils)
    sim_deflection = (sim_load / sim_k) * 1000.0
    st.metric("Spring Deflection", f"{sim_deflection:.2f} mm")
    # Visual spring simulation
    spring_length = max(2.0, 5.0 - (sim_load / 1000.0) * 2.0)
    turns = 8

    spring_x = [0.0]
    spring_y = [0.0]

    for i in range(1, turns * 2 + 1):
        spring_x.append(0.3 if i % 2 else -0.3)
        spring_y.append(spring_length * i / (turns * 2))

    spring_x.append(0.0)
    spring_y.append(spring_length)

    fig, ax = plt.subplots(figsize=(3, 4))
    ax.plot(spring_x, spring_y, linewidth=2)
    ax.set_xlim(-0.8, 0.8)
    ax.set_ylim(-0.3, 5.5)
    ax.set_title("Spring Compression")
    ax.set_ylabel("Relative Spring Length")
    ax.set_xticks([])
    ax.grid(True, alpha=0.3)

    st.pyplot(fig)
    plt.close(fig)
    # Live load-deflection graph
    loads = np.linspace(0, 1000, 50)
    deflections = (loads / sim_k) * 1000

    fig2, ax2 = plt.subplots(figsize=(7, 3))
    ax2.plot(loads, deflections, linewidth=2)
    ax2.scatter([sim_load], [sim_deflection], s=60)
    ax2.set_title("Load vs Spring Deflection")
    ax2.set_xlabel("Load (N)")
    ax2.set_ylabel("Deflection (mm)")
    ax2.grid(True, alpha=0.3)

    st.pyplot(fig2)
    plt.close(fig2)
else:
    st.warning("Please enter valid spring design values.")


# 7. PDF Report Download

def create_spring_pdf():
    import io
    from reportlab.pdfgen import canvas

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer)

    pdf.setTitle("Spring Design Report")
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(50, 790, "Spring Design Report")

    pdf.setFont("Helvetica", 11)
    pdf.drawString(50, 750, "AI-Assisted Spring Designer")
    pdf.drawString(50, 720, f"Wire Diameter: {wire_d} mm")
    pdf.drawString(50, 700, f"Mean Coil Diameter: {mean_d} mm")
    pdf.drawString(50, 680, f"Active Coils: {coils}")
    pdf.drawString(50, 660, f"Applied Load: {load} N")
    pdf.drawString(50, 640, f"Shear Modulus: {shear_modulus} GPa")

    pdf.drawString(50, 600, "Note: Verify all calculations and design")
    pdf.drawString(50, 580, "safety before manufacturing or using the spring.")

    pdf.save()
    buffer.seek(0)
    return buffer.getvalue()


st.subheader("7. Download PDF Report")

pdf_data = create_spring_pdf()

st.download_button(
    label="Download Spring Design Report (PDF)",
    data=pdf_data,
    file_name="spring_design_report.pdf",
    mime="application/pdf"
)








