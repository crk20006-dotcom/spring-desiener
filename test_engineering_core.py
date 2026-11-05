import math
import pytest
from engineering_core import spring_result, symbolic_spring_equations, gear_pair, planar_two_link


def test_spring_load_increases_deflection_and_stress():
    a = spring_result(4, 25, 8, 79300, 60, 100)
    b = spring_result(4, 25, 8, 79300, 60, 200)
    assert b.deflection_mm == pytest.approx(2*a.deflection_mm)
    assert b.corrected_shear_stress_mpa == pytest.approx(2*a.corrected_shear_stress_mpa)
    assert b.loaded_height_mm < a.loaded_height_mm


def test_spring_zero_load_is_uncompressed():
    r = spring_result(4, 25, 8, 79300, 60, 0)
    assert r.deflection_mm == 0
    assert r.loaded_height_mm == 60
    assert not r.travel_exceeded


def test_spring_travel_warning_condition():
    r = spring_result(4, 25, 8, 79300, 60, 10000)
    assert r.travel_exceeded
    assert r.loaded_height_mm == pytest.approx(r.solid_height_mm)


def test_invalid_spring_geometry_rejected():
    with pytest.raises(ValueError):
        spring_result(4, 4, 8, 79300, 60, 100)


def test_symbolic_equations_returned():
    eq = symbolic_spring_equations()
    assert "G" in eq["spring_rate"] and "d" in eq["spring_rate"]
    assert "N/mm" in eq["units"]


def test_gear_pair_ratio_and_speed():
    g = gear_pair(20, 60, 1200, 2, 95)
    assert g["ratio"] == 3
    assert g["output_rpm"] == 400


def test_robot_straight_arm_reach():
    x1, y1, x2, y2, reach = planar_two_link(300, 220, 0, 0)
    assert x2 == pytest.approx(520)
    assert y2 == pytest.approx(0)
    assert reach == pytest.approx(520)



def test_center_loaded_circular_beam_symmetry_and_bending():
    from engineering_core import simply_supported_circular_beam
    r = simply_supported_circular_beam(1000, 400, 20, 200000)
    assert r["reaction_each_n"] == pytest.approx(500)
    assert r["max_moment_nmm"] == pytest.approx(100000)
    assert r["max_bending_stress_mpa"] == pytest.approx(32*100000/(math.pi*20**3))
    assert r["midspan_deflection_mm"] > 0


def test_beam_rejects_invalid_inputs():
    from engineering_core import simply_supported_circular_beam
    with pytest.raises(ValueError):
        simply_supported_circular_beam(-1, 400, 20, 200000)
    with pytest.raises(ValueError):
        simply_supported_circular_beam(100, 0, 20, 200000)


def test_shaft_combined_loading_basic_relations():
    from engineering_core import solid_shaft_combined_load
    r = solid_shaft_combined_load(100, 50, 30, 1000, 79300)
    assert r["bending_stress_mpa"] == pytest.approx(32 * 50000 / (math.pi * 30**3))
    assert r["torsional_shear_mpa"] == pytest.approx(16 * 100000 / (math.pi * 30**3))
    assert r["von_mises_stress_mpa"] == pytest.approx(
        math.sqrt(r["bending_stress_mpa"]**2 + 3*r["torsional_shear_mpa"]**2)
    )
    assert r["angle_of_twist_deg"] > 0


def test_pressure_vessel_closed_end_stress_ratio():
    from engineering_core import thin_wall_cylinder_stress
    r = thin_wall_cylinder_stress(1.0, 500, 10)
    assert r["hoop_stress_mpa"] == pytest.approx(25.0)
    assert r["longitudinal_stress_mpa"] == pytest.approx(12.5)
    assert r["diameter_to_thickness_ratio"] == pytest.approx(50.0)


def test_pipe_flow_turbulent_darcy_estimate():
    from engineering_core import pipe_flow_calculation
    r = pipe_flow_calculation(50, 50, 100, 0.045, 998, 1.0, 2, 70)
    assert r["reynolds_number"] > 4000
    assert 0.005 < r["darcy_friction_factor"] < 0.1
    assert r["total_head_loss_m"] > 0
    assert r["estimated_pump_input_power_w"] > r["hydraulic_power_w"]


