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

    ephemeris_path = tmp_path / "SAT-1.e"
    assert ephemeris_path.exists()
    content = ephemeris_path.read_text(encoding="utf-8").splitlines()
    assert content[0] == "stk.v.11.0"
    assert "BEGIN Ephemeris" in content
    idx_start = content.index("BEGIN EphemerisTimePosVel") + 1
    idx_end = content.index("END EphemerisTimePosVel")
    time_tags = [float(line.split()[0]) for line in content[idx_start:idx_end]]
    assert time_tags == sorted(time_tags)

    scenario_path = tmp_path / "FormationExperiment.sc"
    scenario_text = scenario_path.read_text(encoding="utf-8")
    assert "BEGIN Scenario" in scenario_text
    assert "FormationExperiment" in scenario_text

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

    ground_track_path = tmp_path / "SAT-1_groundtrack.gt"
    track_text = ground_track_path.read_text(encoding="utf-8")
    assert "BEGIN GroundTrack" in track_text
    assert "NumberOfPoints 3" in track_text
