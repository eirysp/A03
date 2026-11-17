
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
