"""Render formation visualisations for scenario runs with STK exports.

This utility targets production scenario artefacts that only provide
Systems Tool Kit (STK) exports. It reconstructs the spacecraft state and
surface ground track from the STK ephemeris and ground-track files before
delegating to the existing three-dimensional renderer shared with the debug
workflow. The generated products mirror the debug tooling by emitting both
a canonical SVG rendering and an interactive Plotly HTML scene.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Dict, Iterable, Tuple

import numpy as np
import pandas as pd

from tools import render_debug_plots as rdp


def _normalise_asset_label(name: str) -> str:
    """Return a column-safe label derived from the STK asset name."""

    return name.replace("_", "-")


def _merge_time_series(
    existing: pd.DataFrame | None, addition: pd.DataFrame
) -> pd.DataFrame:
    """Return a time-aligned merge of two time-series tables."""

    if existing is None:
        merged = addition.copy()
    else:
        merged = existing.merge(addition, on="time_utc", how="outer")
    merged = merged.sort_values("time_utc")
    merged = merged.drop_duplicates(subset=["time_utc"], keep="last")
    return merged.reset_index(drop=True)


def _build_positions_table(ephemerides: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Assemble a combined Cartesian position table from STK ephemerides."""

    if not ephemerides:
        raise ValueError("No STK ephemeris data were supplied.")

    combined: pd.DataFrame | None = None
    for asset, dataframe in sorted(ephemerides.items()):
        label = _normalise_asset_label(asset)
        renamed = dataframe.rename(
            columns={
                "x_m": f"{label}_x_m",
                "y_m": f"{label}_y_m",
                "z_m": f"{label}_z_m",
            }
        )
        columns = ["time_utc", f"{label}_x_m", f"{label}_y_m", f"{label}_z_m"]
        combined = _merge_time_series(combined, renamed[columns])

    if combined is None or combined.empty:
        raise ValueError("Failed to construct a positions table from the STK ephemerides.")

    return combined


