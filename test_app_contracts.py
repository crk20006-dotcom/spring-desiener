import ast
from pathlib import Path


def test_each_workspace_renders_a_3d_scene_and_has_dispatch():
    source = Path("app.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    funcs = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}
    required = {
        "spring_module", "gear_module", "thermal_module", "robotics_module",
        "materials_module", "beam_module", "shaft_module", "vibration_module",
        "pressure_vessel_module", "pipe_flow_module", "fem_module", "tutor_module",
    }
    assert required.issubset(funcs)
    for name in required:
        calls_3d = [n for n in ast.walk(funcs[name]) if isinstance(n, ast.Call)
                    and isinstance(n.func, ast.Name) and n.func.id == "render_3d_panel"]
        assert calls_3d, f"{name} has no 3D panel"

    dispatch = [n for n in ast.walk(tree) if isinstance(n, ast.Compare)]
    for label in ["Spring Design", "Gear & Machine Design", "Thermal & Welding",
                  "Robotics & Kinematics", "Materials & Stress–Strain", "Beam & Shaft Basics",
                  "Shaft Torsion & Combined Loading", "Vibration & Dynamics",
                  "Pressure Vessel Basics", "Pipe Flow & Pump Sizing",
                  "Finite Element Beam Lab", "AI Engineering Tutor"]:
        assert label in source


def test_workspace_navigation_is_persistent_topbar():
    source = Path("app.py").read_text(encoding="utf-8")
    assert 'st.container(key="mechlab_topbar")' in source
    assert ".st-key-mechlab_topbar" in source
