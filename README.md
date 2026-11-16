# india-shc-quality-assessment

Code and aggregated statistics for the paper:

> Gupta, K., Sisaudia, V. (2026). **A national quality assessment of India's Soil Health Card soil nutrient data.** Manuscript submitted to *Geoderma Regional*.

The study assesses the quality of 345,288 topsoil records from India's Soil Health Card (SHC) programme. The records cover 737 districts, 28 states, 5 union territories and six SHC cycles (2015–2026).

## What is in this repository

| Folder | Content | Licence |
|---|---|---|
| `data/` | Aggregated national, state and district statistics (6 CSV files) | CC BY 4.0 |
| `scripts/` | Python scripts for the quality indicators, summary statistics and Fig. 5 | MIT |
| `Figure/` | Fig. 5 of the paper | CC BY 4.0 |

**The record-level SHC data are not included.** The SHC measurements are produced and owned by the Department of Agriculture and Farmers Welfare (DA&FW), Government of India. They can be viewed on the SHC public portal (https://soilhealth.dac.gov.in), which is accessible only from within India. Researchers who need record-level data should contact the concerned District Agriculture Department.

The files in `data/` contain **no individual records, sample identifiers, coordinates or village names**. Any group with fewer than 10 records is left out.

## Data files

| File | One row per | Rows |
|---|---|---|
| `national_summary.csv` | India | 1 |
| `national_cycle_summary.csv` | SHC cycle | 6 |
| `state_summary.csv` | State / UT | 32 |
| `state_cycle_summary.csv` | State / UT × cycle | 116 |
| `district_allcycles_summary.csv` | District (LGD code) | 710 |
| `district_cycle_summary.csv` | District × cycle | 1,881 |

### Columns

- **Grouping keys:** `state_name`, `state_code`, `dist_code` (Local Government Directory code), `district_name`, `cycle`.
- **`n_samples`**: number of records in the group.
- **`pct_flag_range`**: % of records with at least one value outside the plausibility limits below.
- **`pct_N_zero`**: % of records with available nitrogen recorded as exactly 0 (most likely not analysed).
- **`pct_repeat_vector`**: % of records whose values are identical to another record in the same district-cycle layer.
- For each property X in `pH, EC_dSm, OC_pct, N_kg_ha, P_kg_ha, K_kg_ha, S_ppm, Zn_ppm, B_ppm, Fe_ppm, Mn_ppm, Cu_ppm`:
  - `X_n`: number of valid values after screening
  - `X_p25`, `X_median`, `X_p75`: 25th percentile, median and 75th percentile
- `OC_pct_pct_low/med/high`, `N_kg_ha_…`, `P_kg_ha_…`, `K_kg_ha_…`: % in the SHC fertility classes.
  - Organic carbon: < 0.5, 0.5–0.75, > 0.75 %
  - Nitrogen: < 280, 280–560, > 560 kg/ha
  - Phosphorus: < 10, 10–25, > 25 kg/ha
  - Potassium: < 120, 120–280, > 280 kg/ha
- `S/Zn/B/Fe/Mn/Cu_pct_deficient`: % below the SHC deficiency limit (sulphur 10, zinc 0.6, boron 0.5, iron 4.5, manganese 2.0, copper 0.2 ppm).

Units: EC in dS/m; organic carbon in %; nitrogen, phosphorus and potassium in kg/ha; the rest in ppm.

### Screening applied before computing statistics

- **Out-of-range values set to missing.** Plausibility limits:

  | Property | Limits |
  |---|---|
  | pH | 3–11 |
  | EC | 0–20 dS/m |
  | Organic carbon | 0–5 % |
  | Nitrogen | 0–1500 kg/ha |
  | Phosphorus | 0–300 kg/ha |
  | Potassium | 0–2500 kg/ha |
  | Sulphur | 0–200 ppm |
  | Zinc | 0–50 ppm |
  | Boron | 0–20 ppm |
  | Iron | 0–500 ppm |
  | Manganese | 0–300 ppm |
  | Copper | 0–50 ppm |

- **Available nitrogen = 0 treated as missing.**
- **Zeros of the other properties kept**, because they may be values below the detection limit.

## Scripts

All scripts take a CSV of SHC records as input (not provided here). The CSV must have these columns:

```
layer_name, state_name, state_code, dist_code, district_name, cycle, village, lat, lon,
pH, EC_dSm, OC_pct, N_kg_ha, P_kg_ha, K_kg_ha, S_ppm, Zn_ppm, B_ppm, Fe_ppm, Mn_ppm, Cu_ppm
```

| Script | What it produces | Paper |
|---|---|---|
| `quality_indicators.py <records.csv> <out.json>` | Out-of-range values, zero values, repeated records, change over cycles, village clustering, Table 6 statistics, district-boundary effect | Section 6.1, Tables 6, 8, 9 |
| `make_summary_stats.py <records.csv> <out_folder>` | The six CSV files in `data/` | Table 3 |
| `make_fig5.py <records.csv> <out_folder>` | Fig. 5 | Fig. 5 |

Install the requirements with `pip install -r requirements.txt` (Python 3.9 or newer).

## Important limitations

- **The records are a spatially systematic sample of the SHC portal, not a complete copy.** Record counts are **not** the number of samples analysed in a district.
- **Each record's location is known only to within about 1.1 km.**
- **Source data quality varies between districts and laboratories.** See Section 6 of the paper.

## Citation

Please cite the paper and this archive (see `CITATION.cff` or the Zenodo DOI badge).

## Contact

Khushbu Gupta, Delhi Technological University, khushbugupta_23phdit504@dtu.ac.in
