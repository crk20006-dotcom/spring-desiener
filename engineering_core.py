"""Testable engineering calculation kernels for MechLab Studio.

These functions are deliberately UI-independent so pytest can verify calculations
without starting Streamlit. Models are preliminary educational estimates.
"""
from __future__ import annotations
import math
from dataclasses import dataclass
from scipy.optimize import brentq
import sympy as sp


@dataclass(frozen=True)
class SpringResult:
    spring_index: float
    stiffness_n_per_mm: float
    deflection_mm: float
    wahl_factor: float
    corrected_shear_stress_mpa: float
    solid_height_mm: float
    available_travel_mm: float
    loaded_height_mm: float
    travel_limit_load_n: float
    travel_exceeded: bool


def spring_result(wire_d_mm: float, mean_d_mm: float, active_coils: float,
                  shear_modulus_mpa: float, free_length_mm: float, load_n: float) -> SpringResult:
    """Return a linear helical compression-spring estimate using consistent N/mm/MPa units."""
    values = (wire_d_mm, mean_d_mm, active_coils, shear_modulus_mpa, free_length_mm, load_n)
    if not all(math.isfinite(float(v)) for v in values):
        raise ValueError("All spring inputs must be finite numbers.")
    if wire_d_mm <= 0 or mean_d_mm <= wire_d_mm or active_coils <= 0 or shear_modulus_mpa <= 0:
        raise ValueError("Require d > 0, D > d, active coils > 0, and G > 0.")
    if free_length_mm <= 0 or load_n < 0:
        raise ValueError("Free length must be positive and load cannot be negative.")
    c = mean_d_mm / wire_d_mm
    if c <= 1.0:
        raise ValueError("Spring index must exceed 1.")
    solid = wire_d_mm * (active_coils + 2.0)  # simplified end-coil estimate
    if free_length_mm <= solid:
        raise ValueError("Free length must exceed the estimated solid height.")
    k = shear_modulus_mpa * wire_d_mm**4 / (8.0 * mean_d_mm**3 * active_coils)
    delta = load_n / k
    wahl = (4*c - 1)/(4*c - 4) + 0.615/c
    stress = wahl * 8.0 * load_n * mean_d_mm / (math.pi * wire_d_mm**3)
    travel = free_length_mm - solid
    # SciPy root solver gives the load at which the linear model reaches the estimated travel.
    limit_load = float(brentq(lambda force: force/k - travel, 0.0, max(k*travel, 1.0)))
    shown_delta = min(delta, travel)
    return SpringResult(c, k, delta, wahl, stress, solid, travel,
                        free_length_mm - shown_delta, limit_load, delta > travel)


def symbolic_spring_equations() -> dict[str, str]:
    """Symbolically derive/document the core spring equations with SymPy."""
    G, d, D, n, F, k = sp.symbols("G d D n F k", positive=True)
    rate = G*d**4/(8*D**3*n)
    return {
        "spring_rate": f"k = {sp.sstr(rate)}",
        "deflection": f"delta = {sp.sstr(sp.solve(sp.Eq(F, k*sp.Symbol('delta')), sp.Symbol('delta'))[0].subs(k, rate))}",
        "units": "G in MPa (N/mm^2); d and D in mm; F in N; k in N/mm; deflection in mm.",
    }


def gear_pair(z_driver: int, z_driven: int, input_rpm: float, input_power_kw: float, efficiency_pct: float) -> dict[str, float]:
    if z_driver < 1 or z_driven < 1 or input_rpm <= 0 or input_power_kw < 0 or not 0 < efficiency_pct <= 100:
        raise ValueError("Teeth and speed must be positive; power nonnegative; efficiency in (0, 100].")
    ratio = z_driven / z_driver
    output_rpm = input_rpm / ratio
    output_power = input_power_kw * efficiency_pct / 100
    return {"ratio": ratio, "output_rpm": output_rpm,
            "input_torque_nm": 9550 * input_power_kw / input_rpm,
            "output_torque_nm": 9550 * output_power / output_rpm,
            "output_power_kw": output_power}


def planar_two_link(l1: float, l2: float, theta1_deg: float, theta2_relative_deg: float) -> tuple[float, float, float, float, float]:
    if l1 <= 0 or l2 <= 0:
        raise ValueError("Link lengths must be positive.")
    a1 = math.radians(theta1_deg)
    a2 = math.radians(theta1_deg + theta2_relative_deg)
    x1, y1 = l1*math.cos(a1), l1*math.sin(a1)
    x2, y2 = x1 + l2*math.cos(a2), y1 + l2*math.sin(a2)
    return x1, y1, x2, y2, math.hypot(x2, y2)
