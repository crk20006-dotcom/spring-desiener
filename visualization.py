"""Lightweight interactive 3D engineering scenes for MechLab Studio.

All scenes are Plotly WebGL-friendly figures. They visualize the analytical
model state; they are not finite-element/CFD solvers unless the associated
calculation module explicitly says so.
"""
from __future__ import annotations

import math
import numpy as np
import plotly.graph_objects as go


_PALETTE = {
    "blue": "#3B82F6", "teal": "#14B8A6", "orange": "#F59E0B",
    "red": "#EF4444", "slate": "#64748B", "light": "#CBD5E1",
    "dark": "#1E293B", "purple": "#8B5CF6",
}


def _scene(title: str, height: int = 430) -> go.Figure:
    fig = go.Figure()
    fig.update_layout(
        title=dict(text=title, x=0.02, xanchor="left"),
        height=height, autosize=True,
        margin=dict(l=4, r=4, t=54, b=4),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        scene=dict(
            xaxis=dict(title="X", showbackground=True, backgroundcolor="rgba(148,163,184,.07)", gridcolor="rgba(148,163,184,.25)"),
            yaxis=dict(title="Y", showbackground=True, backgroundcolor="rgba(148,163,184,.07)", gridcolor="rgba(148,163,184,.25)"),
            zaxis=dict(title="Z", showbackground=True, backgroundcolor="rgba(148,163,184,.07)", gridcolor="rgba(148,163,184,.25)"),
            aspectmode="data", camera=dict(eye=dict(x=1.65, y=1.7, z=1.35)),
        ),
        legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0),
    )
    return fig


def spring_scene(wire_d: float, mean_d: float, active_coils: float, height: float,
                 turns: float | None = None, title: str = "3D compression spring") -> go.Figure:
    turns = turns or max(3.0, active_coils + 2.0)
    theta = np.linspace(0.0, 2.0 * math.pi * turns, 720)
    radius = mean_d / 2.0
    zc = np.linspace(wire_d / 2.0, max(wire_d, height - wire_d / 2.0), len(theta))
    cx, cy = radius * np.cos(theta), radius * np.sin(theta)
    # A tube mesh around the helix centerline gives the wire a visible 3D body.
    tangent = np.column_stack((-radius * np.sin(theta), radius * np.cos(theta), np.gradient(zc, theta)))
    tangent /= np.maximum(np.linalg.norm(tangent, axis=1)[:, None], 1e-12)
    normal = np.column_stack((np.cos(theta), np.sin(theta), np.zeros_like(theta)))
    binormal = np.cross(tangent, normal)
    phi = np.linspace(0.0, 2.0 * math.pi, 14)
    X = cx[:, None] + (wire_d / 2.0) * (normal[:, 0, None] * np.cos(phi) + binormal[:, 0, None] * np.sin(phi))
    Y = cy[:, None] + (wire_d / 2.0) * (normal[:, 1, None] * np.cos(phi) + binormal[:, 1, None] * np.sin(phi))
    Z = zc[:, None] + (wire_d / 2.0) * (normal[:, 2, None] * np.cos(phi) + binormal[:, 2, None] * np.sin(phi))
    fig = _scene(title)
    fig.add_trace(go.Surface(x=X, y=Y, z=Z, showscale=False, colorscale=[[0, _PALETTE["teal"]], [1, _PALETTE["blue"]]],
                              name="Spring wire", hoverinfo="skip", lighting=dict(ambient=.5, diffuse=.8, specular=.35, roughness=.55)))
    return fig


def gear_scene(z1: int, z2: int, module_mm: float, angle_deg: float = 0.0) -> go.Figure:
    fig = _scene("3D spur-gear pair · schematic tooth geometry")
    theta = np.linspace(0, 2 * math.pi, max(480, (z1 + z2) * 16))
    pitch1, pitch2 = module_mm * z1 / 2, module_mm * z2 / 2
    center = pitch1 + pitch2
    for pitch, teeth, cx, phase, color, label in [
        (pitch1, z1, 0.0, math.radians(angle_deg), _PALETTE["blue"], "Driver"),
        (pitch2, z2, center, -math.radians(angle_deg) * z1 / z2, _PALETTE["teal"], "Driven"),
    ]:
        # Stylized radial tooth tips/roots only; not an involute tooth profile.
        pattern = np.cos(teeth * (theta - phase))
        rr = pitch + module_mm * (0.35 * np.maximum(pattern, 0) - 0.28 * np.maximum(-pattern, 0))
        z = np.vstack((np.full_like(theta, -module_mm * 0.75), np.full_like(theta, module_mm * 0.75)))
        x = np.vstack((cx + rr * np.cos(theta), cx + rr * np.cos(theta)))
        y = np.vstack((rr * np.sin(theta), rr * np.sin(theta)))
        fig.add_trace(go.Surface(x=x, y=y, z=z, opacity=.96, showscale=False,
                                 colorscale=[[0, color], [1, color]], name=f"{label} ({teeth} teeth)",
                                 hoverinfo="skip", lighting=dict(ambient=.55, diffuse=.8, specular=.25)))
        fig.add_trace(go.Scatter3d(x=[cx, cx], y=[0, 0], z=[-module_mm, module_mm], mode="lines",
                                   line=dict(color=_PALETTE["dark"], width=6), showlegend=False, hoverinfo="skip"))
    fig.update_layout(scene=dict(aspectmode="data"))
    return fig


