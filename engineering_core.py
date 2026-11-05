"""Testable engineering calculation kernels for MechLab Studio.

These functions are deliberately UI-independent so pytest can verify calculations
without starting Streamlit. Models are preliminary educational estimates.
"""
from __future__ import annotations
import math
import numpy as np
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



def simply_supported_circular_beam(load_n: float, span_mm: float, diameter_mm: float,
                                   youngs_modulus_mpa: float) -> dict[str, float]:
    """Center-point-load estimate for a simply supported solid circular beam.

    Units: N, mm, MPa (= N/mm²). Small-deflection Euler-Bernoulli model.
    """
    values = (load_n, span_mm, diameter_mm, youngs_modulus_mpa)
    if not all(math.isfinite(float(v)) for v in values):
        raise ValueError("All beam inputs must be finite numbers.")
    if load_n < 0 or span_mm <= 0 or diameter_mm <= 0 or youngs_modulus_mpa <= 0:
        raise ValueError("Load must be nonnegative; span, diameter and modulus must be positive.")
    inertia = math.pi * diameter_mm**4 / 64.0
    moment = load_n * span_mm / 4.0
    stress = 32.0 * moment / (math.pi * diameter_mm**3)
    deflection = load_n * span_mm**3 / (48.0 * youngs_modulus_mpa * inertia)
    return {
        "reaction_each_n": load_n / 2.0,
        "max_moment_nmm": moment,
        "second_moment_mm4": inertia,
        "max_bending_stress_mpa": stress,
        "midspan_deflection_mm": deflection,
    }


def solid_shaft_combined_load(torque_nm: float, bending_moment_nm: float,
                              diameter_mm: float, length_mm: float,
                              shear_modulus_mpa: float) -> dict[str, float]:
    """Elastic stress/twist estimate for a solid circular shaft under T and M.

    Uses N, mm and MPa (= N/mm²). Does not include notches, fatigue or buckling.
    """
    values = (torque_nm, bending_moment_nm, diameter_mm, length_mm, shear_modulus_mpa)
    if not all(math.isfinite(float(v)) for v in values):
        raise ValueError("All shaft inputs must be finite numbers.")
    if torque_nm < 0 or bending_moment_nm < 0 or diameter_mm <= 0 or length_mm < 0 or shear_modulus_mpa <= 0:
        raise ValueError("Torque and bending moment must be nonnegative; diameter and modulus positive; length nonnegative.")
    d = diameter_mm
    t_nmm = torque_nm * 1000.0
    m_nmm = bending_moment_nm * 1000.0
    polar_moment = math.pi * d**4 / 32.0
    bending_stress = 32.0 * m_nmm / (math.pi * d**3)
    torsional_shear = 16.0 * t_nmm / (math.pi * d**3)
    von_mises = math.sqrt(bending_stress**2 + 3.0 * torsional_shear**2)
    twist_rad = t_nmm * length_mm / (shear_modulus_mpa * polar_moment)
    return {
        "polar_moment_mm4": polar_moment,
        "bending_stress_mpa": bending_stress,
        "torsional_shear_mpa": torsional_shear,
        "von_mises_stress_mpa": von_mises,
        "angle_of_twist_deg": math.degrees(twist_rad),
    }


def thin_wall_cylinder_stress(pressure_mpa: float, inside_diameter_mm: float,
                              thickness_mm: float) -> dict[str, float]:
    """Membrane stresses for a closed-ended thin-walled cylindrical vessel.

    Uses internal diameter and gauge pressure. Applicability is weak when D/t < 20.
    This is not a pressure-vessel code design calculation.
    """
    values = (pressure_mpa, inside_diameter_mm, thickness_mm)
    if not all(math.isfinite(float(v)) for v in values):
        raise ValueError("All pressure-vessel inputs must be finite numbers.")
    if pressure_mpa < 0 or inside_diameter_mm <= 0 or thickness_mm <= 0:
        raise ValueError("Pressure must be nonnegative; diameter and thickness must be positive.")
    radius = inside_diameter_mm / 2.0
    ratio = inside_diameter_mm / thickness_mm
    hoop = pressure_mpa * radius / thickness_mm
    longitudinal = pressure_mpa * radius / (2.0 * thickness_mm)
    return {
        "diameter_to_thickness_ratio": ratio,
        "hoop_stress_mpa": hoop,
        "longitudinal_stress_mpa": longitudinal,
        "max_in_plane_shear_mpa": abs(hoop - longitudinal) / 2.0,
    }


