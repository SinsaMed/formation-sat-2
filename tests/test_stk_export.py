from datetime import datetime, timedelta
from pathlib import Path
import sys

import numpy as np

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
    assert content[0] == "stk.v.11.0"
    assert "BEGIN Ephemeris" in content
    idx_start = content.index("BEGIN EphemerisTimePosVel") + 1
    idx_end = content.index("END EphemerisTimePosVel")
    time_tags = [float(line.split()[0]) for line in content[idx_start:idx_end]]
    assert time_tags == sorted(time_tags)

    satellite_path = tmp_path / "SAT_1.sat"
    assert satellite_path.exists()
    satellite_lines = satellite_path.read_text(encoding="utf-8").splitlines()
    assert "BEGIN Satellite" in satellite_lines
    assert "CentralBody Earth" in satellite_lines
    assert any('File "SAT_1.e"' in line for line in satellite_lines)

    scenario_path = tmp_path / "FormationExperiment.sc"
    scenario_text = scenario_path.read_text(encoding="utf-8")
    assert "BEGIN Scenario" in scenario_text
    assert "FormationExperiment" in scenario_text
    assert "Satellite SAT_1.sat" in scenario_text
    assert "BEGIN Animation" in scenario_text
    assert "AnimationStep 1.000" in scenario_text
    assert "Facility Facility_HARPA.fac" in scenario_text

    facility_path = tmp_path / "Facility_HARPA.fac"
    facility_text = facility_path.read_text(encoding="utf-8")
    assert "BEGIN Facility" in facility_text
    assert "Latitude 64.128288" in facility_text

    contact_path = tmp_path / "Contacts_HARPA.int"
    contact_text = contact_path.read_text(encoding="utf-8")
    assert "BEGIN IntervalList" in contact_text
    assert "StartTime 01 Jan 2024 12:03:00.000" in contact_text

    event_path = tmp_path / "formation_events.evt"
    event_text = event_path.read_text(encoding="utf-8")
    assert "BEGIN EventSet" in event_text
    assert "DeltaV 0.120" in event_text

    ground_track_path = tmp_path / "SAT_1_groundtrack.gt"
    track_text = ground_track_path.read_text(encoding="utf-8")
    assert "BEGIN GroundTrack" in track_text
    assert "NumberOfPoints 3" in track_text


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
    scenario_text = scenario_path.read_text(encoding="utf-8")
    assert "Name Tehran_Triangle_Formation" in scenario_text
    assert "Satellite SAT_1_A" in scenario_text
    assert "Facility Facility_Test_Facility.fac" in scenario_text

    ephemeris_path = tmp_path / "SAT_1_A.e"
    assert ephemeris_path.exists()

    satellite_path = tmp_path / "SAT_1_A.sat"
    assert satellite_path.exists()
    satellite_text = satellite_path.read_text(encoding="utf-8")
    assert "Name SAT_1_A" in satellite_text
    assert 'File "SAT_1_A.e"' in satellite_text

    contact_path = tmp_path / "Contacts_Test_Facility.int"
    assert contact_path.exists()
    contact_text = contact_path.read_text(encoding="utf-8")
    assert "Asset SAT_1_A" in contact_text

    facility_path = tmp_path / "Facility_Test_Facility.fac"
    assert facility_path.exists()