def thermal_scene(X: np.ndarray, Y: np.ndarray, temperature: np.ndarray) -> go.Figure:
    fig = _scene("3D plate heat field · color represents illustrative temperature")
    fig.add_trace(go.Surface(x=X, y=Y, z=np.zeros_like(temperature), surfacecolor=temperature,
                             colorscale="Inferno", colorbar=dict(title="°C", thickness=12),
                             name="Temperature field", hovertemplate="x=%{x:.1f} mm<br>y=%{y:.1f} mm<br>T=%{surfacecolor:.1f} °C<extra></extra>"))
    return fig


def robot_scene(x1: float, y1: float, x2: float, y2: float, l1: float, l2: float) -> go.Figure:
    fig = _scene("3D manipulator pose · planar two-link mechanism")
    fig.add_trace(go.Scatter3d(x=[0, x1, x2], y=[0, y1, y2], z=[0, 0, 0], mode="lines+markers",
                               line=dict(color=_PALETTE["blue"], width=14),
                               marker=dict(size=[10, 9, 11], color=[_PALETTE["slate"], _PALETTE["teal"], _PALETTE["orange"]]),
                               name="Robot links and joints"))
    fig.add_trace(go.Scatter3d(x=[0, 0], y=[0, 0], z=[-l1*.04, l1*.08], mode="lines",
                               line=dict(color=_PALETTE["dark"], width=16), name="Base pedestal"))
    fig.add_trace(go.Scatter3d(x=[x2, x2], y=[y2, y2], z=[0, l2*.12], mode="lines",
                               line=dict(color=_PALETTE["orange"], width=9), name="Tool axis"))
    fig.update_layout(scene=dict(aspectmode="manual", aspectratio=dict(x=1.5, y=1.2, z=.55)))
    return fig


def tensile_specimen_scene(strain_fraction: float, stress_mpa: float) -> go.Figure:
    fig = _scene("3D tensile specimen · axial extension visualization")
    length0, radius = 100.0, 5.0
    length = length0 * (1.0 + max(0.0, strain_fraction))
    axial = np.linspace(0.0, length, 32)
    theta = np.linspace(0.0, 2 * math.pi, 40)
    X = np.repeat(axial[:, None], len(theta), axis=1)
    Y = radius * np.cos(theta)[None, :] * np.ones((len(axial), 1))
    Z = radius * np.sin(theta)[None, :] * np.ones((len(axial), 1))
    colors = np.full_like(X, stress_mpa)
    fig.add_trace(go.Surface(x=X, y=Y, z=Z, surfacecolor=colors, colorscale="Turbo",
                             cmin=0, cmax=max(stress_mpa, 1.0), colorbar=dict(title="MPa", thickness=12),
                             name="Specimen surface", hovertemplate="x=%{x:.1f} mm<br>stress=%{surfacecolor:.1f} MPa<extra></extra>"))
    fig.update_layout(scene=dict(aspectmode="manual", aspectratio=dict(x=2.4, y=1, z=1)))
    return fig


def _beam_deflection(x: np.ndarray, load: float, span: float, E: float, I: float) -> np.ndarray:
    a = np.minimum(x, span - x)
    return load * a * (3.0 * span**2 - 4.0 * a**2) / (48.0 * E * I)


