"""Export utilities for translating simulation outputs into STK artefacts.

The implementation focuses on compatibility with STK 11.2 textual formats.
Where the upstream simulation does not provide samples in the TEME frame, the
exporter assumes the caller has already converted the state vectors. This
assumption is stated inline to encourage explicit validation by mission
analysts. NumPy and SciPy are used to guarantee monotonically sampled time
series that satisfy the STK ephemeris specification.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
import re
import string
from typing import Iterable, List, Optional, Sequence

import numpy as np

try:  # pragma: no cover - SciPy is optional at runtime
    from scipy.interpolate import interp1d
except Exception:  # pragma: no cover - fall back to NumPy interpolation
    interp1d = None  # type: ignore

# The poliastro import is retained for future frame transformations. The
# exporter currently expects TEME-compatible inputs and documents this
# constraint to keep the dependency lightweight while signalling the intended
# extension path.
try:  # pragma: no cover - optional import depending on user environment
    from poliastro.frames import TEME  # type: ignore  # noqa: F401
except Exception:  # pragma: no cover - optional dependency handling
    TEME = None  # type: ignore


@dataclass(frozen=True)
class StateSample:
    """A single propagated state vector.

    Attributes
    ----------
    epoch:
        Coordinated Universal Time epoch associated with the state.
    position_eci_km:
        Cartesian position expressed in kilometres within the inertial frame
        expected by the exporter. STK 11.2 accepts TEME or J2000 inertial
        states; here we default to TEME.
    velocity_eci_kms:
        Cartesian velocity expressed in kilometres per second aligned with the
        same inertial frame as the position vector.
    frame:
        Textual identifier describing the coordinate frame. Only "TEME" is
        supported directly; other frames should be converted by the caller or
        extended using poliastro's frame transforms.
    """

    epoch: datetime
    position_eci_km: Sequence[float]
    velocity_eci_kms: Sequence[float]
    frame: str = "TEME"

    def __post_init__(self) -> None:
        object.__setattr__(self, "position_eci_km", np.asarray(self.position_eci_km, dtype=float))
        object.__setattr__(self, "velocity_eci_kms", np.asarray(self.velocity_eci_kms, dtype=float))
        if self.position_eci_km.shape != (3,):
            raise ValueError("Position vector must be three-dimensional in kilometres.")
        if self.velocity_eci_kms.shape != (3,):
            raise ValueError("Velocity vector must be three-dimensional in kilometres per second.")


@dataclass(frozen=True)
class PropagatedStateHistory:
    """Time-ordered state history for an individual spacecraft."""

    satellite_id: str
    samples: Sequence[StateSample]

    def ordered_samples(self) -> List[StateSample]:
        """Return samples sorted by epoch to enforce STK monotonicity requirements."""

        ordered = sorted(self.samples, key=lambda item: item.epoch)
        return ordered


@dataclass(frozen=True)
class GroundTrackPoint:
    """Geodetic ground-track sample expressed in degrees and kilometres."""

    epoch: datetime
    latitude_deg: float
    longitude_deg: float
    altitude_km: float = 0.0


@dataclass(frozen=True)
class GroundTrack:
    """Ground-track definition for a spacecraft."""

    satellite_id: str
    points: Sequence[GroundTrackPoint]

    def ordered_points(self) -> List[GroundTrackPoint]:
        ordered = sorted(self.points, key=lambda item: item.epoch)
        return ordered


@dataclass(frozen=True)
class GroundContactInterval:
    """Visibility interval between a spacecraft and a facility."""

    satellite_id: str
    facility_name: str
    start: datetime
    end: datetime

    def duration(self) -> timedelta:
        return self.end - self.start


@dataclass(frozen=True)
class FacilityDefinition:
    """Geodetic facility description suitable for STK Facility objects."""

    name: str
    latitude_deg: float
    longitude_deg: float
    altitude_km: float = 0.0


@dataclass(frozen=True)
class FormationMaintenanceEvent:
    """Impulse or manoeuvre applied during formation maintenance."""

    name: str
    epoch: datetime
    description: str
    delta_v_mps: Optional[float] = None


@dataclass(frozen=True)
class ScenarioMetadata:
    """Scenario-level metadata guiding the exporter."""

    scenario_name: str
    start_epoch: datetime
    stop_epoch: Optional[datetime] = None
    central_body: str = "Earth"
    coordinate_frame: str = "TEME"
    ephemeris_step_seconds: Optional[float] = None


@dataclass(frozen=True)
class SimulationResults:
    """Container aggregating all artefacts required for STK export."""

    state_histories: Sequence[PropagatedStateHistory]
    ground_tracks: Sequence[GroundTrack] = field(default_factory=list)
    ground_contacts: Sequence[GroundContactInterval] = field(default_factory=list)
    facilities: Sequence[FacilityDefinition] = field(default_factory=list)
    events: Sequence[FormationMaintenanceEvent] = field(default_factory=list)


def _format_epoch(epoch: datetime) -> str:
    """Format datetimes following the `dd MMM yyyy HH:MM:SS.ffffff` convention."""

    return epoch.strftime("%d %b %Y %H:%M:%S.%f")[:-3]


def _offset_seconds(start: datetime, epoch: datetime) -> float:
    delta = epoch - start
    return delta.total_seconds()


def _resample_ephemeris(
    times: np.ndarray,
    positions: np.ndarray,
    velocities: np.ndarray,
    step: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Resample vectors to satisfy STK guidance on ephemeris spacing."""

    if times.size < 2:
        raise ValueError("At least two samples are required for interpolation.")

    new_times = np.arange(times[0], times[-1] + 0.5 * step, step, dtype=float)

    if interp1d is not None:
        interpolator_pos = interp1d(times, positions, axis=0, kind="cubic", fill_value="extrapolate")
        interpolator_vel = interp1d(times, velocities, axis=0, kind="cubic", fill_value="extrapolate")
        resampled_positions = interpolator_pos(new_times)
        resampled_velocities = interpolator_vel(new_times)
        return new_times, resampled_positions, resampled_velocities

    # Fall back to NumPy's linear interpolation when SciPy is unavailable. The
    # linear interpolation maintains monotonicity and still produces valid STK
    # ephemeris data for moderate cadence adjustments.
    resampled_positions = np.empty((new_times.size, positions.shape[1]))
    resampled_velocities = np.empty((new_times.size, velocities.shape[1]))
    for axis in range(positions.shape[1]):
        resampled_positions[:, axis] = np.interp(new_times, times, positions[:, axis])
        resampled_velocities[:, axis] = np.interp(new_times, times, velocities[:, axis])
    return new_times, resampled_positions, resampled_velocities


