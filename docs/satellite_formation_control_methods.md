# Satellite Formation Flying Control Methods Over a Target Region

This document summarizes various methods and mathematical relationships used for controlling satellite formations, particularly when maintaining precise relative positions and velocities over a specific ground target. The goal is to ensure mission objectives are met while optimizing resource usage and stability against orbital perturbations.

## 1. Relative Dynamics Modeling

Accurate modeling of relative motion is fundamental to formation flying control.

### 1.1. Hill-Clohessy-Wiltshire (HCW) Equations

The HCW equations are linearized equations of relative motion, valid for small relative distances in a circular reference orbit, neglecting perturbations. They describe the motion of a "deputy" satellite relative to a "chief" satellite.

Let \(x, y, z\) be the radial, along-track, and cross-track relative positions, respectively. For a chief in a circular orbit with mean motion \(n\), the HCW equations are:

\[
\begin{aligned}
\ddot{x} - 3n^2 x - 2n \dot{y} &= 0 \\
\ddot{y} + 2n \dot{x} &= 0 \\
\ddot{z} + n^2 z &= 0
\end{aligned}
\]

These equations provide periodic solutions that are crucial for initial formation design.

### 1.2. Sedwick-Schweighart Equations

These equations extend the HCW model by incorporating the secular effects of the Earth's oblateness (J2 perturbation), providing a more accurate representation for Low Earth Orbit (LEO) missions. The J2 perturbation causes differential nodal and apsidal precession, which must be accounted for.

The J2 perturbation term (\(J_2\)) is approximately \(1.08262668 \times 10^{-3}\). The secular rates of change for Right Ascension of the Ascending Node (RAAN, \(\dot{\Omega}\)) and Argument of Perigee (\(\dot{\omega}\)) due to J2 are:

\[
\begin{aligned}
\dot{\Omega} &= -\frac{3}{2} J_2 \left(\frac{R_E}{a}\right)^2 n \frac{\cos i}{(1-e^2)^2} \\
\dot{\omega} &= \frac{3}{4} J_2 \left(\frac{R_E}{a}\right)^2 n \frac{5\cos^2 i - 1}{(1-e^2)^2}
\end{aligned}
\]

where \(R_E\) is Earth's equatorial radius, \(a\) is semi-major axis, \(i\) is inclination, \(e\) is eccentricity, and \(n\) is mean motion. The Sedwick-Schweighart equations incorporate these differential rates into the relative dynamics.

### 1.3. Relative Orbital Elements (ROEs)

ROEs directly describe the differences in classical orbital elements between satellites. This approach offers a clear physical interpretation of the formation geometry and is more robust for eccentric orbits or significant perturbations.

Commonly used ROEs include differences in semi-major axis (\(\delta a\)), eccentricity vector components (\(\delta e_x, \delta e_y\)), inclination vector components (\(\delta i_x, \delta i_y\)), and mean anomaly (\(\delta M\)).

### 1.4. Non-linear Models

For large separations or highly eccentric orbits, full non-linear relative motion models are employed to maintain high accuracy, often using quasi-nonsingular relative orbital elements.

## 2. Control Architectures

Different strategies dictate how control is distributed and managed within the formation.

### 2.1. Leader-Follower

One satellite (the "leader") follows a predefined trajectory, and other satellites (the "followers") adjust their positions relative to the leader. This simplifies control design but introduces a single point of failure.

### 2.2. Multiple-Input-Multiple-Output (MIMO)

The entire formation is treated as a single system, allowing for centralized control strategies where all control inputs and outputs are managed holistically.

### 2.3. Virtual Structure

Satellites maintain positions relative to a conceptual "virtual structure" or a common virtual rigid body, which itself follows a desired trajectory. This provides a robust framework for maintaining formation geometry.

### 2.4. Autonomous Formation Control

Onboard systems calculate relative positions and execute maneuvers without continuous ground intervention, essential for tight formations requiring frequent adjustments and rapid response to disturbances.

## 3. Control Techniques and Algorithms

Various control theories are applied to maintain and reconfigure satellite formations.

### 3.1. Linear Quadratic Regulator (LQR)

