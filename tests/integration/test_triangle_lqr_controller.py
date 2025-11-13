import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Tuple

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Tuple

import numpy as np

from sim.formation.triangle import _formation_offsets, simulate_triangle_formation
from sim.formation.design import design_j2_invariant_formation
from src.constellation.orbit import classical_to_cartesian, propagate_perturbed
from src.constellation.roe import OrbitalElements

CONFIG_PATH = Path("config/scenarios/tehran_triangle.json")


def _load_base_configuration() -> Dict[str, object]:
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def _initial_elements(config: Dict[str, object]) -> Tuple[Dict[str, OrbitalElements], datetime]:
    reference_cfg = config["reference_orbit"]
    reference = OrbitalElements(
        semi_major_axis=float(reference_cfg["semi_major_axis_km"]) * 1_000.0,
        eccentricity=float(reference_cfg.get("eccentricity", 0.0)),
        inclination=np.deg2rad(float(reference_cfg.get("inclination_deg", 0.0))),
        raan=np.deg2rad(float(reference_cfg.get("raan_deg", 0.0))),
        arg_perigee=np.deg2rad(float(reference_cfg.get("argument_of_perigee_deg", 0.0))),
        mean_anomaly=np.deg2rad(float(reference_cfg.get("mean_anomaly_deg", 0.0))),
    )
    offsets = _formation_offsets(float(config["formation"]["side_length_m"]))
    design = design_j2_invariant_formation(reference, offsets)
    epoch = datetime.fromisoformat(reference_cfg["epoch_utc"].replace("Z", "+00:00"))
    return design.satellite_elements, epoch


def _propagate_with_segments(
    elements: OrbitalElements, duration_s: float, *, step_s: float = 120.0
) -> OrbitalElements:
    remaining = abs(duration_s)
    propagated = elements
    if remaining == 0.0:
        return propagated
    direction = 1.0 if duration_s >= 0.0 else -1.0
    while remaining > 0.0:
        chunk = min(step_s, remaining) * direction
        propagated = propagate_perturbed(propagated, chunk, 0.025)
        remaining -= min(step_s, remaining)
    return propagated


def _position_error_statistics(
    result, initial_elements: Dict[str, OrbitalElements], epoch: datetime
) -> Tuple[float, float]:
    step_s = 120.0
    errors: list[float] = []
    for index, timestamp in enumerate(result.times):
        if timestamp < epoch:
            continue
        dt = (timestamp - epoch).total_seconds()
        for sat_id, positions in result.positions_m.items():
            propagated = _propagate_with_segments(initial_elements[sat_id], dt, step_s=step_s)
            ideal_pos, _ = classical_to_cartesian(propagated)
            errors.append(float(np.linalg.norm(positions[index] - ideal_pos)))
    array = np.asarray(errors, dtype=float)
    return float(array.max()), float(array.mean())


def test_lqr_controller_reduces_position_error() -> None:
    base_config = _load_base_configuration()
    formation = base_config["formation"]
    formation.update(
        {
            "duration_s": 10_800.0,
            "time_step_s": 60.0,
            "prediction_horizon_s": 600.0,
            "station_keeping_tolerance_m": 10.0,
            "station_keeping_interval_s": 900.0,
            "lqr": {
                "r_diagonal": [1_000_000.0, 1_000_000.0, 1_000_000.0],
                "max_delta_v_mps": 0.005,
                "integration_step_s": 120.0,
            },
        }
    )

    initial_elements, epoch = _initial_elements(base_config)
    controlled_result = simulate_triangle_formation(base_config)
    controlled_max, controlled_mean = _position_error_statistics(
        controlled_result, initial_elements, epoch
    )

    assert controlled_max <= 500.0
    assert controlled_mean <= 400.0

    total_delta_v = controlled_result.metrics["station_keeping"][
        "total_delta_v_consumed_mps"
    ]
    assert total_delta_v <= 0.2
