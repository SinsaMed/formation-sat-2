# **Orbital Design and Mission Analysis of a Three-Satellite LEO Constellation for Repeatable, Transient Triangular Formation over Tehran: Literature Review and Theoretical Foundation**

## **Chapter 2: Literature Review and State-of-the-Art in Distributed Space Systems**

This chapter provides a comprehensive review of the historical development, architectural classification, operational challenges, and enabling technologies pertinent to the proposed mission: a three-satellite Low Earth Orbit (LEO) constellation executing a repeatable, transient triangular formation over a specific metropolitan target, Tehran. The analysis establishes the necessary context regarding orbit selection, formation dynamics, and adherence to modern space governance standards.

### **2.1 Evolution and Classification of Multi-Satellite Missions**

The concept of coordinated space operations has evolved significantly since the dawn of the space age. Historically, the challenge centered on achieving and controlling relative orbits for terminal maneuvers such as rendezvous and docking, a capability critically demonstrated during the Apollo program.1 In this early stage, orbital corrections were specifically performed not to refine the absolute Earth-relative orbit, but rather to manage and adjust the relative trajectory between two vehicles, often decreasing relative distance slowly and controllably.1

Modern objectives, however, extend far beyond simple proximity operations. Contemporary multi-satellite missions prioritize maintaining highly specific, coordinated geometries over extended durations. This shift is driven by the technical and financial impracticality of constructing large, complex monolithic vehicles capable of distributed functions. For instance, distributed apertures, such as sparse aperture radar dishes formed by a cluster of satellites, avoid the significant structural flexing and pointing difficulties associated with constructing a single, kilometer-scale structure in space.1

#### **2.1.1 Classification of Distributed Space Architectures**

Modern multi-satellite deployments are typically classified based on their operational proximity, coordination level, and mission objective: constellations, swarms, and precise formation flying (PFF).2

##### **2.1.1.1 Constellations**

Constellations consist of a collection of similar spacecraft placed in complementary orbits, primarily designed to act as the space element of a distributed mission, often providing communication services or global coverage.2 Key figures of merit for constellations, such as the coverage area and revisit time, drive their design analysis.2 The utilization of small satellites is critical to the feasibility of large LEO constellations, as it dramatically lowers the development cost, time, and launch expense.3

##### **2.1.1.2 Swarms**

Swarms represent a collection of spacecraft operating in close proximity as a single entity, characterized by principles such as task specialization and sociality, mirroring biological systems.4 Mission concepts, such as the Autonomous Nano-Technology Swarm (ANTS) proposed by NASA for the 2020-2025 timeframe, envision autonomous agents that cooperate to achieve high-level goals, such as characterizing thousands of asteroids annually.4

##### **2.1.1.3 Precise Formation Flying (PFF)**

Precise Formation Flying (PFF), the focus of this thesis, requires the maintenance of a specifically targeted orbit configuration, involving desired relative separation and orientation between a few spacecraft.2 PFF technologies have received significant attention due to the advantages they offer in terms of enhanced mission performance, reduced cost, and flexibility compared to monolithic systems.5 The rigorous demand for sustained, specific geometry maintenance necessitates robust and highly accurate relative orbit modeling.1 The challenge in maintaining a cluster configuration over long periods is significantly greater than performing a short-duration rendezvous maneuver because the former is notably more sensitive to accumulated relative orbit modeling errors.1

### **2.2 Design Trade Space for LEO Earth Observation Constellations**

The selection of Low Earth Orbit (LEO) for this mission is fundamentally driven by the requirement for high-resolution, repeated Earth Observation (EO) over a specific, localized area. LEO is generally defined as the region of space below 2,000 kilometers altitude, with most artificial objects peaking around 800 kilometers.6

#### **2.2.1 LEO Justification and Constraints**

LEO provides the closest proximity to the Earth's surface, which is essential for maximizing spatial resolution in remote sensing applications.7 Satellites in LEO operate at high orbital velocities, reaching speeds up to 7.8 kilometers per second 8, resulting in short orbital periods, typically between 90 and 128 minutes.6

Despite the benefits of proximity, LEO presents significant operational challenges compared to higher orbits.

* **Atmospheric Drag:** LEO experiences greater atmospheric drag, especially at altitudes below 500 km, increasing fuel requirements for station-keeping compared to Medium Earth Orbit (MEO).9  
* **Target Visibility:** Due to the low altitude and high velocity, the coverage area over any single ground station or target is small. Consequently, LEO satellites provide a short visibility window, typically ranging from 2 to 15 minutes per pass.10

The restricted visibility window over the target area (Tehran) is a primary constraint that directly dictates the transient nature of the formation design. Since precise formation maintenance requires continuous control and propellant 11, and the window of utility is limited to a few minutes per pass, the most fuel-efficient operational mode involves establishing the critical triangular geometry (the *transient state*) only when required for observation over the target and allowing the satellites to drift passively, or maintain a less constrained configuration, outside this critical window.12 This approach transforms the core GNC challenge into an optimization problem focused on efficient and rapid transient reconfiguration.

The choice of specific LEO altitude must judiciously balance these trade-offs. While lower altitudes yield higher resolution, they dramatically increase drag. Conversely, the density of artificial objects, and thus collision risk, peaks around 800 kilometers.6 Furthermore, dynamical analysis confirms that in this altitude band (around 800 km), the $J\_2$ perturbation effect is much larger in comparison with other perturbations, such as atmospheric drag.13 The selection of an altitude (and corresponding semi-major axis) therefore constrains the magnitude of the dominant natural perturbation ($J\_2$) that the formation control system must counteract.

