#!/usr/bin/env python3
"""plotBeach.py: wave height and phase speed along the beach of A03_beach,
against linear (Airy) shoaling theory.

Run it in the case folder after bash Allrun (no OpenFOAM needed):
    python plotBeach.py
or give the case folder:  python plotBeach.py runs/slope/slope_0.05
The CFD results are taken over the last nAvg wave periods of the run (see
below), once the waves have reached the end of the flume. The wave breaks where
its height starts to fall (see "Breaking point" below). It prints a table
and saves, in the case folder,
    beach.png     (a) snapshots and envelope of eta, (b) wave height H(x),
                  (c) phase speed c(x), CFD and linear theory
    beach.csv     x, d, H and c from the CFD and the linear theory
The last lines it prints (key = value) are the results of the run, for your
scripts (e.g. python plotBeach.py > log.plotBeach).
"""
import re
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

case = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
fmt = sys.argv[2] if len(sys.argv) > 2 else "png"   # figure format: png or pdf
nAvg = 5            # periods over which H and c are averaged (the last ones)
xRef = (50.0, 75.0)  # the CFD wave height over this range is the reference H1
g = 9.81


# ----------------------------------------------------------------------------
# Parameters of the case and the bed
# ----------------------------------------------------------------------------
def read_parameters(path):
    par = {}
    for line in path.read_text().splitlines():
        m = re.match(r"^(\w+)\s+([-+0-9.eE]+);", line)
        if m:
            par[m.group(1)] = float(m.group(2))
    return par


P = read_parameters(case / "parameters")
H_target, Hpaddle = P["H"], P["Hpaddle"]   # wanted over the flat bed / input to the wavemaker
T, d0, dy = P["T"], P["d"], P["dy"]
xFlat = (50.0, P["xToe"])                   # the flat bed away from the wavemaker
xToe, slope, dShelf, lShelf = P["xToe"], P["slope"], P["dShelf"], P["lShelf"]
xShelf = xToe + (d0 - dShelf) / slope
xEnd = xShelf + lShelf
omega = 2 * np.pi / T                                   # its frequency


def depth(x):
    return np.clip(d0 - slope * (x - xToe), dShelf, d0)


# ----------------------------------------------------------------------------
# Linear theory: dispersion relation omega^2 = g k tanh(kd), shoaling H ~ cg^-1/2
# ----------------------------------------------------------------------------
def wavenumber(d):
    kk = np.maximum(omega**2 / g, omega / np.sqrt(g * d))   # deep / shallow start
    for _ in range(50):                                      # Newton iterations
        f = g * kk * np.tanh(kk * d) - omega**2
        df = g * np.tanh(kk * d) + g * kk * d / np.cosh(kk * d) ** 2
        kk = kk - f / df
    return kk


lam = 2 * np.pi / wavenumber(d0)                        # linear wavelength at the wavemaker


def linear(x):
    dd = depth(x)
    kk = wavenumber(dd)
    c = omega / kk
    cg = 0.5 * c * (1 + 2 * kk * dd / np.sinh(2 * kk * dd))
    return kk, c, cg


# ----------------------------------------------------------------------------
# CFD free surface: points of alpha.water = 0.5, written 40 times per period.
# Where the wave overturns there are several points at one x: take the highest.
# ----------------------------------------------------------------------------
folders = sorted((case / "postProcessing/freeSurface").iterdir(), key=lambda d: float(d.name))
times = np.array([float(d.name) for d in folders])
use = times >= times[-1] - nAvg * T - 1e-9
bin = 0.25                                              # bins of 0.25 m (dx/2)
x = np.arange(0.5 * bin, xEnd, bin)
t, eta = [], []
for d, u in zip(folders, use):
    if not u:
        continue
    pts = np.loadtxt(next(d.glob("*.raw")), ndmin=2)
    pts = pts[pts[:, 1] <= 0.5 * dy + 1e-9]       # one plane (front or mid-plane) only
    ib = np.floor(pts[:, 0] / bin).astype(int)
    e = np.full(len(x), -np.inf)
    np.maximum.at(e, np.clip(ib, 0, len(x) - 1), pts[:, 2])
    ok = np.isfinite(e)
    eta.append(np.interp(x, x[ok], e[ok]))
    t.append(float(d.name))
