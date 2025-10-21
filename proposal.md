### **Thesis Title**

**Orbital Design and Mission Analysis of a Three-Satellite LEO Constellation for Repeatable, Transient Triangular Formation over a Mid-Latitude Target**

---

### **Detailed Thesis Proposal (Problem Definition)**

#### 1. Introduction & Background

Satellite Formation Flying (SFF) has emerged as a key enabling technology for advanced space missions, allowing multiple small, coordinated spacecraft to function as a single, large, distributed instrument. This paradigm offers significant advantages in terms of cost, scalability, and mission flexibility over traditional monolithic satellites. Seminal missions such as **TanDEM-X** for synthetic aperture radar interferometry, **GRACE/GRACE-FO** for gravity field mapping, and the **Magnetospheric Multiscale (MMS)** mission for magnetospheric science have successfully demonstrated the immense scientific returns of maintaining precise relative geometries in orbit. Technology demonstrators like **PRISMA** and **CanX-4/5** have further proven the feasibility of autonomous formation control using on-board GPS receivers, even at the nanosatellite scale.

However, the majority of formation flying missions focus on maintaining a *continuous* or quasi-continuous formation throughout their orbit. This thesis explores a novel mission concept: the design of a constellation that achieves a highly precise geometric formation for only a **brief, transient period** when passing over a specific area of interest, and repeats this event on a predictable, periodic basis (e.g., daily). This approach is fundamentally a problem of celestial mechanics and mission design, aimed at creating a precisely choreographed orbital event rather than a sustained state.

#### 2. Problem Statement

The core challenge of this research is to perform the conceptual design and orbital analysis of a small constellation of three satellites in Low Earth Orbit (LEO) that are placed in two distinct, intersecting orbital planes. The orbital parameters must be meticulously designed such that the satellites form a specific **equilateral or isosceles triangular formation** for a short duration (e.g., 90 seconds) as their ground tracks converge over a pre-defined mid-latitude target, such as the city of Tehran. This "formation event" must be passively achieved through the natural intersection of their orbits and be repeatable with a consistent daily period.

The design must account for significant orbital perturbations in LEO, primarily Earth's oblateness (J2 effect) and atmospheric drag, which will cause the formation geometry and timing to degrade. Therefore, a critical part of the problem is to analyze the stability of the formation and devise a conceptual station-keeping strategy to maintain its integrity over a realistic mission lifetime.

#### 3. Mission Objectives & Research Questions

The primary objective of this thesis is to establish the feasibility of the transient triangular formation concept through rigorous design and simulation.

**Specific Objectives:**

1.  To develop an analytical framework for designing the intersecting, repeating ground track orbits required for the mission.
2.  To simulate the relative dynamics of the three-satellite constellation in a high-fidelity environment, including major orbital perturbations.
3.  To analyze the stability and evolution of the transient triangular formation over time.
4.  To determine a conceptual station-keeping strategy and estimate the required propellant budget (ΔV) for formation maintenance.
5.  To evaluate and recommend an optimal orbital configuration based on performance metrics such as formation accuracy, availability, and fuel efficiency.

**Key Research Questions:**

1.  What set of orbital parameters (altitude, inclination, RAAN, phasing) for two intersecting planes can generate a repeating, transient triangular formation over a specified mid-latitude target?
2.  How do dominant LEO perturbations (J2, atmospheric drag) affect the precision and timing of the formation event, and what is the rate of degradation?
3.  What is the required ΔV budget to maintain the formation's geometric integrity and temporal periodicity within acceptable tolerances for a one-year mission lifetime?
4.  What are the key trade-offs between orbital altitude, formation accuracy, and station-keeping costs?

#### 4. Scope & Limitations

This research is a **conceptual design and simulation-based analysis**. The scope is limited to:

*   **Orbital Mechanics & Mission Design:** The primary focus is on trajectory design, relative dynamics, and station-keeping.
*   **Spacecraft:** Satellites are modeled as point masses. Attitude dynamics, control hardware, payload specifics, communication architecture, and power systems are outside the scope.
*   **Control Strategy:** The station-keeping strategy will be conceptual (e.g., impulsive maneuvers), and the design of the detailed GNC algorithm is not included.
*   **Simulation:** The simulation will use high-fidelity force models, but will assume perfect state determination and idealized thruster performance.

#### 5. Methodology

The research will be conducted in a phased approach:
1.  **Literature Review:** A comprehensive review of relative orbital dynamics, formation flying control, and regional constellation design techniques.
2.  **Tool Selection:** Utilization of industry-standard and open-source software, including **STK** for visualization and access analysis, **GMAT** or **Orekit** for high-fidelity propagation, and **Python/MATLAB** for custom analysis and control scripts.
3.  **Analytical Design:** Derivation of the initial orbital parameters for candidate constellations based on celestial mechanics principles, including repeating ground track theory.
4.  **Numerical Simulation:** Propagation of the satellite states over an extended period to model the formation events and their degradation under the influence of perturbations.
5.  **Analysis & Optimization:** Evaluation of simulation results against key performance indicators (KPIs) to identify the optimal design and quantify its performance and costs.

#### 6. Expected Contributions

This thesis will make the following contributions to the field of space engineering:
*   **A Novel Mission Concept:** The formalization of a transient, event-based formation flying architecture, which could enable new types of multi-point, on-demand scientific observations.
*   **A Specific Design Methodology:** A documented process for designing the complex, intersecting orbits required to achieve such a mission concept.
*   **Feasibility Analysis:** A quantitative assessment of the stability and station-keeping requirements for this class of formation, providing a benchmark for future mission planning.