#### **2.2.2 Comparative Orbital Analysis**

LEO contrasts sharply with MEO and GEO in terms of operational requirements and mission type.9

MEO satellites, such as those used for GPS, orbit at significantly higher altitudes (up to 22,236 km).9 Station-keeping in MEO is easier and requires less fuel than in LEO due to minimal atmospheric drag and gravitational pull.9 MEO’s higher vantage point means fewer satellites are needed for global coverage, making it ideal for navigation missions.9 However, reaching MEO requires significantly more fuel and larger launch vehicles, and the resulting higher communication latency and the need for stronger transmit power (requiring larger equipment) generally lead to higher overall satellite costs compared to LEO missions.9

Geostationary Orbit (GEO) satellites operate at 35,786 km, appearing stationary over a fixed spot, making them valuable for continuous monitoring and telecommunications.15 While GEO requires the fewest satellites for coverage, its distance yields the lowest spatial resolution, unsuitable for high-fidelity EO missions.7

The decision to utilize LEO, despite its challenges in drag and short pass duration, is mandatory for achieving the necessary spatial resolution for high-fidelity Earth observation applications, such as the implied tri-stereo imaging or distributed aperture radar required for a triangular formation.

| Orbital Regime | Altitude Range (km) | Typical Orbital Period | Key Driver for FF Missions | Primary Mission Challenge |
| :---- | :---- | :---- | :---- | :---- |
| LEO | 200 \- 2,000 6 | 90 \- 128 minutes 6 | High Spatial Resolution, Small Satellite Feasibility 3 | Atmospheric Drag, Short Visibility Window (2-15 min) 9 |
| MEO | 2,000 \- 35,786 9 | \~12 hours 9 | Global Navigation, Reduced Station-keeping Fuel 9 | Higher Power Requirements, Communication Latency 14 |
| GEO | 35,786 15 | 24 hours (Sidereal Day) 15 | Continuous Coverage (Fixed Spot) 15 | Extreme Latency, Low Spatial Resolution 7 |

### **2.3 The Requirement for Repeatable Target Coverage: Repeat Ground Track (RGT) Orbits**

To ensure repeatable observation over the specific metropolitan area of Tehran, the constellation must operate in a Repeat Ground Track (RGT) orbit. An RGT orbit is defined by the satellite retracing its path over the Earth’s surface after a defined period, $k$ sidereal days, consisting of $j$ orbital revolutions.16 This capability is fundamental to Earth observation, particularly for demanding applications like repeat-pass interferometry, which studies surface changes between acquisitions.16

#### **2.3.1 The Role of J2 in RGT Design**

The primary technical difficulty in RGT design in LEO stems from the non-spherical gravitational influence of the Earth, dominated by the second zonal harmonic ($J\_2$).16 The $J\_2$ effect causes the orbital plane to precess (nodal drift), which must be precisely synchronized with the Earth’s rotation to maintain the ground track repetition.18

The selection of the RGT orbit is critical as it imposes fundamental constraints on the design of the relative formation. The RGT calculation fixes the absolute orbital elements, specifically the inclination ($i$) and the semi-major axis ($a$), necessary to satisfy the target coverage requirement over Tehran. These fixed orbital parameters then fundamentally define the environment, including the magnitude of the $J\_2$ differential effects and aerodynamic drag, which the formation control system must manage.

#### **2.3.2 RGT Solution Methodologies**

RGT orbit design relies on both analytical and numerical methodologies.16

Analytical theory, often based solely on the $J\_2$ effect, provides the initial, approximated orbital elements required for RGT missions.16 This method is vital for rapidly designing constraints and providing insight into the relative motion characteristics.20

However, for high-accuracy mission planning, such as synchronizing the overpass precisely with a specific point like Tehran, numerical and iterative techniques are indispensable. These methods allow for the inclusion of higher-order gravity field effects (e.g., using a 140x140 gravity model) 19 and other non-Keplerian perturbations. Numerical algorithms can be applied to match the specific geographic target with a self-intersection point of the RGT orbit.21 Furthermore, multi-objective optimization techniques, such as genetic algorithms, can be employed during the orbit redesign phase to balance competing performance indexes, such as revisiting accuracy and minimizing fuel consumption associated with orbital maneuvering required to correct injection errors.16

### **2.4 State-of-the-Art in Formation Geometry and Transient Maneuvers**

The mission requires a three-satellite, transient triangular formation. This specific configuration is valuable for advanced remote sensing, such as generating three-dimensional configurations, enabling orthogonal baselines for synthetic aperture applications, or supporting tri-stereo imaging.2 A planar triangular formation geometry in the equatorial plane has been studied in academic literature, demonstrating its theoretical stability potential under specific conditions.22

#### **2.4.1 Transient Formation Flying**

The mission requirement for the formation to be *transient*—established quickly over the target and then relaxed—is critical for mission economics and longevity. Formation flying (FF) scenarios involving transient phases, such as formation reconfiguration or rendezvous, mandate fully autonomous Guidance, Navigation, and Control (GNC) functions for execution.12 Research has successfully developed control strategies that optimize fuel consumption during the transients of formation reconfiguration and maintenance.23

