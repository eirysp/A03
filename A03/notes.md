
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
