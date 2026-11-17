
# A03 notes

## Task 1 — Case 1 original Stokes wave

Run folder: runs/original/stokes_wave
Command: bash Allrun
Student: A
MPI processes: 8
Status: completed successfully
Start date: 17 November 2026
Final simulated time: 27.0149825 s
ExecutionTime: 243.45 s
ClockTime: 253 s
Final progress output: t = 27.01 s
Free-surface output: postProcessing/freeSurface/<time>/

### Task 1(a)(i) — Mesh observations

The smallest cells are concentrated around the curved free-surface region.

The largest cells are at the bottom of the domain.

The mesh is refined through the full vertical region surrounding the free surface, from near the upper interface down towards the lower part of the water domain. The cells become progressively larger away from the free surface, especially near the bed.

### Task 1(a)(ii) — Free-surface observation

The wave retains its shape throughout the animation. The crest remains sharper than the trough, consistent with the nonlinear Stokes-wave shape. The free surface remains smooth, with no visible distortion, smearing, or instability.

### Task 1(a)(iii) — Wave-induced pressure

The wave-induced pressure p_rgh is positive beneath the crest and negative beneath the trough. Its largest values occur near the free surface beneath a crest and it decreases with depth.

The observed colour range was approximately:
- maximum p_rgh: 2.5 × 10^4 Pa
- minimum p_rgh: −1.8 × 10^4 Pa

At the still-water level, z = 0, p_rgh was approximately zero in the observed region. The pressure field changed sign between crest and trough regions.

### Task 1(a)(iv) — Water velocity

The velocity magnitude is highest near the free surface, especially just below the crest. It decreases with depth. The velocity magnitude immediately below the free surface near the trough is relatively small.

The minimum displayed velocity magnitude was approximately 6.6 × 10^-2 m/s. Since this is the magnitude, it is positive everywhere and does not indicate flow direction.

The horizontal velocity component Ux is positive beneath the crest, indicating flow in the +x direction. Beneath the trough, U_x is negative, indicating flow in the -x direction. This is consistent with the wave-particle motion as the wave propagates in the +x direction.

### Task 1(b) — ParaView animation

The animation was created in ParaView using the alpha.water field and saved as:

runs/original/stokes_wave/stokes_wave_alpha_from_paraview.avi

The reusable ParaView trace was saved as:

scripts/animate.py

### Task 1(c) — CFD and theory comparison

Case parameters:
- lambda = 50.0 m
- H = 5.00 m
- d = 25.0 m
- kd = 3.142
- CFD period T = 5.4030 s
- mesh: nx = 100, dz = 0.250 m
- maxCo = 0.1
- run duration: 5 periods

| Quantity | CFD | Stokes V | Stokes III | Airy |
|---|---:|---:|---:|---:|
| Phase speed c (m/s) | 9.2640 | 9.2541 | 9.2190 | 8.8190 |
| Crest elevation (m) | 2.8523 | 2.9322 | 2.8719 | 2.5000 |
| Trough elevation (m) | -2.0384 | -2.0678 | -2.1281 | -2.5000 |
| Wave height H (m) | 4.8907 | 5.0000 | 5.0000 | 5.0000 |
| A1 (m) | 2.3509 | 2.3873 | 2.4147 | 2.5000 |
| A2 (m) | 0.3871 | 0.4100 | 0.3719 | 0 |
| A3 (m) | 0.0897 | 0.1062 | 0.0853 | 0 |
| A4 (m) | 0.0337 | 0.0221 | 0 | 0 |
| A5 (m) | 0.0137 | 0.0065 | 0 | 0 |

Key values:
- c = 9.26402 m/s
- c_V = 9.25412 m/s
- c_III = 9.21900 m/s
- c_Airy = 8.81898 m/s
- H_end = 4.89073 m
- H_0 = 4.99405 m
- crest_end = 2.85228 m
- trough_end = -2.03845 m

Initial-to-final wave-height change:
- H_0 - H_end = 0.10332 m
- percentage decrease = approximately 2.07%

Initial observation:
- The CFD phase speed is closest to Stokes V.
- Airy theory underestimates the phase speed by approximately 5.05%.
- The CFD crest is higher and sharper than the Airy crest.
- The CFD trough is shallower than the Airy trough.
- The non-zero A2-A5 harmonics show the nonlinear wave shape that Airy theory cannot represent.

### Task 1(d) — Features not reproduced by Airy theory

Airy theory fails to reproduce the nonlinear asymmetry of the CFD wave. The CFD has a sharper, higher crest and a flatter, shallower trough, whereas Airy theory produces a sinusoidal wave with equal-magnitude crest and trough elevations.

Airy theory contains only the first harmonic, so it cannot represent the higher-harmonic contributions that produce the nonlinear wave shape. In the CFD results, the harmonic amplitudes were:

- A1 = 2.3509 m
- A2 = 0.3871 m
- A3 = 0.0897 m
- A4 = 0.0337 m
- A5 = 0.0137 m

The non-zero second-, third-, fourth- and fifth-harmonic amplitudes sharpen the crest and modify the trough. Airy theory predicts A2 = A3 = A4 = A5 = 0.

At the end of the simulation, the CFD crest elevation was 2.8523 m and the trough elevation was -2.0384 m. Airy theory predicted a crest of 2.5000 m and a trough of -2.5000 m. Therefore, Airy theory underestimates the crest elevation and predicts a trough that is too deep.

Airy theory also predicts an incorrect phase speed. The CFD phase speed was 9.2640 m/s, while the Airy phase speed was 8.8190 m/s. The Airy wave therefore travels more slowly and increasingly lags behind the CFD wave.

At t = 27.015 s, the phase-speed difference was approximately:

c_CFD - c_Airy = 9.2640 - 8.8190 = 0.445 m/s

The accumulated phase lag was approximately:

(0.445)(27.015) = 12.0 m

This explains the negative gradient of the Airy curve in the x_crest - c_V t plot and its large displacement from the CFD curve in the final free-surface comparison. The displacement is accumulated phase error caused by the lower Airy phase speed, not a numerical delay in the CFD.

Overall, Airy theory does not reproduce the nonlinear crest and trough shape, the higher harmonics, or the correct phase speed. Stokes V gives the closest comparison with the CFD.

### Task 1(c) — Harmonic history

The harmonic amplitudes are not all steady during the simulation. A1 remains approximately constant and A2 shows relatively small variation. A3 varies more noticeably, while A4 has a small mean magnitude compared with A1 but shows strong fluctuations.

The wave-history figure plots A1 to A4 only; A5 is not included in this figure. However, the final-value table from plotWave.py gives A5 = 0.0137 m. This is much smaller than A1 = 2.3509 m, so the fifth harmonic makes only a small contribution to the overall wave shape.

The wave height also changes slightly during the run, decreasing from H0 = 4.99405 m initially to Hend = 4.89073 m at the end. The fluctuations in the higher harmonics and the small reduction in wave height indicate some numerical evolution of the initially prescribed wave during propagation.
