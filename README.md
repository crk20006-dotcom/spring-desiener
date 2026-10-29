# MechLab Studio — technology upgrade candidate

## Included upgrades
- **SciPy**: the spring module now uses a root solver to calculate the load corresponding to the estimated available compression travel.
- **SymPy**: the spring PDF report includes symbolic equation documentation and unit notes.
- **NumPy / Plotly**: retain numerical arrays and responsive interactive plots/3D visualizations.
- **ReportLab + Matplotlib**: PDF reports with embedded plotted outputs.
- **pytest**: UI-independent regression tests for spring behavior, invalid geometry, gear ratios, and two-link kinematics.

## Run locally
```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

## Run calculation tests
```bash
pytest -q
```

## Streamlit Cloud
Commit `app.py`, `engineering_core.py`, `requirements.txt`, and optionally the tests/README to the repository. Keep `GROQ_API_KEY` in Streamlit Secrets; never place the API key in source control.

## Engineering scope
These are preliminary educational models. The spring model uses a linear-elastic round-wire helical spring equation and a simplified solid-height estimate. The thermal field and stress–strain post-yield curve are illustrative. The gear view is schematic and does not validate tooth contact or strength. Validate real designs against authoritative references and applicable standards.

## Verification status
The calculation test suite passes in the build environment. Python syntax compilation passes. Full Streamlit UI execution and live Streamlit Cloud deployment were not run in this environment because Streamlit is not installed here; test the deployed app after updating the repository.