The inherent high precision required for the triangle, coupled with its short duration of utility (the 2-15 minute LEO pass), drives this operational choice. Continuous maintenance of a precise formation demands significant propellant usage.11 By utilizing a transient approach, the mission minimizes propellant consumption by ensuring the rigorous geometry is maintained only during the critical observation window over Tehran.

#### **2.4.2 Safety and Stability Constraints**

For distributed missions, designing the orbits to meet passive safety constraints is paramount.24 Passive safety requires that the relative orbits remain bounded and non-colliding for a predetermined duration (e.g., two or more orbits) in the event of an active control failure, providing sufficient time for an autonomous collision avoidance maneuver.24

Furthermore, during the actual science observation phase, stringent attitude stability requirements often prohibit the execution of translational maneuvers (thrusting).24 Consequently, the absolute and relative orbits must be specifically designed such that the lateral relative acceleration (perpendicular to the boresight) is naturally minimized or perfectly counteracted by differential perturbations during the observation period itself.24 This requires meticulous design of the Relative Orbital Elements (ROE) to ensure inherent stability.

### **2.5 Autonomy and Governance for Distributed LEO Missions**

The complexity introduced by transient formation flying and distributed tasking necessitates advanced onboard autonomy and strict adherence to international space data and operations standards.

#### **2.5.1 Onboard Autonomy and Collaboration**

Distributed space systems (DSS) require high levels of autonomy to manage coordination, collaboration, and opportunistic functions.25 Autonomy enables critical Earth observation functions, such as dynamic tasking and rescheduling, where the spacecraft use lookahead sensors to evaluate utility (e.g., avoiding cloud coverage) and optimize the imaging schedule in real-time.25

The implementation of autonomous operations relies heavily on sophisticated Mission Planning and Scheduling (MPS) frameworks that model the problem, utilize optimization techniques, and manage runtime characteristics, including resource and task constraints.25 In a multi-spacecraft architecture, robustness often requires redundancy, such as providing backup planners and mission managers to allow other spacecraft to replace a disabled leader seamlessly.27

#### **2.5.2 International Standards and Research Governance**

The adherence to formal research governance is critical, especially concerning data exchange and space traffic management (STM).

##### **2.5.2.1 Orbit Data Messaging (ODM)**

Standardized communication protocols are required for the exchange of orbital state information between operators and agencies.28 The Consultative Committee for Space Data Systems (CCSDS) Recommended Standard for Orbit Data Messages (ODM) specifies four formats: the Orbit Parameter Message (OPM), the Orbit Mean-Elements Message (OMM), the Orbit Ephemeris Message (OEM), and the Orbit Comprehensive Message (OCM).28 These standards are fundamental for pre-flight planning, tracking, and navigation support.28 The precise formation flying nature of this mission, particularly if utilizing high-bandwidth inter-satellite optical crosslinks 30, requires highly accurate and timely ODM to maintain strict pointing requirements, as optical links are extremely sensitive to jitter and atmospheric distortion.30

##### **2.5.2.2 Data Exchange and Space Traffic Management**

The proliferation of LEO satellite deployments necessitates strict protocols for safety and coordination. ASTM F3514-21 provides standard guidance for space data exchange necessary to support the integration of space operations into Air Traffic Management (ATM) systems.32 This is particularly relevant for mitigating the collision risk associated with large clusters of objects in LEO altitude bands.34 Furthermore, CCSDS provides extensive standards for Space Link Services (SLS), covering physical and data link layers (e.g., RF, modulation, channel coding) to ensure efficient telemetry and telecommand capabilities necessary for high-rate data downlink required by Earth observation missions.35

## **Chapter 3: Theoretical Foundation and Governing Dynamics**

This chapter derives the necessary dynamical models, coordinate systems, and fundamental mathematical constraints required to design the absolute orbit (RGT over Tehran) and analyze the relative motion of the three-satellite transient triangular formation in LEO.

### **3.1 Classical Two-Body Problem and Fundamental Coordinate Systems**

The motion of a single satellite is typically initiated by solving the two-body problem, defining the trajectory under the influence of the primary gravitational body (Earth).

#### **3.1.1 Earth-Centered Inertial (ECI) Frame**

The ECI frame ($\\mathcal{I}$) is an inertial reference frame used for describing the absolute position ($\\mathbf{r}$) and velocity ($\\mathbf{v}$) of the satellite. The unperturbed equations of motion define the Classical Orbital Elements (COE) that describe the Keplerian ellipse.37

#### **3.1.2 The Local Vertical/Local Horizontal (LVLH) or Radial-Tangential-Normal (RTN) Frame**

For analyzing satellite formation flying, the relative motion is conventionally described in a non-inertial frame centered on the chief or reference spacecraft ($\\text{Sat}\_R$). The Radial-Tangential-Normal (RTN) frame ($\\mathcal{R}$) is chosen, defined by the following axes:

1. **Radial (R):** Points along the position vector $\\mathbf{r}$ of the reference satellite, away from the Earth center.  
2. **Tangential (T):** Points along the velocity vector $\\mathbf{v}$ (or perpendicular to $\\mathbf{r}$ in the orbit plane).  
3. **Normal (N):** Completes the right-handed system, perpendicular to the orbit plane.

The relative motion ($\\Delta \\mathbf{r}$) is expressed in this frame as $\\Delta \\mathbf{r}|\_{\\text{RTN}} \\equiv (\\Delta R, \\Delta T, \\Delta N)^T$.38 This localized frame is essential for relating the mathematical dynamics of the relative motion to the physical geometry of the triangular formation.

