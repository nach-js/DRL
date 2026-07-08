"""
Reads the table.txt output from CoFeB_VMCA_Bext_initialRelax.mx3
(nested sweep: outer loop over Ku1, inner loop over B_ext) and plots:
  1. mz vs B_ext, one line per Ku1 value
  2. A heatmap of mz over the (Ku1, B_ext) grid

Run this from the same folder that contains
CoFeB_VMCA_Bext_initialRelax.out/table.txt
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ── Config: must match the .mx3 script exactly ───────────────
sim_name = "CoFeB_VMCA_Bext_initialRelax"
out_dir = f"{sim_name}.out"

N_ku1 = 20
Ku1_lo = 0.5e6
Ku1_hi = 0.73e6

N_B = 10
B_lo = 0.08
B_step = 0.02

# ── Load table.txt ────────────────────────────────────────────
table_path = os.path.join(out_dir, "table.txt")
table = pd.read_csv(table_path, sep="\t")
table.columns = [c.split(" ")[0] for c in table.columns]  # strip units from headers

if len(table) != N_ku1 * N_B:
    print(f"Warning: expected {N_ku1 * N_B} rows, found {len(table)}. "
          f"Check N_ku1/N_B match the .mx3 script, or the sim didn't finish.")

# ── Reconstruct the Ku1 and B_ext grids (same order as the nested loop) ──
ku1_vals = [Ku1_lo + (Ku1_hi - Ku1_lo) * i / (N_ku1 - 1) for i in range(N_ku1)]
B_vals = [B_lo + B_step * j for j in range(N_B)]

mz = table["mz"].to_numpy().reshape(N_ku1, N_B)  # rows=Ku1, cols=B_ext

# ── Plot 1: mz vs B_ext, one line per Ku1 ─────────────────────
fig1, ax1 = plt.subplots(figsize=(8, 6))
cmap = plt.cm.viridis
for i, ku1 in enumerate(ku1_vals):
    color = cmap(i / (N_ku1 - 1))
    ax1.plot(B_vals, mz[i], marker="o", markersize=3, color=color,
              label=f"{ku1/1e3:.0f} kJ/m³" if i % 4 == 0 else None)

ax1.set_xlabel("B_ext (T)")
ax1.set_ylabel(r"$\langle m_z \rangle$")
ax1.set_title("$m_z$ vs $B_{ext}$ for varying $K_{u1}$")
ax1.legend(title="Ku1", fontsize=8)
ax1.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("mz_vs_Bext_by_Ku1.png", dpi=150)
plt.show()

# ── Plot 2: heatmap of mz over (Ku1, B_ext) ───────────────────
fig2, ax2 = plt.subplots(figsize=(8, 6))
im = ax2.imshow(
    mz,
    aspect="auto",
    origin="lower",
    extent=[B_vals[0], B_vals[-1], ku1_vals[0], ku1_vals[-1]],
    cmap="RdBu",
    vmin=-1, vmax=1,
)
ax2.set_xlabel("B_ext (T)")
ax2.set_ylabel("Ku1 (J/m³)")
ax2.set_title("$m_z$ over the $(K_{u1}, B_{ext})$ grid")
fig2.colorbar(im, ax=ax2, label=r"$\langle m_z \rangle$")
plt.tight_layout()
plt.savefig("mz_heatmap_Ku1_Bext.png", dpi=150)
plt.show()

print("Saved: mz_vs_Bext_by_Ku1.png, mz_heatmap_Ku1_Bext.png")