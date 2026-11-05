# MechLab Studio Pro

A single-workspace mechanical engineering learning and preliminary-analysis app built with Python, Streamlit, NumPy, SciPy, SymPy and Plotly. The UI keeps one workspace active at a time, with a persistent workspace selector; calculations, 3D inspection, plots, notes and exports remain together inside that workspace.

## Workspaces (12)

1. **Spring Design** — helical compression spring rate, deflection, Wahl-corrected shear stress, available travel and a tube-mesh 3D spring representation that follows the selected load.
2. **Gear & Machine Design** — external spur-gear ratio, speed and torque, plus a rotatable extruded 3D schematic gear pair. The tooth form is deliberately identified as schematic, not an involute design.
3. **Thermal & Welding** — illustrative 2D temperature field, time trend and a 3D plate heat-field surface. It is not a validated welding heat-source, metallurgy or phase-change solver.
4. **Robotics & Kinematics** — two-link planar forward kinematics with a 3D manipulator pose, base and tool axis.
5. **Materials & Stress–Strain** — idealized tensile curve and 3D tensile specimen with selected strain/stress. It is not experimental material data or a constitutive plasticity model.
6. **Beam & Shaft Basics** — simply supported circular beam reactions, maximum bending stress and closed-form Euler–Bernoulli deflection with a 3D deformed-beam view.
7. **Shaft Torsion & Combined Loading** — solid circular shaft bending stress, torsional shear, von Mises estimate, angle of twist and 3D twist geometry.
8. **Vibration & Dynamics** — exact closed-form free response for a linear viscously damped SDOF system; an interactive time selector drives a 3D mass–spring–damper scene.
9. **Pressure Vessel Basics** — closed-end thin cylindrical shell membrane stresses and D/t screening, with a 3D shell stress-color visualization.
10. **Pipe Flow & Pump Sizing** — Reynolds number, Darcy friction factor, major/minor losses, pressure drop and pump power with a 3D pipe-and-flow-direction scene.
11. **Finite Element Beam Lab** — 2-node Euler–Bernoulli beam elements, assembled global stiffness matrix, simply-supported boundary conditions, central nodal point load, solved nodal displacement/rotation, reactions and bending-stress recovery. A 3D mesh/deformed shape marks the FE nodes. This is a 1D beam FEM, not 3D solid FEA.
12. **AI Engineering Tutor** — Groq chat-completions integration, short session conversation context, one-page answer PDF and a 3D slider-crank mechanism explorer.

## 3D and UI technology choices

- **Plotly 3D** is used for `Surface`, `Scatter3d`, `Cone` and related WebGL-backed scenes. It avoids adding a large native VTK/PyVista dependency to a lightweight Streamlit-hosted project and provides browser camera interaction on desktop and mobile.
- **Streamlit** owns the application shell, controls, session state, persistent workspace selector and responsive layout.
- **NumPy/SciPy** handle deterministic numerical calculations and matrix operations. **SymPy** provides symbolic equation support where used.
- The 3D scene is a view of computed state or a clearly labelled schematic. A 3D picture does not, by itself, imply finite-element analysis, CFD, contact mechanics or a validated physical simulation.

## Reports

- **PDF:** calculation summary, one page maximum, no graphs. Summary tables are preferred over thousands of sampled rows. Long numerical series remain in CSV.
- **CSV:** full numerical readings and sample histories where applicable, including the spring load sweep, vibration time response, thermal field samples, material-curve samples and FEM nodal data.

The PDF builder uses ReportLab `KeepInFrame(mode="shrink")` to keep the report within one page. Extremely long AI tutor answers may be reduced to fit; use the on-screen conversation as the full-length source.

## Engineering assumptions and boundaries

