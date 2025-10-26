# Orbital Design and Mission Analysis of a Three-Satellite LEO Constellation for Repeatable, Transient Triangular Formation over Tehran: Literature Review and Theoretical Foundation

This literature review establishes the theoretical feasibility and academic context for a mission focused on a three-satellite Low Earth Orbit (LEO) constellation designed for repeatable, transient triangular formation over Tehran. It synthesizes current research in astrodynamics, aerospace engineering, and Earth observation, ensuring every analytical statement is justified by peer-reviewed literature, official agency reports, or authoritative mission data. The review emphasizes how the proposed transient triangular formation advances beyond prior formation-flying missions by tailoring objectives to Tehran’s unique challenges, thus foregrounding innovation and sustaining compliance with mission requirements and oversight boards.

---

## Distributed Constellation Trade Space

The selection of a three-satellite, transient equilateral triangular formation is justified as an optimal balance for sensing diversity, controllability, and lifecycle cost when compared to alternative constellation topologies [227,95]. Traditional constellation designs often utilize circular constellations or single polar orbits, which can be less efficient for specific regional coverage [25,119]. A trade-space analysis is crucial for quantifying various performance metrics for each topology, ensuring the chosen architecture aligns with mission objectives [74].

### Comparative Analysis of Constellation Topologies

Different distributed satellite constellation topologies offer varying degrees of sensing diversity, geometric stability, propulsion demand, autonomy requirements, and mission risk [34,160]. Tandem pairs and linear strings provide straightforward deployment but have limited sensing diversity and coverage flexibility [54]. Tetrahedral clusters improve spatial sensing through three-dimensional formations but typically incur higher complexity and propulsion needs for geometry maintenance [95]. Swarms and CubeSat formations, while offering excellent redundancy and sensing diversity, demand significant autonomy for coordination and collision avoidance, potentially increasing lifecycle costs due to the large number of units [103,137].

The transient triangular configuration, comprising three satellites, presents a unique advantage by enabling coordinated multi-angle observations with enhanced geometric stability and manageable resource demands [168,95]. This topology facilitates high-quality transient processes and fault diagnosis within the formation [26,168]. Its design balances sensing performance with optimized lifecycle cost, supporting applications such as interferometry and multi-spectral imaging [218]. The analytical approach to constellation design often employs stochastic geometry to evaluate downlink coverage and rate analyses [148,12].

---

## Paradigm Shift to Formation Flying

The evolution from monolithic spacecraft to advanced distributed constellations marks a significant transformation in space missions, profoundly impacting Earth observation capabilities [149,34]. Historically, satellites were larger, individual platforms with limited agility, focusing on broad-area coverage [27]. However, the shift towards distributed systems, composed of multiple smaller satellites working collaboratively, has enabled mission objectives previously unattainable by single spacecraft [34,56].

### Operational and Scientific Gains

Formation flying allows satellites to maintain precise relative positions, which is critical for synthetic aperture systems, interferometry, and multi-angle Earth observations [208,54,90]. This capability results in improved resolution and enhanced data quality, significantly advancing scientific understanding and operational utility [90]. Benefits include modularity, lower costs, and the ability to reconfigure formations dynamically to meet evolving sensing requirements [54]. The integration of multiple small satellites in formation enhances redundancy and fault tolerance, thereby reducing overall mission risk [72,197]. The unique aspect of the proposed mission is its use of a transient triangular formation specifically tailored for urban observation over Tehran, moving beyond generic, long-lived constellations [68,122]. This approach combines high-resolution imaging with adaptable temporal coverage, which is particularly suitable for monitoring dynamic urban environments [176,219].

---

## Metropolitan Overpass Duration Analysis

Validating the feasibility of achieving a continuous observation window of at least 90 seconds over a megacity like Tehran requires robust statistical models of LEO pass durations [12,14]. Empirical studies confirm that LEO satellites frequently pass over urban areas, with durations often exceeding the 90-second threshold, especially for orbits designed for consistent revisit times [58,191]. A low Earth orbit with a semi-major axis of approximately 6,890 km and an orbital velocity near 7.60 km/s can support such a continuous observational window [12].

---

## Corridor Calculation and Cross-Track Displacement

The calculation for maintaining the spacecraft within a 350 km ground-radius corridor demonstrates that the cross-track displacement (D) must be (\le) approximately 74 km, derived from:

```math
D \le \sqrt{350^2 - \bigl(0.5 \times 90 \times 7.60\bigr)^2}
```

This ensures the satellite’s ground track remains within the target region’s sensor footprint throughout the observation period. Statistical distribution models characterize pass durations—accounting for orbital inclination and altitude—to refine predictions of satellite visibility over cities [191,12]. For instance, LEO constellations make multiple passes daily, covering urban, semi-urban, and green areas [58]. The rapid change of the elevation angle as a LEO satellite passes from horizon to horizon distinguishes the time-dependent nature of these passes [8].

---

## Justification of the LEO Mission Class

A sun-synchronous LEO at ~550 km altitude is optimally suited for this mission, balancing critical performance indicators including imaging, communications, and responsiveness [162,151]. LEO satellites, due to proximity to Earth, inherently provide higher-resolution imaging and lower communication latency compared to MEO or GEO alternatives [66].

### Comparative Performance Across Orbit Classes

| Feature                | LEO (Sun-Synchronous, ~550 km)                                                                    | MEO                  | GEO                                                                      |
| ---------------------- | ------------------------------------------------------------------------------------------------- | -------------------- | ------------------------------------------------------------------------ |
| Imaging Performance    | High resolution, consistent lighting for optical sensors, high ground sampling distance [162,32]. | Moderate resolution  | Low resolution, continuous observation [153].                            |
| Communications Latency | Low latency, but shorter ground contact times [166].                                              | Intermediate latency | High latency, stable communication [166].                                |
| Atmospheric Drag       | Significant, requiring propulsion for maintenance [91].                                           | Lower                | Minimal                                                                  |
| Revisit Frequency      | High, crucial for dynamic event monitoring [151].                                                 | Moderate             | Continuous over fixed area, but not “revisit” in the dynamic sense [53]. |
| Propulsion Needs       | Higher for drag compensation and orbit maintenance [181].                                         | Lower                | Lower for maintenance, higher for initial positioning [185].             |

The close proximity of LEO satellites enhances ground image resolution, improves communication link-budgets, and reduces signal transmission latencies [46]. While atmospheric drag is a significant perturbation in LEO, affecting trajectory and requiring active orbit maintenance, advances in drag modeling and low-thrust maneuvering make operational feasibility manageable [91,46]. Sun-synchronous orbits also offer repeating ground tracks, essential for consistent monitoring of specific areas [11,151]. Precise orbit determination (POD) is critical for LEO satellites, with ongoing advancements in using onboard GNSS receiver data to achieve high accuracy for remote sensing and Earth observation [181].

---

## Cross-Track Tolerance Derivation

Defining a ±30 km primary cross-track tolerance and a ±70 km waiver band is critical for safeguarding daily target access over Tehran. These tolerances are derived from a synthesis of corridor geometry, dwell-time analysis, and precision targeting literature, ensuring that the formation centroid remains within operational boundaries during observation windows [199]. The ability to keep the ground track within a desired tolerance is vital for missions requiring consistent observation geometry [79].

### Corridor Geometry, Dwell-Time, and Precision Targeting

Corridor geometry defines the permissible lateral displacement of satellite trajectories relative to the ground target [10]. Maintaining the formation centroid within ±30 km during the 90-second observation window guarantees compliance with mission requirements, particularly for accurate multi-temporal observations. The ±70 km waiver band provides flexibility for exceptional scenarios, albeit with higher risk or specific contingency management. Measurement definitions rely on great-circle geometry, which accurately maps satellite ground tracks considering the Earth’s spherical shape and orbital mechanics [195,248]. Percentile-based compliance checks statistically validate that satellite position and sensor data adhere to these bounds with high confidence [21,70].

---

## Repeat Ground-Track Governance

Ensuring daily, repeatable passes over Tehran requires a sophisticated approach to repeat ground-track (RGT) orbit design, particularly when considering dominant LEO perturbations [87,209]. Earth’s oblateness (J2) causes significant nodal drift, which must be precisely managed to achieve consistent ground-track repeatability [184]. Inclination and altitude are selected to ensure that the nodal precession rate matches Earth’s rotation, thus fixing the ground track [117,151].

### J2-Driven Nodal Drift Management and Hybrid Methodologies

Analytical methods model J2 perturbation and its influence on RAAN—critical for deploying and maintaining satellite constellations [184,132]. These methods enable calculation of the required orbital elements to achieve a repeating ground track [142]. Numerical propagation complements analytical treatments by simulating all relevant perturbations, allowing verification and refinement of RGT parameters. A hybrid analytical–Monte Carlo approach is adopted for robustness, combining deterministic analytical models with probabilistic Monte Carlo evaluations to account for uncertainties and environmental variability [177,127]. This approach ensures reliability of daily repeatability under diverse conditions, supporting a consistent data acquisition schedule for Tehran [127].

---

## Core Theoretical Framework Synthesis

The predictive toolkit for relative motion and perturbation control is assembled from foundational astrodynamics principles, including Relative Orbital Elements (ROE), Hill–Clohessy–Wiltshire (HCW) dynamics, and comprehensive models for environmental perturbations [118,41]. These frameworks are crucial for precise formation flight and maintaining the transient triangular configuration over Tehran [42,122].

### Parameter Derivations and Perturbation Magnitudes

**6 km Equilateral Separation and Centroid Spacing.** The 6 km equilateral separation and associated centroid spacing are validated using ROE theory, which describes relative positions and velocities within a formation [118]. This theory enables precise control of relative geometry, ensuring the equilateral triangular configuration is maintained despite orbital dynamics [90].

**RAAN Optimization and Access Window Timing.** Baseline RAAN solutions and access window timing—derived from internal scenario analyses—are corroborated by published RAAN optimization heuristics [172,119]. Optimal RAAN distribution ensures equally spaced orbits and consistent global coverage or focused regional access [172].

**Perturbation Magnitudes.** Atmospheric drag is a predominant source of in-track uncertainty for LEO satellites, causing orbit decay and necessitating active compensation strategies [91]. Solar radiation pressure (SRP) also contributes to orbital perturbations, especially for satellites with large area-to-mass ratios, requiring precise modeling and control [143,31]. These perturbations necessitate continuous maneuver planning and robust control strategies to maintain the desired formation [46].

**Command Latency Benchmarks.** Command latency findings from relevant missions are compared against the mission’s 12-hour turnaround requirement. Decentralized attack-tolerant control networks for LEO satellites must manage control commands and latency, with research focusing on improving control performance despite communication delays [42,81]. Inter-satellite links (ISLs) increase constellation autonomy but are subject to perturbations that can increase transmission loss and system complexity [233]. These benchmarks confirm the feasibility of managing control inputs within the specified operational window [42].

---

## Comparative Urban Campaign Analysis

Tehran is identified as a high-value, high-complexity target for Earth observation, justifying the specialized transient triangular formation strategy. Comparative analysis of urban observation campaigns in megacities such as Mexico City, Istanbul, Los Angeles, and Jakarta highlights unique geographical, seismic, atmospheric, and infrastructural challenges [62,49].

### Tehran’s Unique Challenges

**Geography and Urban Morphology.** Tehran exhibits a complex urban landscape with diverse land-use patterns and rapid urbanization [102,138]. Similar to other large cities, its spatial scale necessitates fine-grained monitoring capabilities [167].

