# Usage: python make_fig5.py <records.csv> <output_folder>
"""make_fig5.py - Fig. 5: distribution of five key soil properties in the screened SHC records.
Screening = same rules as Table 6: plausibility limits, and available N = 0 treated as missing.
n and median are computed on the screened data; the drawing is clipped to the
1st-99th percentile for display only."""
import sys, numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
SRC, OUT = sys.argv[1], sys.argv[2]
LIM = {"pH":(3,11), "OC_pct":(0,5), "N_kg_ha":(0,1500), "P_kg_ha":(0,300), "K_kg_ha":(0,2500)}
PANELS = [("pH","Soil pH","pH",None),
          ("OC_pct","Organic carbon","%",0.50),
          ("N_kg_ha","Available nitrogen","kg ha$^{-1}$",280),
          ("P_kg_ha","Available phosphorus","kg ha$^{-1}$",10),
          ("K_kg_ha","Available potassium","kg ha$^{-1}$",120)]
FILL, EDGE, LIMC, NORMC = "#9db4d6", "#2f4b7c", "#b2182b", "#4d8b31"
df = pd.read_csv(SRC, usecols=[p[0] for p in PANELS], low_memory=False)
MM = 1/25.4
plt.rcParams.update({"font.family":"DejaVu Sans", "font.size":7})
fig, axes = plt.subplots(1, 5, figsize=(190*MM, 62*MM))
for ax,(col,title,ylab,limit) in zip(axes, PANELS):
    s = pd.to_numeric(df[col], errors="coerce")
    s = s[s.between(*LIM[col])]
    if col == "N_kg_ha": s = s[s > 0]
    n, med = len(s), s.median()
    lo, hi = s.quantile([.01,.99]); d = s[(s>=lo)&(s<=hi)].values
    v = ax.violinplot(d, showextrema=False, widths=0.85)
    for b in v["bodies"]: b.set_facecolor(FILL); b.set_edgecolor(EDGE); b.set_linewidth(0.6); b.set_alpha(0.85)
    ax.boxplot(d, widths=0.16, showfliers=False, patch_artist=True,
               boxprops=dict(facecolor="white", edgecolor=EDGE, linewidth=0.9),
               medianprops=dict(color="black", linewidth=1.4),
               whiskerprops=dict(color=EDGE, linewidth=0.9), capprops=dict(color=EDGE, linewidth=0.9))
    trans = ax.get_yaxis_transform()   # x in axes units, y in data units
    if col == "pH":
        ax.axhspan(6.5, 7.5, color=NORMC, alpha=0.12, zorder=0)
        ax.text(1.02, 7.0, "SHC\nnormal", transform=trans, fontsize=6, color=NORMC,
                ha="left", va="center", clip_on=False)
    else:
        ax.axhline(limit, color=LIMC, ls="--", lw=1.0, zorder=3)
        ax.text(1.02, limit, f"SHC low\n< {limit:g}", transform=trans, fontsize=6, color=LIMC,
                ha="left", va="center", clip_on=False)
    ax.set_title(f"{title}\nn = {n:,}\nmedian = {med:.2f}", fontsize=7, pad=4)
    ax.set_ylabel(ylab, fontsize=7); ax.set_xticks([]); ax.set_xlim(0.45, 1.75)
    ax.tick_params(axis="y", labelsize=6.5, length=2)
    ax.grid(axis="y", color="#dddddd", linewidth=0.5); ax.set_axisbelow(True)
    for sd in ("top","right"): ax.spines[sd].set_visible(False)
    for sd in ("left","bottom"): ax.spines[sd].set_linewidth(0.6)
    print(f"{title}: n={n:,} median={med:.2f} drawn {lo:.2f}-{hi:.2f}")
fig.tight_layout(w_pad=3.0)
for ext in ("pdf","png"):
    fig.savefig(f"{OUT}/figure2_soil_distributions.{ext}", dpi=300, bbox_inches="tight")
print("saved")
