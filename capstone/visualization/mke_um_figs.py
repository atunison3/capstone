"""Generate two University-of-Michigan-themed figures from the CES 2024 Common
Content dataset:

  1. um_fig1_hist_age_by_turnout.png  - age distribution by validated turnout
  2. um_fig3_pie_strictness.png       - strength of party identification (pid7)

Requires: pandas, matplotlib, numpy.
Run:  python make_um_figs.py
"""

import pandas as pd
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

# --- University of Michigan theme colors ---
NAVY = "#00274C"  # Michigan Blue
MAIZE = "#FFCB05"  # Michigan Maize
NAVY2 = "#2E4E6E"  # mid navy (ramp)
NAVY3 = "#7C97B3"  # light navy (ramp)
GREY = "#B7B7B7"
INK = "#00274C"

plt.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "figure.dpi": 130,
        "savefig.dpi": 130,
        "axes.edgecolor": "#5A5A5A",
    }
)

# our work directory
work_dir = "/home/user/Downloads/"

# update below with your ces data directory.
f = work_dir + "CCES24_Common_OUTPUT_vv_topost_final.csv"
df = pd.read_csv(f, usecols=["birthyr", "TS_g2024", "pid7"], low_memory=False)

# ================= FIG 1: Age distribution by validated turnout =================
df["age"] = 2024 - df["birthyr"]
# Validated turnout: codes 1-6 = has a general-election vote record -> Voted;
# code 7 (no record) or unmatched (NaN) -> Did not vote.
voted = df["TS_g2024"].isin([1, 2, 3, 4, 5, 6])
age = df["age"].to_numpy()

bins = np.arange(18, 97, 4)
centers = (bins[:-1] + bins[1:]) / 2
c_voted, _ = np.histogram(age[voted.to_numpy()], bins=bins)
c_notvoted, _ = np.histogram(age[(~voted).to_numpy()], bins=bins)

w = (bins[1] - bins[0]) * 0.42
fig, ax = plt.subplots(figsize=(11, 6.3))
ax.bar(centers - w / 2, c_voted, width=w, color=NAVY, label="Voted", zorder=3)
ax.bar(centers + w / 2, c_notvoted, width=w, color=MAIZE, label="Did not vote", zorder=3)

ax.set_title("Age distribution by turnout", fontsize=20, fontweight="bold", color=NAVY, pad=16)
ax.set_xlabel("Age (years)", fontsize=13, color=INK)
ax.set_ylabel("Number of respondents", fontsize=13, color=INK)
ax.tick_params(colors=INK, labelsize=11)
for s in ["top", "right"]:
    ax.spines[s].set_visible(False)
ax.spines["left"].set_color("#5A5A5A")
ax.spines["bottom"].set_color("#5A5A5A")
leg = ax.legend(title="Turnout", fontsize=12, title_fontsize=13, loc="upper right", frameon=False)
plt.setp(leg.get_title(), color=NAVY, fontweight="bold")
for t in leg.get_texts():
    t.set_color(INK)
ax.margins(x=0.01)
fig.text(
    0.5,
    0.005,
    "Source: Cooperative Election Study 2024 Common Content (validated vote, N=60,000, unweighted)",
    ha="center",
    fontsize=9,
    color="#7A7A7A",
    style="italic",
)
rect = (0.0, 0.03, 1.0, 1.0)
fig.tight_layout(rect=rect)
# update below with the directory that you want to save the figure
fig.savefig(work_dir + "um_fig1_hist_age_by_turnout.png", bbox_inches="tight")
plt.close(fig)

# ================= FIG 3: Partisan strength (strictness) pie =================
pid = df["pid7"]
groups = {
    "Strong partisan": pid.isin([1, 7]).sum(),
    "Not very strong": pid.isin([2, 6]).sum(),
    "Leaners": pid.isin([3, 5]).sum(),
    "Independent": (pid == 4).sum(),
    "Not sure": (pid == 8).sum(),
}
labels = list(groups.keys())
vals = np.array(list(groups.values()), dtype=float)
colors = [NAVY, NAVY2, NAVY3, MAIZE, GREY]

fig, ax = plt.subplots(figsize=(9, 7))
wedges, _ = ax.pie(  # type: ignore
    vals,
    colors=colors,
    startangle=90,
    counterclock=False,
    wedgeprops=dict(edgecolor="white", linewidth=2, width=0.42),  # donut
)
# center total
total = int(vals.sum())
ax.text(0, 0.10, f"{total:,}", ha="center", va="center", fontsize=22, fontweight="bold", color=NAVY)
ax.text(0, -0.16, "respondents", ha="center", va="center", fontsize=12, color="#6A6A6A")

# direct % labels outside
pct = vals / vals.sum() * 100
for wdg, p in zip(wedges, pct):
    ang = np.deg2rad((wdg.theta1 + wdg.theta2) / 2)
    r = 0.80
    ax.text(
        r * np.cos(ang),
        r * np.sin(ang),
        f"{p:.0f}%",
        ha="center",
        va="center",
        fontsize=12,
        fontweight="bold",
        color="white" if wdg.get_facecolor()[0] < 0.5 else NAVY,
    )

ax.set_title("Strength of party identification", fontsize=20, fontweight="bold", color=NAVY, pad=18)
legend_handles = [Patch(facecolor=c, edgecolor="white", label=line) for c, line in zip(colors, labels)]
leg = ax.legend(
    handles=legend_handles,
    loc="center left",
    bbox_to_anchor=(0.98, 0.5),
    frameon=False,
    fontsize=12,
    title="Partisan strictness",
)
plt.setp(leg.get_title(), color=NAVY, fontweight="bold")
for t in leg.get_texts():
    t.set_color(INK)
ax.set_aspect("equal")
fig.text(
    0.5,
    0.02,
    "Source: Cooperative Election Study 2024 Common Content (7-point party ID, N=60,000, unweighted)",
    ha="center",
    fontsize=9,
    color="#7A7A7A",
    style="italic",
)
# update below with the directory that you want to save the figure
fig.savefig(work_dir + "um_fig3_pie_strictness.png", bbox_inches="tight")
plt.close(fig)

# --- summary printout ---
print("FIG1 turnout counts:")
print(f"  Voted (record):      {int(voted.sum()):,}  ({voted.mean()*100:.1f}%)")
print(f"  Did not vote:        {int((~voted).sum()):,}  ({(~voted).mean()*100:.1f}%)")
print("\nFIG3 partisan strength:")
for k, v in groups.items():
    print(f"  {k:<18} {int(v):>7,}  ({v/total*100:4.1f}%)")
print("\nSaved both PNGs to" + work_dir)