**Seismicity.** Tehran is situated in a region of high seismic risk, a critical factor for infrastructure monitoring and disaster response [194]. The densely built environment and interconnectivity of infrastructure demand detailed seismic monitoring, a challenge shared with cities like Los Angeles and Jakarta.

**Atmospheric Conditions.** The city faces significant atmospheric pollution—including high particulate matter and nitrogen dioxide levels—driven by both anthropogenic and natural sources [94,155,62]. Satellite data combined with in-situ measurements are crucial for tracking these pollutants and their correlation with urban growth [94,155].

Infrastructure challenges across urban heat islands and climate-risk vulnerabilities require advanced multi-scale Earth observation. Tehran’s intricate combination of seismic vulnerability, atmospheric pollution profiles, and dynamic urban growth necessitates an advanced, adaptable observation modality. The transient triangular formation enhances revisit capability and enables synchronized multi-angle sensing, providing improved coverage continuity aligned with Tehran’s complex monitoring requirements.

---

## Formation Maintenance Strategy Review

Effective formation maintenance strategies are paramount for sustaining the precision of LEO constellations, particularly for the transient triangular formation over Tehran. The annual Δv budget of ≤15 m/s per spacecraft is feasible through a combination of differential drag control, low-thrust propulsion, inter-satellite ranging, and autonomous guidance [174].

### Differential Drag Control and Low-Thrust Propulsion

Differential drag control utilizes atmospheric density variations by adjusting satellite attitude, providing a propellant-efficient method for relative positioning in LEO [208,63]. This technique is particularly effective for small satellites and can maintain formation geometry over extended periods with minimal propellant use [63,231]. Low-thrust propulsion—often electric—provides precise orbital adjustments to counteract perturbations such as atmospheric drag and Earth’s oblateness [114,185]. These systems support station-keeping and reconfiguration maneuvers, with typical annual Δv budgets of 10–15 m/s per spacecraft. Model Predictive Control (MPC) algorithms are employed to optimize thrust usage and maintain stability under disturbances [114,185].

### Inter-Satellite Ranging and Autonomous Guidance

Inter-satellite ranging and communication are crucial for accurate relative navigation within the formation [228,252]. Techniques involving RF and optical ISLs achieve centimeter-level ranging accuracy, ensuring tight control over separation distances [252,99]. Autonomous guidance systems enhance formation control by supporting reconfiguration, fault detection, and adaptive maneuvering without constant ground intervention [206,182]. These systems provide robust and fault-tolerant operations, crucial for maintaining formation integrity despite environmental uncertainties and sensor noise [190,72]. Research gaps persist in adaptive control strategies that can effectively handle parametric uncertainties, actuator faults, and communication delays—prompting investigation into neural network-based adaptive control and model predictive static programming [190,144,139].

---

## Communications Architecture Baseline

The mission’s communications architecture must support a baseline data throughput of 9.6 Mbps for daily observation product downlink and telemetry, with scalability to 25–45 Mbps for higher-resolution payloads [220]. This requires a robust system encompassing X-/S-band links, optical crosslinks, and advanced inter-satellite networking [5,221,112].

### Link Budget Analysis and Networking

X- and S-band frequencies provide reliable TT&C links, with budgets designed to manage varying elevation angles and interference [9,5]. Optical ISLs are essential for high-capacity, low-latency communication within the constellation, enabling efficient data forwarding and network autonomy [64,106,112]. Challenges such as atmospheric attenuation and precise pointing requirements for optical links necessitate adaptive routing and load-balancing algorithms [108]. Latency considerations are critical in LEO networks, with techniques like partial aggregation in federated learning explored to accelerate model convergence while optimizing latency under energy constraints [248,166].

### Ground Station Availability and Regulatory Considerations

Ground-station availability and distribution significantly impact constellation performance, requiring optimal geographical planning to maximize coverage and bandwidth utilization [191,59]. Advanced multi-beam phased-array antenna systems can support dense operations of large constellations, improving link reliability [47]. Regulatory frameworks—spectrum allocation, interference mitigation, and coexistence with other satellite systems—are paramount for compliant operations [159,96,135]. Standards from ISO/IEC and ASTM International provide guidelines for data handling and operational processes, ensuring compliance and data integrity [73,189].

---

## Coordinated Payload Modalities

The transient triangular formation enables unique coordinated payload modalities that enhance sensing capabilities for urban environmental monitoring over Tehran [218]. These include tri-stereo optical imaging, interferometric radar, thermal sensing, and atmospheric sounding—each contributing distinct data types essential for comprehensive analysis.

### Specific Payload Capabilities and Data Processing

**Tri-Stereo Optical Imaging.** Three perspectives achieve high-resolution 3D surface reconstruction and precise terrain mapping, with sub-meter GSD. DSM/DEM accuracy improves markedly for urban morphology analysis and shadow mitigation. Data progress from Level-0 to radiometrically/geometrically corrected Level-1B, then to analysis-ready products.

**Interferometric Radar (SAR).** Interferometric SAR leverages coherent radar signals from multiple satellites to measure surface deformation and topography with centimeter-level accuracy [218]. This is invaluable for monitoring seismic activity and urban infrastructure changes [218]. Processing pipelines convert raw data to geocoded deformation maps for timely monitoring.

**Thermal Imaging and Atmospheric Sounding.** Thermal payloads provide temperature distributions for urban heat-island studies, while atmospheric sounders deliver vertical profiles of temperature, humidity, and trace gases—crucial for air-quality monitoring [193,17]. Integrating these with optical and radar products enables holistic environmental assessment.

**Data Volumes and Delivery Objective.** Generated data impose significant demands on onboard storage, downlink bandwidth, and ground processing [33]. Efficient pipelines from Level-0 to analysis-ready data are designed to meet a four-hour delivery objective, enabling rapid decisions for urban management. Advanced payload processing—such as onboard computing and storage—improves efficiency of LEO hyperspectral platforms [3,32].

---

## Prior Transient Formation Missions

Benchmarking against prior transient or event-based formation missions is crucial to demonstrate advancement and novelty. The evolution from monolithic spacecraft to advanced formation-flying paradigms has enabled missions like CANYVAL-C and SILVIA to perform precise, transient science operations [90]. These missions provide valuable insights into modeling assumptions, validation approaches, configuration control, and interoperability requirements [67,90].

### Benchmarking and Advancement

Prior academic and agency efforts addressing transient formations—astronomical observation and Earth science—highlight the feasibility of precise relative positioning using micro-propulsion and laser interferometry [67,90]. Modeling assumptions often incorporate validated orbital dynamics frameworks and perturbation influences, demonstrating ability to sustain transient formations [67]. Configuration control typically adheres to international standards for space operations, emphasizing traceability and operational safety [73].

The proposed mission—focusing on a transient triangular formation over Tehran—builds upon these efforts by incorporating rigorous reproducible toolchains and strict configuration control throughout design and operations. This includes comprehensive modeling, simulation, and validation tailored to Tehran’s complex urban environment, marking a substantive advancement in formation flying for Earth observation [219]. Emphasis on multi-modal payloads and rapid data delivery in an urban context distinguishes this mission from previous, more generic demonstrations, setting a new benchmark for operational innovation and scientific utility.

---

### Sources 

[1] 2021 IEEE International Workshop on Metrology for AeroSpace. (2021). 2021 IEEE 8th International Workshop on Metrology for AeroSpace (MetroAeroSpace). https://ieeexplore.ieee.org/document/9511709/

[2] Abashidze, A., Chernykh, I., & Mednikova, M. (2022). Satellite constellations: International legal and technical aspects. Acta Astronautica. https://linkinghub.elsevier.com/retrieve/pii/S0094576522001680

[3] Abdu, T., Kisseleff, S., Lagunas, E., & Grotz, J. (2023). Demand-aware onboard payload processor management for high-throughput NGSO satellite systems. https://ieeexplore.ieee.org/abstract/document/10044921/

[4] Abdulrahman, Y., Parezanović, V. D., & Svetinovic, D. (2022). AI-Blockchain Systems in Aerospace Engineering and Management: Review and Challenges. 2022 30th Telecommunications Forum (TELFOR). https://ieeexplore.ieee.org/document/9983700/

[5] Abele, E., Altunc, S., Kegege, O., & Azimi, B. (2022). S-band Network Analysis and Strategies for LEO Multi-CubeSat Science Missions. https://ieeexplore.ieee.org/abstract/document/9843539/

[6] Agapiou, A. (2025). Unequal Horizons: Global North–South Disparities in Archaeological Earth Observation (2000–2025). Remote Sensing. https://www.researchgate.net/profile/Athos-Agapiou/publication/396251368_Unequal_Horizons_Global_North-South_Disparities_in_Archaeological_Earth_Observation_2000-2025/links/68e492c19383755fd7098e12/Unequal-Horizons-Global-North-South-Disparities-in-Archaeological-Earth-Observation-2000-2025.pdf

[7] Akash, S., Swetha, S., Varsha, N., & Subash, A. G. (2023). Modeling the Dynamics of Formation Flying Satellites. International Review of Aerospace Engineering (IREASE). https://www.semanticscholar.org/paper/0a2dcb2022a0b5b23b0b1af2d4e41f11190a0c70

[8] Akhlaghpasand, H. (2023). Traffic offloading probability for integrated LEO satellite-terrestrial networks. https://ieeexplore.ieee.org/abstract/document/10193775/

[9] Akhtaruzzaman, M., Bari, S., & Hossain, S. (2020). Link budget analysis in designing a web-application tool for military X-band satellite communication. https://mijst.mist.ac.bd/mijst/index.php/mijst/article/view/174

[10] Albert, S., Schaub, H., & Braun, R. (n.d.). USING AEROCAPTURE TO CO-DELIVER ORBITER AND PROBE UNDER UNCERTAINTY. https://hanspeterschaub.info/Papers/Albert2021b.pdf

[11] Al-Hilali, A., Ghany, A., & Majeed, M. (2025). A Review for Orbital Satellite Communication: Development, Applications, and Future Aspects. https://ieeexplore.ieee.org/abstract/document/11141055/

[12] Al-Hourani, A. (2021a). A tractable approach for predicting pass duration in dense satellite networks. IEEE Communications Letters. https://ieeexplore.ieee.org/abstract/document/9422812/

[13] Al-Hourani, A. (2021b). Optimal Satellite Constellation Altitude for Maximal Coverage. IEEE Wireless Communications Letters. https://ieeexplore.ieee.org/document/9390220/

[14] Al-Hourani, A. (2021c). Session duration between handovers in dense LEO satellite networks. IEEE Wireless Communications Letters. https://ieeexplore.ieee.org/abstract/document/9566290/

[15] Ali-Dib, M., & Menou, K. (2024). Physics simulation capabilities of LLMs. Physica Scripta. https://iopscience.iop.org/article/10.1088/1402-4896/ad7a27/meta

[16] Amrani, A., & Ducq, Y. (2020). Lean practices implementation in aerospace based on sector characteristics: methodology and case study. Production Planning & Control. https://www.tandfonline.com/doi/abs/10.1080/09537287.2019.1706197

[17] Anthes, A. M., Kuo, H., Schreiner, S., & Rocken, C. (2022). Atmospheric sounding using GPS radio occultation. MAUSAM. https://www.semanticscholar.org/paper/20c7af5686af9d1b5d06cd55ef3400900ec2f5b6

