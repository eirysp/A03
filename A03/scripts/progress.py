# progress.py: shows how far the OpenFOAM runs have got. You do not need to
# edit this file.
#
# create_and_run_sims.py uses it to draw a progress bar while each run goes.
# You can also run it on its own, in a second terminal, to follow a study or
# a single run (Ctrl+C to stop following; the runs go on):
#     cd ~/openfoam/A03
#     python scripts/progress.py runs/courant                # every run of a study
#     python scripts/progress.py runs/original/stokes_wave   # one run
# Allrun also uses it (python .../progress.py --bar .) to draw the bar while
# interFoam runs, when you run Allrun yourself in a terminal.
#
# It reads the log files of each run: which step of Allrun has started, and,
# while interFoam runs, the last "Time =" and "ClockTime =" of log.interFoam,
# compared with endTime in the file parameters.

import os
import re
import signal
import subprocess
import sys
import threading
import time

STEPS = ["stokesV", "blockMesh", "checkMesh", "setExprFields", "decomposePar",
         "interFoam", "reconstructPar", "plot"]   # log.<step>, in the order of Allrun
WIDTH = 30                                        # characters of the bar


def read_numbers(case):
    # the parameters "name  number;" of the files parameters and waveCoeffs
    values = {}
    for file in ["waveCoeffs", "parameters"]:
        path = os.path.join(case, file)
        if os.path.exists(path):
            for line in open(path):
                m = re.match(r"\s*(\w+)\s+([-+0-9.eE]+)\s*;", line)
                if m:
                    values[m.group(1)] = float(m.group(2))
    return values


def end_time(case):
    # endTime of the file parameters: a number or #eval{ $nPeriods*$T }
    path = os.path.join(case, "parameters")
    if not os.path.exists(path):
        return None
    values = read_numbers(case)
    for line in open(path):
        m = re.match(r"\s*endTime\s+(.*?);", line)
        if m:
            text = m.group(1).strip()
            e = re.match(r"#eval\s*\{(.*)\}", text)
            if e:
                text = re.sub(r"\$\{?(\w+)\}?", lambda v: repr(values[v.group(1)]), e.group(1))
            try:
                return float(eval(text, {"__builtins__": {}}))
            except Exception:
                return None
    return None


def tail(path, size=20000):
    # the last size characters of a file
    with open(path, "rb") as file:
        file.seek(0, os.SEEK_END)
        file.seek(max(0, file.tell() - size))
        return file.read().decode(errors="replace")


def status(case):
    # one line that says how far the run in the folder case has got
    log = os.path.join(case, "log.interFoam")
    if not os.path.exists(log):
        started = [s for s in STEPS if os.path.exists(os.path.join(case, f"log.{s}"))]
        return f"preparing ({started[-1]})" if started else "waiting"
    text = tail(log)
    if "FOAM FATAL" in text or "FOAM aborting" in text:
        return "FAILED: see log.interFoam"
    times = re.findall(r"^Time = ([-+0-9.eE]+)", text, re.M)
    clocks = re.findall(r"ClockTime = ([0-9.]+)", text)
    t = float(times[-1]) if times else 0.0
    clock = float(clocks[-1]) if clocks else 0.0
    t_end = end_time(case)
    finished = re.search(r"^End\s*$", text, re.M) is not None
    if finished:
        after = [s for s in STEPS[STEPS.index("interFoam") + 1:]
                 if os.path.exists(os.path.join(case, f"log.{s}"))]
        step = "done" if "plot" in after else "interFoam done"
        return f"[{'#' * WIDTH}] 100%  t = {t:.2f} s   clock {clock:.0f} s   {step}"
    if not t_end:
        return f"running   t = {t:.3f} s   clock {clock:.0f} s"
    fraction = min(max(t / t_end, 0.0), 1.0)
    n = int(round(WIDTH * fraction))
    # no estimate of the time left: the time step changes during the run
    return f"[{'#' * n}{'-' * (WIDTH - n)}] {100 * fraction:3.0f}%  t = {t:.2f} / {t_end:.2f} s   clock {clock:.0f} s"


def run_with_progress(command, case):
    # run command (bash Allrun) in the folder case and draw a progress bar under
    # what it prints; stop with an error if the command fails
    process = subprocess.Popen(command, shell=True, cwd=case, text=True,
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    lines = []                                     # what the command prints

    def read():
        for line in process.stdout:
            lines.append(line)

    reader = threading.Thread(target=read, daemon=True)
    reader.start()
    shown = 0
    while True:
        done = process.poll() is not None
        if done:
            reader.join()
        sys.stdout.write("\r\033[K")               # clear the bar line
        if done and os.path.exists(os.path.join(case, "log.interFoam")):
            sys.stdout.write("   " + status(case) + "\n")   # keep the last bar
        for line in lines[shown:]:                 # print the new lines of the command
            sys.stdout.write("   " + line)
        shown = len(lines)
        if done:
            break
        sys.stdout.write("   " + status(case))
        sys.stdout.flush()
        time.sleep(1)
    sys.stdout.flush()
    if process.returncode != 0:
        raise SystemExit(f"{command} failed in {case}: see its log files")


def bar(case):
    # draw the bar of the run in the folder case on one line until stopped
    # (Allrun stops it when interFoam ends); then leave the last bar on screen
    def stop(*args):
        sys.stdout.write("\r\033[K   " + status(case) + "\n")
        sys.stdout.flush()
        sys.exit(0)

    signal.signal(signal.SIGTERM, stop)
    while True:
        sys.stdout.write("\r\033[K   " + status(case))
        sys.stdout.flush()
        time.sleep(1)


def show(folder):
    # follow the run in folder, or every run in the subfolders of folder
    if os.path.exists(os.path.join(folder, "parameters")):
        cases = [folder]
    else:
        cases = None
    while True:
        names = cases or sorted(os.path.join(folder, d) for d in os.listdir(folder)
                                if os.path.exists(os.path.join(folder, d, "parameters")))
        width = max([len(c) for c in names] + [4])
        sys.stdout.write("\033[H\033[J")           # clear the screen
        print(f"Progress of {folder} (Ctrl+C to stop following; the runs go on)\n")
        for case in names:
            print(f"{case:<{width}}  {status(case)}")
        if not names:
            print("no runs yet")
        sys.stdout.flush()
        time.sleep(2)


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--bar":
        try:
            bar(sys.argv[2])
        except KeyboardInterrupt:
            print()
        sys.exit(0)
    if len(sys.argv) != 2 or not os.path.isdir(sys.argv[1]):
        raise SystemExit("usage: python scripts/progress.py runs/<study>   (or a run folder)")
    try:
        show(sys.argv[1])
    except KeyboardInterrupt:
        print()
