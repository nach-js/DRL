"""
General-purpose plotter for mumax3 Ku1-sweep console output.

Works with lines shaped like either of these (as printed by Print(...)):

    //step= 0  Ku1= 500000  mz= 0.4383954107761383
    //step= 0  Ku1= 500000  mz= [-3.2e-07 3.8e-07 0.4384]

Usage:
    1. Redirect/copy your mumax3 console output (or the //step= ... lines)
       into a text file, e.g. sweep_log.txt
    2. Set LOG_FILE below to that file's path (or pass it as a command-line arg)
    3. Run:  python plot_sweep.py [sweep_log.txt]

It auto-detects:
    - scalar mz=<float>            -> uses that value directly
    - vector mz=[mx my mz]         -> uses the 3rd component (z)
    - the turning point of the sweep (max or min Ku1), splitting the data
      into an "increasing" and "decreasing" branch automatically
"""

import sys
import re
import matplotlib.pyplot as plt

# ---- config -----------------------------------------------------------
LOG_FILE = "sweep_log.txt"   # default, overridden by sys.argv[1] if given
OUT_FILE = "mz_ku1_plot.png"
# -------------------------------------------------------------------------

LINE_RE = re.compile(
    r"step\s*=\s*(\d+)\s+Ku1\s*=\s*([-\d.eE+]+)\s+mz\s*=\s*"
    r"(\[.*?\]|[-\d.eE+]+)"
)


def parse_log(path):
    """Parse a mumax3-style log file into (step, Ku1, mz) tuples."""
    rows = []
    with open(path, "r") as f:
        for line in f:
            m = LINE_RE.search(line)
            if not m:
                continue
            step = int(m.group(1))
            ku1 = float(m.group(2))
            mz_raw = m.group(3)

            if mz_raw.startswith("["):
                # vector form: [mx my mz] -> take z component
                nums = [float(x) for x in mz_raw.strip("[]").split()]
                mz = nums[2] if len(nums) >= 3 else nums[-1]
            else:
                mz = float(mz_raw)

            rows.append((step, ku1, mz))

    if not rows:
        raise ValueError(
            f"No matching 'step=... Ku1=... mz=...' lines found in {path}"
        )
    return rows


def split_branches(ku1, mz):
    """Split into up/down branches at the turning point (extremum of Ku1)."""
    turn = max(range(len(ku1)), key=lambda i: ku1[i])
    turn_low = min(range(len(ku1)), key=lambda i: ku1[i])
    # pick whichever extremum sits in the interior (not at the very ends)
    # -- if Ku1 increases then decreases, the max is the turning point;
    #    if it decreases then increases, the min is the turning point.
    if 0 < turn < len(ku1) - 1:
        idx = turn
    elif 0 < turn_low < len(ku1) - 1:
        idx = turn_low
    else:
        idx = len(ku1) - 1  # monotonic, no second branch

    branch1_ku1, branch1_mz = ku1[: idx + 1], mz[: idx + 1]
    branch2_ku1, branch2_mz = ku1[idx:], mz[idx:]
    return (branch1_ku1, branch1_mz), (branch2_ku1, branch2_mz)


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else LOG_FILE
    rows = parse_log(path)

    step = [r[0] for r in rows]
    ku1 = [r[1] for r in rows]
    mz = [r[2] for r in rows]

    (b1_ku1, b1_mz), (b2_ku1, b2_mz) = split_branches(ku1, mz)

    fig, axes = plt.subplots(1, 2, figsize=(13, 5.5))

    # --- mz vs Ku1 (hysteresis-style view) ---
    ax = axes[0]
    ax.plot(b1_ku1, b1_mz, "o-", color="#2a78d6", markersize=4, label="leg 1")
    if b2_ku1 != b1_ku1:
        ax.plot(b2_ku1, b2_mz, "s-", color="#e34948", markersize=4, label="leg 2")
    ax.set_xlabel("Ku1 (J/m$^3$)")
    ax.set_ylabel("mz")
    ax.set_title("mz vs Ku1")
    ax.axhline(0, color="gray", linewidth=0.6)
    ax.legend()
    ax.grid(alpha=0.3)

    # --- mz and Ku1 vs step (raw sweep view) ---
    ax2 = axes[1]
    ax2.plot(step, mz, color="#1baf7a", linewidth=1.8, label="mz")
    ax2.set_xlabel("step")
    ax2.set_ylabel("mz", color="#1baf7a")
    ax2.tick_params(axis="y", labelcolor="#1baf7a")
    ax2.grid(alpha=0.3)

    ax3 = ax2.twinx()
    ax3.plot(step, ku1, color="#eda100", linewidth=1.2, linestyle="--", label="Ku1")
    ax3.set_ylabel("Ku1 (J/m$^3$)", color="#eda100")
    ax3.tick_params(axis="y", labelcolor="#eda100")
    ax2.set_title("mz and Ku1 vs step")

    plt.tight_layout()
    plt.savefig(OUT_FILE, dpi=150)
    print(f"Saved plot to {OUT_FILE}  ({len(rows)} rows parsed from {path})")


if __name__ == "__main__":
    main()