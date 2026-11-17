# gci.py: Richardson extrapolation and the grid convergence index (GCI) of the
# phase speed c on the three grids of Task 2(b) (lecture L04, as in A02).
#
# Run it from the A03 folder, after scripts/create_and_run_gci.py:
#     cd ~/openfoam/A03
#     python scripts/gci.py
#
# It reads c from the last lines of log.plot (c = ...) of each grid and the
# number of cells N from log.checkMesh, prints the table of the GCI study
# (N_k, r, phi_k and the quantities of L04, with the safety factors Fs = 1.25
# and 3) and writes it to results/gci.csv. Change the folder names below if
# your runs have other names.

import csv
import math
import os

r = 2.0                              # refinement ratio, the same in every direction
grids = {                            # grid number of L04 (1 = fine): run folder
    1: "runs/gci/nx200",
    2: "runs/gci/nx100",
    3: "runs/gci/nx050",
}
key = "c"                            # the quantity phi: a key of log.plot


def read_log_plot(case):
    # the lines "key = value" of log.plot
    values = {}
    for line in open(os.path.join(case, "log.plot")):
        name, sep, value = line.partition(" = ")
        if sep:
            try:
                values[name.strip()] = float(value)
            except ValueError:
                pass
    return values


def read_cells(case):
    # the number of cells, from log.checkMesh ("cells: ...")
    for line in open(os.path.join(case, "log.checkMesh")):
        if line.strip().startswith("cells:"):
            return int(line.split()[1])
    raise ValueError(f"no number of cells in {case}/log.checkMesh")


phi = {n: read_log_plot(case)[key] for n, case in grids.items()}
cells = {n: read_cells(case) for n, case in grids.items()}
phi1, phi2, phi3 = phi[1], phi[2], phi[3]

e21 = phi2 - phi1                    # epsilon_21
e32 = phi3 - phi2                    # epsilon_32
s = math.copysign(1.0, e32 / e21)    # s = 1: monotonic convergence
p = abs(math.log(abs(e32 / e21))) / math.log(r)   # apparent order (r21 = r32 = r)
phi_ext = (r**p * phi1 - phi2) / (r**p - 1)       # extrapolated value phi_ext^21
ea = abs((phi1 - phi2) / phi1)                    # approximate relative error e_a^21
eext = abs((phi_ext - phi1) / phi_ext)            # extrapolated relative error e_ext^21
gci = {fs: fs * ea / (r**p - 1) for fs in (1.25, 3.0)}   # GCI_fine^21

grid_rows = [(k, grids[k], cells[k], f"{phi[k]:.5f}") for k in (1, 2, 3)]
rows = [
    ("r = r21 = r32", f"{r:g}"),
    ("epsilon_21", f"{e21:.5f}"),
    ("epsilon_32", f"{e32:.5f}"),
    ("epsilon_32/epsilon_21", f"{e32 / e21:.3f}"),
    ("s", f"{s:+.0f}"),
    ("p", f"{p:.3f}"),
    ("phi_ext^21", f"{phi_ext:.5f}"),
    ("e_a^21 [%]", f"{100 * ea:.3f}"),
    ("e_ext^21 [%]", f"{100 * eext:.3f}"),
    ("GCI_fine^21, Fs = 1.25 [%]", f"{100 * gci[1.25]:.3f}"),
    ("GCI_fine^21, Fs = 3 [%]", f"{100 * gci[3.0]:.3f}"),
]

print(f"Richardson extrapolation and GCI of {key} (lecture L04)\n")
print(f"{'k':<3} {'run':<20} {'N_k':>8} {'phi_k = ' + key:>12}")
for k, case, n, value in grid_rows:
    print(f"{k:<3} {case:<20} {n:>8} {value:>12}")
print()
for name, value in rows:
    print(f"{name:<40} {value:>10}")
if s < 0:
    print("\ns = -1: the convergence is oscillatory, not monotonic (see L04).")

os.makedirs("results", exist_ok=True)
with open("results/gci.csv", "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["k", "run", "N_k", "phi_k = " + key])
    writer.writerows(grid_rows)
    writer.writerow([])
    writer.writerow(["quantity", "value"])
    writer.writerows(rows)
print("\nWritten: results/gci.csv")
