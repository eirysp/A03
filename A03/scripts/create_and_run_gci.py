## create_and_run_sims.py: one OpenFOAM run for each set of parameters of a study.
#
# Run it from the A03 folder, in a terminal where OpenFOAM is loaded:
#     cd ~/openfoam/A03
#     python scripts/create_and_run_sims.py
#
# Each run is a copy of Case 1 (templates/A03_stokes_wave), in its own folder
# runs/<study>/<name>, and differs from it only in the parameters given below.
# After the run, the script runs the plotting script plotWave.py and saves
# what it prints in log.plot. A run whose folder already exists is not run
# again: delete its folder to run it again. For the other studies, copy this
# script and change study and runs.
#
# As given, it runs the time-step study of Task 2(a): Case 1 with five values
# of the maximum Courant number, maxCo, on the mesh of the template.

import os
import shutil
import subprocess

import progress   # scripts/progress.py: the progress bar of each run

 ============================================================================
# EDIT THESE LINES for each study (in your copy of this script):
#   - study: the folder runs/<study> that the runs go into;
#   - runs: one line per run, its name and the parameters that it changes.
# ============================================================================
study = "gci"

runs = {
    "nx050": {"nx": 50, "nzBand": 14, "nzBed": 6, "nzAir": 4},
    "nx100": {"nx": 100, "nzBand": 28, "nzBed": 12, "nzAir": 8},
    "nx200": {"nx": 200, "nzBand": 56, "nzBed": 24, "nzAir": 16},
}
# ============================================================================
# END OF THE LINES TO EDIT
# ============================================================================

# ----- Do not change anything below this line. -----
template = "templates/A03_stokes_wave"   # Case 1: the case that every run copies
plot = "plotWave.py"                     # its plotting script


def set_parameter(lines, name, value):
    # change the line that starts with name in the lines of the file parameters
    for i in range(len(lines)):
        if lines[i].startswith(name + " "):
            lines[i] = f"{name}  {value};  // set by create_and_run_sims.py\n"
            print("  ", lines[i].strip())  # check that the change was made
            return
    raise ValueError(f"no line starts with {name} in the file parameters")


for n, (name, changes) in enumerate(runs.items(), start=1):
    case = f"runs/{study}/{name}"
    print(f"\nRun {n}/{len(runs)}: {case}")
    if os.path.exists(case):
        print("   already exists: not run again")
        continue

    # ----- Pre-processing: copy the template and set the parameters -----
    shutil.copytree(template, case, ignore=shutil.ignore_patterns(
        "processor*", "postProcessing", "log.*", "*.png", "constant/polyMesh"))
    with open(f"{case}/parameters") as file:
        lines = file.readlines()
    for parameter, value in changes.items():
        set_parameter(lines, parameter, value)
    with open(f"{case}/parameters", "w") as file:
        file.writelines(lines)

    # ----- Simulation (Allrun meshes, sets the initial fields and runs in parallel) -----
    # (with a progress bar; the script stops if Allrun fails)
    progress.run_with_progress("bash Allrun", case)

    # ----- Post-processing: compare with the theory, save the figures -----
    # options: run in a shell, inside the case folder, and stop if a command fails
    options = dict(shell=True, cwd=case, check=True)
    subprocess.run(f"python {plot} > log.plot", **options)
    print(f"   done: table and results in {case}/log.plot")

print(f"\nAll {len(runs)} runs of runs/{study} are done.")
