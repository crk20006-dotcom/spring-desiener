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
