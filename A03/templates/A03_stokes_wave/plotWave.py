#!/usr/bin/env python3
"""plotWave.py: compares the periodic Stokes wave of A03_stokes_wave with
Stokes fifth-order theory (Stokes V, the reference), Stokes third-order theory
and linear (Airy) theory, all for the wave height H and wavelength lambda of
the case (the theories are in stokesV.py).

Run it in the case folder after bash Allrun (no OpenFOAM needed):
    python plotWave.py
or give the case folder:  python plotWave.py runs/gci/nx100
It prints a table of CFD against the three theories and saves, in the case folder,
    wave_surface.png   eta(x) at t = 0 and at the end of the run
    wave_history.png   crest position, wave height and harmonics against time
The last lines it prints (key = value) are the results of the run, for your
scripts (e.g. python plotWave.py > log.plotWave).
"""
import re
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parent))
from stokesV import Wave, read_parameters    # noqa: E402  (stokesV.py, next to this file)

case = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
fmt = sys.argv[2] if len(sys.argv) > 2 else "png"   # figure format: png or pdf
g = 9.81


# ----------------------------------------------------------------------------
# Parameters of the case (from the file parameters) and the three theories
# ----------------------------------------------------------------------------
P = read_parameters(case / "parameters")
lam, H0, d, dy = P["lambda"], P["H"], P["d"], P["dy"]
V = Wave(H0, lam, d, 5)                       # Stokes V: the reference
S3 = Wave(H0, lam, d, 3)                      # Stokes III
L1 = Wave(H0, lam, d, 1)                      # Airy (linear)
theories = ((V, "Stokes V", "C0--"), (S3, "Stokes III", "C2-."), (L1, "Airy", "C3:"))
k, T = V.k, V.T                               # the run uses the Stokes V period


# ----------------------------------------------------------------------------
# CFD free surface: points of alpha.water = 0.5, written 40 times per period
# ----------------------------------------------------------------------------
folders = sorted((case / "postProcessing/freeSurface").iterdir(), key=lambda d: float(d.name))
x = np.arange(256) * lam / 256                # uniform grid for the analysis
t, eta = [], []
for folder in folders:
    pts = np.loadtxt(next(folder.glob("*.raw")), ndmin=2)
    pts = pts[pts[:, 1] <= 0.5 * dy + 1e-9]       # one plane (front or mid-plane) only
    xs, i = np.unique(pts[:, 0], return_index=True)
    eta.append(np.interp(x, xs, pts[i, 2], period=lam))
    t.append(float(folder.name))
t, eta = np.array(t), np.array(eta)

# Harmonics of eta(x) at each time: eta = sum_n A_n cos(n k x + phi_n)
coef = np.fft.rfft(eta, axis=1) / len(x)
A = 2 * np.abs(coef)
phase = np.unwrap(np.angle(coef[:, 1]))       # = -omega t for a wave in +x
x_crest = -phase / k                          # distance travelled by the crest
c_CFD = np.polyfit(t, x_crest, 1)[0]          # phase speed: slope of x_crest(t)
crest, trough = eta.max(1), eta.min(1)
H = crest - trough
last = t >= t[-1] - T                         # the last period
crest_end, trough_end, H_end = crest[last].mean(), trough[last].mean(), H[last].mean()


# ----------------------------------------------------------------------------
# Table
# ----------------------------------------------------------------------------
def row(name, cfd, theory, unit, scale=1):
    """CFD and, for each theory, its value and the error of the CFD against it."""
    cols = "".join(f" {th*scale:9.4f} " + (f"{100*(cfd - th)/abs(th):+7.2f}%" if th else f"{'--':>8s}")
                   for th in theory)
    print(f"{name:32s} {cfd*scale:9.4f}{cols}   {unit}")


print(f"Case {case.resolve().name}: lambda = {lam} m, H = {H0:.2f} m (H/lambda = {H0/lam:.3f}), "
      f"d = {d} m (kd = {k*d:.3f}), T = {T:.4f} s, initial wave {P['initialWave']}")
