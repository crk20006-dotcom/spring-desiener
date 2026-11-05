import numpy as np
from visualization import (
    spring_scene, gear_scene, thermal_scene, robot_scene, tensile_specimen_scene,
    beam_scene, shaft_scene, vibration_scene, pressure_vessel_scene,
    pipe_flow_scene, fem_beam_scene, crank_slider_scene,
)


def _assert_is_3d(fig):
    assert fig.layout.scene is not None
    assert any(getattr(trace, "type", "") in {"surface", "mesh3d", "scatter3d", "cone"}
               for trace in fig.data)
    # Serialize through Plotly's validator to catch malformed trace properties.
    assert '"scene"' in fig.to_json()


def test_every_workspace_has_a_serializable_3d_scene():
    x, y = np.meshgrid(np.linspace(-20, 20, 9), np.linspace(-20, 20, 9))
    scenes = [
        spring_scene(4, 25, 8, 50),
        gear_scene(20, 60, 2, 30),
        thermal_scene(x, y, 20 + 100*np.exp(-(x*x+y*y)/100)),
        robot_scene(150, 100, 300, 200, 300, 220),
        tensile_specimen_scene(.01, 200),
        beam_scene(500, 500, 20, 200000),
        shaft_scene(30, 1000, 2.5),
        vibration_scene(4.2, .5),
        pressure_vessel_scene(500, 10, 1000, 25),
        pipe_flow_scene(50, 100, 1.5),
        fem_beam_scene([0, 100, 200], [0, -.2, -.4], 20),
        crank_slider_scene(40)[0],
    ]
    assert len(scenes) == 12
    for scene in scenes:
        _assert_is_3d(scene)