def test_pipe_flow_laminar_factor_is_64_over_re():
    from engineering_core import pipe_flow_calculation
    r = pipe_flow_calculation(1, 10, 10, 0.001, 1000, 100.0)
    assert r["flow_regime"] == "Laminar"
    assert r["darcy_friction_factor"] == pytest.approx(64 / r["reynolds_number"])


def test_sdof_response_initial_condition_and_damping_regimes():
    from engineering_core import sdof_free_vibration
    under = sdof_free_vibration(10, 4000, 80, 10, 0, [0, 0.1, 0.2])
    critical = sdof_free_vibration(10, 4000, 2*math.sqrt(10*4000), 10, 0, [0, 0.1])
    over = sdof_free_vibration(10, 4000, 2.5*2*math.sqrt(10*4000), 10, 0, [0, 0.1])
    assert under["damping_regime"] == "Underdamped"
    assert critical["damping_regime"] == "Critically damped"
    assert over["damping_regime"] == "Overdamped"
    assert under["displacement_mm"][0] == pytest.approx(10)
    assert critical["displacement_mm"][0] == pytest.approx(10)
    assert over["displacement_mm"][0] == pytest.approx(10)


def test_pipe_flow_transition_band_is_explicitly_flagged():
    from engineering_core import pipe_flow_calculation
    r = pipe_flow_calculation(1.4, 10, 10, 0.001, 1000, 1.0)
    assert 2300 <= r["reynolds_number"] < 4000
    assert r["flow_regime"].startswith("Transitional")
    assert r["darcy_friction_factor"] > 0


def test_pressure_vessel_rejects_nonphysical_inputs():
    from engineering_core import thin_wall_cylinder_stress
    with pytest.raises(ValueError):
        thin_wall_cylinder_stress(-1, 500, 10)


def test_shaft_rejects_invalid_dimensions():
    from engineering_core import solid_shaft_combined_load
    with pytest.raises(ValueError):
        solid_shaft_combined_load(100, 50, 0, 1000, 79300)


def test_vibration_rejects_negative_damping():
    from engineering_core import sdof_free_vibration
    with pytest.raises(ValueError):
        sdof_free_vibration(1, 1000, -1, 1, 0, [0, 1])


def test_tutor_pdf_calls_use_three_argument_signature():
    import ast
    from pathlib import Path
    tree = ast.parse(Path("app.py").read_text(encoding="utf-8"))
    calls = [node for node in ast.walk(tree)
             if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
             and node.func.id == "_make_pdf"]
    assert calls
    assert all(len(call.args) == 3 for call in calls)


def test_euler_bernoulli_fem_matches_center_loaded_beam_solution():
    from engineering_core import beam_fem_euler_bernoulli, simply_supported_circular_beam
    fem = beam_fem_euler_bernoulli(1000, 400, 20, 200000, elements=20)
    exact = simply_supported_circular_beam(1000, 400, 20, 200000)
    assert fem["reaction_left_N"] == pytest.approx(500, rel=1e-8)
    assert fem["reaction_right_N"] == pytest.approx(500, rel=1e-8)
    assert fem["max_deflection_mm"] == pytest.approx(exact["midspan_deflection_mm"], rel=1e-7)
    assert fem["max_bending_stress_MPa"] == pytest.approx(exact["max_bending_stress_mpa"], rel=1e-7)
    assert len(fem["node_x_mm"]) == 21


def test_euler_bernoulli_fem_refuses_odd_or_excessive_mesh():
    from engineering_core import beam_fem_euler_bernoulli
    with pytest.raises(ValueError):
        beam_fem_euler_bernoulli(100, 400, 20, 200000, elements=9)
    with pytest.raises(ValueError):
        beam_fem_euler_bernoulli(100, 400, 20, 200000, elements=82)