t, eta = np.array(t), np.array(eta)
if t[-1] - t[0] < nAvg * T * 0.95:
    sys.exit("The run is shorter than nAvg periods: run it for longer")

# Wave height: mean over the periods of (highest - lowest eta) in each period
per = np.floor((t - t[0]) / T + 1e-9).astype(int)
H = np.mean([eta[per == n].max(0) - eta[per == n].min(0) for n in range(nAvg)], axis=0)
crest = np.mean([eta[per == n].max(0) for n in range(nAvg)], axis=0)
trough = np.mean([eta[per == n].min(0) for n in range(nAvg)], axis=0)
setup = eta.mean(0)                                     # mean water level

# Phase speed from the phase of the first harmonic: eta ~ cos(k x - omega t),
# so the phase of sum(eta e^{i omega t}) is k x and c = omega / (d phase / dx)
phase = np.unwrap(np.angle(np.sum(eta * np.exp(1j * omega * t)[:, None], axis=0)))
half = 10                                               # fit over +-2.5 m
k_cfd = np.full(len(x), np.nan)
for i in range(half, len(x) - half):
    k_cfd[i] = np.polyfit(x[i - half:i + half + 1], phase[i - half:i + half + 1], 1)[0]
c_cfd = omega / k_cfd

# Theory, with the reference height H1 of the CFD over xRef
k_th, c_th, cg_th = linear(x)
ref = (x >= xRef[0]) & (x <= xRef[1])
H1 = H[ref].mean()
cg1 = linear(np.array([0.5 * sum(xRef)]))[2][0]
H_th = H1 * np.sqrt(cg1 / cg_th)                       # linear shoaling
c_sw = np.sqrt(g * depth(x))                            # shallow-water limit

# Breaking point: where the wave height starts to fall. Scanning from the toe,
# find the first point where the (smoothed) H has fallen below 90% of its
# largest value so far; the wave breaks at the largest H in the half
# wavelength before that point.
Hs = np.convolve(H, np.ones(11) / 11, mode="same")      # smoothed over +-1.25 m
onslope = np.where((x > xToe) & (x < xEnd))[0]
runmax = np.maximum.accumulate(Hs[onslope])
drop = onslope[np.argmax(Hs[onslope] < 0.9 * runmax)]
before = np.where((x > x[drop] - 0.5 * lam) & (x <= x[drop]))[0]
ib = before[np.argmax(Hs[before])]
x_b, d_b, H_b = x[ib], depth(x[ib]), Hs[ib]
L0 = g * T**2 / (2 * np.pi)                             # linear deep-water wavelength
_, _, cg_deep = linear(np.array([0.0]))
H0 = H1 * np.sqrt(cg1 / (0.5 * g / omega))              # deep-water height (linear)
xi0 = slope / np.sqrt(H0 / L0)                          # Iribarren number

# ----------------------------------------------------------------------------
# Table
# ----------------------------------------------------------------------------
flat = (x >= xFlat[0]) & (x <= xFlat[1])
H_flat, crest_flat, trough_flat = H[flat].mean(), crest[flat].mean(), trough[flat].mean()
c_flat = omega / np.polyfit(x[flat], phase[flat], 1)[0]
print(f"Case {case.resolve().name}: wavemaker input Hpaddle = {Hpaddle:.2f} m, T = {T:.4f} s, "
      f"slope 1:{1/slope:.0f}, toe at x = {xToe} m, shelf (d = {dShelf} m) from x = {xShelf:.2f} m")
print(f"CFD averaged over t = {t[0]:.2f}-{t[-1]:.2f} s ({nAvg} periods); "
      f"reference H1 = {H1:.3f} m over x = {xRef[0]}-{xRef[1]} m")
print(f"Flat bed, x = {xFlat[0]}-{xFlat[1]} m: H = {H_flat:.3f} m (target H = {H_target:.2f} m, "
      f"{100*(H_flat/H_target-1):+.1f}%), crest {crest_flat:.3f} m, trough {trough_flat:.3f} m, "
      f"c = {c_flat:.4f} m/s")
