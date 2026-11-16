"""
quality_indicators.py
Reproduces the source-data quality indicators reported in Section 6.1 and
Tables 6, 8 and 9 of the paper.

Input : a CSV of Soil Health Card (SHC) records (not distributed with this
        repository; see README). Required columns:
        layer_name, state_name, dist_code, cycle, village, lat, lon,
        pH, EC_dSm, OC_pct, N_kg_ha, P_kg_ha, K_kg_ha,
        S_ppm, Zn_ppm, B_ppm, Fe_ppm, Mn_ppm, Cu_ppm
Output: a JSON file with all indicators.

Usage : python quality_indicators.py <records.csv> <output.json>
"""
import sys, json, itertools
import numpy as np
import pandas as pd

P = ["pH", "EC_dSm", "OC_pct", "N_kg_ha", "P_kg_ha", "K_kg_ha",
     "S_ppm", "Zn_ppm", "B_ppm", "Fe_ppm", "Mn_ppm", "Cu_ppm"]
# Plausibility limits (Table 8)
LIM = {"pH": (3, 11), "EC_dSm": (0, 20), "OC_pct": (0, 5), "N_kg_ha": (0, 1500),
       "P_kg_ha": (0, 300), "K_kg_ha": (0, 2500), "S_ppm": (0, 200), "Zn_ppm": (0, 50),
       "B_ppm": (0, 20), "Fe_ppm": (0, 500), "Mn_ppm": (0, 300), "Cu_ppm": (0, 50)}
# SHC fertility classes (Table 6)
CLS3 = {"OC_pct": (0.5, 0.75), "N_kg_ha": (280, 560), "P_kg_ha": (10, 25), "K_kg_ha": (120, 280)}
DEF = {"S_ppm": 10, "Zn_ppm": 0.6, "B_ppm": 0.5, "Fe_ppm": 4.5, "Mn_ppm": 2.0, "Cu_ppm": 0.2}