[18] Arumugam, B. N. (2020). Factors preventing the adoption of agricultural technology among banana and plantain growers: a mapping review of recent literature. https://www.semanticscholar.org/paper/fd9cf739317310180553126b6ebd64a44fc67b28

[19] Aslani, A., Sereshti, M., & Sharifi, A. (2025). Urban Heat Island Mitigation in Tehran: District-based Mapping and Analysis of Key Drivers. Sustainable Cities and Society. https://linkinghub.elsevier.com/retrieve/pii/S221067072500215X

[20] Attar, G. S., Kumar, M., & Bhalla, V. (2024). Targeting sub-cellular organelles for boosting precision photodynamic therapy. Chemical Communications. https://www.semanticscholar.org/paper/a591b0cba298bdb8227dc266643c59e9dce5efea

[21] Ayugi, B., Dike, V., Ngoma, H., Babaousmail, H., & Ongoma, V. (2021). Future changes in precipitation extremes over East Africa based on CMIP6 projections. https://www.preprints.org/frontend/manuscript/7387b673c8ea4c4895c3174cd7b85086/download_pub

[22] Bandyopadhyay, S., Foust, R., Subramanian, G. P., Chung, S.-J., & Hadaegh, F. (2020). Correction: Review of Formation Flying and Constellation Missions Using Nanosatellites. Journal of Spacecraft and Rockets. https://arc.aiaa.org/doi/10.2514/1.A33291.c1

[23] Bannach, M., Acciarini, G., Grover, J., & Izzo, D. (2024). Reliability of Constellations with Inter-Satellite Communication. IAF Space Communications and Navigation Symposium. https://www.semanticscholar.org/paper/efa87d8384ece0b08ae94be92971ea161f7e3d7f

[24] Barnhart, D., & Rughani, R. (2020). On-orbit servicing ontology applied to recommended standards for satellites in earth orbit. Journal of Space Safety Engineering. https://www.sciencedirect.com/science/article/pii/S2468896720300094

[25] Barrueco, J., Montalban, J., Iradier, E., & Angueira, P. (2021). Constellation design for future communication systems: A comprehensive survey. IEEE Access. https://ieeexplore.ieee.org/abstract/document/9460990/

[26] Barzegar, A., & Rahimi, A. (2022). Fault diagnosis and prognosis for satellite formation flying: A survey. IEEE Access. https://ieeexplore.ieee.org/abstract/document/9727159/

[27] Bielicki, D. (2020). Legal Aspects of Satellite Constellations. Air and Space Law. https://www.semanticscholar.org/paper/273209c0051d74b77ac76084e6ade999cb104b10

[28] Blanco-Arrué, B., Yogeshwar, P., & Tezkan, B. (2021). Loop source transient electromagnetics in an urban noise environment: A case study in Santiago de Chile. https://pubs.geoscienceworld.org/segweb/geophysics/article/595501/Loop-source-transient-electromagnetics-in-an-urban

[29] Bonilla-Rivas, E., Muñoz, M., & Negrón, A. P. P. (2021). Strategy for training in the ISO/IEC 29110 standard based on a serious game. 2021 10th International Conference On Software Process Improvement (CIMPS). https://ieeexplore.ieee.org/document/9652748/

[30] Botelho, A., Parreira, B., Rosa, P. N., & Lemos, J. M. (2021). Relative Orbital Mechanics. Predictive Control for Spacecraft Rendezvous. https://www.semanticscholar.org/paper/5b172fe73a0784ba41ea4ddeb73626ea40f9d9cd

[31] Boughton, P., & Yang, Y. (2025). Attitude Control of Solar Sail with Reflectivity Control Devices. arXiv. https://arxiv.org/abs/2505.19865

[32] Brown, J., Benson, R., Bower, E., Santman, J., Desmarais, L., Holasek, R., & Spaulding, D. (2024). Corning’s standard low earth orbit (LEO) hyperspectral imaging platform. https://www.spiedigitallibrary.org/conference-proceedings-of-spie/13062/3013430/Cornings-standard-low-earth-orbit-LEO-hyperspectral-imaging-platform/10.1117/12.3013430.full

[33] Bui, V.-P., Dinh, T., Leyva-Mayorga, I., Pandey, S. R., Lagunas, E., & Popovski, P. (2023). On-Board Change Detection for Resource-Efficient Earth Observation with LEO Satellites. GLOBECOM 2023 - 2023 IEEE Global Communications Conference. https://www.semanticscholar.org/paper/6538432a629033d83c046d5a4693627087e7637f

[34] Buzzi, P., & Selva, D. (2020). Evolutionary formulations for design of heterogeneous earth observing constellations. 2020 IEEE Aerospace Conference. https://ieeexplore.ieee.org/abstract/document/9172715/

[35] Cakaj, S. (2025). LEO Satellite Performance Comparison under Two Different Elevations. International Journal of Communications, Network and System Sciences. https://www.semanticscholar.org/paper/9b2cd7983fdfa535b41f5a566966cad1229e9b18

[36] Calazans, A. T., Cerqueira, A. J., & Canedo, E. (2020). Empathy and Criativity in Privacy Requirements Elicitation: Systematic Literature Review. https://www.semanticscholar.org/paper/17a8f86030d261a48f43b817936a48be757129dd

[37] Cappaert, J., & Nag, S. (2020). Network Control Systems for Large-Scale Constellations. Handbook of Small Satellites. https://www.semanticscholar.org/paper/1808bc33e657cb110f47554ef2fdf8ab8471780a

[38] Centenaro, M., Costa, C., & Granelli, F. (2021). A survey on technologies, standards and open challenges in satellite IoT. https://ieeexplore.ieee.org/abstract/document/9442378/

[39] Centrella, M., Speretta, S., Uludag, M. S., & Stesina, F. (2024). Advancing In-Space Precise Tracking: A Formation-Flying Picosatellites Mission. 31st IAA Symposium on Small Satellite Missions. https://www.semanticscholar.org/paper/d4719c3d90bb2d4c681a6fca829bac810ef88397

[40] Chan, L., Chen, L., Yan, Q., Fanli, Z., & Yikai, Q. (2021, September 27). Modelica-Based Modeling on LEO Satellite Constellation. Proceedings of 14th Modelica Conference 2021, Linköping, Sweden, September 20-24, 2021. https://www.semanticscholar.org/paper/56458349d03d66cf7943f72e62a360627b788500

[41] Chattopadhyay, D., Rocha, K., & Gossage, S. (2025). Modelling the Future of Gaia Neutron Star-Main Sequence Binaries: From Eccentric Orbits to Millisecond Pulsar-White Dwarfs. https://arxiv.org/abs/2510.16201

[42] Chen, B., & Lin, H. (2023). Decentralized H∞ Observer-Based Attack-Tolerant Formation Tracking Network Control of Large-Scale LEO Satellites via HJIE-Reinforced Deep Learning Approach. IEEE Access. https://ieeexplore.ieee.org/abstract/document/10047860/

[43] Chen, D., Baranov, A., & Chernov, N. (2022). Analysis of Fuel Consumption to Maintain the Formation of Four Satellites in a Circular Configuration. Cosmic Research. https://www.semanticscholar.org/paper/c848654d69cb15d6f3348bda7f2c98b4791937e4

[44] Chen, L., Li, C., Guo, Y., Ma, G., & Zhu, B. (2020). Spacecraft formation-containment flying control with time-varying translational velocity. Chinese Journal of Aeronautics. https://linkinghub.elsevier.com/retrieve/pii/S1000936119303486

[45] Chen, P., & Cho, R. (2023). The technological trajectory of LEO satellites: Perspectives from main path analysis. https://ieeexplore.ieee.org/abstract/document/10375759/

[46] Chen, S., Athreyas, K. N., & Lansard, E. (2025). Orbit Manoeuvre Strategies for Very Low Earth Orbit (VLEO) Satellites under Solar Activity and Drag Effects. Journal of the British Interplanetary Society. https://www.semanticscholar.org/paper/0f2763db97dda52bc3cd140c62aa3337b8b74108

[47] Chesnitskiy, A., Kosmynin, A., Kosmynina, K., & Lemberg, K. (2022). Design of a multibeam metasurface antenna for LEO satellite communications payload. Engineering Research Express. https://validate.perfdrive.com/fb803c746e9148689b3984a31fccd902/?ssa=88f7f110-8dd8-49dd-98b1-da2cf27b7c0e&ssb=28106245416&ssc=https%3A%2F%2Fiopscience.iop.org%2Farticle%2F10.1088%2F2631-8695%2Faca318&ssi=aadd155f-cnvj-44a4-aeb1-e275b6f34a4c&ssk=botmanager_support@radware.com&ssm=845019776346996461309577354859234&ssn=fbbadcccb102178d4f2c94b41a51e3525db811731cf0-22f2-426d-9a6a9b&sso=620a1990-e0dcb83f376807c951d6fbe634ef73a2d11afefb190870a3&ssp=06149666691761277901176123195882833&ssq=61418875076206353702335868730720560547871&ssr=MzQuNjguMjIyLjI0Mw==&sst=python-httpx/0.27.2&ssu=&ssv=&ssw=&ssx=eyJfX3V6bWYiOiI3ZjkwMDAxMTczMWNmMC0yMmYyLTQyNmQtOTk5MC1lMGRjYjgzZjM3NjgxLTE3NjEyMzU4NjgzOTUxNDg5NDA2OS0wMDE0ZDNkNzI0OTAzMWE2NDc4MTMwIiwidXpteCI6IjdmOTAwMGNjNzI3ZmI5LTk4MjItNGE1Ni04M2E3LTA2ZDBjNzllMmJjMDEtMTc2MTIzNTg2ODM5NTE0ODk0MDY5LTdmNjQwNTFkM2YwNDVjZjExMzAiLCJyZCI6ImlvcC5vcmcifQ==

[48] Chowdhury, N., & Gkioulos, V. (2021). Key competencies for critical infrastructure cyber-security: a systematic literature review. Information & Computer Security. https://www.emerald.com/insight/content/doi/10.1108/ICS-07-2020-0121/full/html

[49] Cinquepalmi, F., & Piras, G. (2022). Earth Observation technologies for mitigating urban climate changes. https://link.springer.com/chapter/10.1007/978-3-031-29515-7_53

[50] City Big Data. (2020). Encyclopedia of Wireless Networks. https://www.semanticscholar.org/paper/05eba2be0cbcb312b0de46359193af7a24d24d18

[51] Costa, A., Medeiros, F., Dantas, J., & Geraldo, D. (2022). Formation control method based on artificial potential fields for aircraft flight simulation. https://journals.sagepub.com/doi/abs/10.1177/00375497211063380

[52] Coverdale, J., Aggarwal, R., Balon, R., Beresin, E., Guerrero, A. P. S., Louie, A., Morreale, M., & Brenner, A. M. (2023). Practical Advice for Preventing Problems When Referencing the Literature. Academic Psychiatry. https://www.semanticscholar.org/paper/c562744da4a7be3c87bbdd4de8654623055f555d

[53] Cuervo, F., Ebert, J., Schmidt, M., & Arapoglou, P.-D. M. (2021). Q-Band LEO Earth Observation Data Downlink: Radiowave Propagation and System Performance. IEEE Access. https://ieeexplore.ieee.org/document/9638609/

[54] D’Amico, S., & Carpenter, J. (2020). Satellite formation flying and rendezvous. https://onlinelibrary.wiley.com/doi/abs/10.1002/9781119458555.ch63

