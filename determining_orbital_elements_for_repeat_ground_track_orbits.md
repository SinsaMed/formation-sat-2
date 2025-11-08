# Determining orbital elements for Earth‑Observation Repeat‑Ground‑Track orbits

**P. Torabi¹*** and **A. Naghash²**  
1, 2. Department of Aerospace Engineering, Amirkabir University of Technology  
*Postal Code: 1591634311, Tehran, IRAN*  
*peyman.torabi@aut.ac.ir*

**Journal of Space Science & Technology (JSST)**  
Vol. 9 / No. 2 / 2016  
*Received: 2014‑10‑04; Accepted: 2017‑01‑25*

---

## Abstract
This paper presents a new methodology for a quick and efficient numerical determination of the condition for repeat ground tracks to be employed in an orbital optimization design methodology. This methodology employs the simplicity and reliability of the epicyclical motion condition for a repeat ground track to find a semi‑major axis for a given repetition cycle and inclination. Then the semi‑major axis is refined for application to any elliptical motion. This methodology was discovered by comparing two recent methods in addition to a new proposed method offered in this paper investigating both nonlinear algebraic and polynomial formulations of the governing repeat‑ground‑track condition relationship. A lesser known simplified method is used for preliminary solution refinement. The advantages and disadvantages of each approach are weighed with each method's reliability, performance, and computational ease based on a case study. From these criteria, one method is recommended for use in repeat‑ground‑track orbit design optimization methodology.

**Keywords:** Orbital mechanics; satellite orbit design; repeating ground track

---

## Nomenclature

| Symbol | Description |
| :--- | :--- |
| $T_r$ | Repeat period |
| $T_\Omega$ | Nodal period of the satellite |
| $T_{\Omega G}$ | Greenwich (sidereal) period |
| $N_p$ | Number of satellite revolutions in one repeat period |
| $N_d$ | Number of sidereal days during the repeat period |
| $\omega$ | Argument of perigee |
| $\Omega$ | Longitude of ascending node |
| $M$ | Mean anomaly |
| $n$ | Mean motion |
| $T$ | Anomalistic period |
| $e$ | Eccentricity |
| $a$ | Semi‑major axis |
| $p$ | Semi‑latus rectum, $p=a(1-e^2)$ |
| $h_p$ | Perigee altitude above mean Earth radius |
| $R_E$ | Mean equatorial Earth radius |
| $\mu$ | Earth gravitational parameter |
| $\omega_E$ | Earth rotation rate (Greenwich) |
| $i$ | Inclination |
| $J_2, J_4$ | Zonal harmonics of the geopotential |
| $\tau$ | Repetition ratio $\tau=\dfrac{N_d}{N_p}$ |

---

## 1. Introduction
Orbits with repeating ground‑track capability are those whose ground track repeats after a specific period. This class of orbits is ideal for many Earth‑observation satellites because a specific region (or regions) of the Earth can be monitored/sensed periodically. The goal is to determine the orbital parameters for satellites with such missions so that the ground track repeats in the presence of perturbations.

---

## 2. Conditions for a repeating ground track

The repeat period satisfies

$$\boxed{\;T_r= N_p\,T_\Omega = N_d\,T_{\Omega G}\;}\tag{1}$$

The nodal period (with secular precessions folded into $M$ and $\omega$) is

$$T_\Omega=\frac{2\pi}{\dot M+\dot\omega}.\tag{2}$$

The mean anomaly and mean motion relations are

$$M(t)=M_0+nt,\tag{3}$$
$$\dot M=\dot M_0+n,\tag{4}$$
$$T=\frac{2\pi}{n}.\tag{5}$$

Combining (2) and (5),

$$T_\Omega=\frac{2\pi}{n}\left(1+\frac{\dot M+\dot\omega}{n}\right)^{-1}.\tag{6}$$

The Greenwich period is

$$T_{\Omega G}=\frac{2\pi}{\omega_E-\dot\Omega}.\tag{7}$$

---

## 3. Flower Constellation (FC) method

Under the $J_2$–only secular model, the rates are

$$\dot\omega\;=\;\frac{3nR_E^2J_2}{4p^2}\left(4-5\sin^2 i\right),\tag{9}$$
$$\dot\Omega\;=\;-\,\frac{3nR_E^2J_2}{2p^2}\cos i,\tag{10}$$
$$\dot M\;=\;-\,\frac{3nR_E^2J_2\sqrt{1-e^2}}{4p^2}\left(3\sin^2 i-2\right).\tag{11}$$

Standard geometric/orbital relations:

$$1-e\;=\;\frac{R_E+h_p}{a},\tag{12}$$
$$p\;=\;a(1-e^2),\tag{13}$$
$$n\;=\sqrt{\frac{\mu}{a^3}}.\tag{14}$$

