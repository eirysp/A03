#!/usr/bin/env python3
"""stokesV.py: the regular wave of A03_stokes_wave from Stokes wave theory.

Allrun runs it (python stokesV.py) before blockMesh. It reads lambda, d, H and
initialWave from the file parameters and writes the file waveCoeffs (included
by parameters): the wave period T and the coefficients of the initial wave
used by system/setExprFieldsDict. plotWave.py imports it for the theory.

The theory is the fifth-order Stokes wave of Skjelbreia & Hendrickson (1961),
with the same coefficients and formulas as OpenFOAM's StokesV wave model
($FOAM_SRC/waveModels/waveGenerationModels/derived/StokesV), which makes the
waves of A03_beach. With eps the perturbation parameter (k times the
first-harmonic amplitude), theta = k x - omega t and zb = z + d the height
above the bed:
    k eta = eps cos(theta) + (B22 eps^2 + B24 eps^4) cos(2 theta)
          + (B33 eps^3 + B35 eps^5) cos(3 theta)
          + B44 eps^4 cos(4 theta) + B55 eps^5 cos(5 theta)
    u = sum_n U_n cosh(n k zb) cos(n theta),  w = sum_n U_n sinh(n k zb) sin(n theta)
    U_1 = c (eps A11 + eps^3 A13 + eps^5 A15),   U_2 = 2 c (eps^2 A22 + eps^4 A24),
    U_3 = 3 c (eps^3 A33 + eps^5 A35),   U_4 = 4 c eps^4 A44,   U_5 = 5 c eps^5 A55
    H = (2/k) (eps + B33 eps^3 + (B35 + B55) eps^5)     (crest to trough)
    omega^2 = g k tanh(kd) (1 + C1 eps^2 + C2 eps^4),   c = omega/k
The coefficients A, B, C depend on kd only. Stokes III is the same theory
without the eps^4 and eps^5 terms; Airy (linear) theory keeps only eps.

In the periodic domain the wavelength is fixed (lambda = the domain length),
so the wave is set by its height H: eps follows from H, then omega and T from
the dispersion relation. (The wavemaker of A03_beach is given H and T and
finds the wavelength: the same wave.)
"""
import math
import re
import sys
from pathlib import Path

g = 9.81


def coefficients(kd):
    """Coefficients of the Stokes V wave (as in StokesVWaveModel.C) for depth kd."""
    s, c = math.sinh(kd), math.cosh(kd)
    d1 = 6 * c**2 - 1
    d2 = 8 * c**4 - 11 * c**2 + 3
    return dict(
        A11=1 / s,
        A13=-c**2 * (5 * c**2 + 1) / (8 * s**5),
        A15=-(1184 * c**10 - 1440 * c**8 - 1992 * c**6 + 2641 * c**4 - 249 * c**2 + 18) / (1536 * s**11),
        A22=3 / (8 * s**4),
        A24=(192 * c**8 - 424 * c**6 - 312 * c**4 + 480 * c**2 - 17) / (768 * s**10),
        A33=(13 - 4 * c**2) / (64 * s**7),
        A35=(512 * c**12 + 4224 * c**10 - 6800 * c**8 - 12808 * c**6 + 16704 * c**4 - 3154 * c**2 + 107)
        / (4096 * s**13 * d1),
        A44=(80 * c**6 - 816 * c**4 + 1338 * c**2 - 197) / (1536 * s**10 * d1),
        A55=-(2880 * c**10 - 72480 * c**8 + 324000 * c**6 - 432000 * c**4 + 163470 * c**2 - 16245)
        / (61440 * s**11 * d1 * d2),
        B22=(2 * c**2 + 1) * c / (4 * s**3),
        B24=(272 * c**8 - 504 * c**6 - 192 * c**4 + 322 * c**2 + 21) * c / (384 * s**9),
        B33=(8 * c**6 + 1) * 3 / (64 * s**6),
        B35=(88128 * c**14 - 208224 * c**12 + 70848 * c**10 + 54000 * c**8 - 21816 * c**6 + 6264 * c**4
             - 54 * c**2 - 81) / (12288 * s**12 * d1),
        B44=(768 * c**10 - 448 * c**8 - 48 * c**6 + 48 * c**4 + 106 * c**2 - 21) * c / (384 * s**9 * d1),
        B55=(192000 * c**16 - 262720 * c**14 + 83680 * c**12 + 20160 * c**10 - 7280 * c**8 + 7160 * c**6
             - 1800 * c**4 - 1050 * c**2 + 225) / (12288 * s**10 * d1 * d2),
        C1=(8 * c**4 - 8 * c**2 + 9) / (8 * s**4),
        C2=(3840 * c**12 - 4096 * c**10 + 2592 * c**8 - 1008 * c**6 + 5944 * c**4 - 1830 * c**2 + 147)
        / (512 * s**10 * d1),
    )