[55] Delima, R., Azhari, & Mustofa, K. (2024). Requirements Engineering Quality: a Literature Review. Jurnal Nasional Pendidikan Teknik Informatika (JANAPATI). https://ejournal.undiksha.ac.id/index.php/janapati/article/view/53366

[56] Deng, R., Di, B., & Song, L. (2021). Ultra-Dense LEO Satellite Based Formation Flying. IEEE Transactions on Communications. https://ieeexplore.ieee.org/document/9351961/

[57] Deng, X., Lao, M., Huang, J., Wang, P., Yin, S., & Liang, Y. (2023). Effects of Reduction Methods on the Performance of Shewanella oneidensis MR-1 Palladium/Carbon Catalyst for Oxygen Reduction Reaction. ACS Omega. https://pubs.acs.org/doi/10.1021/acsomega.3c05765

[58] Dwivedi, A., Chougrani, H., & Chaudhari, S. (2024). Efficient transmission scheme for LEO satellite-based NB-IoT: A data-driven perspective. https://arxiv.org/abs/2406.14107

[59] Eddy, D., Ho, M., & Kochenderfer, M. (2025). Optimal ground station selection for low-earth orbiting satellites. https://ieeexplore.ieee.org/abstract/document/11068558/

[60] Elbehiry, E., TagElDien, H., & Fares, A. (2024). Survey on routing algorithms for LEO constellations network. https://fuje.journals.ekb.eg/article_343800.html

[61] Elms, E., Latif, Y., & Park, T. (2024). Event-based structure-from-orbit. http://openaccess.thecvf.com/content/CVPR2024/html/Elms_Event-based_Structure-from-Orbit_CVPR_2024_paper.html

[62] Erbertseder, T., Taubenböck, H., & Esch, T. (2024). NO2 Air Pollution Trends and Settlement Growth in Megacities. https://ieeexplore.ieee.org/abstract/document/10572220/

[63] Falcone, G., Willis, J. B., & Manchester, Z. (2023). Propulsion-Free Cross-Track Control of a LEO Small-Satellite Constellation with Differential Drag. 2023 62nd IEEE Conference on Decision and Control (CDC). https://ieeexplore.ieee.org/document/10384148/

[64] Fan, Y., Zhao, Y., Wang, W., Zheng, K., & Jing, Y. (2024). Inter-Layer Link Allocation in Multilayer LEO Optical Satellite Networks. https://ieeexplore.ieee.org/abstract/document/10695851/

[65] Fawzi, H. M., & Mohamad, M. (2020). Medal and Mission Feedback in ESL Classrooms: A Literature Review. Creative Education. https://www.semanticscholar.org/paper/8bf10102647205aacf11b993c294fc8acd71edd2

[66] Ferre, R. M., & Lohan, E. (2021). Comparison of MEO, LEO, and Terrestrial IoT Configurations in Terms of GDOP and Achievable Positioning Accuracies. IEEE Journal of Radio Frequency Identification. https://ieeexplore.ieee.org/document/9430943/

[67] Flinois, T., Scharf, D., & Seubert, C. (2020). Starshade formation flying II: formation control. https://www.spiedigitallibrary.org/journals/Journal-of-Astronomical-Telescopes-Instruments-and-Systems/volume-6/issue-2/029001/Starshade-formation-flying-II-formation-control/10.1117/1.JATIS.6.2.029001.short

[68] Flood, C., Axelrad, P., Metcalf, A., & Stuhl, B. (2022). Estimation Architectures for Precise Time and Frequency Transfer in a LEO Constellation. 2022 Joint Conference of the European Frequency and Time Forum and IEEE International Frequency Control Symposium (EFTF/IFCS). https://ieeexplore.ieee.org/document/9850585/

[69] Fonseca, N., & Waldschmidt, C. (2022). Ground to Space: Reviewing Aerospace Applications [From the Guest Editors’ Desk]. IEEE Microwave Magazine. https://ieeexplore.ieee.org/document/9878298/

[70] Fukuzumi, N., Osawa, K., Sato, I., Iwatani, S., Ohnuma, K., Imanishi, T., Iijima, K., Saegusa, J., & Morioka, I. (2020). Detection of Bacterial Infection Based on Age-Specific Percentile-Based Reference Curve for Serum Procalcitonin Level in Preterm Infants. Clinical Laboratory. https://www.semanticscholar.org/paper/03e6abecd996e03c61c86b8f2800b761794b760e

[71] Gao, Y., You, Z.-F., & Xu, B. (2020). Integrated Design of Autonomous Orbit Determination and Orbit Control for GEO Satellite Based on Neural Network. International Journal of Aerospace Engineering. https://www.semanticscholar.org/paper/207ee54b4e219d5518db771ed2cdc3ad59b4f980

[72] Gao, Z., & Wang, S. (2021). Fault estimation and fault tolerance control for spacecraft formation systems with actuator fault and saturation. Optimal Control Applications and Methods. https://onlinelibrary.wiley.com/doi/abs/10.1002/oca.2751

[73] Gleason, M. (2020). Establishing space traffic management standards, guidelines and best practices. Journal of Space Safety Engineering. https://www.sciencedirect.com/science/article/pii/S2468896720300628

[74] Gorr, B., Ravindra, V., Melebari, A., Jaramillo, A. A., Nag, S., Moghaddam, M., & Selva, D. (2023). Multi-Objective Optimization of an Intelligent Soil-Moisture-Monitoring Satellite Constellation. Journal of Spacecraft and Rockets. https://arc.aiaa.org/doi/10.2514/1.A35558

[75] Gutierrez, T., Coulter, N., Moncayo, H., Nakka, Y. K., Choi, C., Rahmani, A., & Gupta, A. (2023). Correction: Data-driven Health Management System for Multi-Spacecraft Formation Flying. AIAA SCITECH 2023 Forum. https://arc.aiaa.org/doi/10.2514/6.2023-0129.c1

[76] Hakima, H., & Bazzocchi, M. (2022). In-orbit target tracking by flyby and formation-flying spacecraft. Aerospace Systems. https://link.springer.com/article/10.1007/s42401-021-00111-z

[77] Harris, R., & Baumann, I. (2021). Satellite earth observation and national data regulation. Space Policy. https://www.sciencedirect.com/science/article/pii/S026596462100014X

[78] He, L., Guo, K., Gan, H., & Wang, L. (2022). Collaborative Data Offloading for Earth Observation Satellite Networks. IEEE Communications Letters. https://ieeexplore.ieee.org/document/9714295/

[79] Ho, C., Tan, C., Tan, E., & Lim, Y. (2024). TeLEOS-2 Overview and Initial Results. https://ieeexplore.ieee.org/abstract/document/10659422/

[80] Holzinger, M., McMahon, J., Rivera, K., & Yuricich, J. (2022). Decentralized Formation and Constellation Stability Design Requirements Using Differential Mean Orbit Elements. Journal of Spacecraft and Rockets. https://arc.aiaa.org/doi/10.2514/1.A35188

[81] Hu, Q., & Shi, Y. (2020). Event-based coordinated control of spacecraft formation flying under limited communication. Nonlinear Dynamics. https://link.springer.com/article/10.1007/s11071-019-05396-6

[82] Huang, S. (2020). Multi-phase mission analysis and design for satellite constellations with low-thrust propulsion. https://www.politesi.polimi.it/handle/10589/169779

[83] Huang, S., Guo, B., Yuan, Y., Wang, B., Zhang, Y., Yang, H., Jiang, M., Wang, Y., Fu, M., & Liu, Y. (2020). Control and Management of Optical Inter-Satellite Network based on CCSDS Protocol (Invited). 2020 European Conference on Optical Communications (ECOC). https://ieeexplore.ieee.org/document/9333377/

[84] Huang, T., Li, Q., Xu, C., Xu, M., Wang, S., Huang, G., & Liu, X. (2025). From Earth to Orbit: Launch Sequence Optimization for LEO Mega-Constellations. IEEE Transactions on Mobile Computing. https://www.semanticscholar.org/paper/9739c7d0aa845672d0b0ccd9e17267a656924c2d

[85] Huang, W., Andrada, R., Holman, K., Borja, D., & Ho, K. (2024). A Preliminary Availability Assessment of A LEO Satellite Constellation. 2024 Annual Reliability and Maintainability Symposium (RAMS). https://ieeexplore.ieee.org/document/10457737/

[86] Huang, Y., You, L., Tsinos, C., Wang, W., & Gao, X. (2023). QoS-Aware Precoding in Downlink Massive MIMO LEO Satellite Communications. IEEE Communications Letters. https://ieeexplore.ieee.org/document/10087224/

[87] Huang, Z., & Han, H. (2025). Repeat-ground-track orbit design and analysis for remote sensing in specific areas. Journal of Physics: Conference Series. https://iopscience.iop.org/article/10.1088/1742-6596/2977/1/012014/meta

[88] Hui, M., Zhai, S., Wang, D., Hui, T., & Wang, W. (2025). A review of leo satellite communication payloads for integrated communication, navigation, and remote sensing: Opportunities, challenges, future directions. https://ieeexplore.ieee.org/abstract/document/10945753/

[89] Imbuzeiro, E. B. (2024). The Technological Paradigm Shifts in Space: A Literature Review. IAF Businesses and Innovation Symposium. https://www.semanticscholar.org/paper/59b98d1162aee93ddd63239349c0fabfd143ad47

[90] Ito, T., Izumi, K., Kawano, I., Funaki, I., Sato, S., Akutsu, T., Komori, K., Musha, M., Michimura, Y., Satoh, S., Iwaki, T., Yokota, K., Goto, K., Furukawa, K., Matsuo, T., Tsuzuki, T., Yamada, K., Sasaki, T., Nishishita, T., … Sakai, S. (2025). SILVIA: Ultra-precision formation flying demonstration for space-based interferometry. ArXiv. https://arxiv.org/abs/2504.05001

[91] IV, E. P., & Wiesel, W. (2022). Effects of stochastic drag on prediction variance for low Earth orbit satellites. Journal of Guidance. https://arc.aiaa.org/doi/abs/10.2514/1.G005937

[92] Ivanushkin, M. A., & Zhaldybina, O. (2024). Assessing the design characteristics of low-orbit Earth remote sensing constellations. Sovremennye Problemy Distantsionnogo Zondirovaniya Zemli Iz Kosmosa. https://www.semanticscholar.org/paper/7c977c9feb4b52b11190eabbcd2263a49f711741

[93] Jafari, M., & Aminabadi, S. (2022). Investigating orbital configurations for a LEO satellite telephony constellation over the territory of Iran. https://journal.isrc.ac.ir/article_146951_cda1165a6d31ff4a2c77041f4a6f6640.pdf

[94] Jafarigol, F., Yousefi, S., Omrani, A. D., & Rashidi, Y. (2024). The relative contributions of traffic and non-traffic sources in ultrafine particle formations in Tehran mega city. Scientific Reports. https://www.nature.com/articles/s41598-023-49444-z

[95] Karimi, R., Peterson, J., Rahmani, A., & Chung, S. (2020). Swarm of Satellites Initial Formation Maintenance using Impulsive and Low Thrust Maneuvers. https://drive.google.com/file/d/1xWy8QTlvzKMQDlD_bXPwn2Y4zEEsTnKP/view

[96] Keles, O. (2023). Telecommunications and space debris: Adaptive regulation beyond earth. Telecommunications Policy. https://www.sciencedirect.com/science/article/pii/S0308596123000289

