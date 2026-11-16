# Usage: python make_summary_stats.py <records.csv> <output_folder>
"""Build aggregated (non-record-level) summary statistics from a CSV of SHC records.
No individual sample, coordinate, village or sample_id is written out.
Groups with fewer than MIN_N samples are suppressed."""
import pandas as pd, numpy as np, sys, os
SRC, OUT = sys.argv[1], sys.argv[2]
MIN_N = 10
P = ['pH','EC_dSm','OC_pct','N_kg_ha','P_kg_ha','K_kg_ha','S_ppm','Zn_ppm','B_ppm','Fe_ppm','Mn_ppm','Cu_ppm']
LIM = {'pH':(3.0,11.0),'EC_dSm':(0,20),'OC_pct':(0,5),'N_kg_ha':(0,1500),'P_kg_ha':(0,300),'K_kg_ha':(0,2500),
       'S_ppm':(0,200),'Zn_ppm':(0,50),'B_ppm':(0,20),'Fe_ppm':(0,500),'Mn_ppm':(0,300),'Cu_ppm':(0,50)}
CLS3 = {'OC_pct':(0.5,0.75),'N_kg_ha':(280,560),'P_kg_ha':(10,25),'K_kg_ha':(120,280)}
DEF = {'B_ppm':0.5,'Fe_ppm':4.5,'Zn_ppm':0.6,'Cu_ppm':0.2,'S_ppm':10.0,'Mn_ppm':2.0}
d = pd.read_csv(SRC, low_memory=False)
raw = d[P].apply(pd.to_numeric, errors='coerce')
d['flag_range'] = pd.concat([~raw[c].between(*LIM[c]) & raw[c].notna() for c in P], axis=1).any(axis=1)
d['flag_zeroN'] = raw.N_kg_ha == 0
full = raw.round(4).astype(str).agg('|'.join, axis=1)
d['flag_repeat'] = full.groupby([d.layer_name, full]).transform('size') > 1
clean = raw.copy()
for c in P: clean.loc[~clean[c].between(*LIM[c]), c] = np.nan
clean.loc[clean.N_kg_ha <= 0, 'N_kg_ha'] = np.nan
for c in P: d['v_'+c] = clean[c]

def summarise(g):
    r = {'n_samples': len(g), 'pct_flag_range': round(100*g.flag_range.mean(),2),
         'pct_N_zero': round(100*g.flag_zeroN.mean(),2), 'pct_repeat_vector': round(100*g.flag_repeat.mean(),2)}
    for c in P:
        v = g['v_'+c].dropna()
        r[f'{c}_n'] = len(v)
        if len(v) >= MIN_N:
            r[f'{c}_p25'], r[f'{c}_median'], r[f'{c}_p75'] = [round(x,3) for x in v.quantile([.25,.5,.75])]
        else:
            r[f'{c}_p25']=r[f'{c}_median']=r[f'{c}_p75']=np.nan
        if c in CLS3 and len(v) >= MIN_N:
            lo, hi = CLS3[c]
            r[f'{c}_pct_low']=round(100*(v<lo).mean(),1); r[f'{c}_pct_med']=round(100*v.between(lo,hi).mean(),1); r[f'{c}_pct_high']=round(100*(v>hi).mean(),1)
        if c in DEF and len(v) >= MIN_N:
            r[f'{c}_pct_deficient']=round(100*(v<DEF[c]).mean(),1)
    return pd.Series(r)

def build(keys, name):
    rows=[]
    for k,g in d.groupby(keys, dropna=False):
        k = k if isinstance(k,tuple) else (k,)
        r = dict(zip(keys,k)); r.update(summarise(g).to_dict()); rows.append(r)
    t = pd.DataFrame(rows)
    t = t[t.n_samples >= MIN_N]
    t.to_csv(os.path.join(OUT, name), index=False)
    print(name, t.shape)
    return t
build(['state_name','state_code','dist_code','district_name','cycle'], 'district_cycle_summary.csv')
build(['state_name','state_code','dist_code','district_name'], 'district_allcycles_summary.csv')
build(['state_name','cycle'], 'state_cycle_summary.csv')
build(['state_name'], 'state_summary.csv')
d['all']='India'; build(['all','cycle'], 'national_cycle_summary.csv'); build(['all'], 'national_summary.csv')
