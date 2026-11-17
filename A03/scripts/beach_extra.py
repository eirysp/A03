# beach_extra.py: Task 3(b)-(c) extras for the beach run, from plotBeach.py's output.
#
# Run it from the A03 folder, after plotBeach.py has made beach.csv and log.plot:
#     cd ~/openfoam/A03
#     python scripts/beach_extra.py runs/beach
#
# It reads
#   - <case>/beach.csv : x, d, H_CFD, H_linear, c_CFD, c_linear, ... (plotBeach.py)
#   - <case>/log.plot  : x_b, d_b, H_b (the breaking point found by plotBeach.py)
#   - <case>/parameters: the period T
# and saves results/beach_Hc.png:
#   (a) H(x): CFD and linear shoaling H1 sqrt(cg1/cg);
#   (b) c(x): CFD, linear dispersion, shallow water sqrt(g d) and the
#       solitary-wave estimate sqrt(g (d + H)) with the CFD H(x)  [Task 3(b)]
# It also prints the breaker index against McCowan and Miche [Task 3(c)] and
# writes them to results/breaking.csv.

import csv
import math
import os
import re
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

case = sys.argv[1] if len(sys.argv) > 1 else "runs/beach"
g = 9.81
os.makedirs("results", exist_ok=True)

data = np.genfromtxt(f"{case}/beach.csv", delimiter=",", names=True)
x, d, H, H_lin, c, c_lin = (data[n] for n in ("x", "d", "H_CFD", "H_linear", "c_CFD", "c_linear"))
c_sw = np.sqrt(g * d)                       # shallow-water limit of linear theory
c_sol = np.sqrt(g * (d + H))                # solitary-wave estimate, with the CFD height

res = {}
for line in open(f"{case}/log.plot"):
    m = re.match(r"^(\w+) = ([-+0-9.eE]+)\s*$", line)
    if m:
        res[m.group(1)] = float(m.group(2))
T = None
for line in open(f"{case}/parameters"):
    m = re.match(r"^T\s+([-+0-9.eE]+)\s*;", line)
    if m:
        T = float(m.group(1))
x_b, d_b, H_b = res["x_b"], res["d_b"], res["H_b"]

# linear wavenumber at the breaking depth (Newton on omega^2 = g k tanh(k d))
omega = 2 * math.pi / T
k = max(omega**2 / g, omega / math.sqrt(g * d_b))
for _ in range(50):
    k -= (g * k * math.tanh(k * d_b) - omega**2) / (g * math.tanh(k * d_b) + g * k * d_b / math.cosh(k * d_b) ** 2)
L_b = 2 * math.pi / k
H_mccowan = 0.78 * d_b
H_miche = 0.142 * L_b * math.tanh(k * d_b)

print(f"Breaking point (plotBeach.py): x_b = {x_b:.2f} m, d_b = {d_b:.3f} m, H_b = {H_b:.3f} m")
print(f"  breaker index gamma_b = H_b/d_b       = {H_b/d_b:.3f}")
print(f"  McCowan: H_b/d_b = 0.78  -> H_b      = {H_mccowan:.3f} m   (CFD {100*(H_b/H_mccowan-1):+.1f}%)")
print(f"  linear at d_b: k_b d_b = {k*d_b:.3f}, L_b = {L_b:.2f} m")
print(f"  Miche: H_b = 0.142 L_b tanh(k_b d_b)  = {H_miche:.3f} m   (CFD {100*(H_b/H_miche-1):+.1f}%)"
      f"  i.e. H_b/d_b = {H_miche/d_b:.3f}")
i = np.argmin(abs(x - x_b))
print(f"Phase speed at breaking: CFD {c[i]:.3f}, linear {c_lin[i]:.3f}, sqrt(gd) {c_sw[i]:.3f}, "
      f"sqrt(g(d+H)) {c_sol[i]:.3f} m/s")
with open("results/breaking.csv", "w", newline="") as file:
    w = csv.writer(file)
    w.writerows([("quantity", "value"), ("x_b [m]", f"{x_b:.2f}"), ("d_b [m]", f"{d_b:.3f}"),
                 ("H_b [m]", f"{H_b:.3f}"), ("gamma_b = H_b/d_b", f"{H_b/d_b:.3f}"),
                 ("McCowan H_b = 0.78 d_b [m]", f"{H_mccowan:.3f}"), ("L_b linear [m]", f"{L_b:.2f}"),
                 ("k_b d_b", f"{k*d_b:.3f}"), ("Miche H_b [m]", f"{H_miche:.3f}"),
                 ("Miche H_b/d_b", f"{H_miche/d_b:.3f}"),
                 ("c at x_b: CFD / linear / sqrt(gd) / sqrt(g(d+H)) [m/s]",
                  f"{c[i]:.3f} / {c_lin[i]:.3f} / {c_sw[i]:.3f} / {c_sol[i]:.3f}")])

fig, axs = plt.subplots(2, 1, figsize=(7, 5), sharex=True)
axs[0].plot(x, H, "k-", lw=2, label="CFD")
axs[0].plot(x, H_lin, "C0--", label="linear shoaling")
axs[0].set_ylabel("H [m]")
axs[1].plot(x, c, "k-", lw=2, label="CFD")
axs[1].plot(x, c_lin, "C0--", label="linear dispersion")
axs[1].plot(x, c_sw, "C2:", label=r"$\sqrt{gd}$")
axs[1].plot(x, c_sol, "C3-.", label=r"$\sqrt{g(d+H)}$ (solitary)")
axs[1].set(ylabel="c [m/s]", xlabel="x [m]", ylim=(0, 10.5))
for ax, s in zip(axs, "ab"):
    ax.axvline(x_b, color="C3", ls=":", lw=1)
    ax.axvline(100, color="0.6", lw=0.6)          # toe of the slope
    ax.grid(alpha=0.3)
    ax.legend(fontsize=7, loc="lower left")
    ax.text(0.01, 0.92, f"({s})", transform=ax.transAxes, fontweight="bold")
fig.tight_layout()
fig.savefig("results/beach_Hc.png", dpi=200)
print("Saved results/beach_Hc.png and results/breaking.csv")
