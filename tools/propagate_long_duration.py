"""
Propagates a satellite constellation for a long duration to generate ground track data.
"""
import argparse
import json
from datetime import datetime, timedelta
from pathlib import Path
import math
import pandas as pd
import numpy as np

from src.constellation.orbit import (
    propagate_kepler,
    propagate_perturbed,
    inertial_to_ecef,
    geodetic_coordinates,
    OrbitalElements,
    classical_to_cartesian,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]

def _parse_time(value: str) -> datetime:
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    return datetime.fromisoformat(text)

def _lvlh_frame(position: np.ndarray, velocity: np.ndarray) -> np.ndarray:
    r = np.asarray(position, dtype=float)
    v = np.asarray(velocity, dtype=float)
    r_hat = r / np.linalg.norm(r)
    h = np.cross(r, v)
    k_hat = h / np.linalg.norm(h)
    j_hat = np.cross(k_hat, r_hat)
    j_hat /= np.linalg.norm(j_hat)
    return np.column_stack((r_hat, j_hat, k_hat))

def _formation_offsets(side_length_m: float) -> dict[str, np.ndarray]:
    """Return equilateral offsets constrained to the local horizontal plane."""
    sqrt_three = math.sqrt(3.0)
    return {
        "SAT-1": np.array([0.0, -0.5 * side_length_m, -sqrt_three / 6.0 * side_length_m]),
        "SAT-2": np.array([0.0, 0.5 * side_length_m, -sqrt_three / 6.0 * side_length_m]),
        "SAT-3": np.array([0.0, 0.0, sqrt_three / 3.0 * side_length_m]),
    }

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        type=Path,
        required=True,
        help="Path to the scenario configuration file.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Directory in which to write the ground track data.",
    )
    parser.add_argument(
        "--time-step-s",
        type=int,
        default=60,
        help="Time step for the simulation in seconds.",
    )
    parser.add_argument(
        "--duration-days",
        type=float,
        help="Override the simulation duration in days. Will be converted to seconds.",
    )
    args = parser.parse_args()

    # Load configuration
    with open(args.config, "r") as f:
        config = json.load(f)

    reference = config["reference_orbit"]
    formation = config["formation"]

    epoch = _parse_time(reference["epoch_utc"])
    elements = OrbitalElements(
        semi_major_axis=float(reference["semi_major_axis_km"]) * 1000.0,
        eccentricity=float(reference["eccentricity"]),
        inclination=math.radians(float(reference["inclination_deg"])),
        raan=math.radians(float(reference["raan_deg"])),
        arg_perigee=math.radians(float(reference["argument_of_perigee_deg"])),
        mean_anomaly=math.radians(float(reference["mean_anomaly_deg"])),
    )
    side_length_m = float(formation["side_length_m"])
    offsets_m = _formation_offsets(side_length_m)
    satellite_ids = sorted(offsets_m.keys())
    ballistic_coefficient = float(formation.get("ballistic_coefficient_m2_kg", 0.05)) # Read from config

    # Determine simulation duration
    if args.duration_days is not None:
        simulation_duration_s = args.duration_days * 86400.0
    else:
        simulation_duration_s = float(formation.get("duration_s", 14 * 24 * 3600)) # Default to 14 days if not specified
    
    duration_days = int(round(simulation_duration_s / 86400.0))
    num_steps = int(simulation_duration_s // args.time_step_s)
    records = []

    current_elements = {sat_id: elements for sat_id in satellite_ids}

    for i in range(num_steps):
        dt = args.time_step_s
        current_time = epoch + timedelta(seconds=i * dt)

        for sat_id in satellite_ids:
            # Propagate each satellite with perturbations
            current_elements[sat_id] = propagate_perturbed(
                current_elements[sat_id], dt, ballistic_coefficient
            )
            
            # Convert to Cartesian for LVLH frame calculation
            ref_pos, ref_vel = classical_to_cartesian(current_elements[sat_id])
            frame = _lvlh_frame(ref_pos, ref_vel)

            offset_vec = frame @ offsets_m[sat_id]
            sat_pos_inertial = ref_pos + offset_vec
            
            # Convert to ECEF and then to geodetic
            sat_pos_ecef = inertial_to_ecef(sat_pos_inertial, current_time)
            lat, lon, alt = geodetic_coordinates(sat_pos_ecef)

            records.append({
                "time_utc": current_time.isoformat().replace("+00:00", "Z"),
                "satellite_id": sat_id,
                "latitude_deg": math.degrees(lat),
                "longitude_deg": math.degrees(lon),
                "altitude_km": alt / 1000.0,
            })

    # Save data
    df = pd.DataFrame.from_records(records)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    output_filename = f"ground_track_{duration_days}day.csv"
    output_path = args.output_dir / output_filename
    df.to_csv(output_path, index=False)
    print(f"{duration_days}-day ground track data saved to: {output_path}")

if __name__ == "__main__":
    main()