print()
print(f"{'x [m]':>6s} {'d [m]':>6s} {'kd':>6s} {'H CFD':>7s} {'H lin':>7s} {'err':>7s} "
      f"{'c CFD':>6s} {'c lin':>6s} {'err':>7s}  [H in m, c in m/s]")
for xs in sorted([50, 75, 100, 150, 200, 225, 250, 275, 300, 325, x_b]):
    i = np.argmin(abs(x - xs))
    print(f"{x[i]:6.1f} {depth(x[i]):6.2f} {k_th[i]*depth(x[i]):6.2f} {H[i]:7.3f} {H_th[i]:7.3f} "
          f"{100*(H[i]/H_th[i]-1):+6.1f}% {c_cfd[i]:6.3f} {c_th[i]:6.3f} {100*(c_cfd[i]/c_th[i]-1):+6.1f}%"
          + ("   <- breaking" if i == ib else ""))
print()
print(f"Breaking: x_b = {x_b:.2f} m, d_b = {d_b:.2f} m, H_b = {H_b:.3f} m, "
      f"H_b/d_b = {H_b/d_b:.2f}; deep-water H0/L0 = {H0/L0:.4f}, Iribarren number xi0 = {xi0:.2f}")
np.savetxt(case / "beach.csv", np.column_stack([x, depth(x), H, H_th, c_cfd, c_th, crest, trough, setup]),
           delimiter=",", fmt="%.6g", header="x,d,H_CFD,H_linear,c_CFD,c_linear,crest,trough,mean_level",
           comments="")
print()
print("Results (key = value):")
for key, val in (("H_flat", H_flat), ("crest_flat", crest_flat), ("trough_flat", trough_flat),
                 ("c_flat", c_flat), ("H1", H1), ("x_b", x_b), ("d_b", d_b), ("H_b", H_b), ("gamma_b", H_b / d_b),
                 ("H0_L0", H0 / L0), ("xi0", xi0)):
    print(f"{key} = {val:.6g}")

# ----------------------------------------------------------------------------
# Figure
# ----------------------------------------------------------------------------
plt.rcParams.update({"font.size": 9, "savefig.bbox": "tight", "savefig.dpi": 150})
legend_out = dict(loc="center left", bbox_to_anchor=(1.01, 0.5), frameon=False)
fig, axs = plt.subplots(3, 1, figsize=(8, 7.5), sharex=True)


def label(ax, s):
    ax.text(0.01, 0.95, f"({s})", transform=ax.transAxes, fontweight="bold", va="top")


ax = axs[0]
xb = np.linspace(0, xEnd, 400)
ax.fill_between(xb, -depth(xb), -d0 - 1, color="0.8", lw=0)
ax.fill_between(x, trough, crest, color="C0", alpha=0.2, lw=0, label="crest and trough (mean)")
for j, f in enumerate((0, 0.25, 0.5, 0.75)):
    i = np.argmin(abs(t - (t[-1] - f * T)))
    ax.plot(x, eta[i], color="k", lw=0.8, alpha=1 - 0.2 * j, label="$\\eta$, last period" if j == 0 else None)
ax.axvline(x_b, color="C3", ls=":", lw=1, label="breaking")
ax.set_ylabel(r"$z$ [m]")
ax.set_ylim(-d0 - 1, 7.5)
ax.legend(**legend_out)
label(ax, "a")
ax = axs[1]
ax.plot(x, H, "k-", lw=2, label="CFD")
ax.plot(x, H_th, "C0--", label="linear shoaling")
ax.axvline(x_b, color="C3", ls=":", lw=1)
ax.set_ylabel(r"$H$ [m]")
ax.legend(**legend_out)
label(ax, "b")
ax = axs[2]
ax.plot(x, c_cfd, "k-", lw=2, label="CFD")
ax.plot(x, c_th, "C0--", label="linear dispersion")
ax.plot(x, c_sw, "C2:", label=r"$\sqrt{gd}$")
ax.axvline(x_b, color="C3", ls=":", lw=1)
ax.set_ylim(0, 10.5)
ax.set_ylabel(r"$c$ [m/s]")
ax.set_xlabel(r"$x$ [m]")
ax.legend(**legend_out)
label(ax, "c")
fig.tight_layout()
fig.savefig(case / f"beach.{fmt}")
print("Figure: beach.png; table: beach.csv")
