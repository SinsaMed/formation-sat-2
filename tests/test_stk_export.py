from datetime import datetime, timedelta
from pathlib import Path
import sys

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools import (
    FacilityDefinition,
    FormationMaintenanceEvent,
    GroundContactInterval,
    GroundTrack,
    GroundTrackPoint,
    PropagatedStateHistory,
    ScenarioMetadata,
    SimulationResults,
    StateSample,
    export_simulation_to_stk,
)


def test_exporter_generates_stk_files(tmp_path: Path) -> None:
    start_epoch = datetime(2024, 1, 1, 12, 0, 0)
    samples = [
        StateSample(
            epoch=start_epoch + timedelta(minutes=i * 10),
            position_eci_km=np.array([7000 + i, 0.1 * i, -0.2 * i]),
            velocity_eci_kms=np.array([0.0, 7.5 + 0.01 * i, 0.0]),
        )
        for i in range(3)
    ]
    history = PropagatedStateHistory(satellite_id="SAT-1", samples=samples)

    ground_track = GroundTrack(
        satellite_id="SAT-1",
        points=[
            GroundTrackPoint(
                epoch=start_epoch + timedelta(minutes=5 * i),
                latitude_deg=0.5 * i,
                longitude_deg=1.0 * i,
                altitude_km=400.0,
            )
            for i in range(3)
        ],
    )

    contact = GroundContactInterval(
        satellite_id="SAT-1",
        facility_name="HARPA",
        start=start_epoch + timedelta(minutes=3),
        end=start_epoch + timedelta(minutes=13),
    )

    facility = FacilityDefinition(
        name="HARPA",
        latitude_deg=64.128288,
        longitude_deg=-21.827774,
        altitude_km=0.050,
    )

    event = FormationMaintenanceEvent(
        name="DV1",
        epoch=start_epoch + timedelta(minutes=15),
        description="Phasing correction burn",
        delta_v_mps=0.12,
    )

    sim_results = SimulationResults(
        state_histories=[history],
        ground_tracks=[ground_track],
        ground_contacts=[contact],
        facilities=[facility],
        events=[event],
    )
    metadata = ScenarioMetadata(
        scenario_name="FormationExperiment",
        start_epoch=start_epoch,
        central_body="Earth",
        coordinate_frame="TEME",
    )

    export_simulation_to_stk(sim_results, tmp_path, metadata)

    ephemeris_path = tmp_path / "SAT_1.e"
    assert ephemeris_path.exists()
    content = ephemeris_path.read_text(encoding="utf-8").splitlines()
    stripped = [line.strip() for line in content]
    assert stripped[0] == "stk.v.11.0"
    assert "BEGIN Ephemeris" in stripped
    idx_start = stripped.index("BEGIN EphemerisTimePosVel") + 1
    idx_end = stripped.index("END EphemerisTimePosVel")
    time_tags = [float(stripped[i].split()[0]) for i in range(idx_start, idx_end)]
    assert time_tags == sorted(time_tags)

    satellite_path = tmp_path / "SAT_1.sat"
    assert satellite_path.exists()
    satellite_lines = [line.strip() for line in satellite_path.read_text(encoding="utf-8").splitlines()]
    assert "BEGIN Satellite" in satellite_lines
    assert any(line.split()[:2] == ["CentralBody", "Earth"] for line in satellite_lines if line)
    assert any(line.split()[:2] == ["File", '"SAT_1.e"'] for line in satellite_lines if line)

    scenario_path = tmp_path / "FormationExperiment.sc"
    scenario_lines = [line.strip() for line in scenario_path.read_text(encoding="utf-8").splitlines()]
    assert "BEGIN Scenario" in scenario_lines
    assert any(line.split() == ["Name", "FormationExperiment"] for line in scenario_lines if line)
    assert any(line.split()[:2] == ["Satellite", "SAT_1.sat"] for line in scenario_lines if line)
    assert "BEGIN Animation" in scenario_lines
    assert any(line.split()[:2] == ["AnimationStep", "1.000000"] for line in scenario_lines if line)
    assert any(
        line.split()[:2] == ["Facility", "Facility_HARPA.fac"] for line in scenario_lines if line
    )

    facility_path = tmp_path / "Facility_HARPA.fac"
    facility_lines = [line.strip() for line in facility_path.read_text(encoding="utf-8").splitlines()]
    assert "BEGIN Facility" in facility_lines
    latitude_line = next(line for line in facility_lines if line.startswith("Latitude"))
    assert float(latitude_line.split()[1]) == pytest.approx(64.128288, abs=1e-9)

    contact_path = tmp_path / "Contacts_HARPA.int"
    contact_lines = [line.strip() for line in contact_path.read_text(encoding="utf-8").splitlines()]
    assert "BEGIN IntervalList" in contact_lines
    start_line = next(line for line in contact_lines if line.startswith("StartTime"))
    assert start_line.endswith("12:03:00.000000000 UTCG")

    event_path = tmp_path / "formation_events.evt"
    event_lines = [line.strip() for line in event_path.read_text(encoding="utf-8").splitlines()]
    assert "BEGIN EventSet" in event_lines
    delta_v_line = next(line for line in event_lines if line.startswith("DeltaV"))
    assert float(delta_v_line.split()[1]) == pytest.approx(0.12, abs=1e-6)

    ground_track_path = tmp_path / "SAT_1_groundtrack.gt"
    track_lines = [line.strip() for line in ground_track_path.read_text(encoding="utf-8").splitlines()]
    assert "BEGIN GroundTrack" in track_lines
    assert any(line.split()[:2] == ["NumberOfPoints", "3"] for line in track_lines if line)