print(f"Stokes V: eps = {V.eps:.4f}; first-harmonic amplitude A1 = {V.A[0]:.3f} m (k A1 = {k*V.A[0]:.3f})")
print(f"Run of {t[-1]/T:.1f} periods; mesh nx = {P['nx']:.0f}, dz = {2*P['zBand']/P['nzBand']:.3f} m, maxCo = {P['maxCo']}")
print()
print(f"{'quantity':32s} {'CFD':>9s}" + "".join(f" {n:>9s} {'error':>8s}" for _, n, _ in theories))
row("phase speed c", c_CFD, [W.c for W, _, _ in theories], "m/s")
row("crest elevation (last period)", crest_end, [W.crest for W, _, _ in theories], "m")
row("trough elevation (last period)", trough_end, [W.trough for W, _, _ in theories], "m")
row("wave height H (last period)", H_end, [W.crest - W.trough for W, _, _ in theories], "m")
for n in range(1, 6):
    row(f"harmonic A{n} of eta (last period)", A[last, n].mean(), [W.A[n - 1] for W, _, _ in theories], "m")
print()
print("Results (key = value):")
for key, val in (("c", c_CFD), ("c_V", V.c), ("c_III", S3.c), ("c_Airy", L1.c), ("H_end", H_end), ("H_0", H[0]),
                 ("crest_end", crest_end), ("trough_end", trough_end)):
    print(f"{key} = {val:.6g}")


# ----------------------------------------------------------------------------
# Figures
# ----------------------------------------------------------------------------
plt.rcParams.update({"font.size": 9, "savefig.bbox": "tight", "savefig.dpi": 150})
legend_out = dict(loc="center left", bbox_to_anchor=(1.01, 0.5), frameon=False)
xf = np.linspace(0, lam, 400)


def label(ax, s):
    ax.text(0, 1.02, f"({s})", transform=ax.transAxes, fontweight="bold", va="bottom")  # above the corner


fig, axs = plt.subplots(2, 1, figsize=(7, 5), sharex=True)
for ax, i, s in ((axs[0], 0, "a"), (axs[1], len(t) - 1, "b")):
    ax.plot(x, eta[i], "k-", lw=2, label="CFD")
    for W, name, st in theories:
        ax.plot(xf, W.eta(xf, t[i]), st, lw=1.2, label=name)
    ax.axhline(0, color="0.7", lw=0.5)
    ax.set_ylabel(r"$\eta$ [m]")
    ax.set_title(f"$t = {t[i]:.3f}$ s $= {t[i]/T:.1f}\\,T$", fontsize=9)
    label(ax, s)
axs[0].legend(**legend_out)
axs[1].set_xlabel(r"$x$ [m]")
fig.tight_layout()
fig.savefig(case / f"wave_surface.{fmt}")

fig, axs = plt.subplots(3, 1, figsize=(7, 7), sharex=True)
ax = axs[0]
ax.plot(t / T, x_crest - V.c * t, "k-", lw=2, label="CFD")
for W, name, st in theories:
    ax.plot(t / T, (W.c - V.c) * t, st, lw=1.2, label=name)
ax.set_ylabel(r"$x_\mathrm{crest} - c_\mathrm{V}\,t$ [m]")
ax.legend(**legend_out)
label(ax, "a")
ax = axs[1]
ax.plot(t / T, H / H0, "k-", lw=2, label="CFD")
ax.axhline(1, color="C0", ls="--", label="theory")
ax.set_ylabel(r"$H/H_0$ [–]")
ax.legend(**legend_out)
label(ax, "b")
ax = axs[2]
for n, c in ((1, "C0"), (2, "C1"), (3, "C2"), (4, "C4")):
    ax.plot(t / T, A[:, n] / V.A[n - 1], color=c, label=f"$A_{n}$")
ax.axhline(1, color="0.5", ls="--", lw=0.8)
ax.set_ylabel(r"$A_n/A_{n,\mathrm{V}}$ [–]")
ax.set_xlabel(r"$t/T$ [–]")
ax.legend(**legend_out)
label(ax, "c")
fig.tight_layout()
fig.savefig(case / f"wave_history.{fmt}")

print("Figures: wave_surface.png, wave_history.png")
