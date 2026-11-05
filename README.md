# MechLab Studio Pro — Mechanical Engineering Workbench

A mobile-friendly Streamlit learning workbench with deterministic calculation kernels, interactive plots/simulations, an AI engineering tutor, concise one-page PDF summaries and full-detail CSV exports.

## Workspaces

1. **Spring Design** — helical compression spring rate, deflection, Wahl-corrected shear stress, available travel and a 3D helix view.
2. **Gear & Machine Design** — ideal external spur-gear ratio, output speed/torque and schematic pitch-circle views.
3. **Thermal & Welding** — explicitly illustrative heat-field views (not a calibrated welding or transient heat-transfer solver).
4. **Robotics & Kinematics** — two-link planar forward kinematics.
5. **Materials & Stress–Strain** — idealized tensile curve (not experimental material data).
6. **Beam & Shaft Basics** — centered point-load reactions, bending stress and small-deflection estimate for a solid round beam.
7. **Shaft Torsion & Combined Loading** — solid circular shaft bending stress, torsional shear, von Mises equivalent stress and angle of twist.
8. **Vibration & Dynamics** — exact closed-form free response of a linear viscously damped single-degree-of-freedom system; underdamped, critical and overdamped regimes.
9. **Pressure Vessel Basics** — closed-end thin cylindrical shell membrane stresses and an elementary D/t screening check.
10. **Pipe Flow & Pump Sizing** — Reynolds number, Darcy friction factor, major/minor head losses, pressure drop and estimated pump input power.
11. **AI Engineering Tutor** — Groq chat-completions integration with session context and concise PDF export.

## Reports

- **PDF:** One page maximum, calculation summary only, with a compact parameter/result table, equations, units, assumptions and warnings. Graphs and plot images are excluded.
- **CSV:** Retains the detailed numerical readings/time histories (for example, the spring load sweep, vibration response samples, thermal field values and material curve samples).

PDF summaries intentionally condense large arrays into their key design readings; use CSV when you need every sampled point. A one-page PDF can reduce type size for unusually long user-generated notes rather than spilling onto additional pages.

## Calculation basis and limitations

- Spring: linear-elastic round-wire helical compression-spring approximation; estimated solid height uses active coils plus two end coils. Fatigue, buckling, clash, end geometry and material allowables are not certified.
- Gears: ideal kinematic ratio and power/efficiency conversion. Tooth bending/contact strength, backlash, lubrication, bearings and ISO/AGMA rating checks are not included.
- Beam: Euler–Bernoulli, simply supported, prismatic solid circular beam with centered static point load and small deflection.
- Shaft: elastic solid circular section; assumes the entered maximum bending moment and torque act at the same section. No keyway/shoulder stress concentration, fatigue, critical-speed or bearing calculation.
- SDOF vibration: linear mass–spring–viscous-damper free response with constant properties and specified initial conditions; no forcing, nonlinearities or multi-mode effects.
- Pressure vessel: membrane stress equations for a closed-ended thin cylinder under internal gauge pressure. The D/t ratio is a preliminary thin-wall screen, not code acceptance. Heads, openings, weld efficiency, corrosion, external pressure, thermal loads, cyclic service and fabrication details are omitted.
- Pipe flow: steady, fully developed, incompressible, constant-property flow in a circular pipe. Transitional friction is an interpolated estimate. Fitting K values must be supplied by the user; elevation/static head and network balancing are not included.
- Thermal and materials pages remain teaching illustrations, not calibrated physics/material models.

These workspaces are for learning and preliminary estimates, not certified design or safety approval. Validate actual designs with qualified engineering review and the applicable jurisdictional code. Pressure-vessel design, for example, requires checking the governing edition and scope of ASME BPVC Section VIII plus material, weld, inspection, testing and certification provisions.

## Research references used for equation selection

- NPTEL, *Mechanical Engineering — Nonlinear Vibration*, review of linear systems and SDOF free vibration: https://archive.nptel.ac.in/content/storage2/courses/112103022/module1/lec1/7.html
- TU Delft OpenCourseWare, *Friction losses in pipelines*, Darcy–Weisbach and Colebrook equations: https://ocw.tudelft.nl/wp-content/uploads/Friction_losses_in_pipelines.pdf
- KFUPM engineering notes, *Stresses in Thin-Walled Pressure Vessels*: https://faculty.kfupm.edu.sa/ce/agadhib/Note/Chapter%20-%2006a.pdf
- ASME, *BPVC Section VIII — Rules for Construction of Pressure Vessels*: https://www.asme.org/codes-standards/find-codes-standards/bpvc-viii-1-bpvc-section-viii-rules-construction-pressure-vessels-division-1
- Groq documentation, GPT-OSS 120B model: https://console.groq.com/docs/model/openai/gpt-oss-120b and chat completions API: https://console.groq.com/docs/api-reference

## Run locally (Windows)

Python 3.10+ recommended.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
streamlit run app.py
```

Run calculation tests:

```powershell
pytest -q
```

## Configure AI tutor

Create `.streamlit/secrets.toml` locally:

```toml
GROQ_API_KEY = "paste-your-own-key-here"
```

For Streamlit Community Cloud, set `GROQ_API_KEY` in the app's Secrets settings. Never commit a real key to source control. The tutor depends on network access, model access and provider limits; local engineering calculation modules do not require the AI key.

## Deployment

Deploy `app.py`, `engineering_core.py`, `requirements.txt`, `README.md` and tests from the same folder. Select `app.py` as Streamlit's entry point. Keep the `.streamlit/secrets.toml` secret out of GitHub.
