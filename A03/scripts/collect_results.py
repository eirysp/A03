# collect_results.py: one row per run of a study -> results/<study>.csv
#
# Run it from the A03 folder, after the study has run:
#     cd ~/openfoam/A03
#     python scripts/collect_results.py courant     # runs/courant -> results/courant.csv
#     python scripts/collect_results.py gci         # runs/gci     -> results/gci_runs.csv
#
# For every run folder in runs/<study>/ it reads
#   - parameters     : nx, nzBand, nzBed, nzAir, maxCo, initialWave
#   - log.plot       : the "key = value" lines at the end (c, c_V, c_III, c_Airy,
#                      H_end, H_0, crest_end, trough_end)
#   - log.checkMesh  : the number of cells
#   - log.interFoam  : number of cores (nProcs), the last ExecutionTime and
#                      ClockTime, and the number of time steps
# (gci.py writes results/gci.csv, so the GCI runs go to gci_runs.csv here.)

import csv
import os
import re
import sys

study = sys.argv[1] if len(sys.argv) > 1 else "courant"
runs_dir = f"runs/{study}"
os.makedirs("results", exist_ok=True)


def numbers(path, pattern):
    # every "name number" pair that matches pattern, as a dict
    values = {}
    if os.path.exists(path):
        for line in open(path):
            m = re.match(pattern, line)
            if m:
                try:
                    values[m.group(1)] = float(m.group(2))
                except ValueError:
                    pass
    return values


def solver_stats(path):
    # cores, last ExecutionTime / ClockTime [s] and number of time steps
    cores, exe, clock, steps = 1, None, None, 0
    if os.path.exists(path):
        for line in open(path):
            m = re.search(r"nProcs\s*:\s*(\d+)", line)
            if m:
                cores = int(m.group(1))
            m = re.search(r"ExecutionTime = ([0-9.eE+-]+) s\s+ClockTime = ([0-9.eE+-]+) s", line)
            if m:
                exe, clock = float(m.group(1)), float(m.group(2))
            if line.startswith("Time = "):
                steps += 1
    return cores, exe, clock, steps


def cells(path):
    if os.path.exists(path):
        for line in open(path):
            if line.strip().startswith("cells:"):
                return int(line.split()[1])
    return None


rows = []
for name in sorted(os.listdir(runs_dir)):
    case = f"{runs_dir}/{name}"
    if not os.path.isfile(f"{case}/log.plot"):
        print(f"skip {case}: no log.plot (not run, or the plotting script failed)")
        continue
    par = numbers(f"{case}/parameters", r"^(\w+)\s+([-+0-9.eE]+)\s*;")
    res = numbers(f"{case}/log.plot", r"^(\w+) = ([-+0-9.eE]+)\s*$")
    cores, exe, clock, steps = solver_stats(f"{case}/log.interFoam")
    row = dict(case=name, maxCo=par.get("maxCo"), nx=par.get("nx"), nzBand=par.get("nzBand"),
               nzBed=par.get("nzBed"), nzAir=par.get("nzAir"), N=cells(f"{case}/log.checkMesh"),
               cores=cores, ExecutionTime=exe, ClockTime=clock, timeSteps=steps)
    row.update(res)
    if "c" in res and "c_V" in res:
        row["c_err_vs_V_pct"] = round(100 * (res["c"] - res["c_V"]) / res["c_V"], 4)
    if "H_end" in res and "H_0" in res:
        row["H_end_over_H0"] = round(res["H_end"] / res["H_0"], 5)
    rows.append(row)
    print(f"{name:14s} N={row['N']}  c={res.get('c')}  H_end/H_0={row.get('H_end_over_H0')}  "
          f"ExecutionTime={exe} s  ClockTime={clock} s  cores={cores}  steps={steps}")

if not rows:
    sys.exit(f"no finished runs in {runs_dir}")
fields = []
for row in rows:
    fields += [k for k in row if k not in fields]
out = f"results/{study}_runs.csv" if study == "gci" else f"results/{study}.csv"
with open(out, "w", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)
print(f"Wrote {out} ({len(rows)} runs)")