def beam_scene(load: float, span: float, diameter: float, E: float) -> go.Figure:
    fig = _scene("3D simply supported beam · deflection shape")
    I = math.pi * diameter**4 / 64.0
    x = np.linspace(0, span, 42)
    defl = _beam_deflection(x, load, span, E, I)
    theta = np.linspace(0, 2 * math.pi, 24)
    radius = diameter / 2.0
    X = np.repeat(x[:, None], len(theta), axis=1)
    Y = radius * np.cos(theta)[None, :] * np.ones((len(x), 1))
    Z = -defl[:, None] + radius * np.sin(theta)[None, :] * np.ones((len(x), 1))
    fig.add_trace(go.Surface(x=X, y=Y, z=Z, surfacecolor=np.repeat(defl[:, None], len(theta), axis=1),
                             colorscale="Viridis", showscale=False, name="Deflected beam", hoverinfo="skip"))
    fig.add_trace(go.Scatter3d(x=[0, span], y=[0, 0], z=[-diameter, -diameter], mode="markers",
                               marker=dict(size=9, color=_PALETTE["orange"], symbol="diamond"), name="Supports"))
    fig.add_trace(go.Scatter3d(x=[span/2, span/2], y=[0, 0], z=[diameter*1.5, diameter*.7], mode="lines+markers",
                               line=dict(color=_PALETTE["red"], width=8), marker=dict(size=5), name="Applied load direction"))
    fig.update_layout(scene=dict(aspectmode="manual", aspectratio=dict(x=2.8, y=.6, z=.8)))
    return fig


def shaft_scene(diameter: float, length: float, twist_deg: float) -> go.Figure:
    fig = _scene("3D solid shaft · accumulated torsional twist")
    L = max(length, 100.0)
    x = np.linspace(0, L, 46)
    theta = np.linspace(0, 2 * math.pi, 32)
    phase = math.radians(twist_deg) * x / L
    X = np.repeat(x[:, None], len(theta), axis=1)
    ang = theta[None, :] + phase[:, None]
    R = diameter / 2.0
    Y, Z = R * np.cos(ang), R * np.sin(ang)
    phase_color = np.repeat(np.degrees(phase)[:, None], len(theta), axis=1)
    fig.add_trace(go.Surface(x=X, y=Y, z=Z, surfacecolor=phase_color, colorscale="Turbo",
                             colorbar=dict(title="Twist °", thickness=12), name="Shaft surface"))
    fig.update_layout(scene=dict(aspectmode="manual", aspectratio=dict(x=2.6, y=1, z=1)))
    return fig


def vibration_scene(displacement_mm: float, preview_time_s: float, scale: float = 3.0) -> go.Figure:
    fig = _scene(f"3D mass–spring–damper · t={preview_time_s:.3f} s")
    r = 7.0
    mass_z = 125.0 + displacement_mm * scale
    top = mass_z - 10.0
    turns = 9
    th = np.linspace(0, 2 * math.pi * turns, 360)
    z = np.linspace(0, max(20.0, top), len(th))
    fig.add_trace(go.Scatter3d(x=r*np.cos(th), y=r*np.sin(th), z=z, mode="lines",
                               line=dict(color=_PALETTE["teal"], width=7), name="Spring"))
    fig.add_trace(go.Scatter3d(x=[0], y=[0], z=[mass_z], mode="markers+text",
                               text=["Mass"], textposition="top center",
                               marker=dict(size=19, color=_PALETTE["orange"], symbol="square"), name="Mass block"))
    fig.add_trace(go.Surface(x=[[-16, 16], [-16, 16]], y=[[-16, -16], [16, 16]], z=[[0, 0], [0, 0]],
                             opacity=.25, showscale=False, colorscale=[[0, _PALETTE["slate"]], [1, _PALETTE["slate"]]],
                             name="Ground", hoverinfo="skip"))
    fig.update_layout(scene=dict(aspectmode="manual", aspectratio=dict(x=1, y=1, z=2.8)))
    return fig


def pressure_vessel_scene(diameter: float, thickness: float, length: float, hoop_stress: float) -> go.Figure:
    fig = _scene("3D closed cylindrical shell · hoop-stress field")
    r = diameter / 2.0 + thickness / 2.0
    theta = np.linspace(0, 2 * math.pi, 54)
    z = np.linspace(0, max(length, diameter), 36)
    T, Z = np.meshgrid(theta, z)
    X, Y = r * np.cos(T), r * np.sin(T)
    stress = np.full_like(X, hoop_stress)
    fig.add_trace(go.Surface(x=X, y=Y, z=Z, surfacecolor=stress, colorscale="Turbo",
                             cmin=0, cmax=max(hoop_stress, 1), colorbar=dict(title="MPa", thickness=12),
                             name="Shell wall"))
    for zz in [0, max(length, diameter)]:
        fig.add_trace(go.Scatter3d(x=r*np.cos(theta), y=r*np.sin(theta), z=np.full_like(theta, zz),
                                   mode="lines", line=dict(color=_PALETTE["dark"], width=4), showlegend=False))
    fig.update_layout(scene=dict(aspectmode="manual", aspectratio=dict(x=1, y=1, z=2.2)))
    return fig


