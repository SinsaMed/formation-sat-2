"""Shared helpers for exporting triangle simulation artefacts."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Mapping, MutableMapping, Sequence

from sim.formation.triangle import CLASSICAL_ELEMENT_FIELDS, TriangleFormationResult


@dataclass(frozen=True)
class TriangleCsvArtefacts:
    """Container capturing the CSV artefacts emitted for a triangle run."""

    csv_paths: Mapping[str, Path]
    per_satellite_csvs: Mapping[str, Path]


def export_triangle_time_series(
    result: TriangleFormationResult, output_directory: Path
) -> TriangleCsvArtefacts:
    """Serialise the canonical triangle time-series artefacts to CSV files."""

    output_directory.mkdir(parents=True, exist_ok=True)

    csv_paths: MutableMapping[str, Path] = {}

    times = result.times
    satellite_ids = sorted(result.positions_m)

    csv_paths["positions_m"] = _write_mapping_csv(
        output_directory / "positions_m.csv",
        times,
        satellite_ids,
        result.positions_m,
        ("x_m", "y_m", "z_m"),
    )
    csv_paths["velocities_mps"] = _write_mapping_csv(
        output_directory / "velocities_mps.csv",
        times,
        satellite_ids,
        result.velocities_mps,
        ("vx_mps", "vy_mps", "vz_mps"),
    )
    csv_paths["latitudes_rad"] = _write_mapping_csv(
        output_directory / "latitudes_rad.csv",
        times,
        satellite_ids,
        result.latitudes_rad,
        None,
    )
    csv_paths["longitudes_rad"] = _write_mapping_csv(
        output_directory / "longitudes_rad.csv",
        times,
        satellite_ids,
        result.longitudes_rad,
        None,
    )
    csv_paths["altitudes_m"] = _write_mapping_csv(
        output_directory / "altitudes_m.csv",
        times,
        satellite_ids,
        result.altitudes_m,
        None,
    )
    csv_paths["triangle_geometry"] = _write_triangle_geometry_csv(
        output_directory / "triangle_geometry.csv",
        times,
        result.triangle_area_m2,
        result.triangle_aspect_ratio,
        result.triangle_sides_m,
    )
    csv_paths["ground_ranges"] = _write_ground_ranges_csv(
        output_directory / "ground_ranges.csv",
        times,
        result.max_ground_distance_km,
        result.min_command_distance_km,
    )
    orbital_path = _write_orbital_elements_csv(
        output_directory / "orbital_elements.csv",
        times,
        result.classical_elements,
    )
    csv_paths["orbital_elements"] = orbital_path

    per_satellite_dir = output_directory / "orbital_elements"
    per_satellite_dir.mkdir(parents=True, exist_ok=True)
    per_satellite_csvs = _write_orbital_elements_per_spacecraft(
        per_satellite_dir, times, result.classical_elements
    )

    _update_result_artefacts(result, csv_paths, per_satellite_dir, per_satellite_csvs)

    return TriangleCsvArtefacts(csv_paths=dict(csv_paths), per_satellite_csvs=per_satellite_csvs)


def _update_result_artefacts(
    result: TriangleFormationResult,
    csv_paths: Mapping[str, Path],
    per_satellite_dir: Path,
    per_satellite_csvs: Mapping[str, Path],
) -> None:
    """Ensure :class:`TriangleFormationResult` tracks the exported artefacts."""

    artefacts = result.artefacts
    if isinstance(artefacts, MutableMapping):
        target = artefacts
    else:  # pragma: no cover - defensive, depends on call-site usage
        target = dict(artefacts)
        setattr(result, "artefacts", target)

    target.setdefault("positions_csv", str(csv_paths["positions_m"]))
    target.setdefault("velocities_csv", str(csv_paths["velocities_mps"]))
    target.setdefault("latitudes_csv", str(csv_paths["latitudes_rad"]))
    target.setdefault("longitudes_csv", str(csv_paths["longitudes_rad"]))
    target.setdefault("altitudes_csv", str(csv_paths["altitudes_m"]))
    target.setdefault("triangle_geometry_csv", str(csv_paths["triangle_geometry"]))
    target.setdefault("ground_ranges_csv", str(csv_paths["ground_ranges"]))
    target.setdefault("orbital_elements_csv", str(csv_paths["orbital_elements"]))
    if per_satellite_csvs:
        target.setdefault("orbital_elements_directory", str(per_satellite_dir))
        target.setdefault(
            "orbital_elements_per_satellite",
            {sat_id: str(path) for sat_id, path in sorted(per_satellite_csvs.items())},
        )


def _write_mapping_csv(
    path: Path,
    times: Sequence[datetime],
    satellite_ids: Sequence[str],
    data: Mapping[str, Sequence[Sequence[float]] | Sequence[float]],
    component_labels: Sequence[str] | None,
) -> Path:
    """Serialise mapping data keyed by satellite into a CSV file."""

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        header = ["time_utc"]
        if component_labels:
            for sat_id in satellite_ids:
                for label in component_labels:
                    header.append(f"{sat_id}_{label}")
        else:
            header.extend(satellite_ids)
        writer.writerow(header)

        for index, epoch in enumerate(times):
            row = [_format_time(epoch)]
            for sat_id in satellite_ids:
                sample = data[sat_id][index]
                if component_labels:
                    for component_index in range(len(component_labels)):
                        row.append(_format_number(sample[component_index]))
                else:
                    row.append(_format_number(sample))
            writer.writerow(row)
    return path


def _write_triangle_geometry_csv(
    path: Path,
    times: Sequence[datetime],
    areas_m2: Sequence[float],
    aspects: Sequence[float],
    sides_m: Sequence[Sequence[float]],
) -> Path:
    """Export triangle geometry diagnostics to CSV."""

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "time_utc",
                "triangle_area_m2",
                "triangle_aspect_ratio",
                "side_length_1_m",
                "side_length_2_m",
                "side_length_3_m",
            ]
        )
        for index, epoch in enumerate(times):
            row = [
                _format_time(epoch),
                _format_number(areas_m2[index]),
                _format_number(aspects[index]),
            ]
            side_samples = sides_m[index]
            for component in range(3):
                try:
                    value = side_samples[component]
                except (IndexError, TypeError):
                    value = float("nan")
                row.append(_format_number(value))
            writer.writerow(row)
    return path


def _write_ground_ranges_csv(
    path: Path,
    times: Sequence[datetime],
    max_ground_distance_km: Sequence[float],
    min_command_distance_km: Sequence[float],
) -> Path:
    """Serialise ground- and command-range diagnostics to CSV."""

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "time_utc",
                "max_ground_distance_km",
                "min_command_distance_km",
            ]
        )
        for index, epoch in enumerate(times):
            writer.writerow(
                [
                    _format_time(epoch),
                    _format_number(max_ground_distance_km[index]),
                    _format_number(min_command_distance_km[index]),
                ]
            )
    return path


def _write_orbital_elements_csv(
    path: Path,
    times: Sequence[datetime],
    classical_elements: Mapping[str, Mapping[str, Sequence[float]]],
) -> Path:
    """Serialise orbital elements into a consolidated CSV."""

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["time_utc", "satellite_id", *CLASSICAL_ELEMENT_FIELDS])
        for index, epoch in enumerate(times):
            for sat_id, series in sorted(classical_elements.items()):
                row = [_format_time(epoch), sat_id]
                for field in CLASSICAL_ELEMENT_FIELDS:
                    row.append(_format_number(series[field][index]))
                writer.writerow(row)
    return path


def _write_orbital_elements_per_spacecraft(
    directory: Path,
    times: Sequence[datetime],
    classical_elements: Mapping[str, Mapping[str, Sequence[float]]],
) -> Mapping[str, Path]:
    """Serialise orbital element histories for each spacecraft individually."""

    directory.mkdir(parents=True, exist_ok=True)
    output: MutableMapping[str, Path] = {}
    for sat_id, series in sorted(classical_elements.items()):
        filename = f"{sat_id.lower().replace(' ', '_')}_orbital_elements.csv"
        path = directory / filename
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(["time_utc", *CLASSICAL_ELEMENT_FIELDS])
            for index, epoch in enumerate(times):
                row = [_format_time(epoch)]
                for field in CLASSICAL_ELEMENT_FIELDS:
                    row.append(_format_number(series[field][index]))
                writer.writerow(row)
        output[sat_id] = path
    return dict(output)


def _format_time(epoch: datetime) -> str:
    """Render *epoch* using ISO-8601 with explicit UTC suffix."""

    if epoch.tzinfo is None:
        epoch = epoch.replace(tzinfo=timezone.utc)
    return epoch.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _format_number(value: float) -> str:
    """Render floats consistently for CSV export."""

    if value is None:
        return ""
    if isinstance(value, (float, int)) and not isinstance(value, bool):
        return f"{float(value):.15g}"
    return str(value)