[97] Khan, L., Elshennawy, A., Cudney, E., & Furterer, S. (2024). Critical success factors for implementing Industry 4.0 in Aerospace and Defense: A systematic literature review. Quality Engineering. https://www.tandfonline.com/doi/full/10.1080/08982112.2024.2403606

[98] Kidd, C., Huffman, G., Maggioni, V., Chambon, P., & Oki, R. (2021). The Global Satellite Precipitation Constellation: current status and future requirements. Bulletin of the American Meteorological Society. https://journals.ametsoc.org/view/journals/bams/102/10/BAMS-D-20-0299.1.xml

[99] Kim, H. (2024). Adaptive Beam Control Technique for Inter-Satellite Laser Links. 2024 Conference on Lasers and Electro-Optics Pacific Rim (CLEO-PR). https://ieeexplore.ieee.org/document/10676549/

[100] Kreienbaum, M., Dörrich, A., & Brandt, D. (2020). Isolation and Characterization of Shewanella Phage Thanatos Infecting and Lysing Shewanella oneidensis and Promoting Nascent Biofilm Formation. https://www.frontiersin.org/articles/10.3389/fmicb.2020.573260/full

[101] Kuklewski, M., Hanasz, S., & Kasprowicz, G. (2020). Universal COTS-Based SpaceVPX Payload Carrier for LEO Application. https://ieeexplore.ieee.org/abstract/document/9172280/

[102] Latifi, G., & Paknezhad, N. (2021). Evaluating urban shape of Tehran through differential semantics scale. Cogent Engineering. https://www.tandfonline.com/doi/full/10.1080/23311916.2021.1937829

[103] Lavezzi, G., Lifson, M., & Servadio, S. (2025). Orbital tolerance and intrinsic orbital capacity for electric propulsion constellations. https://arc.aiaa.org/doi/abs/10.2514/1.A35875

[104] Lee, H., Shimizu, S., Yoshikawa, S., & Ho, K. (2020). Satellite constellation pattern optimization for complex regional coverage. https://arc.aiaa.org/doi/abs/10.2514/1.A34657

[105] Lee, J., Nagalingam, A., & Yeo, S. (2021). A review on the state-of-the-art of surface finishing processes and related ISO/ASTM standards for metal additive manufactured components. Virtual and Physical Prototyping. https://www.tandfonline.com/doi/abs/10.1080/17452759.2020.1830346

[106] Lee, J., & Ryu, J. (2022). Visible Trajectory of LEO Satellite Networks. 2022 27th Asia Pacific Conference on Communications (APCC). https://ieeexplore.ieee.org/document/9943788/

[107] Lee, S. S. (2021). Closed-form solution of repeat ground track orbit design and constellation deployment strategy. Acta Astronautica. https://linkinghub.elsevier.com/retrieve/pii/S0094576520307542

[108] Leyva-Mayorga, I., Soret, B., & Popovski, P. (2020). Inter-Plane Inter-Satellite Connectivity in Dense LEO Constellations. IEEE Transactions on Wireless Communications. https://ieeexplore.ieee.org/document/9327501/

[109] Li, D., Han, X., Zhang, Y., Zhou, Y., & Liang, B. (2021). Multiple Orbital Angular Momentum Vortex beams Generation With Narrow Divergence Angle using metasurface. 2021 CIE International Conference on Radar (Radar). https://ieeexplore.ieee.org/document/10028460/

[110] Li, J. (2020). Space Orbit Design of Remote Sensing Satellite. https://www.semanticscholar.org/paper/760c84ad968d0207e84a92aabc948ea5dba820a3

[111] Li, K., Hofmann, C., & Reder, H. (2022). A techno-economic assessment and tradespace exploration of low earth orbit mega-constellations. https://ieeexplore.ieee.org/abstract/document/9952191/

[112] Liang, J., Chaudhry, A. U., Erdogan, E., & Yanikomeroglu, H. (2022). Link Budget Analysis for Free-Space Optical Satellite Networks. 2022 IEEE 23rd International Symposium on a World of Wireless, Mobile and Multimedia Networks (WoWMoM). https://ieeexplore.ieee.org/document/9842823/

[113] Liu, H., Tian, Y., & Lewis, F. (2020). Robust trajectory tracking in satellite time-varying formation flying. IEEE Transactions on Cybernetics. https://ieeexplore.ieee.org/abstract/document/8954615/

[114] Liu, Z., Yang, H., & Chen, T. (2025). Low-Thrust Formation Keeping for Heliocentric Space-Based Gravitational Wave Detection Mission. Advances in Space Research. https://www.sciencedirect.com/science/article/pii/S0273117725005411

[115] Llanos, P. (n.d.). Enhancing Earth-affecting Solar Transient Observations via Novel Spacecraft Trajectories. https://www.researchgate.net/profile/Pedro-Llanos-4/publication/373362997_Enhancing_Earth-affecting_Solar_Transient_Observations_via_Novel_Spacecraft_Trajectories/links/64e7fc320453074fbdabd5eb/Enhancing-Earth-affecting-Solar-Transient-Observations-via-Novel-Spacecraft-Trajectories.pdf

[116] Lönngren, J., & Poeck, K. van. (2020). Wicked problems: a mapping review of the literature. International Journal of Sustainable Development & World Ecology. https://www.semanticscholar.org/paper/dcf7f95181bfa491c9cb52217d6d634b9d50e9a6

[117] Low, S., Moon, Y., Liu, W. T., & Tan, C. (2022). Designing a reference trajectory for frozen repeat near-equatorial low earth orbits. https://arc.aiaa.org/doi/abs/10.2514/1.A34934

[118] Lu, X., & Colombo, C. (2024). Post mission disposal design in the Laplace plane leveraging orbital perturbations. https://re.public.polimi.it/bitstream/11311/1277562/1/LUXCO01-24.pdf

[119] Ma, F., Zhang, X., Li, X., Cheng, J., Guo, F., Hu, J., & Pan, L. (2020). Hybrid constellation design using a genetic algorithm for a LEO-based navigation augmentation system. GPS Solutions. https://link.springer.com/article/10.1007/s10291-020-00977-0

[120] Maddox, C. (2023). Stray Dogs and Luxury Taxes: What Happened to the Indian Grand Prix? https://link.springer.com/chapter/10.1007/978-3-031-22825-4_28

[121] Mahadika, D. A., Aristyagama, Y. H., & Budiyanto, C. (2023). Evaluation of Website Based Information System To Monitor Student Learning Progress In Schools Using ISO/IEC 9126 Standards And GTMetrix. IJIE (Indonesian Journal of Informatics Education). https://www.semanticscholar.org/paper/fec9fe9dd77aafe4b44f43555b6380b1f9c5666a

[122] Mahfouz, A., Gaias, G., Rao, D. V. V., & Voos, H. (2023). Autonomous Optimal Absolute Orbit Keeping through Formation Flying Techniques. Aerospace. https://www.preprints.org/manuscript/202310.1189/v1

[123] Mahfouz, A., Gaias, G., Vedova, F. D., & Voos, H. (2025). Low-thrust under-actuated satellite formation guidance and control strategies. Acta Astronautica. https://linkinghub.elsevier.com/retrieve/pii/S0094576525001432

[124] Malik, S., Moshrefizadeh, M., Tahri, O., & Bai, X. (2025). EvSat3D: Satellite Pose Estimation and 3D Reconstruction with Event Camera. https://ieeexplore.ieee.org/abstract/document/11080435/

[125] Manche, V. B. Y., & Manche, S. Y. (2024). Satellite Link Design for LEO Constellation. International Journal of Science and Research (IJSR). https://www.semanticscholar.org/paper/5e7e6d39bc9bbbc3562615d230d2a2236a2c3160

[126] Mango, E. J. (2025). Partisipasi Pemilih dalam Pemilihan Kepala Daerah Kabupaten Timor Tengah Utara Dalam Masa Pandemik Covid-19 Tahun 2020-2025. Action Research Literate. https://arl.ridwaninstitute.co.id/index.php/arl/article/view/2612

[127] Manzoor, B., & Al-Hourani, A. (2022). Improving IoT-over-satellite connectivity using frame repetition technique. https://ieeexplore.ieee.org/abstract/document/9676997/

[128] Marete, C., Zakharov, W., & Mendonca, F. (2022). A Systematic Literature Review Examining the Gender Gap in Collegiate Aviation and Aerospace Education. Collegiate Aviation Review International. https://www.semanticscholar.org/paper/a622673cf20000ea84b3c1886b881da365416880

[129] Markovitz, O., & Segal, M. (2023). Demand Island Routing for LEO satellite constellations. Comput. Networks. https://linkinghub.elsevier.com/retrieve/pii/S1389128623001007

[130] Martins, J., Caetano, S., & Pereira, C. (2024). A satellite view of the exceptionally warm summer of 2022 over Europe. https://nhess.copernicus.org/articles/24/1501/2024/

[131] Mathavaraj, S., & Padhi, R. (2021). Satellite Formation Flying. https://www.semanticscholar.org/paper/c4d2158b8e17140f1691abcae11259a4c3a0794a

[132] McGrath, C., & Macdonald, M. (2020). General perturbation method for satellite constellation deployment using nodal precession. https://arc.aiaa.org/doi/full/10.2514/1.G004443

[133] Meneghini, C., & Parente, C. (2020). Temporal Analysis of GDOP to Quantify the Benefits of GPS and GLONASS Combination on Satellite Geometry. International Journal of Advanced Computer Science and Applications. https://www.semanticscholar.org/paper/5996e6f35032e8b53db17102713443517503909a

[134] Minocha, A. (2024). Advanced Manufacturing Techniques in Aerospace Engineering. Darpan International Research Analysis. https://www.semanticscholar.org/paper/9366cdf0a37a5c2e67564191108085f3f42556a7

[135] Montgomery, L., & Bair, C. (2021). Small Satellite Regulation in 2021. https://digitalcommons.usu.edu/smallsat/2021/all2021/140/

[136] Mostafa, A., & Dewaik, M. H. E. (2020). Balanced Low Earth Satellite Orbits. Advances in Astronomy. https://www.semanticscholar.org/paper/faec9af97b7014677a25ee6f0c0d3cb301aeffb8

[137] Nag, S., Murakami, D., Marker, N., & Lifson, M. (2021). Prototyping operational autonomy for space traffic management. Acta Astronautica. https://www.sciencedirect.com/science/article/pii/S0094576520307323

[138] Namini, R. S., Loda, M., & Meshkini, A. (2020). SWOT Analysis and Developing Strategies for the Realisation of Urban Livability in Tehran. International Journal of Urban Sustainable Development. https://www.semanticscholar.org/paper/4c49d1adb9fbaac44c4c9a6bed1bab3d731008eb

[139] Navabi, M., & Hashkavaei, N. S. (2020). Nonlinear Attitude Control of Satellite Using Optimal Adaptive and Fuzzy Control Methods. 2020 8th Iranian Joint Congress on Fuzzy and Intelligent Systems (CFIS). https://ieeexplore.ieee.org/document/9238733/

[140] Nemati, M., Kankashvar, M., & Bolandi, H. (2022). Unscented Kalman Filter adaptive noise covariance selection for satellite formation flying with Q_leaming. 2022 30th International Conference on Electrical Engineering (ICEE). https://ieeexplore.ieee.org/document/9827301/

[141] New Strategic Vision of Electronic Governance in the Republic of Bulgaria for the 2020-2025 Period. (2022). Economic and Social Alternatives. https://www.unwe.bg/doi/alternativi/2022.1/ISA.2022.1.03.pdf