# STK imposes constraints on object identifiers: they must begin with a letter
# or underscore and contain only alphanumeric characters or underscores. To
# prevent runtime errors during import we sanitise every identifier before
# serialising artefacts.


def sanitize_stk_identifier(name: str, default: str = "Object") -> str:
    """Return an identifier compatible with STK naming constraints."""

    stripped = name.strip()
    if not stripped:
        stripped = default
    transformed = [
        char if char.isalnum() or char == "_" else "_"
        for char in stripped
    ]
    candidate = "".join(transformed)
    candidate = re.sub("_+", "_", candidate).strip("_")
    if not candidate:
        candidate = default
    if candidate[0] not in string.ascii_letters + "_":
        candidate = f"_{candidate}"
    return candidate


def unique_stk_names(names: Iterable[str]) -> dict[str, str]:
    """Map the supplied identifiers to unique, STK-safe alternatives."""

    mapping: dict[str, str] = {}
    used: set[str] = set()
    for name in names:
        if name in mapping:
            continue
        base = sanitize_stk_identifier(name)
        candidate = base
        index = 1
        while candidate in used:
            index += 1
            candidate = f"{base}_{index}"
        mapping[name] = candidate
        used.add(candidate)
    return mapping


def export_simulation_to_stk(
    sim_results: SimulationResults,
    output_path: Path | str,
    scenario_metadata: ScenarioMetadata,
) -> None:
    """Serialise simulation artefacts into STK textual products.

    Parameters
    ----------
    sim_results:
        Aggregated simulation outputs comprising state histories, ground tracks,
        contact intervals, facility metadata, and formation-maintenance events.
    output_path:
        Directory to receive the generated STK files. The path is created if it
        does not already exist.
    scenario_metadata:
        Scenario-level configuration controlling naming, timing, and coordinate
        frame assumptions.

    Notes
    -----
    * State vectors are assumed to be expressed in the TEME frame. Analysts can
      extend the exporter by leveraging :mod:`poliastro` transforms if other
      frames are needed.
    * When `ephemeris_step_seconds` is provided, SciPy's interpolation routines
      are used to densify the ephemeris in accordance with STK guidance on
      maximum sample spacing for high-accuracy propagation.
    """

    output_dir = Path(output_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    safe_metadata = ScenarioMetadata(
        scenario_name=sanitize_stk_identifier(
            scenario_metadata.scenario_name, default="Scenario"
        ),
        start_epoch=scenario_metadata.start_epoch,
        stop_epoch=scenario_metadata.stop_epoch,
        central_body=scenario_metadata.central_body,
        coordinate_frame=scenario_metadata.coordinate_frame,
        ephemeris_step_seconds=scenario_metadata.ephemeris_step_seconds,
    )

    satellite_names: list[str] = []
    satellite_names.extend(history.satellite_id for history in sim_results.state_histories)
    satellite_names.extend(track.satellite_id for track in sim_results.ground_tracks)
    satellite_names.extend(interval.satellite_id for interval in sim_results.ground_contacts)
    satellite_map = unique_stk_names(satellite_names)

    facility_names: list[str] = []
    facility_names.extend(facility.name for facility in sim_results.facilities)
    facility_names.extend(interval.facility_name for interval in sim_results.ground_contacts)
    facility_map = unique_stk_names(facility_names)

    event_names = [event.name for event in sim_results.events]
    event_map = unique_stk_names(event_names)

    sanitised_histories = [
        PropagatedStateHistory(
            satellite_id=satellite_map.get(
                history.satellite_id,
                sanitize_stk_identifier(history.satellite_id),
            ),
            samples=history.samples,
        )
        for history in sim_results.state_histories
    ]

    sanitised_tracks = [
        GroundTrack(
            satellite_id=satellite_map.get(
                track.satellite_id, sanitize_stk_identifier(track.satellite_id)
            ),
            points=track.points,
        )
        for track in sim_results.ground_tracks
    ]

    sanitised_contacts = [
        GroundContactInterval(
            satellite_id=satellite_map.get(
                interval.satellite_id,
                sanitize_stk_identifier(interval.satellite_id),
            ),
            facility_name=facility_map.get(
                interval.facility_name,
                sanitize_stk_identifier(interval.facility_name, default="Facility"),
            ),
            start=interval.start,
            end=interval.end,
        )
        for interval in sim_results.ground_contacts
    ]

    sanitised_facilities = [
        FacilityDefinition(
            name=facility_map.get(
                facility.name,
                sanitize_stk_identifier(facility.name, default="Facility"),
            ),
            latitude_deg=facility.latitude_deg,
            longitude_deg=facility.longitude_deg,
            altitude_km=facility.altitude_km,
        )
        for facility in sim_results.facilities
    ]

    sanitised_events = [
        FormationMaintenanceEvent(
            name=event_map.get(event.name, sanitize_stk_identifier(event.name, default="Event")),
            epoch=event.epoch,
            description=event.description,
            delta_v_mps=event.delta_v_mps,
        )
        for event in sim_results.events
    ]

    sanitised_results = SimulationResults(
        state_histories=sanitised_histories,
        ground_tracks=sanitised_tracks,
        ground_contacts=sanitised_contacts,
        facilities=sanitised_facilities,
        events=sanitised_events,
    )

    # Derive an effective stop epoch if one is not supplied. The propagation
    # end time is the latest asset sample, ensuring the scenario bounds wrap
    # the exported ephemerides.
    if safe_metadata.stop_epoch is None:
        latest_state_epoch = max(
            sample.epoch
            for history in sanitised_results.state_histories
            for sample in history.samples
        )
        stop_epoch = latest_state_epoch
    else:
        stop_epoch = safe_metadata.stop_epoch

    _write_ephemerides(sanitised_results, output_dir, safe_metadata)
    _write_satellite_objects(sanitised_results, output_dir, safe_metadata)
    _write_ground_tracks(sanitised_results, output_dir, safe_metadata)
    _write_facilities(sanitised_results, output_dir, safe_metadata)
    _write_ground_contacts(sanitised_results, output_dir)
    _write_events(sanitised_results, output_dir)
    _write_scenario_file(
        sanitised_results,
        output_dir,
        safe_metadata,
        stop_epoch,
    )


def _write_ephemerides(
    sim_results: SimulationResults,
    output_dir: Path,
    scenario_metadata: ScenarioMetadata,
) -> None:
    for history in sim_results.state_histories:
        samples = history.ordered_samples()
        times = np.array([
            _offset_seconds(scenario_metadata.start_epoch, sample.epoch)
            for sample in samples
        ], dtype=float)
        if np.any(np.diff(times) <= 0):
            raise ValueError(
                f"Ephemeris samples for {history.satellite_id} must be strictly increasing."
            )

        positions = np.vstack([sample.position_eci_km for sample in samples])
        velocities = np.vstack([sample.velocity_eci_kms for sample in samples])

        if scenario_metadata.ephemeris_step_seconds:
            times, positions, velocities = _resample_ephemeris(
                times,
                positions,
                velocities,
                scenario_metadata.ephemeris_step_seconds,
            )

        ephemeris_path = output_dir / f"{history.satellite_id}.e"
        with ephemeris_path.open("w", encoding="utf-8") as stream:
            stream.write("stk.v.11.0\n")
            stream.write("BEGIN Ephemeris\n")
            stream.write(f"NumberOfEphemerisPoints {positions.shape[0]}\n")
            stream.write(f"ScenarioEpoch {_format_epoch(scenario_metadata.start_epoch)}\n")
            stream.write("InterpolationMethod Lagrange\n")
            stream.write("InterpolationOrder 7\n")
            stream.write(f"CentralBody {scenario_metadata.central_body}\n")
            stream.write(f"CoordinateSystem {scenario_metadata.coordinate_frame}\n")
            stream.write("DistanceUnit Kilometers\n")
            stream.write("BEGIN EphemerisTimePosVel\n")
            for t, pos, vel in zip(times, positions, velocities):
                line = "{time:.6f} {px:.9f} {py:.9f} {pz:.9f} {vx:.9f} {vy:.9f} {vz:.9f}\n".format(
                    time=t,
                    px=pos[0],
                    py=pos[1],
                    pz=pos[2],
                    vx=vel[0],
                    vy=vel[1],
                    vz=vel[2],
                )
                stream.write(line)
            stream.write("END EphemerisTimePosVel\n")
            stream.write("END Ephemeris\n")


def _write_satellite_objects(
    sim_results: SimulationResults,
    output_dir: Path,
    scenario_metadata: ScenarioMetadata,
) -> None:
    for history in sim_results.state_histories:
        satellite_path = output_dir / f"{history.satellite_id}.sat"
        ephemeris_filename = f"{history.satellite_id}.e"
        with satellite_path.open("w", encoding="utf-8") as stream:
            stream.write("stk.v.11.0\n")
            stream.write("BEGIN Satellite\n")
            stream.write(f"Name {history.satellite_id}\n")
            stream.write(f"CentralBody {scenario_metadata.central_body}\n")
            stream.write("BEGIN Ephemeris\n")
            stream.write("   Type External\n")
            stream.write(f"   File \"{ephemeris_filename}\"\n")
            stream.write("END Ephemeris\n")
            stream.write("END Satellite\n")


def _write_ground_tracks(
    sim_results: SimulationResults,
    output_dir: Path,
    scenario_metadata: ScenarioMetadata,
) -> None:
    for track in sim_results.ground_tracks:
        points = track.ordered_points()
        times = np.array([
            _offset_seconds(scenario_metadata.start_epoch, point.epoch)
            for point in points
        ], dtype=float)
        if np.any(np.diff(times) < 0):
            raise ValueError(
                f"Ground-track samples for {track.satellite_id} must be non-decreasing."
            )
        track_path = output_dir / f"{track.satellite_id}_groundtrack.gt"
        with track_path.open("w", encoding="utf-8") as stream:
            stream.write("stk.v.11.0\n")
            stream.write("BEGIN GroundTrack\n")
            stream.write(f"SatelliteId {track.satellite_id}\n")
            stream.write(f"CoordinateSystem {scenario_metadata.coordinate_frame}\n")
            stream.write(f"NumberOfPoints {len(points)}\n")
            stream.write("BEGIN Points\n")
            for time_offset, point in zip(times, points):
                stream.write(
                    "{time:.6f} {lat:.6f} {lon:.6f} {alt:.3f}\n".format(
                        time=time_offset,
                        lat=point.latitude_deg,
                        lon=point.longitude_deg,
                        alt=point.altitude_km,
                    )
                )
            stream.write("END Points\n")
            stream.write("END GroundTrack\n")


def _write_facilities(
    sim_results: SimulationResults,
    output_dir: Path,
    scenario_metadata: ScenarioMetadata,
) -> None:
    for facility in sim_results.facilities:
        facility_path = output_dir / f"Facility_{facility.name}.fac"
        with facility_path.open("w", encoding="utf-8") as stream:
            stream.write("stk.v.11.0\n")
            stream.write("BEGIN Facility\n")
            stream.write(f"Name {facility.name}\n")
            stream.write(f"CentralBody {scenario_metadata.central_body}\n")
            stream.write("BEGIN Location\n")
            stream.write(f"Latitude {facility.latitude_deg:.6f}\n")
            stream.write(f"Longitude {facility.longitude_deg:.6f}\n")
            stream.write(f"Altitude {facility.altitude_km:.3f}\n")
            stream.write("END Location\n")
            stream.write("END Facility\n")


def _write_ground_contacts(sim_results: SimulationResults, output_dir: Path) -> None:
    if not sim_results.ground_contacts:
        return
    grouped: dict[str, List[GroundContactInterval]] = {}
    for interval in sim_results.ground_contacts:
        grouped.setdefault(interval.facility_name, []).append(interval)
    for facility_name, intervals in grouped.items():
        intervals_sorted = sorted(intervals, key=lambda item: item.start)
        contacts_path = output_dir / f"Contacts_{facility_name}.int"
        with contacts_path.open("w", encoding="utf-8") as stream:
            stream.write("stk.v.11.0\n")
            stream.write("BEGIN IntervalList\n")
            stream.write(f"Name {facility_name}_Contacts\n")
            stream.write(f"NumberOfIntervals {len(intervals_sorted)}\n")
            for interval in intervals_sorted:
                stream.write("BEGIN Interval\n")
                stream.write(f"   Asset {interval.satellite_id}\n")
                stream.write(f"   StartTime {_format_epoch(interval.start)}\n")
                stream.write(f"   StopTime {_format_epoch(interval.end)}\n")
                stream.write("END Interval\n")
            stream.write("END IntervalList\n")


def _write_events(sim_results: SimulationResults, output_dir: Path) -> None:
    events = sorted(sim_results.events, key=lambda item: item.epoch)
    if not events:
        return
    events_path = output_dir / "formation_events.evt"
    with events_path.open("w", encoding="utf-8") as stream:
        stream.write("stk.v.11.0\n")
        stream.write("BEGIN EventSet\n")
        stream.write(f"NumberOfEvents {len(events)}\n")
        for event in events:
            stream.write("BEGIN Event\n")
            stream.write(f"   Name {event.name}\n")
            stream.write(f"   Time {_format_epoch(event.epoch)}\n")
            stream.write(f"   Description {event.description}\n")
            if event.delta_v_mps is not None:
                stream.write(f"   DeltaV {event.delta_v_mps:.3f}\n")
            stream.write("END Event\n")
        stream.write("END EventSet\n")


def _write_scenario_file(
    sim_results: SimulationResults,
    output_dir: Path,
    scenario_metadata: ScenarioMetadata,
    stop_epoch: datetime,
) -> None:
    scenario_path = output_dir / f"{scenario_metadata.scenario_name}.sc"
    with scenario_path.open("w", encoding="utf-8") as stream:
        stream.write("stk.v.11.0\n")
        stream.write("BEGIN Scenario\n")
        stream.write(f"Name {scenario_metadata.scenario_name}\n")
        stream.write(f"CentralBody {scenario_metadata.central_body}\n")
        stream.write("BEGIN TimePeriod\n")
        stream.write(f"   StartTime {_format_epoch(scenario_metadata.start_epoch)}\n")
        stream.write(f"   StopTime {_format_epoch(stop_epoch)}\n")
        stream.write("END TimePeriod\n")
        stream.write("BEGIN Assets\n")
        for history in sim_results.state_histories:
            stream.write(f"   Satellite {history.satellite_id}.sat\n")
        stream.write("END Assets\n")
        if sim_results.events:
            stream.write("BEGIN EventFiles\n")
            stream.write("   formation_events.evt\n")
            stream.write("END EventFiles\n")
        stream.write("END Scenario\n")