def pipe_flow_calculation(flow_l_min: float, diameter_mm: float, length_m: float,
                          roughness_mm: float, density_kg_m3: float,
                          viscosity_mpa_s: float, minor_loss_k: float = 0.0,
                          pump_efficiency_pct: float = 70.0) -> dict[str, float | str]:
    """Steady incompressible pipe-flow estimate using Darcy-Weisbach/Colebrook.

    Transitional friction is smoothly interpolated between laminar and turbulent
    estimates and explicitly flagged as approximate.
    """
    values = (flow_l_min, diameter_mm, length_m, roughness_mm, density_kg_m3,
              viscosity_mpa_s, minor_loss_k, pump_efficiency_pct)
    if not all(math.isfinite(float(v)) for v in values):
        raise ValueError("All pipe-flow inputs must be finite numbers.")
    if flow_l_min <= 0 or diameter_mm <= 0 or length_m < 0 or roughness_mm < 0 or density_kg_m3 <= 0 or viscosity_mpa_s <= 0 or minor_loss_k < 0 or not 0 < pump_efficiency_pct <= 100:
        raise ValueError("Flow, diameter, density and viscosity must be positive; lengths, roughness and K nonnegative; efficiency in (0,100].")
    q = flow_l_min / 1000.0 / 60.0
    d = diameter_mm / 1000.0
    eps = roughness_mm / 1000.0
    mu = viscosity_mpa_s / 1000.0  # mPa.s -> Pa.s
    area = math.pi * d**2 / 4.0
    velocity = q / area
    reynolds = density_kg_m3 * velocity * d / mu
    relative_roughness = eps / d
    if relative_roughness >= 0.2:
        raise ValueError("Relative pipe roughness is too large for this friction-factor model.")

    def colebrook(re: float) -> float:
        def residual(f: float) -> float:
            return 1.0 / math.sqrt(f) + 2.0 * math.log10(relative_roughness / 3.7 + 2.51 / (re * math.sqrt(f)))
        return float(brentq(residual, 0.005, 0.2, xtol=1e-12))

    if reynolds < 2300.0:
        friction = 64.0 / reynolds
        regime = "Laminar"
    elif reynolds >= 4000.0:
        friction = colebrook(reynolds)
        regime = "Turbulent (Colebrook-White)"
    else:
        f_lam = 64.0 / reynolds
        f_turb = colebrook(reynolds)
        u = (reynolds - 2300.0) / 1700.0
        blend = u*u*(3.0 - 2.0*u)
        friction = f_lam * (1.0 - blend) + f_turb * blend
        regime = "Transitional (interpolated estimate)"

    g = 9.80665
    velocity_head = velocity**2 / (2.0 * g)
    major_head = friction * (length_m / d) * velocity_head
    minor_head = minor_loss_k * velocity_head
    total_head = major_head + minor_head
    pressure_drop_pa = density_kg_m3 * g * total_head
    hydraulic_power_w = density_kg_m3 * g * q * total_head
    pump_input_power_w = hydraulic_power_w / (pump_efficiency_pct / 100.0)
    return {
        "flow_m3_s": q,
        "velocity_m_s": velocity,
        "reynolds_number": reynolds,
        "relative_roughness": relative_roughness,
        "darcy_friction_factor": friction,
        "flow_regime": regime,
        "velocity_head_m": velocity_head,
        "major_head_loss_m": major_head,
        "minor_head_loss_m": minor_head,
        "total_head_loss_m": total_head,
        "pressure_drop_kpa": pressure_drop_pa / 1000.0,
        "hydraulic_power_w": hydraulic_power_w,
        "estimated_pump_input_power_w": pump_input_power_w,
    }


def sdof_free_vibration(mass_kg: float, stiffness_n_m: float, damping_ns_m: float,
                        initial_displacement_mm: float, initial_velocity_mm_s: float,
                        times_s: Iterable[float]) -> dict[str, float | list[float] | str]:
    """Exact free response of a linear viscously damped SDOF oscillator."""
    values = (mass_kg, stiffness_n_m, damping_ns_m, initial_displacement_mm, initial_velocity_mm_s)
    if not all(math.isfinite(float(v)) for v in values):
        raise ValueError("All vibration inputs must be finite numbers.")
    if mass_kg <= 0 or stiffness_n_m <= 0 or damping_ns_m < 0:
        raise ValueError("Mass and stiffness must be positive; damping cannot be negative.")
    times = [float(t) for t in times_s]
    if not times or any(not math.isfinite(t) or t < 0 for t in times):
        raise ValueError("Provide one or more finite, nonnegative time values.")
    wn = math.sqrt(stiffness_n_m / mass_kg)
    cc = 2.0 * math.sqrt(stiffness_n_m * mass_kg)
    zeta = damping_ns_m / cc
    x0 = initial_displacement_mm / 1000.0
    v0 = initial_velocity_mm_s / 1000.0
    if zeta < 1.0 - 1e-10:
        wd = wn * math.sqrt(1.0 - zeta*zeta)
        response_m = [
            math.exp(-zeta*wn*t) * (
                x0*math.cos(wd*t) + (v0 + zeta*wn*x0)/wd * math.sin(wd*t)
            ) for t in times
        ]
        regime = "Underdamped"
    elif zeta <= 1.0 + 1e-10:
        response_m = [(x0 + (v0 + wn*x0)*t) * math.exp(-wn*t) for t in times]
        wd = 0.0
        regime = "Critically damped"
    else:
        root = math.sqrt(zeta*zeta - 1.0)
        r1 = -wn * (zeta - root)
        r2 = -wn * (zeta + root)
        c1 = (v0 - r2*x0) / (r1 - r2)
        c2 = (r1*x0 - v0) / (r1 - r2)
        response_m = [c1*math.exp(r1*t) + c2*math.exp(r2*t) for t in times]
        wd = 0.0
        regime = "Overdamped"
    return {
        "natural_frequency_rad_s": wn,
        "natural_frequency_hz": wn / (2.0 * math.pi),
        "critical_damping_ns_m": cc,
        "damping_ratio": zeta,
        "damped_frequency_rad_s": wd,
        "damped_frequency_hz": wd / (2.0 * math.pi),
        "damping_regime": regime,
        "displacement_mm": [x * 1000.0 for x in response_m],
    }


