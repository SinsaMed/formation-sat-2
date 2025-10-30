"""Unit tests for the debug plot rendering utilities."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from tools import render_debug_plots


def test_render_3d_outputs_vector_svg(tmp_path: Path) -> None:
    """The three-dimensional renderer should emit a vector-only SVG artefact."""

    time_index = pd.date_range("2025-03-20T00:00:00Z", periods=5, freq="min", tz="UTC")
    positions = pd.DataFrame(
        {
            "time_utc": time_index,
            "SAT-1_x_m": np.linspace(6.9e6, 7.0e6, 5),
            "SAT-1_y_m": np.linspace(0.0, 1.0e5, 5),
            "SAT-1_z_m": np.linspace(0.0, 2.0e5, 5),
            "SAT-2_x_m": np.linspace(-6.9e6, -7.0e6, 5),
            "SAT-2_y_m": np.linspace(0.0, -1.0e5, 5),
            "SAT-2_z_m": np.linspace(0.0, -2.0e5, 5),
            "SAT-3_x_m": np.linspace(0.0, 5.0e4, 5),
            "SAT-3_y_m": np.linspace(6.9e6, 7.0e6, 5),
            "SAT-3_z_m": np.linspace(-5.0e4, 5.0e4, 5),
        }
    )

    latitudes = pd.DataFrame(
        {
            "SAT-1": np.linspace(np.radians(35.5), np.radians(36.0), len(time_index)),
            "SAT-2": np.linspace(np.radians(35.5), np.radians(35.0), len(time_index)),
            "SAT-3": np.linspace(np.radians(35.7), np.radians(35.9), len(time_index)),
        }
    )
    longitudes = pd.DataFrame(
        {
            "SAT-1": np.linspace(np.radians(51.2), np.radians(51.4), len(time_index)),
            "SAT-2": np.linspace(np.radians(51.2), np.radians(51.0), len(time_index)),
            "SAT-3": np.linspace(np.radians(51.3), np.radians(51.5), len(time_index)),
        }
    )

    formation_window = (time_index[1], time_index[3])
    design_altitude_km = 520.0
    run_dir = tmp_path / "run"
    output_dir = tmp_path / "artefacts"
    run_dir.mkdir()
    output_dir.mkdir()

    artefacts = render_debug_plots._render_3d_formation(  # noqa: SLF001
        run_dir,
        positions["time_utc"],
        positions,
        latitudes,
        longitudes,
        formation_window,
        design_altitude_km,
        output_dir,
    )

    svg_path = artefacts["svg"]
    html_path = artefacts["html"]

    assert svg_path.exists()
    assert html_path.exists()

    svg_payload = svg_path.read_text(encoding="utf-8").lower()
    assert "<svg" in svg_payload
    assert "<image" not in svg_payload

    html_payload = html_path.read_text(encoding="utf-8")
    assert "plotly" in html_payload
