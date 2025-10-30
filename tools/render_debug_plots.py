"""Generate SVG and HTML visualisations for debug artefacts.

This utility reads the CSV exports produced by ``run_debug.py`` for the
Tehran triangle scenario and renders time-series charts alongside an
interactive three-dimensional formation view. The canonical three-dimensional
representation is emitted as an SVG for archival review, whilst an HTML scene
remains available for exploratory analysis via Plotly.
"""

from __future__ import annotations

import argparse
import json
import logging
import math
from datetime import timedelta
from pathlib import Path
from typing import Iterable, List, Tuple, Optional, Dict

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
from plotly.colors import qualitative
from plotly.subplots import make_subplots
from matplotlib.lines import Line2D
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401  # Required for 3D projection

try:  # pragma: no cover - optional dependency
    import cartopy.crs as ccrs
    import cartopy.feature as cfeature
except Exception:  # pragma: no cover - optional dependency
    ccrs = None
    cfeature = None

try:  # pragma: no cover - optional dependency
    from shapely.geometry import LineString, MultiLineString
except Exception:  # pragma: no cover - optional dependency
    LineString = None
    MultiLineString = None


LOGGER = logging.getLogger(__name__)


CLASSICAL_ELEMENT_FIELDS = (
    "semi_major_axis_km",
    "eccentricity",
    "inclination_deg",
    "raan_deg",
    "argument_of_perigee_deg",
    "mean_anomaly_deg",
)

CLASSICAL_ELEMENT_LABELS = {
    "semi_major_axis_km": "Semi-major axis (km)",
    "eccentricity": "Eccentricity (–)",
    "inclination_deg": "Inclination (deg)",
    "raan_deg": "RAAN (deg)",
    "argument_of_perigee_deg": "Argument of perigee (deg)",
    "mean_anomaly_deg": "Mean anomaly (deg)",
}


TEHRAN_LATITUDE_DEG = 35.6892
TEHRAN_LONGITUDE_DEG = 51.3890
EARTH_MEAN_RADIUS_KM = 6371.0

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _load_sensor_swath_width_km() -> float:
    """Return the primary sensor swath width declared in the project configuration."""

    project_config = PROJECT_ROOT / "config" / "project.yaml"
    if not project_config.exists():
        LOGGER.warning("Project configuration %s not found; using default swath width.", project_config)
        return 60.0

    try:
        import yaml
    except ImportError:  # pragma: no cover - dependency is part of requirements
        LOGGER.warning("PyYAML not available; falling back to default swath width value.")
        return 60.0

    try:
        with project_config.open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle)
    except (OSError, yaml.YAMLError) as exc:  # pragma: no cover - defensive
        LOGGER.warning("Failed to parse %s: %s", project_config, exc)
        return 60.0

    try:
        swath_width = float(
            data["platform"]["payload"]["primary_sensor"]["swath_width_km"]
        )
    except (KeyError, TypeError, ValueError):  # pragma: no cover - defensive
        LOGGER.warning(
            "platform.payload.primary_sensor.swath_width_km missing or invalid in %s; using default.",
            project_config,
        )
        return 60.0

    return swath_width


def _wrap_longitudes_around_tehran(longitudes_rad: np.ndarray) -> np.ndarray:
    """Normalise longitudes around Tehran to avoid map discontinuities."""

    unwrapped = np.rad2deg(np.unwrap(longitudes_rad))
    centred = ((unwrapped - TEHRAN_LONGITUDE_DEG + 180.0) % 360.0) - 180.0
    return centred + TEHRAN_LONGITUDE_DEG