def beam_fem_euler_bernoulli(load_n: float, span_mm: float, diameter_mm: float,
                              youngs_modulus_mpa: float, elements: int = 20) -> dict[str, float | list[float]]:
    """Simply-supported solid-round beam with a centre point load using 2-node EB beam FEM.

    Consistent units: N, mm, MPa (= N/mm²). Each node has transverse
    displacement and rotation DOFs. The element is slender-beam Euler-Bernoulli;
    shear deformation, geometric nonlinearity and material plasticity are omitted.
    The mesh must have an even element count so the point load is a node load.
    """
    values = (load_n, span_mm, diameter_mm, youngs_modulus_mpa)
    if not all(math.isfinite(float(v)) for v in values):
        raise ValueError("All FEM beam inputs must be finite numbers.")
    if load_n < 0 or span_mm <= 0 or diameter_mm <= 0 or youngs_modulus_mpa <= 0:
        raise ValueError("Load must be nonnegative; span, diameter and modulus must be positive.")
    if isinstance(elements, bool) or int(elements) != elements or elements < 2 or elements > 80 or elements % 2:
        raise ValueError("Element count must be an even integer from 2 to 80.")

    n = int(elements)
    node_count = n + 1
    dx = span_mm / n
    inertia = math.pi * diameter_mm**4 / 64.0
    ei = youngs_modulus_mpa * inertia
    ke = (ei / dx**3) * np.array([
        [12, 6*dx, -12, 6*dx],
        [6*dx, 4*dx**2, -6*dx, 2*dx**2],
        [-12, -6*dx, 12, -6*dx],
        [6*dx, 2*dx**2, -6*dx, 4*dx**2],
    ], dtype=float)
    K = np.zeros((2*node_count, 2*node_count), dtype=float)
    for e in range(n):
        dofs = [2*e, 2*e+1, 2*e+2, 2*e+3]
        K[np.ix_(dofs, dofs)] += ke

    F = np.zeros(2*node_count, dtype=float)
    mid_node = n // 2
    F[2*mid_node] = -load_n
    fixed = np.array([0, 2*n], dtype=int)  # vertical translation fixed at both simple supports
    free = np.setdiff1d(np.arange(2*node_count), fixed)
    displacement = np.zeros(2*node_count, dtype=float)
    if free.size:
        try:
            displacement[free] = np.linalg.solve(K[np.ix_(free, free)], F[free])
        except np.linalg.LinAlgError as exc:
            raise ValueError("FEM stiffness matrix could not be solved; check the mesh and support conditions.") from exc
    reactions = K @ displacement - F

    node_x = np.linspace(0.0, span_mm, node_count)
    w = displacement[0::2]
    rotations = displacement[1::2]
    moments = []
    end_moments = []
    for e in range(n):
        d_local = displacement[2*e:2*e+4]
        # Cubic Hermite curvature at xi=0.5 for one representative element value.
        curvature_mid = np.array([0.0, -1/dx, 0.0, 1/dx], dtype=float) @ d_local
        moments.append(ei * float(curvature_mid))
        # Evaluate both element ends as well: the maximum bending moment occurs
        # at the loaded centre node and can be missed by midpoint-only sampling.
        curvature_left = np.array([-6/dx**2, -4/dx, 6/dx**2, -2/dx], dtype=float) @ d_local
        curvature_right = np.array([6/dx**2, 2/dx, -6/dx**2, 4/dx], dtype=float) @ d_local
        end_moments.extend([ei * float(curvature_left), ei * float(curvature_right)])
    moments_arr = np.asarray(moments, dtype=float)
    max_moment = float(np.max(np.abs(end_moments))) if end_moments else 0.0
    stresses = np.abs(moments_arr) * (diameter_mm/2.0) / inertia
    return {
        "node_x_mm": node_x.tolist(),
        "deflection_mm": w.tolist(),
        "rotation_rad": rotations.tolist(),
        "element_mid_x_mm": ((node_x[:-1] + node_x[1:]) / 2.0).tolist(),
        "bending_moment_Nmm": moments_arr.tolist(),
        "bending_stress_MPa": stresses.tolist(),
        "reaction_left_N": float(reactions[0]),
        "reaction_right_N": float(reactions[2*n]),
        "max_deflection_mm": float(np.max(np.abs(w))),
        "max_bending_moment_Nmm": max_moment,
        "max_bending_stress_MPa": max_moment * (diameter_mm/2.0) / inertia,
        "second_moment_mm4": inertia,
        "element_length_mm": dx,
        "element_count": n,
    }