def main(src, out):
    d = pd.read_csv(src, low_memory=False)
    for c in P:
        d[c] = pd.to_numeric(d[c], errors="coerce")
    n = len(d)
    r = {"n_records": n}

    # 1. Out-of-range and impossible values
    flag = pd.concat([~d[c].between(*LIM[c]) & d[c].notna() for c in P], axis=1)
    flag.columns = P
    anyflag = flag.any(axis=1)
    neg = (d[P] < 0).any(axis=1)
    imp = neg | (d.pH > 14) | (d.OC_pct > 100)
    r["out_of_range"] = {"records": int(anyflag.sum()), "pct": round(100 * anyflag.mean(), 2),
                         "by_property": {c: int(flag[c].sum()) for c in P}}
    r["impossible"] = {"records": int(imp.sum()), "negative": int(neg.sum()),
                       "pH_gt_14": int((d.pH > 14).sum()), "OC_gt_100": int((d.OC_pct > 100).sum()),
                       "pH_eq_0": int((d.pH == 0).sum())}
    r["out_of_range_pct_by_state"] = (anyflag.groupby(d.state_name).mean() * 100).round(1).to_dict()
    key = [d.state_name, d.dist_code]
    size = d.groupby(key).size()
    rate = anyflag.groupby(key).mean()
    r["districts_ge200"] = int((size >= 200).sum())
    r["districts_ge200_gt5pct"] = int((rate[size >= 200] > 0.05).sum())

    # 2. Zero values
    n0 = d.N_kg_ha == 0
    lay = n0.groupby(d.layer_name).mean()
    zl = lay[lay >= 0.95].index
    r["zeros"] = {"N": int(n0.sum()), "N_pct": round(100 * n0.mean(), 2),
                  "N_layers_ge95pct_zero": int(len(zl)),
                  "N_zero_in_those_layers": int((n0 & d.layer_name.isin(zl)).sum()),
                  "B": int((d.B_ppm == 0).sum()), "S": int((d.S_ppm == 0).sum())}

    # 3. Repeated measurement vectors (same 12 values, same layer)
    v = d.dropna(subset=P, thresh=10)
    vec = v[P].round(4).astype(str).agg("|".join, axis=1)
    rep = v.assign(_k=vec).duplicated(["layer_name", "_k"], keep=False)
    r["repeated"] = {"records": int(rep.sum()), "pct_of_all": round(100 * rep.sum() / n, 2),
                     "by_state_pct": (rep.groupby(v.state_name).mean() * 100).round(1).to_dict()}

    # 4. Change over cycles
    r["out_of_range_pct_by_cycle"] = (anyflag.groupby(d.cycle).mean() * 100).round(1).to_dict()
    r["share_2023_25_pct"] = round(100 * d.cycle.isin(["2023-24", "2024-25"]).mean(), 1)

    # 5. Clustered sampling (records with village names)
    vv = d[d.village.notna() & (d.village.astype(str).str.strip() != "")]
    g = vv.groupby(["layer_name", "village"]).size()
    r["villages"] = {"unique_state_district_village":
                     int(vv.drop_duplicates(["state_name", "dist_code", "village"]).shape[0]),
                     "median_records_per_village": float(g.median()),
                     "villages_gt50": int((g > 50).sum()), "records_in_them": int(g[g > 50].sum())}

    # Screened data (used for Table 6 and Table 9)
    s = d.copy()
    for c in P:
        s.loc[~s[c].between(*LIM[c]), c] = np.nan
    s.loc[s.N_kg_ha <= 0, "N_kg_ha"] = np.nan

    # 6. Table 6 statistics after screening
    t6 = {}
    for c in P:
        x = s[c].dropna(); q = x.quantile([.25, .5, .75])
        e = {"n": int(len(x)), "missing_pct": round(100 * (n - len(x)) / n, 2),
             "mean": round(x.mean(), 2), "median": round(q[.5], 2),
             "p25": round(q[.25], 2), "p75": round(q[.75], 2)}
        if c in CLS3:
            lo, hi = CLS3[c]
            e.update(low=round(100 * (x < lo).mean(), 2), medium=round(100 * x.between(lo, hi).mean(), 2),
                     high=round(100 * (x > hi).mean(), 2))
        if c in DEF:
            e.update(deficient=round(100 * (x < DEF[c]).mean(), 2))
        t6[c] = e
    r["table6"] = t6

    # 7. District-boundary effect (Table 9)
    s["bi"] = np.floor(s.lat / 0.2).astype(int)
    s["bj"] = np.floor(s.lon / 0.2).astype(int)
    s["dk"] = s.state_name + "|" + s.dist_code.astype(str)
    gr = s.groupby(["cycle", "bi", "bj", "dk"])
    med = gr[["pH", "OC_pct", "N_kg_ha", "K_kg_ha"]].median().join(gr.size().rename("n"))
    med = med[med.n >= 10].reset_index()
    t9 = {}
    for prop in ["pH", "OC_pct", "N_kg_ha", "K_kg_ha"]:
        m = med.dropna(subset=[prop])
        between = [abs(a - b) for _, grp in m.groupby(["cycle", "bi", "bj"]) if len(grp) > 1
                   for a, b in itertools.combinations(grp[prop].values, 2)]
        dd = m.set_index(["cycle", "dk", "bi", "bj"])[prop].to_dict()
        within = [abs(val - dd[(cy, dk, i + di, j + dj)]) for (cy, dk, i, j), val in dd.items()
                  for di, dj in ((1, 0), (0, 1)) if (cy, dk, i + di, j + dj) in dd]
        t9[prop] = {"different_districts_same_cell": round(float(np.median(between)), 3),
                    "same_district_adjacent_cells": round(float(np.median(within)), 3),
                    "ratio": round(float(np.median(between) / np.median(within)), 2),
                    "pairs_between": len(between), "pairs_within": len(within)}
    r["table9_boundary_effect"] = t9

    json.dump(r, open(out, "w"), indent=1)
    print(json.dumps({k: r[k] for k in ["n_records", "out_of_range", "impossible", "zeros",
                                         "out_of_range_pct_by_cycle", "villages",
                                         "table9_boundary_effect"]}, indent=1))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
