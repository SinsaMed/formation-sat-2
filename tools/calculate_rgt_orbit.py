"""
Calculates the semi-major axis for a repeating ground track orbit.

This script implements the J2-only "Flower Constellation (FC)" method to find
the required semi-major axis for a satellite to have a repeating ground track.
"""
import argparse
import math
from scipy.optimize import fsolve

# WGS-84 Earth constants
MU_EARTH = 3.986004418e14  # Gravitational parameter (m^3/s^2)
R_E = 6378137.0  # Earth equatorial radius (m)
J2 = 0.00108262668  # J2 perturbation term
OMEGA_E = 7.2921150e-5  # Earth rotation rate (rad/s)

def rgt_equation(a, Np, Nd, i, e):
    """
    The repeating ground track condition equation to be solved for 'a'.

    This is based on Equation (15) from the reference paper, rearranged to
    form a function f(a) = 0.
    """
    if a <= R_E:
        return float('inf') # Invalid solution

    n = math.sqrt(MU_EARTH / a**3)  # Mean motion
    p = a * (1 - e**2)  # Semi-latus rectum

    # Secular drift rates due to J2
    dot_omega = (3 * n * R_E**2 * J2) / (4 * p**2) * (4 - 5 * math.sin(i)**2)
    dot_Omega = -(3 * n * R_E**2 * J2) / (2 * p**2) * math.cos(i)
    dot_M = (3 * n * R_E**2 * J2 * math.sqrt(1 - e**2)) / (4 * p**2) * (2 - 3 * math.sin(i)**2)

    # Nodal period (T_omega) and Greenwich period (T_omega_G)
    T_omega = (2 * math.pi) / (n + dot_M + dot_omega)
    T_omega_G = (2 * math.pi) / (OMEGA_E - dot_Omega)

    # The error function to be minimized
    error = (Nd / Np) - (T_omega / T_omega_G)
    return error

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--Np', type=int, required=True, help='Number of satellite revolutions in the repeat cycle.')
    parser.add_argument('--Nd', type=int, required=True, help='Number of sidereal days in the repeat cycle.')
    parser.add_argument('--inclination', type=float, required=True, help='Orbit inclination in degrees.')
    parser.add_argument('--eccentricity', type=float, default=0.0, help='Orbit eccentricity.')
    args = parser.parse_args()

    inclination_rad = math.radians(args.inclination)

    # Initial guess for semi-major axis (from two-body dynamics)
    T_orb_approx = (args.Nd * 2 * math.pi / OMEGA_E) / args.Np
    a_guess = (MU_EARTH * (T_orb_approx / (2 * math.pi))**2)**(1/3)

    # Solve for the precise semi-major axis
    a_solution, = fsolve(rgt_equation, a_guess, args=(args.Np, args.Nd, inclination_rad, args.eccentricity))

    altitude_km = (a_solution - R_E) / 1000.0
    semi_major_axis_km = a_solution / 1000.0

    print(f"Calculation for Np={args.Np}, Nd={args.Nd}, i={args.inclination} deg:")
    print(f"  - Solved Semi-major Axis: {semi_major_axis_km:.6f} km")
    print(f"  - Corresponding Altitude: {altitude_km:.6f} km")

if __name__ == "__main__":
    main()