def _load_lat_lon(run_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    lat_path = run_dir / "latitudes_rad.csv"
    lon_path = run_dir / "longitudes_rad.csv"
    if not lat_path.exists() or not lon_path.exists():
        raise FileNotFoundError(
            "Expected latitudes_rad.csv and longitudes_rad.csv within the run directory."
        )

    lat_df = pd.read_csv(lat_path, parse_dates=["time_utc"])
    lon_df = pd.read_csv(lon_path, parse_dates=["time_utc"])
    return lat_df, lon_df


def _load_altitudes(run_dir: Path) -> pd.DataFrame:
    altitude_path = run_dir / "altitudes_m.csv"
    if not altitude_path.exists():
        raise FileNotFoundError(
            "Expected altitudes_m.csv within the run directory."
        )

    dataframe = pd.read_csv(altitude_path, parse_dates=["time_utc"])
    value_columns = [
        column for column in dataframe.columns if column != "time_utc"
    ]
    if value_columns:
        dataframe[value_columns] = dataframe[value_columns].apply(
            pd.to_numeric, errors="coerce"
        )
    return dataframe


def _load_positions(run_dir: Path) -> pd.DataFrame:
    pos_path = run_dir / "positions_m.csv"
    if not pos_path.exists():
        raise FileNotFoundError("Expected positions_m.csv within the run directory.")

    return pd.read_csv(pos_path, parse_dates=["time_utc"])


def _cartesian_from_lat_lon(
    latitude_deg: np.ndarray,
    longitude_deg: np.ndarray,
    radius_m: float,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Convert spherical coordinates to Cartesian arrays."""

    lat_rad = np.deg2rad(latitude_deg)
    lon_rad = np.deg2rad(longitude_deg)
    cos_lat = np.cos(lat_rad)
    x = radius_m * cos_lat * np.cos(lon_rad)
    y = radius_m * cos_lat * np.sin(lon_rad)
    z = radius_m * np.sin(lat_rad)
    return x, y, z


def _parse_stk_epoch(value: str) -> pd.Timestamp:
    """Parse an STK timestamp expressed as ``DD Mon YYYY HH:MM:SS.sss``."""

    timestamp = pd.to_datetime(value + "Z", utc=True, format="%d %b %Y %H:%M:%S.%fZ")
    if pd.isna(timestamp):
        raise ValueError(f"Failed to parse STK timestamp: {value}")
    return timestamp


def _load_stk_ephemerides(stk_dir: Path) -> dict[str, pd.DataFrame]:
    """Read all STK ephemeris files available in the directory."""

    ephemerides: dict[str, pd.DataFrame] = {}
    for ephemeris_file in sorted(stk_dir.glob("*.e")):
        name = ephemeris_file.stem
        with ephemeris_file.open("r", encoding="utf-8") as handle:
            epoch: Optional[pd.Timestamp] = None
            rows: list[tuple[pd.Timestamp, float, float, float]] = []
            for line in handle:
                stripped = line.strip()
                if stripped.startswith("ScenarioEpoch"):
                    epoch = _parse_stk_epoch(stripped.split("ScenarioEpoch", 1)[1].strip())
                elif stripped.startswith("BEGIN EphemerisTimePosVel"):
                    break

            if epoch is None:
                LOGGER.warning("%s missing ScenarioEpoch; skipping ephemeris import.", ephemeris_file)
                continue

            for line in handle:
                stripped = line.strip()
                if stripped.startswith("END EphemerisTimePosVel"):
                    break
                if not stripped or stripped.startswith("#"):
                    continue
                parts = stripped.split()
                if len(parts) < 4:
                    continue
                try:
                    offset = float(parts[0])
                    x_km, y_km, z_km = map(float, parts[1:4])
                except ValueError:
                    continue
                timestamp = epoch + timedelta(seconds=offset)
                rows.append((timestamp, x_km * 1000.0, y_km * 1000.0, z_km * 1000.0))

        if rows:
            df = pd.DataFrame(rows, columns=["time_utc", "x_m", "y_m", "z_m"])
            ephemerides[name] = df

    return ephemerides


def _load_stk_groundtracks(stk_dir: Path) -> dict[str, pd.DataFrame]:
    """Read STK ground track files if available."""

    groundtracks: dict[str, pd.DataFrame] = {}
    for gt_file in sorted(stk_dir.glob("*groundtrack.gt")):
        name = gt_file.stem.replace("_groundtrack", "")
        with gt_file.open("r", encoding="utf-8") as handle:
            epoch: Optional[pd.Timestamp] = None
            rows: list[tuple[pd.Timestamp, float, float, float]] = []
            for line in handle:
                stripped = line.strip()
                if stripped.startswith("ScenarioEpoch"):
                    epoch = _parse_stk_epoch(stripped.split("ScenarioEpoch", 1)[1].strip())
                elif stripped.startswith("BEGIN Points"):
                    break

            if epoch is None:
                LOGGER.warning("%s missing ScenarioEpoch; skipping ground track import.", gt_file)
                continue

            for line in handle:
                stripped = line.strip()
                if stripped.startswith("END Points"):
                    break
                if not stripped or stripped.startswith("#"):
                    continue
                parts = stripped.split()
                if len(parts) < 4:
                    continue
                try:
                    offset = float(parts[0])
                    latitude = float(parts[1])
                    longitude = float(parts[2])
                    altitude_km = float(parts[3])
                except ValueError:
                    continue
                timestamp = epoch + timedelta(seconds=offset)
                rows.append((timestamp, latitude, longitude, altitude_km * 1000.0))

        if rows:
            df = pd.DataFrame(
                rows,
                columns=["time_utc", "latitude_deg", "longitude_deg", "altitude_m"],
            )
            groundtracks[name] = df

    return groundtracks


def _load_stk_facilities(stk_dir: Path) -> dict[str, dict[str, float]]:
    """Parse facility definitions exported for STK."""

    facilities: dict[str, dict[str, float]] = {}
    for fac_file in sorted(stk_dir.glob("*.fac")):
        name = fac_file.stem.replace("Facility_", "")
        latitude = longitude = altitude = None
        with fac_file.open("r", encoding="utf-8") as handle:
            for line in handle:
                stripped = line.strip()
                if stripped.startswith("Latitude"):
                    try:
                        latitude = float(stripped.split()[1])
                    except (ValueError, IndexError):
                        latitude = None
                elif stripped.startswith("Longitude"):
                    try:
                        longitude = float(stripped.split()[1])
                    except (ValueError, IndexError):
                        longitude = None
                elif stripped.startswith("Altitude"):
                    try:
                        altitude = float(stripped.split()[1])
                    except (ValueError, IndexError):
                        altitude = None
        if latitude is None or longitude is None:
            continue
        facilities[name] = {
            "latitude_deg": latitude,
            "longitude_deg": longitude,
            "altitude_km": 0.0 if altitude is None else altitude / 1000.0,
        }
    return facilities


def _load_stk_contacts(stk_dir: Path) -> dict[str, list[dict[str, object]]]:
    """Return contact intervals keyed by filename stem."""

    contacts: dict[str, list[dict[str, object]]] = {}
    for contact_file in sorted(stk_dir.glob("*.int")):
        name = contact_file.stem.replace("Contacts_", "")
        intervals: list[dict[str, object]] = []
        with contact_file.open("r", encoding="utf-8") as handle:
            current: dict[str, object] | None = None
            for line in handle:
                stripped = line.strip()
                if stripped.startswith("BEGIN Interval"):
                    current = {}
                elif stripped.startswith("END Interval") and current is not None:
                    intervals.append(current)
                    current = None
                elif current is not None:
                    if stripped.startswith("Asset"):
                        parts = stripped.split()
                        if len(parts) >= 2:
                            current["asset"] = parts[1]
                    elif stripped.startswith("StartTime"):
                        current["start"] = _parse_stk_epoch(stripped.split("StartTime", 1)[1].strip())
                    elif stripped.startswith("StopTime"):
                        current["end"] = _parse_stk_epoch(stripped.split("StopTime", 1)[1].strip())
        if intervals:
            contacts[name] = intervals

    return contacts


def _build_coastline_traces(earth_radius_m: float) -> list[go.Scatter3d]:
    """Generate coastline polylines projected on the Earth sphere."""

    if cfeature is None:
        return []

    coast_feature = cfeature.NaturalEarthFeature("physical", "coastline", "110m")
    traces: list[go.Scatter3d] = []
    try:
        geometries = list(coast_feature.geometries())
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.warning("Failed to load Natural Earth coastline data: %s", exc)
        return traces

    for geometry in geometries:
        components = []
        if hasattr(geometry, "geoms"):
            for geom in geometry.geoms:
                components.append(geom)
        else:
            components.append(geometry)

        for component in components:
            coords = list(component.coords)
            if len(coords) < 2:
                continue
            if len(coords) > 1000:
                step = max(1, len(coords) // 1000)
                coords = coords[::step]
            lon, lat = zip(*coords)
            x, y, z = _cartesian_from_lat_lon(np.array(lat), np.array(lon), earth_radius_m)
            traces.append(
                go.Scatter3d(
                    x=x,
                    y=y,
                    z=z,
                    mode="lines",
                    line=dict(color="rgba(255,255,255,0.6)", width=1),
                    name="Coastlines",
                    showlegend=False,
                    hoverinfo="skip",
                )
            )

    return traces


def _create_cone_mesh(
    apex: np.ndarray,
    target: np.ndarray,
    half_angle_rad: float,
    name: str,
    colour: str,
) -> go.Mesh3d:
    """Construct a conical field-of-view mesh between a spacecraft and the target."""

    axis = target - apex
    length = float(np.linalg.norm(axis))
    if not math.isfinite(length) or length <= 0:
        raise ValueError("Apex and target must not coincide when constructing a cone.")

    axis_unit = axis / length
    base_radius = length * math.tan(half_angle_rad)

    reference = np.array([0.0, 0.0, 1.0])
    cross = np.cross(axis_unit, reference)
    norm = np.linalg.norm(cross)
    if norm < 1e-6:
        reference = np.array([0.0, 1.0, 0.0])
        cross = np.cross(axis_unit, reference)
        norm = np.linalg.norm(cross)
        if norm < 1e-6:
            raise ValueError("Unable to construct orthonormal basis for cone generation.")

    u = cross / norm
    v = np.cross(axis_unit, u)

    segments = 48
    angles = np.linspace(0, 2 * math.pi, segments, endpoint=False)
    vertices = [apex]
    for angle in angles:
        direction = math.cos(angle) * u + math.sin(angle) * v
        point = target + base_radius * direction
        vertices.append(point)

    vertices_array = np.vstack(vertices)
    apex_index = 0
    i_indices: list[int] = []
    j_indices: list[int] = []
    k_indices: list[int] = []
    for idx in range(1, segments + 1):
        next_idx = 1 + (idx % segments)
        i_indices.append(apex_index)
        j_indices.append(idx)
        k_indices.append(next_idx)

    colour_rgba = colour
    return go.Mesh3d(
        x=vertices_array[:, 0],
        y=vertices_array[:, 1],
        z=vertices_array[:, 2],
        i=i_indices,
        j=j_indices,
        k=k_indices,
        opacity=0.25,
        color=colour_rgba,
        name=f"{name} FOV",
        showscale=False,
    )


def _load_orbital_elements(run_dir: Path) -> pd.DataFrame:
    orbital_path = run_dir / "orbital_elements.csv"
    if not orbital_path.exists():
        raise FileNotFoundError(
            "Expected orbital_elements.csv within the run directory."
        )

    dataframe = pd.read_csv(orbital_path, parse_dates=["time_utc"])
    value_columns = [
        column
        for column in dataframe.columns
        if column not in {"time_utc", "satellite_id"}
    ]
    dataframe[value_columns] = dataframe[value_columns].apply(
        pd.to_numeric, errors="coerce"
    )
    return dataframe


def _load_ground_command_ranges(run_dir: Path) -> pd.DataFrame:
    ground_path = run_dir / "ground_ranges.csv"
    if not ground_path.exists():
        raise FileNotFoundError(
            "Expected ground_ranges.csv within the run directory."
        )

    dataframe = pd.read_csv(ground_path, parse_dates=["time_utc"])
    numeric_columns = [
        column for column in dataframe.columns if column != "time_utc"
    ]
    dataframe[numeric_columns] = dataframe[numeric_columns].apply(
        pd.to_numeric, errors="coerce"
    )
    return dataframe


def _load_triangle_geometry(run_dir: Path) -> pd.DataFrame:
    geometry_path = run_dir / "triangle_geometry.csv"
    if not geometry_path.exists():
        raise FileNotFoundError(
            "Expected triangle_geometry.csv within the run directory."
        )

    dataframe = pd.read_csv(geometry_path, parse_dates=["time_utc"])
    numeric_columns = [
        column for column in dataframe.columns if column != "time_utc"
    ]
    dataframe[numeric_columns] = dataframe[numeric_columns].apply(
        pd.to_numeric, errors="coerce"
    )
    return dataframe


def _load_formation_window(run_dir: Path) -> Tuple[pd.Timestamp, pd.Timestamp]:
    summary_path = run_dir / "triangle_summary.json"
    if not summary_path.exists():
        raise FileNotFoundError(
            "Expected triangle_summary.json within the run directory to derive formation window."
        )

    with summary_path.open("r", encoding="utf-8") as handle:
        summary = json.load(handle)

    try:
        window = summary["metrics"]["formation_window"]
        start = pd.to_datetime(window["start"], utc=True)
        end = pd.to_datetime(window["end"], utc=True)
    except (KeyError, TypeError) as exc:  # pragma: no cover - defensive
        raise KeyError(
            "triangle_summary.json is missing metrics.formation_window start/end entries."
        ) from exc

    if pd.isna(start) or pd.isna(end):
        raise ValueError("Formation window timestamps could not be parsed into datetimes.")

    if start >= end:
        raise ValueError("Formation window start time must precede the end time.")

    return start, end


def _resolve_configuration_path(run_dir: Path) -> Optional[Path]:
    metadata_path = run_dir / "run_metadata.json"
    if metadata_path.exists():
        try:
            with metadata_path.open("r", encoding="utf-8") as handle:
                metadata = json.load(handle)
        except (OSError, json.JSONDecodeError) as exc:
            LOGGER.warning("Failed to parse %s: %s", metadata_path, exc)
        else:
            scenario_path = metadata.get("scenario_path")
            if isinstance(scenario_path, str):
                candidate = Path(scenario_path)
                if not candidate.is_absolute():
                    candidate = PROJECT_ROOT / candidate
                if candidate.exists():
                    return candidate
                LOGGER.warning(
                    "Scenario path %s from %s does not exist.",
                    candidate,
                    metadata_path,
                )

    default_path = PROJECT_ROOT / "config" / "scenarios" / "tehran_triangle.json"
    if default_path.exists():
        return default_path
    return None


def _load_design_altitude_km(run_dir: Path) -> float:
    config_path = _resolve_configuration_path(run_dir)
    if config_path is None:
        LOGGER.warning(
            "Design altitude unavailable; formation configuration file not located."
        )
        return float("nan")

    try:
        with config_path.open("r", encoding="utf-8") as handle:
            config = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        LOGGER.warning("Failed to parse formation configuration %s: %s", config_path, exc)
        return float("nan")

    try:
        reference = config["reference_orbit"]
        semi_major_axis = float(reference["semi_major_axis_km"])
    except (KeyError, TypeError, ValueError) as exc:
        LOGGER.warning(
            "reference_orbit.semi_major_axis_km missing or invalid in %s: %s",
            config_path,
            exc,
        )
        return float("nan")

    design_altitude = semi_major_axis - EARTH_MEAN_RADIUS_KM
    if not math.isfinite(design_altitude):
        return float("nan")
    return design_altitude


def _load_geometry_tolerances(run_dir: Path) -> dict[str, float]:
    tolerances = {
        "nominal_side_m": float("nan"),
        "side_fraction": 0.05,
        "aspect_ratio_limit": 1.02,
    }

    config_path = _resolve_configuration_path(run_dir)
    if config_path is None:
        LOGGER.warning(
            "Falling back to default triangle tolerances; configuration file not located."
        )
        return tolerances

    try:
        with config_path.open("r", encoding="utf-8") as handle:
            config = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        LOGGER.warning("Failed to parse formation configuration %s: %s", config_path, exc)
        return tolerances

    formation = config.get("formation", {})
    if isinstance(formation, dict):
        side_length = formation.get("side_length_m")
        if side_length is not None:
            try:
                tolerances["nominal_side_m"] = float(side_length)
            except (TypeError, ValueError):
                LOGGER.warning(
                    "side_length_m in %s is not numeric; retaining default.",
                    config_path,
                )

        fraction_value = formation.get("side_length_tolerance_fraction")
        if fraction_value is None:
            percent_value = formation.get("side_length_tolerance_percent")
            if percent_value is not None:
                try:
                    fraction_value = float(percent_value) / 100.0
                except (TypeError, ValueError):
                    fraction_value = None
        if fraction_value is not None:
            try:
                tolerances["side_fraction"] = float(fraction_value)
            except (TypeError, ValueError):
                LOGGER.warning(
                    "Side-length tolerance in %s is invalid; retaining default.",
                    config_path,
                )

        aspect_limit = formation.get("aspect_ratio_tolerance")
        if aspect_limit is not None:
            try:
                tolerances["aspect_ratio_limit"] = float(aspect_limit)
            except (TypeError, ValueError):
                LOGGER.warning(
                    "Aspect ratio tolerance in %s is invalid; retaining default.",
                    config_path,
                )

    return tolerances


def _load_ground_command_limits(run_dir: Path) -> dict[str, float]:
    limits = {
        "ground_tolerance_km": float("nan"),
        "command_contact_range_km": float("nan"),
    }

    config_path = _resolve_configuration_path(run_dir)
    if config_path is None:
        LOGGER.warning(
            "Falling back to default ground and command limits; configuration file not located."
        )
        return limits

    try:
        with config_path.open("r", encoding="utf-8") as handle:
            config = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        LOGGER.warning(
            "Failed to parse formation configuration %s: %s", config_path, exc
        )
        return limits

    formation = config.get("formation", {})
    if isinstance(formation, dict):
        tolerance = formation.get("ground_tolerance_km")
        if tolerance is not None:
            try:
                limits["ground_tolerance_km"] = float(tolerance)
            except (TypeError, ValueError):
                LOGGER.warning(
                    "ground_tolerance_km in %s is not numeric; retaining default.",
                    config_path,
                )

        command_cfg = formation.get("command", {})
        if isinstance(command_cfg, dict):
            contact_range = command_cfg.get("contact_range_km")
            if contact_range is not None:
                try:
                    limits["command_contact_range_km"] = float(contact_range)
                except (TypeError, ValueError):
                    LOGGER.warning(
                        "command.contact_range_km in %s is not numeric; retaining default.",
                        config_path,
                    )

    return limits


def _reshape_orbital_elements(
    dataframe: pd.DataFrame,
) -> dict[str, pd.DataFrame]:
    """Pivot the orbital elements into per-satellite time series."""

    if dataframe.empty:
        raise ValueError("Orbital elements CSV is empty.")

    missing_columns = [
        field for field in CLASSICAL_ELEMENT_FIELDS if field not in dataframe.columns
    ]
    if missing_columns:
        raise ValueError(
            "Orbital elements CSV is missing columns: " + ", ".join(missing_columns)
        )

    dataframe = dataframe.sort_values("time_utc").copy()
    satellites = sorted(dataframe["satellite_id"].unique())
    pivots: dict[str, pd.DataFrame] = {}
    for field in CLASSICAL_ELEMENT_FIELDS:
        pivot = dataframe.pivot(
            index="time_utc", columns="satellite_id", values=field
        )
        pivot = pivot.reindex(columns=satellites)
        pivots[field] = pivot
    return pivots


def _extract_satellite_labels(columns: Iterable[str]) -> List[str]:
    sats: List[str] = []
    for column in columns:
        if column == "time_utc":
            continue
        label = column.split("_")[0]
        if label not in sats:
            sats.append(label)
    return sats


def _ensure_output_directory(run_dir: Path) -> Path:
    output_dir = run_dir / "plots"
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def _plot_latitude(times: pd.Series, latitudes: pd.DataFrame, output_dir: Path) -> Path:
    fig, ax = plt.subplots(figsize=(10, 6))
    for satellite in latitudes.columns:
        if satellite == "time_utc":
            continue
        ax.plot(times, np.rad2deg(latitudes[satellite]), label=satellite)

    ax.set_title("Latitude evolution for Tehran triangle formation")
    ax.set_xlabel("Time (UTC)")
    ax.set_ylabel("Latitude (degrees)")
    ax.legend(loc="best")
    ax.grid(True, linestyle=":", linewidth=0.5)
    fig.autofmt_xdate()

    output_path = output_dir / "latitude_timeseries.svg"
    fig.savefig(output_path, format="svg", bbox_inches="tight")
    plt.close(fig)
    return output_path


def _plot_longitude(times: pd.Series, longitudes: pd.DataFrame, output_dir: Path) -> Path:
    fig, ax = plt.subplots(figsize=(10, 6))
    for satellite in longitudes.columns:
        if satellite == "time_utc":
            continue
        wrapped = np.rad2deg(np.unwrap(longitudes[satellite].to_numpy()))
        wrapped = ((wrapped + 180.0) % 360.0) - 180.0
        ax.plot(times, wrapped, label=satellite)

    ax.set_title("Longitude evolution for Tehran triangle formation")
    ax.set_xlabel("Time (UTC)")
    ax.set_ylabel("Longitude (degrees)")
    ax.legend(loc="best")
    ax.grid(True, linestyle=":", linewidth=0.5)
    fig.autofmt_xdate()

    output_path = output_dir / "longitude_timeseries.svg"
    fig.savefig(output_path, format="svg", bbox_inches="tight")
    plt.close(fig)
    return output_path


def _plot_altitudes(
    altitudes: pd.DataFrame,
    design_altitude_km: float,
    output_dir: Path,
) -> Path:
    if altitudes.empty:
        raise ValueError("altitudes_m.csv is empty.")

    dataframe = altitudes.sort_values("time_utc").copy()
    value_columns = [
        column for column in dataframe.columns if column != "time_utc"
    ]
    if not value_columns:
        raise ValueError("altitudes_m.csv is missing satellite altitude columns.")

    dataframe[value_columns] = (
        dataframe[value_columns].apply(pd.to_numeric, errors="coerce") / 1_000.0
    )

    times = dataframe["time_utc"]
    fig, ax = plt.subplots(figsize=(10, 6))
    for column in value_columns:
        ax.plot(times, dataframe[column], label=column)

    centroid = dataframe[value_columns].mean(axis=1)
    if not centroid.isna().all():
        ax.plot(
            times,
            centroid,
            label="Centroid altitude",
            color="#4d4d4d",
            linestyle="--",
            linewidth=2.0,
        )

    if math.isfinite(design_altitude_km):
        ax.axhline(
            design_altitude_km,
            color="#b2182b",
            linestyle=":",
            linewidth=1.5,
            label=f"Design altitude ({design_altitude_km:.1f} km)",
        )

    ax.set_title("Altitude evolution for Tehran triangle formation")
    ax.set_xlabel("Time (UTC)")
    ax.set_ylabel("Altitude (km)")
    ax.legend(loc="best")
    ax.grid(True, linestyle=":", linewidth=0.5)
    fig.autofmt_xdate()

    output_path = output_dir / "altitude_timeseries.svg"
    fig.savefig(output_path, format="svg", bbox_inches="tight")
    plt.close(fig)
    return output_path


def _annotate_threshold_crossings(
    ax: plt.Axes,
    times: pd.Series,
    values: pd.Series,
    threshold: float,
    label: str,
) -> None:
    """Mark transitions where a series exceeds a threshold."""

    if not np.isfinite(threshold):
        return

    try:
        series = values.astype(float)
    except (TypeError, ValueError):  # pragma: no cover - defensive
        return

    exceed_mask = series > threshold
    if not exceed_mask.any():
        return

    crossing_indices: list[int] = []
    previous = False
    for index, current in enumerate(exceed_mask):
        if bool(current) and not previous:
            crossing_indices.append(index)
        previous = bool(current)

    if not crossing_indices:
        return

    for index in crossing_indices[:3]:  # limit annotations to the first few crossings
        try:
            time_value = times.iloc[index]
            sample = series.iloc[index]
        except IndexError:  # pragma: no cover - defensive
            continue
        if pd.isna(sample):
            continue
        annotation = f"{label} > {threshold:.0f} km"
        ax.annotate(
            annotation,
            xy=(time_value, sample),
            xytext=(0, 15),
            textcoords="offset points",
            arrowprops=dict(arrowstyle="->", color="#d62728"),
            fontsize=9,
            color="#d62728",
        )


def _plot_ground_command_ranges(
    ranges: pd.DataFrame,
    limits: dict[str, float],
    output_dir: Path,
) -> Path:
    if ranges.empty:
        raise ValueError("ground_ranges.csv is empty.")

    times = ranges["time_utc"]
    max_ground = ranges["max_ground_distance_km"]
    min_command = ranges["min_command_distance_km"]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(times, max_ground, label="Max ground distance", color="#1f77b4")
    ax.plot(times, min_command, label="Min command distance", color="#ff7f0e")

    ground_tol = limits.get("ground_tolerance_km", float("nan"))
    command_range = limits.get("command_contact_range_km", float("nan"))

    if np.isfinite(ground_tol):
        ax.axhline(
            ground_tol,
            color="#2ca02c",
            linestyle="--",
            linewidth=1.2,
            label=f"Ground tolerance ({ground_tol:.0f} km)",
        )
        _annotate_threshold_crossings(
            ax, times, max_ground, ground_tol, "Ground range"
        )

    if np.isfinite(command_range):
        ax.axhline(
            command_range,
            color="#9467bd",
            linestyle=":",
            linewidth=1.2,
            label=f"Command contact range ({command_range:.0f} km)",
        )
        _annotate_threshold_crossings(
            ax, times, min_command, command_range, "Command range"
        )

    ax.set_title("Ground and command ranges versus time")
    ax.set_xlabel("Time (UTC)")
    ax.set_ylabel("Range (km)")
    ax.legend(loc="best")
    ax.grid(True, linestyle=":", linewidth=0.5)
    fig.autofmt_xdate()

    output_path = output_dir / "ground_command_ranges.svg"
    fig.savefig(output_path, format="svg", bbox_inches="tight")
    plt.close(fig)
    return output_path


def _plot_ground_track(
    latitudes: pd.DataFrame, longitudes: pd.DataFrame, output_dir: Path
) -> Path:
    columns = [column for column in latitudes.columns if column != "time_utc"]
    output_path = output_dir / "ground_track_tehran_map.svg"

    if ccrs is None:
        LOGGER.warning(
            "Cartopy is unavailable; generating planar ground-track plot instead."
        )
        fig, ax = plt.subplots(figsize=(8, 8))
        for satellite in columns:
            lat_deg = np.rad2deg(latitudes[satellite].to_numpy())
            lon_wrapped = _wrap_longitudes_around_tehran(
                longitudes[satellite].to_numpy()
            )
            ax.plot(lon_wrapped, lat_deg, label=satellite)

        ax.scatter(
            [TEHRAN_LONGITUDE_DEG],
            [TEHRAN_LATITUDE_DEG],
            color="red",
            marker="*",
            s=120,
            label="Tehran",
        )
        ax.set_title("Ground track projection over Tehran")
        ax.set_xlabel("Longitude (degrees)")
        ax.set_ylabel("Latitude (degrees)")
        ax.legend(loc="best")
        ax.set_aspect("equal", adjustable="datalim")
        ax.grid(True, linestyle=":", linewidth=0.5)
        fig.savefig(output_path, format="svg", bbox_inches="tight")
        plt.close(fig)
        return output_path

    projection = ccrs.PlateCarree()
    fig = plt.figure(figsize=(10, 8))
    ax = plt.axes(projection=projection)
    extent = (
        TEHRAN_LONGITUDE_DEG - 20.0,
        TEHRAN_LONGITUDE_DEG + 20.0,
        TEHRAN_LATITUDE_DEG - 12.0,
        TEHRAN_LATITUDE_DEG + 12.0,
    )
    ax.set_extent(extent, crs=projection)

    ax.coastlines(resolution="110m", linewidth=0.6, zorder=1)
    if cfeature is not None:  # pragma: no branch - follows cartopy import
        ax.add_feature(cfeature.BORDERS, linewidth=0.4, edgecolor="grey", zorder=1)
        ax.add_feature(cfeature.LAND, facecolor="#f5f5f5", zorder=0)
        ax.add_feature(cfeature.OCEAN, facecolor="#dce9f5", zorder=0)

    gridlines = ax.gridlines(
        draw_labels=True,
        linestyle=":",
        linewidth=0.4,
        color="grey",
        x_inline=False,
        y_inline=False,
    )
    gridlines.top_labels = False
    gridlines.right_labels = False

    for satellite in columns:
        lat_deg = np.rad2deg(latitudes[satellite].to_numpy())
        lon_wrapped = _wrap_longitudes_around_tehran(
            longitudes[satellite].to_numpy()
        )
        ax.plot(
            lon_wrapped,
            lat_deg,
            transform=ccrs.Geodetic(),
            label=satellite,
            linewidth=1.5,
        )

    ax.scatter(
        [TEHRAN_LONGITUDE_DEG],
        [TEHRAN_LATITUDE_DEG],
        color="red",
        marker="*",
        s=120,
        transform=projection,
        zorder=5,
        label="Tehran",
    )
    ax.text(
        TEHRAN_LONGITUDE_DEG + 0.5,
        TEHRAN_LATITUDE_DEG + 0.5,
        "Tehran",
        transform=projection,
        fontsize=10,
        fontweight="bold",
        zorder=5,
    )

    ax.set_title("Ground tracks over Tehran in regional context")
    ax.legend(loc="upper right")

    fig.savefig(output_path, format="svg", bbox_inches="tight")
    plt.close(fig)
    return output_path


def _plot_orbital_elements(
    pivots: dict[str, pd.DataFrame], output_dir: Path
) -> Path:
    fig, axes = plt.subplots(
        len(CLASSICAL_ELEMENT_FIELDS), 1, sharex=True, figsize=(12, 18)
    )
    if not isinstance(axes, np.ndarray):  # pragma: no cover - defensive
        axes = np.array([axes])

    line_handles: list[Line2D] = []
    legend_labels: list[str] = []
    for index, field in enumerate(CLASSICAL_ELEMENT_FIELDS):
        axis = axes[index]
        pivot = pivots[field]
        for column in pivot.columns:
            line, = axis.plot(pivot.index, pivot[column], label=column)
            if column not in legend_labels:
                legend_labels.append(column)
                line_handles.append(line)
        axis.set_ylabel(CLASSICAL_ELEMENT_LABELS[field])
        axis.grid(True, linestyle=":", linewidth=0.5)

    axes[-1].set_xlabel("Time (UTC)")
    fig.suptitle("Classical orbital elements per satellite")
    fig.legend(line_handles, legend_labels, loc="upper center", ncol=len(legend_labels))
    fig.autofmt_xdate()
    fig.tight_layout(rect=(0.0, 0.0, 1.0, 0.95))

    output_path = output_dir / "orbital_elements_timeseries.svg"
    fig.savefig(output_path, format="svg", bbox_inches="tight")
    plt.close(fig)
    return output_path


def _plot_orbital_elements_formation_window(
    pivots: dict[str, pd.DataFrame],
    formation_start: pd.Timestamp,
    formation_end: pd.Timestamp,
    output_dir: Path,
) -> Path:
    fig, axes = plt.subplots(
        len(CLASSICAL_ELEMENT_FIELDS), 1, sharex=True, figsize=(12, 18)
    )
    if not isinstance(axes, np.ndarray):  # pragma: no cover - defensive
        axes = np.array([axes])

    line_handles: list[Line2D] = []
    legend_labels: list[str] = []

    for index, field in enumerate(CLASSICAL_ELEMENT_FIELDS):
        axis = axes[index]
        pivot = pivots[field]
        if pivot.index.tz is None:
            start_cmp = formation_start.tz_convert("UTC").tz_localize(None)
            end_cmp = formation_end.tz_convert("UTC").tz_localize(None)
        else:
            start_cmp = formation_start.tz_convert("UTC")
            end_cmp = formation_end.tz_convert("UTC")

        window_slice = pivot.loc[(pivot.index >= start_cmp) & (pivot.index <= end_cmp)]
        if window_slice.empty:
            raise ValueError(
                "Orbital elements time series do not contain samples within the formation window."
            )

        for column in window_slice.columns:
            line, = axis.plot(window_slice.index, window_slice[column], label=column)
            if column not in legend_labels:
                legend_labels.append(column)
                line_handles.append(line)
        axis.set_ylabel(CLASSICAL_ELEMENT_LABELS[field])
        axis.grid(True, linestyle=":", linewidth=0.5)

    axes[-1].set_xlabel("Time (UTC)")
    start_label = formation_start.tz_convert("UTC").strftime("%Y-%m-%d %H:%M:%SZ")
    end_label = formation_end.tz_convert("UTC").strftime("%Y-%m-%d %H:%M:%SZ")
    fig.suptitle(
        "Classical orbital elements during formation window\n"
        f"{start_label} to {end_label}"
    )
    fig.legend(line_handles, legend_labels, loc="upper center", ncol=len(legend_labels))
    fig.autofmt_xdate()
    fig.tight_layout(rect=(0.0, 0.05, 1.0, 0.92))
    fig.text(
        0.5,
        0.01,
        f"Formation window applied: {start_label} – {end_label} (UTC)",
        ha="center",
        va="bottom",
    )

    output_path = output_dir / "orbital_elements_formation_window.svg"
    fig.savefig(output_path, format="svg", bbox_inches="tight")
    plt.close(fig)
    return output_path


def _plot_triangle_geometry(
    geometry: pd.DataFrame, tolerances: dict[str, float], output_dir: Path
) -> Path:
    geometry = geometry.sort_values("time_utc")
    times = geometry["time_utc"]
    area = geometry["triangle_area_m2"]
    aspect = geometry["triangle_aspect_ratio"]
    side_columns = [
        column for column in geometry.columns if column.startswith("side_length_")
    ]
    if not side_columns:
        LOGGER.warning(
            "triangle_geometry.csv is missing side_length_* columns; side length traces will be omitted."
        )

    fig, axes = plt.subplots(3, 1, sharex=True, figsize=(12, 12))
    nominal_side = tolerances.get("nominal_side_m", float("nan"))
    side_fraction = tolerances.get("side_fraction", 0.05)
    aspect_limit = tolerances.get("aspect_ratio_limit", 1.02)

    axes[0].plot(times, area, color="#2166ac", linewidth=1.8, label="Triangle area")
    axes[0].set_ylabel("Area (m²)")
    if math.isfinite(nominal_side):
        nominal_area = (math.sqrt(3.0) / 4.0) * nominal_side ** 2
        lower_area = nominal_area * (1.0 - side_fraction) ** 2
        upper_area = nominal_area * (1.0 + side_fraction) ** 2
        axes[0].fill_between(
            times,
            lower_area,
            upper_area,
            color="#fddbc7",
            alpha=0.4,
            label=f"±{side_fraction * 100:.1f} % side-length envelope",
        )
        axes[0].axhline(
            nominal_area,
            color="#b2182b",
            linestyle="--",
            linewidth=1.0,
            label="Nominal area",
        )
    axes[0].legend(loc="upper right")

    axes[1].plot(times, aspect, color="#238b45", linewidth=1.8, label="Aspect ratio")
    axes[1].set_ylabel("Aspect ratio (–)")
    axes[1].fill_between(
        times,
        1.0,
        aspect_limit,
        color="#d0d1e6",
        alpha=0.4,
        label=f"Aspect ratio ≤ {aspect_limit:.2f}",
    )
    axes[1].axhline(
        aspect_limit,
        color="#6a51a3",
        linestyle="--",
        linewidth=1.0,
        label="Aspect ratio tolerance",
    )
    axes[1].axhline(
        1.0,
        color="#005a32",
        linestyle=":",
        linewidth=1.0,
        label="Equilateral ideal",
    )
    axes[1].legend(loc="upper right")

    for column in side_columns:
        label = (
            column.replace("side_length_", "Side ")
            .replace("_m", " (m)")
            .replace("_", " ")
        )
        axes[2].plot(times, geometry[column], linewidth=1.5, label=label)
    if math.isfinite(nominal_side):
        lower_side = nominal_side * (1.0 - side_fraction)
        upper_side = nominal_side * (1.0 + side_fraction)
        axes[2].fill_between(
            times,
            lower_side,
            upper_side,
            color="#c7e9c0",
            alpha=0.4,
            label=f"±{side_fraction * 100:.1f} % side-length band",
        )
        axes[2].axhline(
            nominal_side,
            color="#31a354",
            linestyle="--",
            linewidth=1.0,
            label="Nominal side length",
        )
    axes[2].set_ylabel("Side length (m)")
    axes[2].set_xlabel("Time (UTC)")
    axes[2].legend(loc="upper right")

    for axis in axes:
        axis.grid(True, linestyle=":", linewidth=0.5)

    fig.suptitle("Triangle geometry diagnostics over time")
    fig.autofmt_xdate()
    fig.tight_layout(rect=(0.0, 0.0, 1.0, 0.95))

    output_path = output_dir / "triangle_geometry_timeseries.svg"
    fig.savefig(output_path, format="svg", bbox_inches="tight")
    plt.close(fig)
    return output_path


def _set_3d_equal_aspect(ax: plt.Axes, points: np.ndarray) -> None:
    """Set equal aspect ratios for three-dimensional axes."""

    ranges = points.max(axis=0) - points.min(axis=0)
    max_range = ranges.max() / 2.0
    centres = (points.max(axis=0) + points.min(axis=0)) / 2.0

    if max_range == 0.0:
        max_range = 1.0

    x_centre, y_centre, z_centre = centres
    ax.set_xlim(x_centre - max_range, x_centre + max_range)
    ax.set_ylim(y_centre - max_range, y_centre + max_range)
    ax.set_zlim(z_centre - max_range, z_centre + max_range)

    if hasattr(ax, "set_box_aspect"):
        ax.set_box_aspect((1, 1, 1))


def _render_formation_svg(
    positions: pd.DataFrame,
    satellites: list[str],
    earth_radius: float,
    output_path: Path,
) -> None:
    """Create a static SVG visualisation of the formation using Matplotlib."""

    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111, projection="3d")

    theta = np.linspace(0, 2 * math.pi, 120)
    phi = np.linspace(0, math.pi, 60)
    theta_grid, phi_grid = np.meshgrid(theta, phi)
    earth_x = earth_radius * np.sin(phi_grid) * np.cos(theta_grid)
    earth_y = earth_radius * np.sin(phi_grid) * np.sin(theta_grid)
    earth_z = earth_radius * np.cos(phi_grid)
    ax.plot_surface(
        earth_x,
        earth_y,
        earth_z,
        rstride=1,
        cstride=1,
        linewidth=0,
        antialiased=True,
        alpha=0.25,
        color="#1f78b4",
        edgecolor="none",
    )

    point_clouds = [
        np.column_stack((earth_x.ravel(), earth_y.ravel(), earth_z.ravel()))
    ]

    for satellite in satellites:
        x = positions[f"{satellite}_x_m"].to_numpy()
        y = positions[f"{satellite}_y_m"].to_numpy()
        z = positions[f"{satellite}_z_m"].to_numpy()
        ax.plot(x, y, z, label=satellite, linewidth=2.0)
        point_clouds.append(np.column_stack((x, y, z)))

    stacked_points = np.vstack(point_clouds)
    _set_3d_equal_aspect(ax, stacked_points)

    ax.set_title("Tehran triangle formation in Earth-centred coordinates")
    ax.set_xlabel("x (m)")
    ax.set_ylabel("y (m)")
    ax.set_zlabel("z (m)")
    ax.view_init(elev=20.0, azim=45.0)
    ax.legend(loc="upper left")

    fig.tight_layout()
    fig.savefig(output_path, format="svg", bbox_inches="tight")
    plt.close(fig)


def _render_3d_formation(
    run_dir: Path,
    times: pd.Series,
    positions: pd.DataFrame,
    latitudes: pd.DataFrame,
    longitudes: pd.DataFrame,
    formation_window: Tuple[pd.Timestamp, pd.Timestamp],
    design_altitude_km: float,
    output_dir: Path,
) -> dict[str, Path]:
    """Create the combined three-dimensional and ground-track visualisation."""

    satellites = _extract_satellite_labels(positions.columns)
    if times.dt.tz is not None:
        utc_times = times.dt.tz_convert("UTC")
    else:
        utc_times = times.dt.tz_localize("UTC")
    iso_times = utc_times.dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    earth_radius_m = EARTH_MEAN_RADIUS_KM * 1000.0
    swath_width_km = _load_sensor_swath_width_km()
    half_angle_rad = math.atan2(swath_width_km * 500.0, design_altitude_km * 1000.0)
    if not math.isfinite(half_angle_rad) or half_angle_rad <= 0:
        half_angle_rad = math.radians(3.0)

    formation_start, formation_end = formation_window
    formation_midpoint = formation_start + (formation_end - formation_start) / 2
    if formation_start.tzinfo is None:
        formation_start_utc = formation_start.tz_localize("UTC")
    else:
        formation_start_utc = formation_start.tz_convert("UTC")
    if formation_end.tzinfo is None:
        formation_end_utc = formation_end.tz_localize("UTC")
    else:
        formation_end_utc = formation_end.tz_convert("UTC")

    stk_dir = run_dir / "stk_export"
    ephemerides: dict[str, pd.DataFrame] = {}
    groundtracks: dict[str, pd.DataFrame] = {}
    facilities: dict[str, dict[str, float]] = {}
    contacts: dict[str, list[dict[str, object]]] = {}
    if stk_dir.exists():
        ephemerides = _load_stk_ephemerides(stk_dir)
        groundtracks = _load_stk_groundtracks(stk_dir)
        facilities = _load_stk_facilities(stk_dir)
        contacts = _load_stk_contacts(stk_dir)

    figure = make_subplots(
        rows=1,
        cols=2,
        specs=[[{"type": "scene"}, {"type": "scattergeo"}]],
        column_widths=[0.55, 0.45],
        subplot_titles=("3D formation context", "Global ground tracks"),
    )

    theta = np.linspace(0, 2 * math.pi, 90)
    phi = np.linspace(0, math.pi, 45)
    theta_grid, phi_grid = np.meshgrid(theta, phi)
    x = earth_radius_m * np.sin(phi_grid) * np.cos(theta_grid)
    y = earth_radius_m * np.sin(phi_grid) * np.sin(theta_grid)
    z = earth_radius_m * np.cos(phi_grid)
    earth_surface = go.Surface(
        x=x,
        y=y,
        z=z,
        colorscale="earth",
        opacity=0.35,
        showscale=False,
        name="Earth",
        hoverinfo="skip",
        legendgroup="Earth",
        showlegend=False,
    )
    figure.add_trace(earth_surface, row=1, col=1)

    for coastline in _build_coastline_traces(earth_radius_m):
        coastline.legendgroup = "Earth"
        figure.add_trace(coastline, row=1, col=1)

    tehran_xyz = np.column_stack(
        _cartesian_from_lat_lon(
            np.array([TEHRAN_LATITUDE_DEG]), np.array([TEHRAN_LONGITUDE_DEG]), earth_radius_m
        )
    )[0]

    palette = qualitative.D3
    trace_colours: Dict[str, str] = {}
    for idx, satellite in enumerate(satellites):
        colour = palette[idx % len(palette)]
        trace_colours[satellite] = colour
        figure.add_trace(
            go.Scatter3d(
                x=positions[f"{satellite}_x_m"],
                y=positions[f"{satellite}_y_m"],
                z=positions[f"{satellite}_z_m"],
                mode="lines",
                name=f"{satellite} formation",
                legendgroup=f"{satellite}_orbit",
                line=dict(color=colour, width=4),
                text=[f"{satellite} @ {timestamp}" for timestamp in iso_times],
                hovertemplate=(
                    "<b>%{text}</b><br>"
                    "x: %{x:.0f} m<br>"
                    "y: %{y:.0f} m<br>"
                    "z: %{z:.0f} m"
                ),
            ),
            row=1,
            col=1,
        )

        window_mask = (utc_times >= formation_start) & (utc_times <= formation_end)
        if window_mask.any():
            figure.add_trace(
                go.Scatter3d(
                    x=positions.loc[window_mask, f"{satellite}_x_m"],
                    y=positions.loc[window_mask, f"{satellite}_y_m"],
                    z=positions.loc[window_mask, f"{satellite}_z_m"],
                    mode="lines",
                    name=f"{satellite} formation window",
                    legendgroup=f"{satellite}_window",
                    line=dict(color=colour, width=6, dash="dot"),
                    showlegend=True,
                ),
                row=1,
                col=1,
            )

        lat_deg = np.rad2deg(latitudes[satellite])
        lon_deg = np.rad2deg(longitudes[satellite])
        figure.add_trace(
            go.Scattergeo(
                lat=lat_deg,
                lon=lon_deg,
                mode="lines",
                name=f"{satellite} ground track",
                legendgroup=f"{satellite}_orbit",
                line=dict(color=colour, width=1.5),
                showlegend=False,
            ),
            row=1,
            col=2,
        )

        if window_mask.any():
            figure.add_trace(
                go.Scattergeo(
                    lat=lat_deg[window_mask.to_numpy()],
                    lon=lon_deg[window_mask.to_numpy()],
                    mode="lines",
                    name=f"{satellite} window track",
                    legendgroup=f"{satellite}_window",
                    line=dict(color=colour, width=3),
                    showlegend=False,
                ),
                row=1,
                col=2,
            )

    for asset, dataframe in sorted(ephemerides.items()):
        colour = "#555555"
        figure.add_trace(
            go.Scatter3d(
                x=dataframe["x_m"],
                y=dataframe["y_m"],
                z=dataframe["z_m"],
                mode="lines",
                name=f"{asset} daily pass",
                legendgroup=f"{asset}_daily",
                line=dict(color=colour, width=2, dash="dash"),
                showlegend=True,
            ),
            row=1,
            col=1,
        )

        window_mask = (
            (dataframe["time_utc"] >= formation_start_utc)
            & (dataframe["time_utc"] <= formation_end_utc)
        )
        if window_mask.any():
            figure.add_trace(
                go.Scatter3d(
                    x=dataframe.loc[window_mask, "x_m"],
                    y=dataframe.loc[window_mask, "y_m"],
                    z=dataframe.loc[window_mask, "z_m"],
                    mode="lines",
                    name=f"{asset} daily window",
                    legendgroup=f"{asset}_window",
                    line=dict(color="#ff7f0e", width=4),
                    showlegend=True,
                ),
                row=1,
                col=1,
            )

        groundtrack = groundtracks.get(asset)
        if groundtrack is not None:
            figure.add_trace(
                go.Scattergeo(
                    lat=groundtrack["latitude_deg"],
                    lon=groundtrack["longitude_deg"],
                    mode="lines",
                    name=f"{asset} daily ground track",
                    legendgroup=f"{asset}_daily",
                    line=dict(color="#555555", width=1, dash="dash"),
                    showlegend=False,
                ),
                row=1,
                col=2,
            )
            gt_mask = (
                (groundtrack["time_utc"] >= formation_start_utc)
                & (groundtrack["time_utc"] <= formation_end_utc)
            )
            if gt_mask.any():
                figure.add_trace(
                    go.Scattergeo(
                        lat=groundtrack.loc[gt_mask, "latitude_deg"],
                        lon=groundtrack.loc[gt_mask, "longitude_deg"],
                        mode="lines",
                        name=f"{asset} window track",
                        legendgroup=f"{asset}_window",
                        line=dict(color="#ff7f0e", width=2),
                        showlegend=False,
                    ),
                    row=1,
                    col=2,
                )

    for facility, attributes in facilities.items():
        facility_lat = attributes.get("latitude_deg", TEHRAN_LATITUDE_DEG)
        facility_lon = attributes.get("longitude_deg", TEHRAN_LONGITUDE_DEG)
        x_fac, y_fac, z_fac = _cartesian_from_lat_lon(
            np.array([facility_lat]), np.array([facility_lon]), earth_radius_m
        )
        figure.add_trace(
            go.Scatter3d(
                x=x_fac,
                y=y_fac,
                z=z_fac,
                mode="markers",
                name=f"Facility: {facility}",
                legendgroup=f"facility_{facility}",
                marker=dict(size=6, color="#d62728", symbol="diamond"),
                showlegend=True,
            ),
            row=1,
            col=1,
        )

        figure.add_trace(
            go.Scattergeo(
                lat=[facility_lat],
                lon=[facility_lon],
                mode="markers+text",
                text=[facility.replace("_", " ")],
                textposition="top right",
                name=f"Facility: {facility}",
                legendgroup=f"facility_{facility}",
                marker=dict(size=8, color="#d62728", symbol="star"),
                showlegend=False,
            ),
            row=1,
            col=2,
        )

    if np.linalg.norm(tehran_xyz) > 0:
        figure.add_trace(
            go.Scatter3d(
                x=[tehran_xyz[0]],
                y=[tehran_xyz[1]],
                z=[tehran_xyz[2]],
                mode="markers",
                name="Tehran",
                legendgroup="facility_Tehran",
                marker=dict(color="#e31a1c", size=7, symbol="x"),
                showlegend=True,
            ),
            row=1,
            col=1,
        )
        figure.add_trace(
            go.Scattergeo(
                lat=[TEHRAN_LATITUDE_DEG],
                lon=[TEHRAN_LONGITUDE_DEG],
                mode="markers+text",
                text=["Tehran"],
                textposition="bottom right",
                name="Tehran",
                legendgroup="facility_Tehran",
                marker=dict(size=9, color="#e31a1c", symbol="star"),
                showlegend=False,
            ),
            row=1,
            col=2,
        )

    for contact_name, intervals in contacts.items():
        for interval in intervals:
            asset = str(interval.get("asset", contact_name))
            start = interval.get("start")
            end = interval.get("end")
            dataframe = ephemerides.get(asset)
            if dataframe is None:
                continue
            mask = (dataframe["time_utc"] >= start) & (dataframe["time_utc"] <= end)
            if not mask.any():
                continue
            figure.add_trace(
                go.Scatter3d(
                    x=dataframe.loc[mask, "x_m"],
                    y=dataframe.loc[mask, "y_m"],
                    z=dataframe.loc[mask, "z_m"],
                    mode="lines",
                    name=f"{contact_name} contact",
                    legendgroup=f"contact_{contact_name}",
                    line=dict(color="#9467bd", width=4),
                    showlegend=True,
                ),
                row=1,
                col=1,
            )

    window_mid_idx = (np.abs((utc_times - formation_midpoint).to_numpy())).argmin()
    apex_points: Dict[str, np.ndarray] = {}
    for satellite in satellites:
        apex_points[satellite] = np.array(
            [
                positions.iloc[window_mid_idx][f"{satellite}_x_m"],
                positions.iloc[window_mid_idx][f"{satellite}_y_m"],
                positions.iloc[window_mid_idx][f"{satellite}_z_m"],
            ]
        )

    for satellite, apex in apex_points.items():
        try:
            cone = _create_cone_mesh(apex, tehran_xyz, half_angle_rad, satellite, trace_colours[satellite])
        except Exception as exc:  # pragma: no cover - diagnostic fallback
            LOGGER.warning("Failed to build cone for %s: %s", satellite, exc)
        else:
            cone.legendgroup = f"{satellite}_cones"
            cone.showlegend = True
            figure.add_trace(cone, row=1, col=1)

    figure.update_scenes(
        dict(
            xaxis=dict(title="x (m)", showgrid=False),
            yaxis=dict(title="y (m)", showgrid=False),
            zaxis=dict(title="z (m)", showgrid=False),
            aspectmode="data",
        )
    )
    figure.update_geos(
        dict(
            showcountries=True,
            showcoastlines=True,
            showland=True,
            landcolor="#f0f4f8",
            oceancolor="#ccd9e8",
            lakecolor="#ccd9e8",
            projection=dict(type="natural earth"),
        ),
        row=1,
        col=2,
    )
    figure.update_layout(
        title="Tehran formation and daily pass overview",
        legend=dict(
            title="Display settings (click entries to toggle)",
            yanchor="top",
            y=1.0,
            xanchor="left",
            x=1.05,
            bgcolor="rgba(255,255,255,0.7)",
            bordercolor="#cccccc",
            borderwidth=1,
        ),
        margin=dict(l=0, r=200, t=60, b=0),
        hovermode="closest",
    )

    html_path = output_dir / "formation_3d.html"
    pio.write_html(figure, file=html_path, include_plotlyjs="cdn", auto_play=False, full_html=True)

    svg_path = output_dir / "formation_3d.svg"
    _render_formation_svg(positions, satellites, earth_radius_m, svg_path)

    return {"svg": svg_path, "html": html_path}


def generate_visualisations(run_directory: Path) -> dict[str, Path | dict[str, Path]]:
    latitudes, longitudes = _load_lat_lon(run_directory)
    altitudes = _load_altitudes(run_directory)
    positions = _load_positions(run_directory)
    orbital_elements = _load_orbital_elements(run_directory)
    triangle_geometry = _load_triangle_geometry(run_directory)
    ground_ranges = _load_ground_command_ranges(run_directory)
    formation_start, formation_end = _load_formation_window(run_directory)
    orbital_pivots = _reshape_orbital_elements(orbital_elements)
    tolerances = _load_geometry_tolerances(run_directory)
    range_limits = _load_ground_command_limits(run_directory)
    design_altitude_km = _load_design_altitude_km(run_directory)
    output_dir = _ensure_output_directory(run_directory)

    time_index = latitudes["time_utc"]
    outputs: dict[str, Path | dict[str, Path]] = {
        "latitude": _plot_latitude(time_index, latitudes, output_dir),
        "longitude": _plot_longitude(time_index, longitudes, output_dir),
        "altitude_timeseries": _plot_altitudes(
            altitudes, design_altitude_km, output_dir
        ),
        "ground_track": _plot_ground_track(latitudes, longitudes, output_dir),
        "ground_command_ranges": _plot_ground_command_ranges(
            ground_ranges, range_limits, output_dir
        ),
        "formation_3d": _render_3d_formation(
            run_directory,
            time_index,
            positions,
            latitudes,
            longitudes,
            (formation_start, formation_end),
            design_altitude_km,
            output_dir,
        ),
        "orbital_elements_timeseries": _plot_orbital_elements(
            orbital_pivots, output_dir
        ),
        "orbital_elements_formation_window": _plot_orbital_elements_formation_window(
            orbital_pivots, formation_start, formation_end, output_dir
        ),
        "triangle_geometry_timeseries": _plot_triangle_geometry(
            triangle_geometry, tolerances, output_dir
        ),
    }
    return outputs


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Render SVG charts, a canonical 3D SVG, and an HTML Plotly scene for a debug run directory."
    )
    parser.add_argument(
        "run_directory",
        type=Path,
        help="Path to the timestamped debug run directory (e.g. artefacts/debug/20250930T185811Z)",
    )
    args = parser.parse_args()

    run_directory = args.run_directory
    if not run_directory.exists():
        raise FileNotFoundError(f"Run directory {run_directory} does not exist.")

    outputs = generate_visualisations(run_directory)
    for label, artefact in outputs.items():
        if isinstance(artefact, dict):
            canonical = artefact.get("svg")
            if canonical is not None:
                print(
                    f"Generated {label} visualisation at {canonical} (canonical SVG)"
                )
            for fmt, path in artefact.items():
                if fmt == "svg":
                    continue
                print(f"Generated {label} visualisation at {path} ({fmt})")
        else:
            print(f"Generated {label} visualisation at {artefact}")


if __name__ == "__main__":
    main()