def test_exporter_sanitises_object_names(tmp_path: Path) -> None:
    start_epoch = datetime(2024, 5, 1, 8, 0, 0)
    samples = [
        StateSample(
            epoch=start_epoch + timedelta(seconds=i * 30),
            position_eci_km=np.array([6800 + i, 0.0, 0.0]),
            velocity_eci_kms=np.array([0.0, 7.5, 0.0]),
        )
        for i in range(2)
    ]
    history = PropagatedStateHistory(satellite_id="SAT-1 A", samples=samples)

    ground_track = GroundTrack(
        satellite_id="SAT-1 A",
        points=[
            GroundTrackPoint(
                epoch=start_epoch + timedelta(seconds=15 * i),
                latitude_deg=1.2 * i,
                longitude_deg=-0.6 * i,
                altitude_km=410.0,
            )
            for i in range(2)
        ],
    )

    contact = GroundContactInterval(
        satellite_id="SAT-1 A",
        facility_name="Test Facility",
        start=start_epoch + timedelta(seconds=10),
        end=start_epoch + timedelta(seconds=70),
    )

    facility = FacilityDefinition(
        name="Test Facility",
        latitude_deg=35.0,
        longitude_deg=51.0,
        altitude_km=1.0,
    )

    sim_results = SimulationResults(
        state_histories=[history],
        ground_tracks=[ground_track],
        ground_contacts=[contact],
        facilities=[facility],
    )

    metadata = ScenarioMetadata(
        scenario_name="Tehran Triangle Formation",
        start_epoch=start_epoch,
        central_body="Earth",
        coordinate_frame="TEME",
    )

    export_simulation_to_stk(sim_results, tmp_path, metadata)

    scenario_path = tmp_path / "Tehran_Triangle_Formation.sc"
    assert scenario_path.exists()
    scenario_lines = [line.strip() for line in scenario_path.read_text(encoding="utf-8").splitlines()]
    assert any(line.split() == ["Name", "Tehran_Triangle_Formation"] for line in scenario_lines if line)
    assert any(line.split()[:2] == ["Satellite", "SAT_1_A.sat"] for line in scenario_lines if line)
    assert any(
        line.split()[:2] == ["Facility", "Facility_Test_Facility.fac"] for line in scenario_lines if line
    )

    ephemeris_path = tmp_path / "SAT_1_A.e"
    assert ephemeris_path.exists()

    satellite_path = tmp_path / "SAT_1_A.sat"
    assert satellite_path.exists()
    satellite_lines = [line.strip() for line in satellite_path.read_text(encoding="utf-8").splitlines()]
    assert any(line.split() == ["Name", "SAT_1_A"] for line in satellite_lines if line)
    assert any(line.split()[:2] == ["File", '"SAT_1_A.e"'] for line in satellite_lines if line)

    contact_path = tmp_path / "Contacts_Test_Facility.int"
    assert contact_path.exists()
    contact_lines = [line.strip() for line in contact_path.read_text(encoding="utf-8").splitlines()]
    assert any(line.split()[:2] == ["Asset", "SAT_1_A"] for line in contact_lines if line)

    facility_path = tmp_path / "Facility_Test_Facility.fac"
    assert facility_path.exists()
