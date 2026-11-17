# plot_study.py: the figures of a Case 1 study (Task 2), from its runs.
#
# Run it from the A03 folder, after collect_results.py:
#     cd ~/openfoam/A03
#     python scripts/plot_study.py courant maxCo     # Task 2(a)
#     python scripts/plot_study.py gci nx            # Task 2(b)-(c)
#
# It saves results/<study>.png with four panels:
#   (a) wave height H/H_0 against t/T for every run (read from
#       postProcessing/freeSurface, as plotWave.py does);
#   (b) phase speed c against the parameter, with the Stokes V and Stokes III
#       phase speeds (Airy is printed: it is far below);
#   (c) the free surface eta(x) at the end of every run, with Stokes V;
#   (d) cost: ExecutionTime against the parameter.

import csv
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

study = sys.argv[1] if len(sys.argv) > 1 else "courant"
param = sys.argv[2] if len(sys.argv) > 2 else "maxCo"
table = Path("results") / (f"{study}_runs.csv" if study == "gci" else f"{study}.csv")
rows = sorted(csv.DictReader(open(table)), key=lambda r: float(r[param]))

# the theory: stokesV.py of the template (same H, lambda and d in every run)
sys.path.insert(0, str(Path("templates/A03_stokes_wave").resolve()))
from stokesV import Wave, read_parameters  # noqa: E402


def surface(case):
    # t and eta(x) on 256 points, from the free-surface points of the run
    P = read_parameters(case / "parameters")
    lam, dy = P["lambda"], P["dy"]
    x = np.arange(256) * lam / 256
    folders = sorted((case / "postProcessing/freeSurface").iterdir(), key=lambda d: float(d.name))
    t, eta = [], []
    for folder in folders:
        pts = np.loadtxt(next(folder.glob("*.raw")), ndmin=2)
        pts = pts[pts[:, 1] <= 0.5 * dy + 1e-9]
        xs, i = np.unique(pts[:, 0], return_index=True)
        eta.append(np.interp(x, xs, pts[i, 2], period=lam))
        t.append(float(folder.name))
    return x, np.array(t), np.array(eta), P


fig, axs = plt.subplots(2, 2, figsize=(9, 6))
V = None
for j, r in enumerate(rows):
    case = Path("runs") / study / r["case"]
    x, t, eta, P = surface(case)
    if V is None:
        V, S3 = Wave(P["H"], P["lambda"], P["d"], 5), Wave(P["H"], P["lambda"], P["d"], 3)
    H = eta.max(1) - eta.min(1)
    label = f"{param} = {float(r[param]):g}"
    axs[0, 0].plot(t / V.T, H / H[0], color=f"C{j}", label=label)
    axs[1, 0].plot(x, eta[-1], color=f"C{j}", label=label)

p = [float(r[param]) for r in rows]
c = [float(r["c"]) for r in rows]
axs[0, 1].plot(p, c, "ko-", label="CFD")
axs[0, 1].axhline(V.c, color="C0", ls="--", label=f"Stokes V {V.c:.4f}")
axs[0, 1].axhline(S3.c, color="C2", ls="-.", label=f"Stokes III {S3.c:.4f}")
axs[1, 0].plot(x, V.eta(x, t[-1]), "k--", lw=1, label="Stokes V")
exe = [float(r["ExecutionTime"]) if r["ExecutionTime"] else np.nan for r in rows]
axs[1, 1].plot(p, exe, "ko-")

axs[0, 0].set(xlabel="t/T [-]", ylabel="H/H_0 [-]", title="(a) wave height")
axs[0, 1].set(xlabel=param, ylabel="c [m/s]", title="(b) phase speed")
axs[1, 0].set(xlabel="x [m]", ylabel="eta [m]", title=f"(c) free surface at t = {t[-1]:.1f} s")
axs[1, 1].set(xlabel=param, ylabel="ExecutionTime [s]", title="(d) cost")
for ax in axs.flat:
    ax.grid(alpha=0.3)
axs[0, 0].legend(fontsize=7)
axs[0, 1].legend(fontsize=7)
axs[1, 0].legend(fontsize=7)
if param == "nx":
    axs[0, 1].set_xscale("log", base=2)
    axs[1, 1].set_xscale("log", base=2)
fig.tight_layout()
fig.savefig(f"results/{study}.png", dpi=200)
print(f"Saved results/{study}.png  (Airy c = {Wave(P['H'], P['lambda'], P['d'], 1).c:.4f} m/s, not drawn)")