### **3.2 Modeling Absolute Orbit Dynamics: The $J\_2$ Perturbation and RGT Constraint**

In LEO, the long-term maintenance of the ground track requires accounting for the dominant gravitational perturbation, $J\_2$.

#### **3.2.1 Secular Effects of the $J\_2$ Perturbation**

The Earth’s oblateness induces secular (long-term, linear) drifts in the Right Ascension of the Ascending Node ($\\Omega$) and the Argument of Perigee ($\\omega$). The secular rate of change of the node, $\\dot{\\Omega}\_{J\_2}$, must be precisely accounted for when designing a stable RGT orbit.

#### **3.2.2 RGT Constraint Derivation**

The RGT constraint ensures that the ground track repeats exactly after $j$ orbits and $k$ sidereal days. This is achieved by balancing the nodal precession caused by $J\_2$ with the rotation of the Earth beneath the orbit. The fundamental RGT equation is expressed as a required relationship between the change in longitude ($\\Delta L$) over $j$ orbits and the Earth's sidereal rotation ($\\omega\_E$) over $k$ days 16:

$$j \\cdot \\left| \\Delta L\_1 \+ \\Delta L\_2 \\right| \= k \\cdot 2\\pi$$  
Where $\\Delta L\_1$ represents the angular rotation of the Earth during one orbital period of the satellite, and $\\Delta L\_2$ represents the change in $\\Omega$ (nodal precession) due to the $J\_2$ effect during one orbit.18 This constraint establishes a tight interdependence between the semi-major axis ($a$) and the inclination ($i$).

Given that Tehran is located at approximately 35.7° N latitude, the inclination ($i$) must be greater than this value to ensure coverage. This requirement restricts the acceptable range of $i$. The resulting RGT relationship then dictates the precise semi-major axis $a$ required for the orbital period to synchronize the nodal precession with Earth rotation. Since the ground track drift is a highly sensitive function of $a$ and $i$, and $J\_2$ effects are pronounced in LEO, the initial analytically derived $(a, i)$ pair must be validated using high-fidelity numerical propagation incorporating full gravity models (up to 140x140) and differential corrections to achieve the required mission accuracy.19

Table 3.2 illustrates the key parameters constrained by the RGT design targeting Tehran:

Table 3.2 Key Input Parameters for Repeat Ground Track (RGT) Design Targeting Tehran

| Parameter | Symbol | Required Calculation/Derivation | Influence on Mission Design |
| :---- | :---- | :---- | :---- |
| Geocentric Latitude of Tehran | $\\varphi\_T$ | Geographical Input (\~35.7° N) | Dictates minimum required inclination ($i \\ge \\varphi\_T$). |
| Nodal Period Ratio (Orbits/Days) | $j/k$ | Optimization Input (e.g., 15/1 or 16/1) | Dictates the overall revisit frequency over the target area. |
| Inclination | $i$ | Function of $j, k$, and $J\_2$ correction 18 | Ensures repeatable tracks (max latitude defines coverage bounds). |
| Mean Semi-Major Axis | $a$ | Solved analytically using the RGT constraint and J2 equations 16 | Defines the precise energy level required to synchronize nodal drift with Earth rotation. |

### **3.3 Relative Motion Dynamics: Linearized Models**

To control and maintain the transient triangular formation, the relative motion must be modeled accurately.

#### **3.3.1 Limitations of Hill-Clohessy-Wiltshire (C-W) Equations**

The classical Hill-Clohessy-Wiltshire (C-W) equations provide the simplest linear model for relative motion, derived by linearizing the equations around a circular reference orbit.39 While useful for initial approximations, the C-W formulation is known to be inadequate for missions involving eccentric orbits or significant perturbations.39 Given that RGT orbits often possess slight eccentricity and operate in the heavily perturbed LEO environment, a more sophisticated model is essential.

#### **3.3.2 Relative Orbital Elements (ROE) Formulation**

The Relative Orbital Elements (ROE) approach is mandatory for formation design due to its capacity to provide intuitive geometric control insights and superior handling of perturbations.20 ROE defines the relative motion ($\\Delta \\mathbf{x}$) not in the Cartesian RTN coordinates, but as the difference in the Classical Orbital Elements (COE) between the deputy satellite ($\\mathbf{EO}$) and the chief reference satellite ($\\mathbf{EO}\_r$): $\\Delta \\mathbf{EO} \= \\mathbf{EO} \- \\mathbf{EO}\_r$.38

The linearized analytical solution for relative motion in non-circular orbits includes complex terms:

1. **Elliptical terms:** These are proportional to the eccentricity of the reference orbit.  
2. **Double Orbital Frequency terms:** These terms demonstrate that the relative motion trajectory is no longer a simple ellipse, even under linearized, non-perturbed dynamics.38

The primary advantage of ROE is its ability to define the desired geometric formation (the triangle) directly in terms of constant orbital element differences (e.g., $\\Delta a, \\Delta i, \\Delta \\Omega$). The goal of the Guidance, Navigation, and Control (GNC) system then reduces to stabilizing and maintaining these constant ROE differences against external disturbances, directly translating geometric constraints into control objectives.20

### **3.4 Modeling Perturbed Relative Motion in LEO**

The primary challenge in long-duration formation maintenance in LEO is managing the differential effects of non-Keplerian forces.

#### **3.4.1 Differential $J\_2$ Effects**