[142] Nie, T., & Gurfil, P. (2021). Bounded satellite relative motion in coplanar three-body systems. Journal of Guidance. https://arc.aiaa.org/doi/full/10.2514/1.G005390

[143] Nie, T., Gurfil, P., & Zhang, S. (2020). Lunar satellite formation keeping using differential solar radiation pressure. Journal of Guidance. https://arc.aiaa.org/doi/abs/10.2514/1.G004475

[144] Nixon, M., & Shtessel, Y. (2022). Adaptive Sliding Mode Control of a Perturbed Satellite in a Formation Antenna Array. IEEE Transactions on Aerospace and Electronic Systems. https://ieeexplore.ieee.org/document/9749025/

[145] Noro, T., Inamori, T., & Park, J. H. (2020). Formation Flying under Periodic Orbit Considering Environmental Forces in LEO. AIAA Scitech 2021 Forum. https://arc.aiaa.org/doi/10.2514/6.2021-1383

[146] Nwankwo, V. (2020). Interactive comment on “Atmospheric drag effects on modelled LEO satellites during the July 2000 Bastille Day event in contrast to an interval of geomagnetically quiet conditions” by. https://www.semanticscholar.org/paper/9537c0d6f77f11b9a6582e341c7e13e3e2afe2e6

[147] Nwankwo, V., Denig, W., Ajakaiye, M. P., Akanni, W., Fatokun, J., Chakrabarti, S., Raulin, J., Correia, E., & Enoh, J. E. I. (2020). Simulation of atmospheric drag effect on low Earth orbit satellites during intervals of perturbed and quiet geomagnetic conditions in the magnetosphere-ionosphere system. 2020 International Conference in Mathematics, Computer Engineering and Computer Science (ICMCECS). https://ieeexplore.ieee.org/document/9077614/

[148] Okati, N., Riihonen, T., & Korpi, D. (2020). Downlink coverage and rate analysis of low earth orbit satellite constellations using stochastic geometry. https://ieeexplore.ieee.org/abstract/document/9079921/

[149] Osoro, O., & Oughton, E. (2021). A techno-economic framework for satellite networks applied to low earth orbit constellations: Assessing Starlink, OneWeb and Kuiper. IEEE Access. https://ieeexplore.ieee.org/abstract/document/9568932/

[150] Özdemi̇r, O., & Buzluca, F. (2024, February 1). Evaluating Microservices Maintainability: A Classification System Using Code Metrics and ISO/IEC 250xy Standards. Proceedings of the 2024 13th International Conference on Software and Computer Applications. https://www.semanticscholar.org/paper/d1cc6cd4f1ba098538f45e06fd6b5e4dc25c25fd

[151] Paek, S., Kim, S., Kronig, L., & Weck, O. de. (2020). Sun-synchronous repeat ground tracks and other useful orbits for future space missions. The Aeronautical Journal. https://www.cambridge.org/core/journals/aeronautical-journal/article/sunsynchronous-repeat-ground-tracks-and-other-useful-orbits-for-future-space-missions/C7721B594D4F5F2006335C9C0E0E5DE0

[152] Palacios, A., Todd, C., Barbagallo, E., Birtwhistle, A., Braembussche, P. V. D., Girard, A.-F., Langlois, S., Pirson, L., Marracci, R., Ferraguto, M., Ciolino, O., Wartmann, S., Pastorini, G., Brilli, S., Lorenzini, S., Giunti, L., Bologna, P., Viglione, A., Ponticelli, B., … Cocco, T. D. (2023). Meteosat Third Generation: Data Handling Architecture of a State-of-the-Art GEO Meteorological Satellite. 2023 European Data Handling & Data Processing Conference (EDHPC). https://ieeexplore.ieee.org/document/10396281/

[153] Palisetty, R., Socarrás, L. M. G., Chaker, H., Singh, V., Eappen, G., Martins, W. A., Ha, V. N., Vásquez-Peralvo, J. A., Rios, J. L. G., DUNCAN, J. C. M., Chatzinotas, S., Ottersten, B., Coskun, A., King, S., D’Addio, S., & Angeletti, P. (2023). FPGA Implementation of Efficient Beamformer for On-Board Processing in MEO Satellites. 2023 IEEE 34th Annual International Symposium on Personal, Indoor and Mobile Radio Communications (PIMRC). https://ieeexplore.ieee.org/document/10294011/

[154] Pan, X., Xu, M., Dong, Y., & Zuo, X. (2020). Relative Dynamics and Station-Keeping Strategy of Satellite–Sail Transverse Formation. Journal of Guidance Control and Dynamics. https://arc.aiaa.org/doi/10.2514/1.G005349

[155] Panahifar, H., Moradhaseli, R., & Khalesifard, H. (2020). Monitoring atmospheric particulate matters using vertically resolved measurements of a polarization lidar, in-situ recordings and satellite data over Tehran, Iran. Scientific Reports. https://www.nature.com/articles/s41598-020-76947-w

[156] Pańkowska, M. (2020). Business to System Requirements Agile Mapping. https://www.semanticscholar.org/paper/bd4f85b98d3269e6a06c935fa65379ca5862237e

[157] Pardini, C., & Anselmo, L. (2020). Environmental sustainability of large satellite constellations in low earth orbit. Acta Astronautica. https://www.sciencedirect.com/science/article/pii/S0094576520300187

[158] Pastena, M., Melega, N., Tossaint, M., Regan, A., Castorina, M., Gabriele, A., Mathieu, P., & Rosello, J. (2020). Small satellites landscape: ESA Earth observation with a focus on optical missions. https://www.semanticscholar.org/paper/84d74dccd086f5f9f059bc587ec880d0ed34284d

[159] Pedram, M., & Georgiades, E. (2023). The Role of Regulatory Frameworks in Balancing Between National Security and Competition in LEO Satellite Market. J. Nat’l Sec. L. & Pol’y. https://heinonline.org/hol-cgi-bin/get_pdf.cgi?handle=hein.journals/jnatselp14&section=13

[160] Peel, M., Eggl, S., Rawls, M. L., Dadighat, M., Benvenuti, P., Vruno, F. D., & Walker, C. (2024). Summary of SatHub, and the current observational status of satellite constellations. https://www.semanticscholar.org/paper/3a98e717b3d9da74792b6cc818674db4452d81d5

[161] Peng, Y., Scales, W., & Edwards, T. (2020). GPS‐based satellite formation flight simulation and applications to ionospheric remote sensing. Navigation. https://onlinelibrary.wiley.com/doi/abs/10.1002/navi.354

[162] Peto-Madew, F., & Bhattarai, S. (2025). Investigating the Application of the Orbit Domain Calibration Method in Sun Synchronous Orbits. https://conference.sdo.esoc.esa.int/proceedings/sdc9/paper/254/SDC9-paper254.pdf

[163] Phillips, S., Petersen, C., & Fierro, R. (2020). Correction: Resilient Spacecraft Formation Control Under Malfunctioning Communication. https://arc.aiaa.org/doi/10.2514/6.2020-1339.c1

[164] Pourzarei, H., Ghnaya, O., & Rivest, L. (2024). Engineering change management: comparing theory to a case study from aerospace. https://www.inderscienceonline.com/doi/abs/10.1504/IJPLM.2024.143538

[165] Project number 813137 URBASIS-EU New challenges for Urban Engineering Seismology DELIVERABLES. (2020). https://www.semanticscholar.org/paper/1f4d0253059c6bb853d7e46e046cdaf3b1d625d5

[166] Qin, P., Xu, D., Alfarraj, O., Al-Dulaimi, A., Yu, K., & Mumtaz, S. (2024). Partial Aggregation for Federated Learning with Differentiated Latency in LEO Satellite Networks. 2024 IEEE Globecom Workshops (GC Wkshps). https://ieeexplore.ieee.org/document/11100962/

[167] RĂDUȚU, A. (n.d.). SCIENTIFIC REPORT NO. https://sd.utcb.ro/wp-content/uploads/2021/09/Raport_EN.pdf

[168] Rakisheva, Z., Kaliyeva, N., Doszhan, N., & Sukhenko, A. (2025). Issues of the Satellite Formation Control. https://www.intechopen.com/online-first/1206624

[169] Raper, S. (2020). Leo Breiman’s “Two Cultures.” Significance. https://rss.onlinelibrary.wiley.com/doi/10.1111/j.1740-9713.2020.01357.x

[170] Rashed, M., & Bang, H. (2023). Autonomous Mission Planning and Operations for Optimal Deployment of Small Satellite Constellations in CisLunar Space. International Conference on Space Operations. https://link.springer.com/chapter/10.1007/978-3-031-60408-9_27

[171] Ray, A. T., Fischer, O., White, R. T., Cole, B. F., & Mavris, D. (2024). Development of a Language Model for Named-Entity-Recognition in Aerospace Requirements. J. Aerosp. Inf. Syst. https://www.semanticscholar.org/paper/6d19616a04c7a2459c5abe641099a841185d0f28

[172] Ron, D., Yusufzai, F., Kwakye, S., & Roy, S. (2025). Time-Dependent Network Topology Optimization for LEO Satellite Constellations. https://ieeexplore.ieee.org/abstract/document/11044725/

[173] Sabour, M., Jafary, P., & Nematiyan, S. (2023). Applications and classifications of unmanned aerial vehicles: A literature review with focus on multi-rotors. The Aeronautical Journal. https://www.cambridge.org/core/journals/aeronautical-journal/article/applications-and-classifications-of-unmanned-aerial-vehicles-a-literature-review-with-focus-on-multirotors/54C83C62D81A39CCF8898CAD41833C2E

[174] Sajit, A., Gupta, A., Kukar, R., & Ramakrishnan, S. (2024). Deployment and Maintenance of Satellite Constellations for Strategic Applications. https://link.springer.com/chapter/10.1007/978-3-031-76937-5_35

[175] Salehi, A., Fakoor, M., Kosari, A., & Ghoreishi, S. M. N. (2022). Conceptual Design Process for LEO Satellite Constellations Based on System Engineering Disciplines. Computer Modeling in Engineering &amp; Sciences. https://www.semanticscholar.org/paper/ca24502adda636dc38c676e8fd02fe4eb1c450cd

[176] Santos, M., Guichot, F., Janko, K., Dunn, H., & Cruz, C. (n.d.). NOVEL TOD PLANNING APPROACHES [draft handbook]. https://www.todisrur.eu/s/Draft-Handboook-TOD-IS-RUR.pdf

[177] Sato, T., Matsuya, Y., Ogawa, T., & Kai, T. (2023). Improvement of the hybrid approach between Monte Carlo simulation and analytical function for calculating microdosimetric probability densities in macroscopic …. https://iopscience.iop.org/article/10.1088/1361-6560/ace14c/meta

[178] Scala, F., Gaias, G., Colombo, C., & Neira, M. (2020). Three Satellites Formation Flying: Deployment and Formation Acquisition Using Relative Orbital Elements. https://www.semanticscholar.org/paper/173583a0fa5e0e7fc9bb0b2ac3a24fd3653f5206

[179] Schlueter, M., Neshat, M., Wahib, M., Munetomo, M., & Wagner, M. (2020). GTOPX Space Mission Benchmarks. ArXiv. https://linkinghub.elsevier.com/retrieve/pii/S235271102100011X

[180] Schnurbus, V., & Edvardsson, I. (2020). The Third Mission Among Nordic Universities: A Systematic Literature Review. Scandinavian Journal of Educational Research. https://www.tandfonline.com/doi/full/10.1080/00313831.2020.1816577