Using (9)–(14), the repeat‑condition can be written as

$$\boxed{\;\tau\;=\;\frac{\omega_E-2A(a)\cos i}{\sqrt{\mu/a^3}\;+\;A(a)\Big[\,\big(1-\tfrac{R_E+h_p}{a}\big)(2-3\sin^2 i)\;+(4-5\sin^2 i)\Big]}\;,}\tag{15}$$

with

$$A(a)=\frac{3R_E^2J_2}{4}\,\frac{\sqrt{\mu/a^3}}{\,(R_E+h_p)-\dfrac{(R_E+h_p)^2}{a}\,}.\tag{15a}$$

> **Polynomial form.** Relation (15) can be recast as a polynomial in a normalized variable $x(a)$ with inclination‑dependent coefficients. (See Eq. (16) in the source.)

\[\textit{Eq. (16) — polynomial form omitted here pending faithful typesetting from the source.}\]

---

## 4. Modified method (adding $J_4$ and higher‑order $J_2$ terms)

In the modified method, additional zonal‑harmonic terms (notably $J_4$ as well as second‑order $J_2^2$ contributions) are included in $\dot\omega,\dot\Omega,\dot M$. The full expressions (Eqs. (17)–(19)) are lengthy.

\[\textit{Eqs. (17)–(19) — full $J_2,J_2^2,J_4$ secular rates omitted here pending faithful typesetting from the source.}\]

This leads to an improved polynomial repeat‑condition with coefficients depending on combinations
$\beta,\gamma,\delta,\ldots$ (see Eq. (20) definitions).

\[\textit{Eq. (20) — full polynomial form omitted here pending faithful typesetting from the source; coefficient definitions included below.}\]

**Coefficient definitions used in the modified polynomial (Eq. (20))**

- $\displaystyle \beta=\tfrac{3}{1536}\,J_4 R_E^4,\qquad \gamma=\tfrac{15}{128}\,J_4 R_E^4,\qquad \delta=\tfrac{3}{4}\,J_2 R_E^2.$
- $x(a)$, $y(a)$, $\phi,\,\omega,\,\ldots$ are inclination‑dependent combinations (e.g., terms like $\sin^2 i,\cos i$) and multiples of $\tau,\mu$; see the source for the exact forms.
- Auxiliary angle functions (examples): $d(i)=48\cos i-54\sin^2 i,\; b(i)=48\cos i-12\,\ldots$ *(exact forms to be transcribed from the source).*

> **Note.** For rigorous reproduction, these long expressions should be typeset from a clearer copy of the source to avoid OCR ambiguities.

---

## 5. Sample analysis and evaluation

For a given $\tau$ and inclination, the FC polynomial is used to obtain an initial $a$, which is then refined using the modified method that includes $J_4$ and $J_2^2$ terms.

To quantify the repeat‑ground‑track condition, the error function

$$\boxed{\;f\;=\;\tau\; -\; \frac{\omega_E-\dot\Omega}{n+\dot M+\dot\omega}\;}\tag{21}$$

is used (ideal case: $f=0$).

*Illustrative results reported in the source show that for cases such as $\tau=\tfrac12, \tfrac14,$ and $\tfrac1{16}$, the modified method removes the $i=90^\circ$ singularity seen with FC and reduces the repeat‑error from $\mathcal{O}(10^{-3})$ to $\mathcal{O}(10^{-7}\text{–}10^{-8})$.*

---

## 6. Conclusion
A two‑step approach is effective for RGT orbit design: (i) solve the FC‑based polynomial to get a fast initial semi‑major axis; (ii) refine using the modified model including $J_4$ and higher‑order $J_2$ effects. This yields higher accuracy while remaining computationally efficient.

---

## References
[1] Vallado, D., *Fundamentals of Astrodynamics and Applications*, 2nd ed., 2001, pp. 623, 646–649.  
[2] Mortari, D., Wilkins, M., and Bruccoleri, C., “The Flower Constellations,” *J. Astronautical Sciences*, Vol. 52, Nos. 1–2, 2004, pp. 107–127.  
[3] Aorpimai, M., and Palmer, P., “Repeat‑Groundtrack Orbit Acquisition and Maintenance for Earth‑Observation Satellites,” *J. Guidance, Control, and Dynamics*, Vol. 30, No. 3, 2007, pp. 654–659.  
[4] Vtipil, S., and Newman, B., “Determining an Efficient Repeat Ground Track Method for Earth Observation Satellites: For Use in Optimization Algorithms,” *AIAA Paper 2010‑8266*, Aug. 2010.  
[5] Collins, S. K., *Computationally Efficient Modelling for Long‑Term Prediction of GPS Orbits*, M.Sc. Thesis, MIT, 1977.