The differential gravitational force, primarily due to the Earth's oblateness ($J\_2$), is the dominant source of drift in LEO formations, significantly exceeding other perturbations like atmospheric drag at typical altitudes (around 800 km).13 The differential $J\_2$ effect causes the relative orbital elements to drift secularly, leading to the rapid decay or expansion of the formation geometry if left uncorrected. Modeling this effect is vital to determine the required $\\Delta V$ budget for station-keeping.

#### **3.4.2 Differential Aerodynamic Drag and Control Strategy**

Atmospheric drag, although less dominant than $J\_2$ for secular drift above 600 km, is a critical factor and, paradoxically, a primary mechanism for low-authority control. Differential aerodynamic drag arises because small differences in satellite ballistic coefficients or atmospheric density result in varying drag forces across the cluster.41

For formation keeping, differential aerodynamic force (specifically drag and potentially lift through specialized attitude control) can be intentionally utilized to counteract the differential drift caused by the $J\_2$ perturbation.13 This strategy is exceptionally attractive because it is propellant-free for the continuous, fine adjustment required during formation maintenance.42 Such a strategy, however, is limited exclusively to LEO environments.41 The implementation requires a robust, potentially nonlinear, Lyapunov-based feedback control law designed specifically to use the differential aerodynamic acceleration to keep the formation bounded.41

This dynamic environment necessitates a hybrid control architecture. Chemical propulsion is necessary for the high-authority, transient maneuvers required to establish the precise triangle rapidly before the observation pass begins. In contrast, during the observation phase, continuous, minute corrections must rely on low-authority, propellant-saving techniques like differential drag to maximize the mission lifetime.42

### **3.5 Three-Satellite Transient Formation Geometry Definition**

The geometric definition of the triangle must be established relative to the reference satellite ($\\text{Sat}\_R$).

#### **3.5.1 Geometric Relationships and Baselines**

The positions of the two deputy satellites ($\\text{Sat}\_1, \\text{Sat}\_2$) relative to the chief are represented by the relative position vectors $\\mathbf{r}\_{rel, i}$ in the RTN frame 38:

$$\\mathbf{r}\_{rel, i} \= (\\Delta R\_i, \\Delta T\_i, \\Delta N\_i)^T, \\quad i \\in \\{1, 2\\}$$  
The design of the triangular formation requires specific baseline lengths (distances between satellites) and orientations to satisfy the geometric requirements of the distributed sensing payload (e.g., tri-stereo baselines).2

#### **3.5.2 Linking Geometry to Relative Orbital Elements**

The operational precision of the formation dictates that the geometric constraints (desired baselines) must be translated into targeted Relative Orbital Elements (ROE) that ensure the relative motion is stable or bounded around a specific relative trajectory.11 This ROE-based definition allows the separation distances ($\\mathbf{r}\_{rel, i}$) to remain consistent throughout the brief observation window, minimizing the need for active thrusting during observation.

Crucially, the triangular formation must be designed to satisfy passive safety requirements, guaranteeing that the separation remains non-zero for a sufficient period (e.g., $\\ge 2$ orbits) if control authority is lost.24 This mandates that the initial ROE parameters are selected such that the natural differential perturbations do not induce a collision or proximity violation within the emergency avoidance timeframe.

### **3.6 Mission Geometry and Constraint Analysis over Tehran**

The final layer of the theoretical foundation integrates the orbital dynamics with the ground coverage requirements over the specified target, Tehran (approximate Coordinates: Latitude: 35.7° N, Longitude: 51.4° E).

#### **3.6.1 RGT Targeting Methodology for Urban Area**

The derived RGT parameters ($a, i$) must ensure the ground track passes over or within the sensor swath width of the target. Ground corridor width is determined by the satellite’s altitude, the sensor field of view, and the minimum acceptable elevation angle ($\\theta\_{\\text{min}}$) for data acquisition.43 Specialized orbit prediction tools are utilized to compute simulated overpasses based on the target’s latitude and longitude and the planned satellite swath.43

#### **3.6.2 Visibility and Transient GNC Requirements**

The short duration of the visibility window is the most critical driver for the mission’s GNC requirement. LEO passes typically range from 2 to 15 minutes, depending on altitude and the licensed elevation angle (e.g., 25° or 40°).10 This duration is calculated using orbital mechanics procedures that account for the satellite’s velocity relative to the rotating ground target.45

If the optimal observation window, during which the triangular formation must be stable and thrust-free, is 8 minutes 24, and the total visibility window is, for instance, 10 minutes, the GNC system is only allocated 2 minutes for the *transient maneuver*—moving the satellites from their passively safe, dispersed configuration into the precise, meter-level triangular geometry. This requirement imposes a high demand on the GNC system for rapid, high-authority maneuvers preceding the observation phase, demanding significantly larger $\\Delta V$ compared to the continuous, low-authority corrections used for maintenance during the stable observation period.11

Table 3.3 summarizes the applicability of the fundamental relative motion models to this complex LEO mission.

Table 3.3 Fundamental Relative Motion Models and Applicability

| Model | Reference Orbit Assumption | Primary Output | Applicability to Thesis |
| :---- | :---- | :---- | :---- |
| Hill-Clohessy-Wiltshire (C-W) | Circular, Unperturbed | Relative Position/Velocity (Cartesian) | Insufficient baseline model; fails to account for eccentricity and differential perturbations inherent to LEO RGT operations.39 |
| Relative Orbital Elements (ROE) | Circular/Eccentric, Perturbed | Differences in Classical Orbital Elements ($\\delta a, \\delta i$, etc.) | Essential for defining and controlling the geometric constraints of the triangular formation and simplifying mission planning.20 |
| Perturbed Linearized Equations | Eccentric, $J\_2$/Drag Effects Included | Boundedness analysis, Secular drift rates, Control authority requirements | Necessary for developing the high-fidelity GNC architecture utilizing differential aerodynamic control for fuel-efficient station-keeping.39 |