def pipe_flow_scene(diameter: float, length_m: float, velocity_m_s: float) -> go.Figure:
    fig = _scene("3D pipe-flow visualization · velocity arrows")
    Lmm = max(length_m * 1000.0, diameter * 3.0)
    r = diameter / 2.0
    theta = np.linspace(0, 2 * math.pi, 40)
    z = np.linspace(0, Lmm, 30)
    T, Z = np.meshgrid(theta, z)
    X, Y = r*np.cos(T), r*np.sin(T)
    fig.add_trace(go.Surface(x=X, y=Y, z=Z, opacity=.28, showscale=False,
                             colorscale=[[0, _PALETTE["blue"]], [1, _PALETTE["blue"]]],
                             name="Pipe wall", hoverinfo="skip"))
    zs = np.linspace(Lmm*.15, Lmm*.85, 6)
    fig.add_trace(go.Cone(x=np.zeros_like(zs), y=np.zeros_like(zs), z=zs,
                          u=np.zeros_like(zs), v=np.zeros_like(zs), w=np.full_like(zs, max(r*2.5, 1)),
                          anchor="tail", sizemode="absolute", sizeref=max(r*1.8, 1),
                          colorscale="Turbo", showscale=False, name=f"Flow direction · {velocity_m_s:.3f} m/s"))
    fig.update_layout(scene=dict(aspectmode="manual", aspectratio=dict(x=1, y=1, z=3.2)))
    return fig


def fem_beam_scene(node_x: list[float], deflection_mm: list[float], diameter: float,
                   displacement_scale: float = 4.0) -> go.Figure:
    fig = _scene("3D FEM beam mesh · deformed shape")
    x = np.linspace(float(min(node_x)), float(max(node_x)), 60)
    w = np.interp(x, np.asarray(node_x, dtype=float), np.asarray(deflection_mm, dtype=float))
    theta = np.linspace(0, 2*math.pi, 24)
    R = diameter/2.0
    X = np.repeat(x[:, None], len(theta), axis=1)
    Y = R*np.cos(theta)[None, :]*np.ones((len(x), 1))
    Z = displacement_scale*w[:, None] + R*np.sin(theta)[None, :]*np.ones((len(x), 1))
    fig.add_trace(go.Surface(x=X, y=Y, z=Z, surfacecolor=np.repeat(np.abs(w)[:, None], len(theta), axis=1),
                             colorscale="Viridis", showscale=False, name="Deformed beam"))
    # Mesh nodes are marked along the beam centreline.
    fig.add_trace(go.Scatter3d(x=node_x, y=np.zeros(len(node_x)), z=displacement_scale*np.asarray(deflection_mm),
                               mode="markers", marker=dict(size=3, color=_PALETTE["orange"]), name="FE nodes"))
    fig.update_layout(scene=dict(aspectmode="manual", aspectratio=dict(x=2.8, y=.6, z=.8)))
    return fig


def crank_slider_scene(angle_deg: float, crank_radius: float = 45.0, rod_length: float = 170.0) -> tuple[go.Figure, float]:
    theta = math.radians(angle_deg)
    y = crank_radius * math.sin(theta)
    slider_x = crank_radius * math.cos(theta) + math.sqrt(max(rod_length**2-y**2, 0.0))
    crank_x, crank_z = crank_radius*math.cos(theta), crank_radius*math.sin(theta)
    fig = _scene("3D slider-crank teaching mechanism")
    fig.add_trace(go.Scatter3d(x=[0, crank_x], y=[0, 0], z=[0, crank_z], mode="lines+markers",
                               line=dict(color=_PALETTE["blue"], width=13), marker=dict(size=8), name="Crank"))
    fig.add_trace(go.Scatter3d(x=[crank_x, slider_x], y=[0, 0], z=[crank_z, 0], mode="lines+markers",
                               line=dict(color=_PALETTE["teal"], width=11), marker=dict(size=7), name="Connecting rod"))
    fig.add_trace(go.Scatter3d(x=[slider_x], y=[0], z=[0], mode="markers+text", text=["Slider"],
                               textposition="top center", marker=dict(size=18, symbol="square", color=_PALETTE["orange"]),
                               name="Slider block"))
    fig.add_trace(go.Scatter3d(x=[0], y=[0], z=[0], mode="markers", marker=dict(size=14, color=_PALETTE["dark"]), name="Crank pivot"))
    fig.update_layout(scene=dict(aspectmode="manual", aspectratio=dict(x=2.5, y=.7, z=1.2)))
    return fig, slider_x