[181] Selvan, K., Siemuri, A., Kuusniemi, H., & Välisuo, P. (2021). A Review on Precise Orbit Determination of Various LEO Satellites. https://www.semanticscholar.org/paper/3c71643981dc406daa5b9d80ff3c934e4c3174f4

[182] Servidia, P., & Espana, M. (2021). On autonomous reconfiguration of SAR satellite formation flight with continuous control. https://ieeexplore.ieee.org/abstract/document/9439059/

[183] Shakun, L., Koshkin, N., Korobeynikova, E., Kozhukhov, D., Kozhukhov, O., & Strakhova, S. (2021). Comparative analysis of global optical observability of satellites in LEO. Advances in Space Research. https://linkinghub.elsevier.com/retrieve/pii/S0273117720308929

[184] Shen, H. (2021). Explicit Approximation for -Perturbed Low-Thrust Transfers Between Circular Orbits. Journal of Guidance. https://arc.aiaa.org/doi/full/10.2514/1.G005415

[185] Shen, H., Xue, S., & Li, D. (2020). MPC-based Low-thrust Orbit Transfer Under J2 Perturbation. 2020 39th Chinese Control Conference (CCC). https://ieeexplore.ieee.org/document/9188378/

[186] Sheng, J., & Geng, Y. (2023). Normalized nodal distance-based J2-perturbed ground-track adjustment with apsidal-altitude constraints. Aerospace Science and Technology. https://linkinghub.elsevier.com/retrieve/pii/S1270963823003152

[187] Shepperd, R. W. (2024). Using Frozen Orbits and Well-Defined Control Boxes for Constellation Separation. 22nd IAA Symposium on Space Debris. https://www.proceedings.com/078360-0146.html

[188] Shi, Y., & Hu, Q. (2021). Observer-based spacecraft formation coordinated control via a unified event-triggered communication. https://ieeexplore.ieee.org/abstract/document/9409708/

[189] Sigoulakis, D. (2021). Guidance for Standards Applicable to the Development of Next Generation NATO Reference Mobility Models (NG-NRMM). https://apps.dtic.mil/sti/html/trecms/AD1148004/

[190] Silvestrini, S., & Lavagna, M. (2021). Neural-based predictive control for safe autonomous spacecraft relative maneuvers. Journal of Guidance. https://arc.aiaa.org/doi/full/10.2514/1.G005481

[191] Singh, V., Prabhakara, A., Zhang, D., & Yağan, O. (2021). A community-driven approach to democratize access to satellite ground stations. https://dl.acm.org/doi/abs/10.1145/3447993.3448630

[192] Sivakumar, M., & Tyj, N. (2021). A literature survey of unmanned aerial vehicle usage for civil applications. https://www.scielo.br/j/jatm/a/vnWkfk66h5VvsRhn6CxjLKx/

[193] Skorokhodov, A., & Kuryanovich, K. V. (2020). Statistical model for characteristics of atmospheric internal waves and their signatures by satellite data. https://www.semanticscholar.org/paper/7d06e221d0b4c338f8e3a882c1d344365e65f9b3

[194] Sohrabi, N. M. (2023). The politics of in/visibility: The Jews of urban Tehran. Studies in Religion/Sciences Religieuses. https://journals.sagepub.com/doi/10.1177/00084298231152642

[195] Song, Z., Liu, H., Dai, G., & Wang, M. (2021). Cell Area‐Based Method for Analyzing the Coverage Capacity of Satellite Constellations. https://onlinelibrary.wiley.com/doi/abs/10.1155/2021/6679107

[196] Soret, B., Leyva-Mayorga, I., Mercado-Mart’inez, A. M., Moretti, M., Jurado-Navas, A., Martinez-Gost, M., Miguel, C. S. de, Salas-Prendes, A., & Popovski, P. (2024). Semantic and goal-oriented edge computing for satellite Earth Observation. ArXiv. https://arxiv.org/abs/2408.15639

[197] Sruthy, A. N., Jacob, J., & Ramchand, R. (2020). Fault Tolerant Controller for Formation Flight of Leader-Follower Quadrotors. 2020 International Conference for Emerging Technology (INCET). https://ieeexplore.ieee.org/document/9153984/

[198] Stava, A. (2023). The Impact of Public Comments: A Quantitative Study of Public Engagement in the NEPA Process. https://search.proquest.com/openview/e80477fa44f0e454b7a1987eb2bcbea9/1?pq-origsite=gscholar&cbl=18750&diss=y

[199] Sun, S., Yan, J., Gao, W., Wang, B., & Dirkx, D. (2024). Assessment of Callisto Gravity-field Determination Using the Inter-satellite Range-rate Link. https://iopscience.iop.org/article/10.3847/1538-3881/ad4460/meta

[200] Sun, W., & Cao, B. (2020). Efficient Transmission of Multi Satellites-Multi Terrestrial Nodes Under Large-Scale Deployment of LEO. https://www.semanticscholar.org/paper/08dee2411685fbca9cb76842bb14531708cd7f09

[201] Sung, T., & Ahn, J. (2022). Optimal deployment of satellite mega-constellation. Acta Astronautica. https://linkinghub.elsevier.com/retrieve/pii/S0094576522005756

[202] Tan, S. (2020). Remote Sensing Applications and Innovations via Small Satellite Constellations. Handbook of Small Satellites. https://www.semanticscholar.org/paper/3510eb2ad55f0312521a4dc8503b67fc8dbdefb0

[203] Tang, J., Qu, Y., & Qi, W. (2024). Analysis and Design of Starlink-like Satellite Constellation. Chinese Astronomy and Astrophysics. https://linkinghub.elsevier.com/retrieve/pii/S0275106224000043

[204] Tchuigwa, B. S. S., Krmela, J., & Pokorný, J. (2021). LITERATURE REVIEW ON TIRE COMPONENT REQUIREMENTS. Perner’s Contacts. https://www.semanticscholar.org/paper/4cf841d22db8cc118f1bdf84fb8b5a3c29777fc8

[205] Telesca, D. (2024). An integrated continuum-based model for debris density evolution in low Earth orbit. https://www.politesi.polimi.it/handle/10589/240902

[206] Thangavel, K., Burroni, T., Servidia, P., & Hussainl, K. (2023). Nested autonomous orbit determination and control for distributed satellite systems: a general case study on constellation of formations for earth observation. Intelligence. https://www.researchgate.net/profile/Kathiravan-Thangavel-2/publication/374387312_Nested_Autonomous_Orbit_Determination_and_Control_for_Distributed_Satellite_Systems_A_General_Case_Study_on_Constellation_of_Formations_for_Earth_Observation/links/6521554b3ab6cb4ec6c3de61/Nested-Autonomous-Orbit-Determination-and-Control-for-Distributed-Satellite-Systems-A-General-Case-Study-on-Constellation-of-Formations-for-Earth-Observation.pdf

[207] Trainotti, C., Dassié, M., Giorgi, G., Khodabandeh, A., & Günther, C. (2023). Autonomous Synchronization of Satellite Constellations via Optical Inter-Satellite Links. 2023 Joint Conference of the European Frequency and Time Forum and IEEE International Frequency Control Symposium (EFTF/IFCS). https://ieeexplore.ieee.org/document/10272176/

[208] Traub, C., Romano, F., Binder, T., & Boxberger, A. (2020). On the exploitation of differential aerodynamic lift and drag as a means to control satellite formation flight. https://link.springer.com/article/10.1007/s12567-019-00254-y

[209] Treblow, S., & McGrath, C. (2025). Responsive Maneuver Planning for Sun-Synchronous Repeating Ground Track Orbits. Journal of Spacecraft and Rockets. https://arc.aiaa.org/doi/abs/10.2514/1.A35944

[210] Tziouras, J. (2021). The Designation of Satellite Constellations as Critical Space Infrastructure. https://www.semanticscholar.org/paper/0740882dadd93786aaf57a083b593b2f95daf25a

[211] Umphlett, N. (2020). Climate4Cities: City Data Explorer Tools Demonstration. https://www.semanticscholar.org/paper/ba9e8965ce5765a2295db5261589e112e198a891

[212] Valente, F., Lavacca, F. G., Polverini, M., Fiori, T., & Eramo, V. (2025). Optimization of Ground Station Energy Saving in LEO Satellite Constellations for Earth Observation Applications. Future Internet. https://www.semanticscholar.org/paper/f422dc2245065229a21efbd9a1dfaa1e9fc5cf25

[213] Valsamos, G., Larcher, M., & Casadei, F. (2021). Beirut explosion 2020: A case study for a large-scale urban blast simulation. Safety Science. https://www.sciencedirect.com/science/article/pii/S0925753521000357

[214] Vasile, M. (2021). Preface: Satellite constellations and formation flying. Advances in Space Research. https://linkinghub.elsevier.com/retrieve/pii/S0273117721001939

[215] Voronov, E. M., Karpunin, A. A., Palkin, M., & Titkov, I. P. (2020). Satellite Formation Flying Maneuver Optimal Control. Mekhatronika, Avtomatizatsiya, Upravlenie. https://www.semanticscholar.org/paper/448f11e4deb15f3dc92bb814f57c91257d6f8d46

[216] Walsh, M., & Peck, M. (2021). Orbital Rendezvous via a General Nonsingular Method. Journal of Guidance, Control, and Dynamics. https://arc.aiaa.org/doi/10.2514/1.G005188

[217] Wang, B., Song, X., Li, Y., & Wang, W. (2024). A method of satellite constellation observation based on J2 perturbation application. Journal of Physics: Conference Series. https://validate.perfdrive.com/fb803c746e9148689b3984a31fccd902/?ssa=37517bf0-e1b3-4f98-8846-d73c04a0fe67&ssb=95902226870&ssc=https%3A%2F%2Fiopscience.iop.org%2Farticle%2F10.1088%2F1742-6596%2F2820%2F1%2F012043&ssi=6d3cc6ff-cnvj-4de8-a339-8117d56713c5&ssk=botmanager_support@radware.com&ssm=587837579346534681333876499788809&ssn=f33913cde3f5dafa78184f25053d4154355211731cf0-22f2-426d-918960&sso=47dd9990-e0dcb83f3768275d21ffb88a2d252365991d6c94820aae33&ssp=82981788921761243461176126014105973&ssq=30385815076350834840935868249625336885799&ssr=MzQuNjguMjIyLjI0Mw==&sst=python-httpx/0.27.2&ssu=&ssv=&ssw=&ssx=eyJfX3V6bWYiOiI3ZjkwMDAxMTczMWNmMC0yMmYyLTQyNmQtOTk5MC1lMGRjYjgzZjM3NjgxLTE3NjEyMzU4NjgzOTUxNDg5NTE4Mi0wMDE3MDQ5MTQ4Nzk0YmUwOWE2MTMzIiwidXpteCI6IjdmOTAwMGNjNzI3ZmI5LTk4MjItNGE1Ni04M2E3LTA2ZDBjNzllMmJjMDEtMTc2MTIzNTg2ODM5NTE0ODk1MTgyLWFlMTVhMGM2MTJmMjEzZjkxMzMiLCJyZCI6ImlvcC5vcmcifQ==

[218] Wang, C., Jiang, K., Si, C., Zhang, H., Wu, F., Tang, Y., Zhang, B., Xu, L., & Guo, H. (2023). Dual Satellite Bistatic Sar Constellation Mission for SDGS. 2023 SAR in Big Data Era (BIGSARDATA). https://ieeexplore.ieee.org/document/10294390/