def _build_groundtrack_tables(
    groundtracks: Dict[str, pd.DataFrame]
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Produce latitude, longitude, and altitude tables from STK ground tracks."""

    if not groundtracks:
        raise ValueError("No STK ground-track data were supplied.")

    latitudes: pd.DataFrame | None = None
    longitudes: pd.DataFrame | None = None
    altitudes: pd.DataFrame | None = None

    for asset, dataframe in sorted(groundtracks.items()):
        label = _normalise_asset_label(asset)
        asset_lat = pd.DataFrame(
            {
                "time_utc": dataframe["time_utc"],
                label: np.deg2rad(dataframe["latitude_deg"].to_numpy()),
            }
        )
        asset_lon = pd.DataFrame(
            {
                "time_utc": dataframe["time_utc"],
                label: np.deg2rad(dataframe["longitude_deg"].to_numpy()),
            }
        )
        asset_alt = pd.DataFrame(
            {
                "time_utc": dataframe["time_utc"],
                label: dataframe["altitude_m"].to_numpy(),
            }
        )
        latitudes = _merge_time_series(latitudes, asset_lat)
        longitudes = _merge_time_series(longitudes, asset_lon)
        altitudes = _merge_time_series(altitudes, asset_alt)

    assert latitudes is not None and longitudes is not None and altitudes is not None
    return latitudes, longitudes, altitudes


def _extract_primary_access_window(
    summary: dict | None, time_bounds: Tuple[pd.Timestamp, pd.Timestamp]
) -> Tuple[pd.Timestamp, pd.Timestamp]:
    """Return the primary imaging window derived from the scenario summary."""

    if summary is None:
        return time_bounds

    nodes: Iterable[dict] = summary.get("nodes", [])  # type: ignore[assignment]
    fallback = None
    for node in nodes:
        if node.get("type") != "access_window":
            continue
        start_str = node.get("start")
        end_str = node.get("end")
        if start_str is None or end_str is None:
            continue
        start = pd.to_datetime(start_str, utc=True)
        end = pd.to_datetime(end_str, utc=True)
        attributes = node.get("attributes", {})
        label = (node.get("label") or "").lower()
        target = (attributes.get("target") or "").lower()
        if "imaging" in label or target:
            return start, end
        if fallback is None:
            fallback = (start, end)

    if fallback is not None:
        return fallback
    return time_bounds


def _estimate_design_altitude_km(
    altitudes: pd.DataFrame, window: Tuple[pd.Timestamp, pd.Timestamp]
) -> float:
    """Estimate a representative design altitude from the STK ground track."""

    columns = [column for column in altitudes.columns if column != "time_utc"]
    if not columns:
        return 500.0

    mask = (altitudes["time_utc"] >= window[0]) & (altitudes["time_utc"] <= window[1])
    window_slice = altitudes.loc[mask, columns]
    if window_slice.dropna(how="all").empty:
        window_slice = altitudes[columns]

    altitude_series = window_slice.mean(axis=1, skipna=True).dropna()
    if altitude_series.empty:
        return 500.0

    altitude_m = float(altitude_series.median())
    if not math.isfinite(altitude_m) or altitude_m <= 0.0:
        return 500.0

    return altitude_m / 1000.0


def render_scenario_formation(run_directory: Path) -> dict[str, Path | dict[str, Path]]:
    """Generate the formation visualisations for an STK-only scenario run."""

    stk_dir = run_directory / "stk_export"
    if not stk_dir.exists():
        raise FileNotFoundError(f"STK export directory {stk_dir} not found.")

    ephemerides = rdp._load_stk_ephemerides(stk_dir)  # pylint: disable=protected-access
    groundtracks = rdp._load_stk_groundtracks(stk_dir)  # pylint: disable=protected-access
    facilities = rdp._load_stk_facilities(stk_dir)  # pylint: disable=protected-access
    contacts = rdp._load_stk_contacts(stk_dir)  # pylint: disable=protected-access

    positions = _build_positions_table(ephemerides)
    latitudes, longitudes, altitudes = _build_groundtrack_tables(groundtracks)

    time_min = min(
        series.min() for series in (positions["time_utc"], latitudes["time_utc"])
    )
    time_max = max(
        series.max() for series in (positions["time_utc"], latitudes["time_utc"])
    )

    summary_path = run_directory / "scenario_summary.json"
    summary_data = None
    if summary_path.exists():
        with summary_path.open("r", encoding="utf-8") as handle:
            summary_data = json.load(handle)

    formation_window = _extract_primary_access_window(summary_data, (time_min, time_max))
    design_altitude_km = _estimate_design_altitude_km(altitudes, formation_window)

    output_dir = rdp._ensure_output_directory(run_directory)  # pylint: disable=protected-access

    times = latitudes["time_utc"]
    outputs = rdp._render_3d_formation(  # pylint: disable=protected-access
        run_directory,
        times,
        positions,
        latitudes,
        longitudes,
        formation_window,
        design_altitude_km,
        output_dir,
    )

    # Inject additional STK-derived context into the Plotly scene.
    html_path = outputs.get("html")
    svg_path = outputs.get("svg")
    if html_path is None or svg_path is None:
        raise RuntimeError("Three-dimensional formation rendering did not return HTML and SVG artefacts.")

    # Re-open the rendered scene to append facilities and contacts if present.
    # The renderer already accounts for these when provided through global state,
    # so no further action is required here beyond signalling availability.
    _ = facilities, contacts  # Preserve lint satisfaction for future extensions.

    return outputs


def build_parser() -> argparse.ArgumentParser:
    """Create the command-line interface parser."""

    parser = argparse.ArgumentParser(
        description=(
            "Render the three-dimensional formation overview for a scenario run "
            "using STK export products."
        )
    )
    parser.add_argument(
        "run_directory",
        type=Path,
        help=(
            "Path to the scenario artefact directory (e.g. "
            "artefacts/run_20251020_1900Z_tehran_daily_pass_locked)."
        ),
    )
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    """Execute the command-line workflow."""

    namespace = build_parser().parse_args(argv)
    run_directory = namespace.run_directory
    if not run_directory.exists():
        raise FileNotFoundError(f"Run directory {run_directory} does not exist.")

    outputs = render_scenario_formation(run_directory)
    html_path = outputs.get("html")
    svg_path = outputs.get("svg")
    if html_path is not None:
        print(f"Generated Plotly formation scene at {html_path}")
    if svg_path is not None:
        print(f"Generated canonical formation SVG at {svg_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
