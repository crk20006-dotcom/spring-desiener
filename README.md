# MechLab Studio — revised mobile-friendly engineering workbench

## Workspaces
1. Spring Design — helical compression-spring estimate, load/deflection curve, 3D helix.
2. Gear & Machine Design — ideal external spur-gear ratio, speed, torque and pitch-circle view.
3. Thermal & Welding — explicitly illustrative heat-field visualizations.
4. Robotics & Kinematics — two-link planar forward kinematics.
5. Materials & Stress–Strain — idealized tensile curve.
6. Beam & Shaft Basics — center-loaded, simply supported solid circular beam estimate.
7. AI Engineering Tutor — Groq-powered tutor with short conversation context.

## Improvements in this revision
- Compact workspace selector instead of a long sidebar radio list.
- Mobile spacing, metric sizing and touch-target adjustments.
- CSV data export is now available alongside PDF reports (the prior report helper accepted a DataFrame but did not export it).
- Tutor keeps recent turns in the current browser session, uses a lower temperature and token cap, and has a clear-chat action.
- Added beam/shaft starter calculations and regression tests.
- Clearer assumption and validation warnings in educational engineering modules.

## Run locally
Python 3.10+ recommended.
```bash
python -m venv .venv
# Windows PowerShell:
.venv\\Scripts\\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
streamlit run app.py
```
Open the local URL shown by Streamlit. To test calculations:
```bash
pytest -q
```

## Configure the AI tutor
Create `.streamlit/secrets.toml` locally:
```toml
GROQ_API_KEY = "paste-your-own-key-here"
```
Do not commit this file. For Streamlit Community Cloud, add `GROQ_API_KEY` under App → Settings → Secrets. The tutor requires internet and a valid Groq key/model access; the engineering calculators work without the AI key.

## Deploy
Push `app.py`, `engineering_core.py`, `requirements.txt`, `README.md`, and tests to a GitHub repository. In Streamlit Community Cloud, deploy the repository and select `app.py` as the entry point. Keep secrets in the platform settings, never in source code.

## Engineering limitations
These are educational preliminary calculators, not certified engineering design software. The spring model assumes linear elasticity and simplified end coils; fatigue, buckling, clash and material allowables are not validated. Gear calculations do not check tooth strength, contact ratio, backlash or lubrication. Thermal and materials curves are illustrative. Robotics is planar forward kinematics only. The beam module assumes a simply supported prismatic solid circular beam, central static point load, linear elasticity and small deflection. Always verify loads, materials, safety factors, units and applicable standards with authoritative references before real-world use.

## Verification
The calculation test suite is run with `pytest -q`. UI and live API behavior still need to be checked on the actual deployment and on the target Android/iOS browser because screen sizes, browser rendering and provider availability vary.