## **Conclusions**

The literature review and theoretical foundation confirm that the proposed mission—a three-satellite LEO constellation executing a repeatable, transient triangular formation over Tehran—represents a frontier problem in astrodynamics. The mission design is fundamentally defined by three coupled constraints:

1. **RGT Constraint:** Requires precise synchronization of the absolute orbit ($a, i$) against the dominant $J\_2$ perturbation to ensure repeatable coverage over Tehran.  
2. **LEO Velocity/Pass Duration Constraint:** Imposes a strict time limit (2-15 minutes) for high-precision operations, demanding a *transient* formation management strategy.  
3. **Formation Control Constraint:** Necessitates the use of the Relative Orbital Elements (ROE) framework to define the geometric triangle and requires a hybrid GNC approach, balancing high-authority transient chemical maneuvers with continuous, low-authority differential aerodynamic control for efficiency and longevity.

Future chapters must proceed sequentially, first determining the definitive RGT orbital elements ($a, i$) using iterative numerical methods based on the $J\_2$ constraint. Subsequently, these fixed absolute parameters will be used to derive the specific perturbed relative motion equations, enabling the design of the passively safe ROE geometry and the calculation of the required $\\Delta V$ budgets for the rapid transient reconfiguration maneuvers. The entire operational framework must adhere rigorously to governance standards, specifically CCSDS Orbit Data Messages, to ensure data integrity and interoperability for high-precision autonomous navigation.

#### **Works cited**