- **Spring:** linear-elastic round-wire helical compression approximation. Estimated solid height assumes active coils plus two end coils. Fatigue, buckling, clash, end geometry, material allowables and manufacturing tolerances are not certified.
- **Gears:** ideal kinematic ratio and power/efficiency conversion. The 3D tooth shape is schematic, not involute. Tooth bending/contact strength, backlash, lubrication, bearings and ISO/AGMA rating checks are omitted.
- **Thermal:** teaching-level Gaussian heat-field approximation only; no calibrated material data, phase change, convection, radiation, moving weld source or validated transient conduction solver.
- **Robotics:** planar forward kinematics only; joint dynamics, collision, inverse kinematics and actuator sizing are not assessed.
- **Materials:** post-yield curve is a simplified interpolation; not experimental data, damage, necking or a validated constitutive law.
- **Beam closed-form:** simply supported, prismatic, solid circular Euler–Bernoulli beam with a centered static point load, linear elasticity and small deflection.
- **Shaft:** elastic solid circular section. Entered maximum bending moment and torque are assumed to act at the same section. No notches, fatigue, critical speed, bearings or shaft deflection limits.
- **SDOF vibration:** linear mass–spring–viscous-damper free response with constant properties and specified initial conditions; no forcing, nonlinearities or multiple modes.
- **Pressure vessel:** closed-end, thin cylindrical shell under internal gauge pressure. D/t is a screening flag, not code acceptance. Heads, openings, nozzles, weld efficiency, corrosion, external pressure, thermal loads and cyclic service are excluded.
- **Pipe flow:** steady, fully developed, incompressible, constant-property flow in a circular pipe. Transitional friction is an interpolation and is explicitly flagged. The supplied total K represents minor losses; elevation, network balancing and pump curves are omitted.
- **Beam FEM:** linear 1D Euler–Bernoulli beam elements with two DOFs per node, constant EI, simply supported ends and a central nodal point load. Slender-beam assumptions apply; shear deformation, distributed loads, local 2D/3D stress concentrations, buckling and material nonlinearity are excluded.

These are educational and preliminary-analysis tools, not certified engineering software or safety approval. Always validate real designs using qualified engineering review, material traceability, appropriate load cases, safety factors and the governing jurisdictional standards. For pressure vessels, consult the applicable edition and scope of ASME BPVC Section VIII and all relevant material, welding, inspection and certification requirements.

## Research and technical references

- Plotly, **3D Charts in Python** (3D scatter, surfaces, meshes, cones and related scene types): https://plotly.com/python/3d-charts/
- Streamlit, **`st.plotly_chart`** (embedding interactive Plotly figures in Streamlit): https://docs.streamlit.io/develop/api-reference/charts/st.plotly_chart
- Streamlit, **`st.container`** (stable keyed containers for layout and CSS targeting): https://docs.streamlit.io/1.40.0/develop/api-reference/layout/st.container
- TU Delft OpenCourseWare, **Euler–Bernoulli beam elements** (Hermite interpolation and finite-element formulation): https://teachbooks.tudelft.nl/computational-modelling/structural_linear/euler_bernouilli.html
- University of Edinburgh, **Finite Element Method and Implementation** (beam element stiffness matrices and assumptions): https://www.drps.ed.ac.uk/14-15_Archive_at_01-09-2014/dpt/cxpgee11086.htm
- NPTEL, **Mechanical Engineering — Nonlinear Vibration**: https://archive.nptel.ac.in/content/storage2/courses/112103022/module1/lec1/7.html
- TU Delft OpenCourseWare, **Friction losses in pipelines**: https://ocw.tudelft.nl/wp-content/uploads/Friction_losses_in_pipelines.pdf
- ASME, **BPVC Section VIII — Rules for Construction of Pressure Vessels**: https://www.asme.org/codes-standards/find-codes-standards/bpvc-viii-1-bpvc-section-viii-rules-construction-pressure-vessels-division-1
- Groq, **GPT-OSS 120B model** and **Chat Completions API**: https://console.groq.com/docs/model/openai/gpt-oss-120b · https://console.groq.com/docs/api-reference

## Run locally on Windows

Python 3.10+ is recommended.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
streamlit run app.py
```

Run tests:

```powershell
pytest -q
```

## Configure the AI tutor

Create `.streamlit/secrets.toml` locally:

```toml
GROQ_API_KEY = "paste-your-own-key-here"
```

For Streamlit Community Cloud, set `GROQ_API_KEY` in the app's Secrets settings. Never commit a real key to GitHub. The AI Tutor requires internet access, a valid API key, model access and provider availability; the engineering calculators run without the AI key.

## Deploy

Deploy the contents of this folder to your GitHub repository. Set `app.py` as the Streamlit entry point and keep `.streamlit/secrets.toml` out of source control. Verify the live UI on target phone browsers after deployment; browser WebGL support, device memory and display size can affect 3D performance.