LQR is an optimal control technique that minimizes a quadratic cost function of state deviations and control effort. It is effective for formation keeping and reconfigurations, especially when applied to linearized relative dynamics (e.g., HCW equations).

The control law \(u = -Kx\) is derived by minimizing the cost function:

\[
J = \int_{t_0}^{t_f} (x^T Q x + u^T R u) dt
\]

where \(x\) is the state vector, \(u\) is the control input, and \(Q\) and \(R\) are weighting matrices.

### 3.2. Model Predictive Control (MPC)

MPC uses a predictive model of the satellite dynamics to optimize control inputs over a future horizon, considering constraints and disturbances. It can handle non-linear dynamics and is robust against feedback delays.

### 3.3. H2/H-infinity Optimal Control

These techniques are used for robust control design, aiming to minimize the effect of disturbances and uncertainties on the formation's performance.

### 3.4. Adaptive Control

Adaptive control methods allow the controller to adjust its parameters online in response to changes in the system dynamics or unknown disturbances, making them suitable for environments with varying conditions.

### 3.5. Sliding Mode Control

A robust non-linear control technique that forces the system's state trajectory onto a predefined "sliding surface" in the state space, making it insensitive to certain disturbances and model uncertainties.

## 4. Perturbations and Control Forces

Maintaining a formation requires counteracting various environmental disturbances.

### 4.1. J2 Perturbation

As mentioned in Section 1.2, the Earth's oblateness causes differential precession. Control strategies must actively compensate for these effects to maintain formation integrity.

### 4.2. Atmospheric Drag

For LEO satellites, differential atmospheric drag is a significant disturbance. The drag force (\(F_D\)) is given by:

\[
F_D = \frac{1}{2} \rho v^2 C_D A
\]

where \(\rho\) is atmospheric density, \(v\) is satellite velocity, \(C_D\) is drag coefficient, and \(A\) is the cross-sectional area. Differential drag can be used as a control force by varying the drag area of individual satellites.

### 4.3. Solar Radiation Pressure (SRP)

SRP can perturb orbits, especially for satellites with large area-to-mass ratios. The force due to SRP (\(F_{SRP}\)) is:

\[
F_{SRP} = P_{SRP} C_R A_{SRP}
\]

where \(P_{SRP}\) is solar radiation pressure, \(C_R\) is reflectivity coefficient, and \(A_{SRP}\) is the area exposed to solar radiation. SRP can be harnessed for control using solar sails or differential reflectivity.

### 4.4. Thrusting

Chemical or electric propulsion systems are used to generate control forces (delta-V maneuvers) to establish, maintain, and reconfigure formations. The change in velocity (\(\Delta V\)) required for a maneuver is a key metric for fuel consumption.

## 5. Target Region Considerations

When focusing on a specific target region, additional mathematical relationships and constraints come into play.

### 5.1. Ground Track Repeatability

Designing orbits that repeat their ground track over the target region is crucial for consistent coverage. This involves specific relationships between orbital period, Earth's rotation, and the number of orbits per day. For a repeating ground track, the orbital period \(T\) must satisfy:

\[
T = \frac{2\pi}{\dot{\theta}_E - \dot{\Omega}} \frac{N_p}{N_d}
\]

where \(\dot{\theta}_E\) is Earth's rotation rate, \(\dot{\Omega}\) is the nodal precession rate (due to J2), \(N_p\) is the number of orbits, and \(N_d\) is the number of days for the repeat cycle.

### 5.2. Revisit Performance

Mathematical models are used to optimize constellation design to achieve desired revisit times and coverage over the target, often involving optimization techniques to determine the number of satellites and their orbital planes.

### 5.3. Formation Geometry Optimization

The specific geometry of the satellite formation (e.g., triangular, linear, tetrahedral) is optimized to meet mission requirements over the target, such as synthetic aperture radar (SAR) imaging or interferometry. This involves defining relative position constraints in a local orbital frame (e.g., LVLH).

## Conclusion

Controlling satellite formations over a target region is a multidisciplinary challenge involving precise orbital mechanics, robust control theory, and optimization. The methods outlined above, supported by their mathematical foundations, enable the design and maintenance of complex satellite constellations for various Earth observation and scientific missions.