1. Spacecraft Formation Flying \- Dr. Hanspeter Schaub, accessed October 23, 2025, [https://hanspeterschaub.info/research-ff.html](https://hanspeterschaub.info/research-ff.html)  
2. Formation Flying \- NASA, accessed October 23, 2025, [https://www.nasa.gov/ames-engineering/spaceflight-division/flight-dynamics/formation-flying/](https://www.nasa.gov/ames-engineering/spaceflight-division/flight-dynamics/formation-flying/)  
3. Introduction to Small Satellite Constellation \- UNOOSA, accessed October 23, 2025, [https://www.unoosa.org/documents/pdf/Access2Space4All/KiboCUBE/KiboCUBEAcademy/2025/KiboCUBE\_Academy\_2025\_OPL27.pdf](https://www.unoosa.org/documents/pdf/Access2Space4All/KiboCUBE/KiboCUBEAcademy/2025/KiboCUBE_Academy_2025_OPL27.pdf)  
4. ANTS for the Human Exploration and Development of Space, accessed October 23, 2025, [https://science.gsfc.nasa.gov/attic/ants/documents.d/ieeeac03%20paper1248.pdf](https://science.gsfc.nasa.gov/attic/ants/documents.d/ieeeac03%20paper1248.pdf)  
5. Survey on Guidance Navigation and Control Requirements for Spacecraft Formation-Flying Missions \- AIAA ARC, accessed October 23, 2025, [https://arc.aiaa.org/doi/pdf/10.2514/1.G002868](https://arc.aiaa.org/doi/pdf/10.2514/1.G002868)  
6. Low Earth orbit \- Wikipedia, accessed October 23, 2025, [https://en.wikipedia.org/wiki/Low\_Earth\_orbit](https://en.wikipedia.org/wiki/Low_Earth_orbit)  
7. Remote Sensing | NASA Earthdata, accessed October 23, 2025, [https://www.earthdata.nasa.gov/learn/earth-observation-data-basics/remote-sensing](https://www.earthdata.nasa.gov/learn/earth-observation-data-basics/remote-sensing)  
8. Low Earth Orbit \- Explained \- NSTXL, accessed October 23, 2025, [https://nstxl.org/low-earth-orbit-explained/](https://nstxl.org/low-earth-orbit-explained/)  
9. LEO, MEO or GEO? Diversifying orbits is not a one-size-fits-all mission (Part 2 of 3), accessed October 23, 2025, [https://www.ssc.spaceforce.mil/Newsroom/Article-Display/Article/3465697/leo-meo-or-geo-diversifying-orbits-is-not-a-one-size-fits-all-mission-part-2-of](https://www.ssc.spaceforce.mil/Newsroom/Article-Display/Article/3465697/leo-meo-or-geo-diversifying-orbits-is-not-a-one-size-fits-all-mission-part-2-of)  
10. LEO Satellite Performance Comparison under Two Different Elevations, accessed October 23, 2025, [https://www.scirp.org/journal/paperinformation?paperid=138890](https://www.scirp.org/journal/paperinformation?paperid=138890)  
11. (PDF) The Dynamics of Formation Flight About a Stable Trajectory \- ResearchGate, accessed October 23, 2025, [https://www.researchgate.net/publication/228874688\_The\_Dynamics\_of\_Formation\_Flight\_About\_a\_Stable\_Trajectory](https://www.researchgate.net/publication/228874688_The_Dynamics_of_Formation_Flight_About_a_Stable_Trajectory)  
12. Autonomous Formation Flying in Low Earth Orbit \- electronic library \-, accessed October 23, 2025, [https://elib.dlr.de/63481/1/Damico\_PhD\_01022010.pdf](https://elib.dlr.de/63481/1/Damico_PhD_01022010.pdf)  
13. J2 DYNAMICS AND FORMATION FLIGHT, accessed October 23, 2025, [https://www.cds.caltech.edu/\~marsden/bib/2001/15-KoMaMaMu2001/KoMaMaMu2001.pdf](https://www.cds.caltech.edu/~marsden/bib/2001/15-KoMaMaMu2001/KoMaMaMu2001.pdf)  
14. LEO vs MEO vs GEO Satellites \- Symmetry Electronics, accessed October 23, 2025, [https://www.symmetryelectronics.com/blog/leo-vs-meo-vs-geo-satellites/](https://www.symmetryelectronics.com/blog/leo-vs-meo-vs-geo-satellites/)  
15. ESA \- Types of orbits \- European Space Agency, accessed October 23, 2025, [https://www.esa.int/Enabling\_Support/Space\_Transportation/Types\_of\_orbits](https://www.esa.int/Enabling_Support/Space_Transportation/Types_of_orbits)  
16. Multi-objective Optimization Method For Repeat Ground-track Orbit Design Considering the Orbit Injection Error \- SciELO, accessed October 23, 2025, [https://www.scielo.br/j/jatm/a/VYWKKzcWkCfq6zTp6RY9jsM/?format=pdf\&lang=en](https://www.scielo.br/j/jatm/a/VYWKKzcWkCfq6zTp6RY9jsM/?format=pdf&lang=en)  
17. Repeat-pass interferometry \- STEP Forum, accessed October 23, 2025, [https://forum.step.esa.int/t/repeat-pass-interferometry/3605](https://forum.step.esa.int/t/repeat-pass-interferometry/3605)  
18. Spacecraft Dynamics and Control \- Lecture 13: The Effect of a Non-Spherical Earth \- Matthew M. Peet \- Arizona State University, accessed October 23, 2025, [https://control.asu.edu/Classes/MAE462/462Lecture13.pdf](https://control.asu.edu/Classes/MAE462/462Lecture13.pdf)  
19. Fast Design of Repeat Ground Track Orbits in High-Fidelity Geopotentials \- Georgia Institute of Technology, accessed October 23, 2025, [https://repository.gatech.edu/bitstreams/e1c32efc-a064-4387-9ba4-03da318be945/download](https://repository.gatech.edu/bitstreams/e1c32efc-a064-4387-9ba4-03da318be945/download)  
20. Analysis of Formation Flying in Eccentric Orbits Using Linearized Equations of Relative Motion, accessed October 23, 2025, [https://ntrs.nasa.gov/api/citations/20060048540/downloads/20060048540.pdf](https://ntrs.nasa.gov/api/citations/20060048540/downloads/20060048540.pdf)  
21. Closed-form solution of repeat ground track orbit design and constellation deployment strategy \- ResearchGate, accessed October 23, 2025, [https://www.researchgate.net/publication/348039781\_Closed-form\_solution\_of\_repeat\_ground\_track\_orbit\_design\_and\_constellation\_deployment\_strategy](https://www.researchgate.net/publication/348039781_Closed-form_solution_of_repeat_ground_track_orbit_design_and_constellation_deployment_strategy)  
22. Electrostatic Forces for Satellite Swarm Navigation and Reconfiguration \- European Space Agency, accessed October 23, 2025, [https://www.esa.int/gsp/ACT/doc/ARI/ARI%20Study%20Report/ACT-RPT-MAD-ARI-05-4107b-Electrostatic-Surrey.pdf](https://www.esa.int/gsp/ACT/doc/ARI/ARI%20Study%20Report/ACT-RPT-MAD-ARI-05-4107b-Electrostatic-Surrey.pdf)  
23. Spacecraft formation flying: A review and new results on state feedback control, accessed October 23, 2025, [https://www.researchgate.net/publication/223299653\_Spacecraft\_formation\_flying\_A\_review\_and\_new\_results\_on\_state\_feedback\_control](https://www.researchgate.net/publication/223299653_Spacecraft_formation_flying_A_review_and_new_results_on_state_feedback_control)  
24. Formation Flying Orbit and Control Concept for the VISORS Mission \- Stanford University, accessed October 23, 2025, [https://slab.sites.stanford.edu/sites/g/files/sbiybj25201/files/media/file/scitech\_visors\_2021\_final.pdf](https://slab.sites.stanford.edu/sites/g/files/sbiybj25201/files/media/file/scitech_visors_2021_final.pdf)  
25. Applying Autonomy to Distributed Satellite Systems: trends, challenges and future prospects \- UPCommons, accessed October 23, 2025, [https://upcommons.upc.edu/bitstreams/5a2a4278-f253-45af-b8c6-4f87343b7d74/download](https://upcommons.upc.edu/bitstreams/5a2a4278-f253-45af-b8c6-4f87343b7d74/download)  
26. Vision-Based Dynamic Tasking for Earth-Observing Satellite Constellations \- DigitalCommons@USU, accessed October 23, 2025, [https://digitalcommons.usu.edu/smallsat/2025/all2025/27/](https://digitalcommons.usu.edu/smallsat/2025/all2025/27/)  
27. AUTONOMY ARCHITECTURES FOR A CONSTELLATION OF SPACECRAFT Anthony Barrett Jet Propulsion Laboratory, California Institute of Tech, accessed October 23, 2025, [https://ntrs.nasa.gov/api/citations/20000056916/downloads/20000056916.pdf](https://ntrs.nasa.gov/api/citations/20000056916/downloads/20000056916.pdf)  
28. Orbit Data Messages \- CCSDS.org, accessed October 23, 2025, [https://ccsds.org/Pubs/502x0b3e1.pdf](https://ccsds.org/Pubs/502x0b3e1.pdf)  
29. orbit data messages | nasa, accessed October 23, 2025, [https://www.nasa.gov/wp-content/uploads/2017/12/orbit\_data\_messages.pdf](https://www.nasa.gov/wp-content/uploads/2017/12/orbit_data_messages.pdf)  
30. Probabilistic Link Budget Analysis for Low Earth Orbit Satellites in the Optical Regime \- arXiv, accessed October 23, 2025, [https://arxiv.org/html/2507.20908v1](https://arxiv.org/html/2507.20908v1)  
31. Study of LEO-SAT microwave link for broad-band mobile satellite communication system, accessed October 23, 2025, [https://ntrs.nasa.gov/citations/19940018296](https://ntrs.nasa.gov/citations/19940018296)  
32. Standards & Publications \- Products & Services \- ASTM, accessed October 23, 2025, [https://www.astm.org/products-services/standards-and-publications/standards/bos-standards.html?volume=15.09\&year=2024\&month=june](https://www.astm.org/products-services/standards-and-publications/standards/bos-standards.html?volume=15.09&year=2024&month=june)  
33. COMSTAC Safety Working Group Report \- Federal Aviation Administration, accessed October 23, 2025, [https://www.faa.gov/media/31151](https://www.faa.gov/media/31151)  
34. Examining Short-term Space Safety Effects from LEO Constellations and Clusters, accessed October 23, 2025, [https://www.hou.usra.edu/meetings/orbitaldebris2019/orbital2019paper/pdf/6010.pdf](https://www.hou.usra.edu/meetings/orbitaldebris2019/orbital2019paper/pdf/6010.pdf)  
35. Space Link Services Area \- CCSDS.org, accessed October 23, 2025, [https://ccsds.org/publications/sls/](https://ccsds.org/publications/sls/)  
36. All Active Publications \- CCSDS.org, accessed October 23, 2025, [https://ccsds.org/publications/allpubs/](https://ccsds.org/publications/allpubs/)  
37. Orbital elements \- Wikipedia, accessed October 23, 2025, [https://en.wikipedia.org/wiki/Orbital\_elements](https://en.wikipedia.org/wiki/Orbital_elements)  
38. Topology of the relative motion: circular and eccentric reference orbit cases, accessed October 23, 2025, [https://ntrs.nasa.gov/api/citations/20080012640/downloads/20080012640.pdf](https://ntrs.nasa.gov/api/citations/20080012640/downloads/20080012640.pdf)  
39. Relative Spacecraft Motion: A Hamiltonian Approach to Eccentricity Perturbations \- Princeton University, accessed October 23, 2025, [https://www.princeton.edu/\~ekolemen/publications/AAS\_04\_294\_Maui\_Conference.doc.pdf](https://www.princeton.edu/~ekolemen/publications/AAS_04_294_Maui_Conference.doc.pdf)  
40. UNIVERSITY OF SOUTHAMPTON Dynamics of Spacecraft Formation Flight, accessed October 23, 2025, [https://eprints.soton.ac.uk/465627/1/981686.pdf](https://eprints.soton.ac.uk/465627/1/981686.pdf)  
41. Satellite formation keeping using differential lift and drag under J2 perturbation, accessed October 23, 2025, [https://www.researchgate.net/publication/312252561\_Satellite\_formation\_keeping\_using\_differential\_lift\_and\_drag\_under\_J2\_perturbation](https://www.researchgate.net/publication/312252561_Satellite_formation_keeping_using_differential_lift_and_drag_under_J2_perturbation)  
42. (PDF) Modelling natural formations of LEO satellites \- ResearchGate, accessed October 23, 2025, [https://www.researchgate.net/publication/226241444\_Modelling\_natural\_formations\_of\_LEO\_satellites](https://www.researchgate.net/publication/226241444_Modelling_natural_formations_of_LEO_satellites)  
43. SMAP Orbit Overpass Calculator, accessed October 23, 2025, [https://smap.jpl.nasa.gov/files/smap2/orbit\_calculator.pdf](https://smap.jpl.nasa.gov/files/smap2/orbit_calculator.pdf)  
44. EVDC Orbit Prediction Tool \- ESA Earth Online \- European Space Agency, accessed October 23, 2025, [https://earth.esa.int/eogateway/tools/evdc-orbit-prediction-tool](https://earth.esa.int/eogateway/tools/evdc-orbit-prediction-tool)  
45. Elevation Angle Characterization for LEO Satellites: First and Second Order Statistics \- MDPI, accessed October 23, 2025, [https://www.mdpi.com/2076-3417/13/7/4405](https://www.mdpi.com/2076-3417/13/7/4405)  
46. RECOMMENDATION ITU-R SA.1156 \- Methods of calculating low-orbit satellite visibility statistics, accessed October 23, 2025, [https://www.itu.int/dms\_pubrec/itu-r/rec/sa/r-rec-sa.1156-0-199510-w\!\!pdf-e.pdf](https://www.itu.int/dms_pubrec/itu-r/rec/sa/r-rec-sa.1156-0-199510-w!!pdf-e.pdf)