class Wave:
    """Stokes wave of height H and wavelength lam in depth d, to order 5 (Stokes V),
    3 (Stokes III) or 1 (Airy). Crest at x = 0 at t = 0, travelling in +x."""

    def __init__(self, H, lam, d, order=5):
        self.H, self.lam, self.d, self.order = H, lam, d, order
        self.k = k = 2 * math.pi / lam
        C = self.coef = coefficients(k * d)
        o5 = order >= 5                      # keep the eps^4 and eps^5 terms
        o3 = order >= 3                      # keep the eps^2 and eps^3 terms

        def height(e):
            return 2 / k * (e + o3 * C["B33"] * e**3 + o5 * (C["B35"] + C["B55"]) * e**5)

        lo, hi = 0.0, 0.6                    # eps from H by bisection
        for _ in range(100):
            mid = 0.5 * (lo + hi)
            lo, hi = (mid, hi) if height(mid) < H else (lo, mid)
        self.eps = e = 0.5 * (lo + hi)
        self.omega = math.sqrt(g * k * math.tanh(k * d) * (1 + o3 * C["C1"] * e**2 + o5 * C["C2"] * e**4))
        self.T = 2 * math.pi / self.omega
        self.c = self.omega / k
        # Amplitudes of the harmonics of eta [m] and of the velocity [m/s], n = 1..5
        self.A = [e / k,
                  o3 * (C["B22"] * e**2 + o5 * C["B24"] * e**4) / k,
                  o3 * (C["B33"] * e**3 + o5 * C["B35"] * e**5) / k,
                  o5 * C["B44"] * e**4 / k,
                  o5 * C["B55"] * e**5 / k]
        c = self.c
        self.U = [c * (e * C["A11"] + o3 * C["A13"] * e**3 + o5 * C["A15"] * e**5),
                  2 * c * o3 * (C["A22"] * e**2 + o5 * C["A24"] * e**4),
                  3 * c * o3 * (C["A33"] * e**3 + o5 * C["A35"] * e**5),
                  4 * c * o5 * C["A44"] * e**4,
                  5 * c * o5 * C["A55"] * e**5]
        self.crest = sum(self.A)
        self.trough = sum((-1) ** n * a for n, a in enumerate(self.A, 1))

    def eta(self, x, t=0.0):
        """Free-surface elevation [m] (x, t numbers or numpy arrays)."""
        th = self.k * x - self.omega * t
        return sum(a * _cos(n * th) for n, a in enumerate(self.A, 1))

    def u(self, x, z, t=0.0):
        """Horizontal velocity [m/s] at height z above the still-water level."""
        th, kb = self.k * x - self.omega * t, self.k * (z + self.d)
        return sum(U * _cosh(n * kb) * _cos(n * th) for n, U in enumerate(self.U, 1))

    def w(self, x, z, t=0.0):
        """Vertical velocity [m/s]."""
        th, kb = self.k * x - self.omega * t, self.k * (z + self.d)
        return sum(U * _sinh(n * kb) * _sin(n * th) for n, U in enumerate(self.U, 1))


def _f(name):                                 # math or numpy function, as the argument needs
    def f(x):
        return getattr(math, name)(x) if isinstance(x, (int, float)) else getattr(sys.modules["numpy"], name)(x)
    return f


_cos, _sin, _cosh, _sinh = _f("cos"), _f("sin"), _f("cosh"), _f("sinh")


def read_parameters(path):
    """The plain entries (name value;) of the file parameters."""
    par = {}
    for line in Path(path).read_text().splitlines():
        m = re.match(r"^(\w+)\s+([-+0-9.eE]+|\w+);", line)
        if m:
            try:
                par[m.group(1)] = float(m.group(2))
            except ValueError:
                par[m.group(1)] = m.group(2)
    return par


ORDER = {"StokesV": 5, "StokesIII": 3, "Airy": 1}

if __name__ == "__main__":
    case = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    P = read_parameters(case / "parameters")
    init = P["initialWave"]
    if init not in ORDER:
        sys.exit(f"initialWave {init}: use StokesV, StokesIII or Airy")
    V = Wave(P["H"], P["lambda"], P["d"], 5)
    W = Wave(P["H"], P["lambda"], P["d"], ORDER[init])
    lines = [
        "// Written by stokesV.py (run by Allrun) from parameters: do not edit.",
        f"// Wave of height H = {P['H']} m, wavelength lambda = {P['lambda']} m, depth d = {P['d']} m",
        "",
        f"T           {V.T:.8g};   // period of the Stokes V wave [s]: c = lambda/T = {V.c:.5f} m/s",
        f"epsV        {V.eps:.8g};   // its perturbation parameter (k times the first-harmonic amplitude)",
        "",
        f"// The initial wave, initialWave {init}:",
        "//   eta = sum_n A_n cos(n k x)",
        "//   u = sum_n U_n cosh(n k (z + d)) cos(n k x),  w = sum_n U_n sinh(n k (z + d)) sin(n k x)",
    ]
    lines += [f"A{n}          {a or 0.0:.8g};   // [m]" for n, a in enumerate(W.A, 1)]
    lines += [f"U{n}          {U or 0.0:.8g};   // [m/s]" for n, U in enumerate(W.U, 1)]
    (case / "waveCoeffs").write_text("\n".join(lines) + "\n")
    print(f"Stokes V wave: H = {V.H} m, lambda = {V.lam} m, d = {V.d} m, kd = {V.k*V.d:.4f}, "
          f"eps = {V.eps:.5f}, H/lambda = {V.H/V.lam:.4f}, T = {V.T:.6f} s, c = {V.c:.5f} m/s")
    print(f"initialWave {init}: eta harmonics [m] " + " ".join(f"{a:.5f}" for a in W.A)
          + f"; crest {W.crest:.4f} m, trough {W.trough:.4f} m")
    print("Written: waveCoeffs")