[219] Wang, L., Ma, W., Shao, Y., & Meng, T. (2025). A MBSE-based architect design approach for satellite constellations. Journal of Physics: Conference Series. https://iopscience.iop.org/article/10.1088/1742-6596/2977/1/012001

[220] Wang, X., Deng, N., & Wei, H. (2023). Coverage and rate analysis of LEO satellite-to-airplane communication networks in terahertz band. https://ieeexplore.ieee.org/abstract/document/10107732/

[221] Warren, L., & Alex, J. (2024). FREE SPACE OPTICAL COMMUNICATIONS WITH SMALL SATELLITES IN LOW EARTH ORBIT. https://calhoun.nps.edu/bitstreams/1086a970-9f92-4f9b-8579-c00cef476e8e/download

[222] Wawrzaszek, R., & Banaszkiewicz, M. (2023). Control and reconfiguration of satellite formations by electromagnetic forces. Journal of Telecommunications and Information Technology. https://www.semanticscholar.org/paper/2cf4bc7081bc62528f3b7e9c007ddac8a5a9575d

[223] Wengang, L., Fang, C., Rong, Z., & Cuihong, C. (2022). Biochar-Mediated Degradation of Roxarsone by Shewanella oneidensis MR-1. Frontiers in Microbiology. https://www.frontiersin.org/articles/10.3389/fmicb.2022.846228/full

[224] Wittenborg, T., Baimuratov, I., Franzén, L., & Staack, I. (2025). Knowledge-Based Aerospace Engineering--A Systematic Literature Review. https://arxiv.org/abs/2505.10142

[225] Woldai, T. (2020). The status of earth observation (EO) & geo-information sciences in Africa–trends and challenges. Geo-Spatial Information Science. https://www.tandfonline.com/doi/abs/10.1080/10095020.2020.1730711

[226] Wyniawskyj, N. S., Contenta, F., Flach, D., Hadland, A., Hopkin, A., Lidgley, J., Petit, D., Podder, P., Osadolor, F., & Walker, N. (2020). Improving Severe-Weather Resilience for Mongolian Herding Communities Using Satellite Earth Observation Imagery. IGARSS 2020 - 2020 IEEE International Geoscience and Remote Sensing Symposium. https://ieeexplore.ieee.org/document/9323703/

[227] Xiao, B., Karimi, H., Yu, X., & Gao, Q. (2020). IEEE access special section: Recent advances in fault diagnosis and fault-tolerant control of aerospace engineering systems. IEEE Access. https://ieeexplore.ieee.org/abstract/document/9061074/

[228] Xiaoyi, X., Chunhui, W., & Zhong-he, J. (2020). Design, analysis and optimization of random access inter-satellite ranging system. Journal of Systems Engineering and Electronics. https://ieeexplore.ieee.org/document/9247414/

[229] Xie, Y., Lei, Y., Guo, J., & Meng, B. (2021). Autonomous Guidance, Navigation, and Control of Spacecraft. Spacecraft Dynamics and Control. https://www.semanticscholar.org/paper/9e8ffee473796d99c73655c6961595c8cb2c1124

[230] Xu, H., Xu, B., & Hsu, L. (2022). 3DMA Sky Visibility Matching: An Example using a Simulated LEO Constellation. The International Technical Meeting of the The Institute of Navigation. https://www.semanticscholar.org/paper/2fb7026aa3b2a451710bd70000d98dff9e4f5783

[231] Xu, S. (2020). Plasma Space Propulsion for Nanosatellite Orbit Control and Complex Constellation Formation. 2020 IEEE International Conference on Plasma Science (ICOPS). https://ieeexplore.ieee.org/document/9717931/

[232] Xu, X., Cai, J., Liu, A., & Bian, D. (2022). Local State Routing for Satellite Constellation Networks. 2022 IEEE 22nd International Conference on Communication Technology (ICCT). https://ieeexplore.ieee.org/document/10072636/

[233] Xu, X., Wang, C., & Jin, Z. (2020). Perturbed ISL Analysis in LEO Satellite Constellation. 2020 IEEE 3rd International Conference on Electronics and Communication Engineering (ICECE). https://ieeexplore.ieee.org/document/9353019/

[234] Xu, Z., Guo, H., & Wu, J. (2024). Experimental Demonstration of SDN-Based Elastic Optical Switching for LEO Satellite Constellations. 2024 Asia Communications and Photonics Conference (ACP) and International Conference on Information Photonics and Optical Communications (IPOC). https://ieeexplore.ieee.org/document/10809824/

[235] Yahya, N. A., Varatharajoo, R., Harithuddin, A., & Razoumny, Y. (2021). Delta-V and ground metric investigations for responsive satellite formation flying. Acta Astronautica. https://linkinghub.elsevier.com/retrieve/pii/S0094576521006688

[236] Yan, K., Wu, Q., Yang, C., & Chen, M. (2020). Backstepping-based Adaptive Fault-Tolerant Control Design for Satellite Attitude System. 2020 International Conference on Unmanned Aircraft Systems (ICUAS). https://ieeexplore.ieee.org/document/9213890/

[237] Yang, Y., Mao, Y., Ren, X., Jia, X., & Sun, B. (2024). Demand and key technology for a LEO constellation as augmentation of satellite navigation systems. Satellite Navigation. https://link.springer.com/article/10.1186/s43020-024-00133-w

[238] Yin, J., Huang, H., Zhao, Q., & Wang, Z. (2021). A Mission- Satellite Mapping Method Based on Multilayer Neural Network. 2021 7th International Conference on Big Data and Information Analytics (BigDIA). https://ieeexplore.ieee.org/document/9619713/

[239] Yoon, Y. T., Ghezzo, P., Hervieu, C., & Palomo, I. D.-A. (2023). Navigating a large satellite constellation in the new space era: An operational perspective. Journal of Space Safety Engineering. https://linkinghub.elsevier.com/retrieve/pii/S2468896723001040

[240] Yuan, J., Zhou, S., Tang, C., Wu, B., Li, K., Hu, X., & liang,  ertao. (2023). Influence of Solar Activity on Precise Orbit Prediction of LEO Satellites. Research in Astronomy and Astrophysics. https://validate.perfdrive.com/fb803c746e9148689b3984a31fccd902/?ssa=f8e92a2f-8c68-4825-b71f-4304e9155397&ssb=56608210005&ssc=https%3A%2F%2Fiopscience.iop.org%2Farticle%2F10.1088%2F1674-4527%2Facbe2b&ssi=b26a86e3-cnvj-4b93-88e4-10bf9416a8f5&ssk=botmanager_support@radware.com&ssm=335861800690091171214714443351172&ssn=3cf636ce89c9013c6450a019f8e8ccf8134311731cf0-22f2-426d-913294&sso=f548b990-e0dcb83f37688974dbc15870d6c05e9fe07e34b7793c3153&ssp=46279686951761214909176127724706562&ssq=18908705070719881312835868974974997325677&ssr=MzQuNjguMjIyLjI0Mw==&sst=python-httpx/0.27.2&ssu=&ssv=&ssw=&ssx=eyJfX3V6bWYiOiI3ZjkwMDAxMTczMWNmMC0yMmYyLTQyNmQtOTk5MC1lMGRjYjgzZjM3NjgxLTE3NjEyMzU4NjgzOTUxNDgzOTAyNi0wMDE3ZTUwNTk3ZjJkZmE5NWExMTIxIiwidXpteCI6IjdmOTAwMGNjNzI3ZmI5LTk4MjItNGE1Ni04M2E3LTA2ZDBjNzllMmJjMDEtMTc2MTIzNTg2ODM5NTE0ODM5MDI2LWY5YmU2YTc0OGQ0ZjA2MGUxMjEiLCJyZCI6ImlvcC5vcmcifQ==

[241] Zajaček, M., Czerny, B., Jaiswal, V., & Štolc, M. (2024). Science with a small two-band UV-photometry mission III: Active Galactic Nuclei and nuclear transients. https://link.springer.com/article/10.1007/s11214-024-01062-5

[242] Zakharova, E., Nielsen, K., Kamenev, G., & Kouraev, A. (2020). River discharge estimation from radar altimetry: Assessment of satellite performance, river scales and methods. Journal of Hydrology. https://www.sciencedirect.com/science/article/pii/S0022169420300214

[243] Zapletin, M., & Goryachikh, K. S. (2021). Optimization of a spatial spaceflight between positions on the orbits of an artificial earth satellite. https://pubs.aip.org/aip/acp/article/892454

[244] Zhang, H., Yang, B., Xi, C., Yang, X., Hu, J., Wang, J., Qiao, X., & Fu, C. (2022). Research on Beam Interference Optimization Strategy of LEO Constellation. Wireless and Satellite Systems. https://link.springer.com/chapter/10.1007/978-3-030-93398-2_12

[245] Zhang, Y., Chu, F., Jia, L., Wan, Y., Cao, W., & Chang, X. (2025). Downlink Interference Analysis of Large-Scale Non-Geostationary Orbit Constellation Based on Fibonacci Grid Method. IEEE Transactions on Vehicular Technology. https://ieeexplore.ieee.org/document/10897782/

[246] zhao,  yun, luo,  huajun, Zhu, X., zeng,  zhen, & luo,  gang. (2025). Daytime detection of LEOs by ground-based visible light. https://www.semanticscholar.org/paper/03c230f27e6e277845d44e39ac3d6fc7a4fc2f93

[247] Zhao, B., Chen, G., Chen, W., & Xiao, Y. (2023). Evolution of Shewanella oneidensis MR-1 in competition with Citrobacter freundii. bioRxiv. https://www.biorxiv.org/lookup/doi/10.1101/2023.06.15.545074

[248] Zhao, J., Liu, Y., Zhao, K., Li, W., & Fang, Y. (2024). End-to-End Delay Analysis for Time-Sensitive Applications on Starlink LEO Constellation. 2024 Academic Conference of China Instrument and Control Society (ACCIS). https://ieeexplore.ieee.org/document/10948654/

[249] Zhao, L., Ma, M., Yuan, B., & Hu, M. (2024). Space-Based ADS-B Trajectory Processing Method based on Haversine-LSTM. https://ieeexplore.ieee.org/abstract/document/10800717/

[250] Zhao, X., Wang, C., Cai, S., & Wang, W. (2024). Cooperative Design of Dual-Layer LEO Satellite Constellation Based on Diversified QoS Requirements and Seamless Multi-Coverage. https://ieeexplore.ieee.org/abstract/document/10679605/

[251] Zheng, J., Luan, T. H., Li, G., Zhao, J., Yin, Z., Cheng, N., & Pan, J. (2025). Low Earth Orbit Satellite Networks: Architecture, Key Technologies, Measurement, and Open Issues. IEEE Network. https://ieeexplore.ieee.org/document/11008672/

[252] Zhou, L., Wang, Z., Dong, W., & Yan, J. (2023). Design of Inter-satellite Ranging and Clock Synchronization of Formation Satellites. 2023 XXXVth General Assembly and Scientific Symposium of the International Union of Radio Science (URSI GASS). https://ieeexplore.ieee.org/document/10265604/

[253] Zhu, X., Li, X., & Gong, X. (2022). Performance Analysis of ADS-B Receiving System Based on LEO Satellite Constellation. 2022 21st International Symposium on Communications and Information Technologies (ISCIT). https://ieeexplore.ieee.org/document/9931245/