---

### **6-Chapter Thesis Outline & Key Concepts**

#### **Chapter 1: Introduction**

*   **Key Concepts:** Motivation for satellite formation flying, overview of existing formation missions, introduction to the novel concept of transient and event-based formations, problem statement, research objectives and questions, scope and limitations, and an outline of the thesis structure.
*   **Expected Outcome:** A clear and compelling introduction that frames the research problem and provides a roadmap for the reader.

#### **Chapter 2: Theoretical Background and Literature Review**

*   **Key Concepts:**
    *   **Fundamentals of Orbital Mechanics:** The two-body problem, orbital elements, and a detailed treatment of key perturbations in LEO (Earth's gravity harmonics, especially J2, atmospheric drag, solar radiation pressure, third-body effects). Theory of repeating ground tracks.
    *   **Spacecraft Formation Flying Dynamics:** Derivation and application of the Clohessy-Wiltshire (Hill's) equations for relative motion. Introduction to Relative Orbital Elements (ROEs) for describing and controlling formations.
    *   **Formation Control & Station-Keeping:** Overview of control strategies (e.g., impulsive vs. continuous thrust), common controllers (LQR, SDRE), and fuel-optimal maneuver planning.
    *   **Review of Analogue Missions:** In-depth analysis of missions like TanDEM-X, GRACE, CanX-4/5, and MMS, focusing on their formation control strategies, relative navigation techniques, and lessons learned.
*   **Expected Outcome:** A comprehensive theoretical foundation that equips the reader with the necessary knowledge to understand the design and analysis presented in later chapters.

#### **Chapter 3: Mission Design and Simulation Environment**

*   **Key Concepts:**
    *   **Mission Requirements Definition:** Detailed definition of the target (Tehran: latitude, longitude), desired formation geometry (e.g., equilateral triangle with 50 km sides), formation duration (90 seconds), and repetition period (1 sidereal day). Definition of acceptable geometric tolerances.
    *   **Analytical Orbit Design:** Step-by-step derivation of the orbital elements for the three satellites across two planes. This includes the calculation of altitude and period for the repeating ground track, the selection of inclination for target access, and the precise determination of RAAN and mean anomaly for the intersection and phasing.
    *   **Modeling and Simulation Framework:** Description of the software tools used (GMAT, STK, Python). Detailed explanation of the numerical propagator setup, including the force models, atmospheric density models (e.g., NRLMSISE-00), and integration settings.
    *   **Formation Verification Model:** The mathematical algorithm developed to process the simulation output and automatically detect and evaluate the quality of the formation events based on the predefined requirements.
*   **Expected Outcome:** A complete and repeatable description of the "how" – how the mission was designed and how the simulation was built.

#### **Chapter 4: Simulation Results**

*   **Key Concepts:** This chapter presents the raw data and findings from the simulation campaign.
    *   **Presentation of Candidate Scenarios:** Detailing the orbital parameters for several competing design options (e.g., different altitudes, inclinations).
    *   **Nominal Simulation Results (No Perturbations):** Visualization of the ground tracks, confirmation of the formation event timing and geometry in an idealized environment.
    *   **High-Fidelity Simulation Results (With Perturbations):** Analysis of the formation's natural decay. Plots showing the drift in relative positions and the degradation of the triangle's geometry over days and weeks.
    *   **Station-Keeping Performance:** Results of applying the conceptual control strategy. Plots showing the corrected trajectories and the sequence of ΔV maneuvers. Presentation of the final ΔV budget for each scenario.
*   **Expected Outcome:** A data-rich chapter filled with plots, graphs, and tables that objectively present the results of all simulations.

#### **Chapter 5: Analysis and Discussion**

*   **Key Concepts:** This chapter interprets the results from Chapter 4 and discusses their implications.
    *   **Comparison of Design Scenarios:** A trade-off analysis comparing the candidate scenarios against Key Performance Indicators (KPIs) like formation accuracy, revisit time, and total ΔV cost.
    *   **Sensitivity Analysis:** Discussion of how sensitive the final design is to initial conditions or modeling assumptions (e.g., variations in atmospheric density).
    *   **Discussion of Feasibility:** A critical discussion on the overall viability of the mission concept. Is the ΔV budget realistic for a small satellite? What are the primary technological and operational challenges?
    *   **Revisiting Research Questions:** An explicit section that answers each of the research questions posed in Chapter 1, using evidence from the simulation results.
*   **Expected Outcome:** A chapter that transforms raw data into knowledge, providing a deep understanding of the design trade-offs and the overall feasibility of the proposed mission.

#### **Chapter 6: Conclusion and Future Work**

*   **Key Concepts:**
    *   **Conclusion:** A concise summary of the entire research effort, including the problem, methodology, key findings, and the final recommended orbital design.
    *   **Summary of Contributions:** A brief restatement of the novel contributions of the thesis to the field.
    *   **Recommendations for Future Work:** A detailed list of potential extensions to this research, such as:
        *   Development of a high-fidelity, autonomous GNC algorithm for formation maintenance.
        *   Integrated simulation of attitude control and orbit control.
        *   Hardware-in-the-loop testing of the GNC system.
        *   Analysis of potential scientific or commercial applications for this mission concept.
        *   Mission cost and risk analysis.
*   **Expected Outcome:** A strong concluding chapter that summarizes the work and provides a clear path forward for future research in this area.