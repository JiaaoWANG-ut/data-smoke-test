# Data Smoke Test (Hands-on Demo)

> **What this repo is**  
> A **data smoke test** for the manuscript analysis pipeline: confirm that
> shipped numerical products load correctly, that the plotting scripts run,
> and that expected figure artifacts are produced on a normal desktop —
> **without** GPUs, OVITO, or full MD dumps.
>
> **What this case is**  
> The files here are **one representative case** (metal–metal / M–M bond vs
> time). The same smoke-test pattern applies to other analyses in the full
> methods package (entropy, contact ratio, bond angles, coordination, …).

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22816324.svg)](https://doi.org/10.5281/zenodo.22816324)
[![License: CC BY-NC 4.0](https://img.shields.io/badge/License-CC%20BY--NC%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc/4.0/)

**Full original scripts & data (all analysis cases):**  
DOI [`10.5281/zenodo.22816324`](https://doi.org/10.5281/zenodo.22816324) ·  
Record: [https://zenodo.org/records/22816324](https://zenodo.org/records/22816324)

This GitHub repo is only a **data smoke-test slice**. The complete Methods package
lives on Zenodo at the link above.

**License:** [CC BY-NC 4.0](LICENSE) — free for non-commercial use with attribution;
**commercial use is not permitted.**

---

## Smoke-test goal

Pass / fail in under a few minutes:

| Check | Pass criterion |
|-------|----------------|
| Dependencies install | `pip install -r requirements.txt` succeeds |
| Script runs | `python plot_MM_bond_time.py --plot-only` exits 0 |
| Outputs appear | `MM_bond_time.png`, `.svg`, and `.csv` are written |
| Runtime | Typically **1–3 seconds** on a normal desktop |
| Sanity | Figure shows six temperatures (1500–3000 K); high-T curves rise |

If those hold, the **data product + plotting path** for this case is healthy.

---

## This case (example)

**Case ID:** M–M bond time series  
**Script:** `plot_MM_bond_time.py`  
**Shipped data:** `MM_bond_time_data.npz` / `MM_bond_time_data.csv`  
**Reference figure:**

![Data smoke test — example case output](MM_bond_time.png)

Other cases in the full deposit follow the same idea: ship a small numerical
cache (or tiny demo dump) + a one-command plot/rebuild path.

---

## Repository layout

```text
data-smoke-test/
├── README.md / README_zh.md       # Smoke-test instructions
├── requirements.txt               # Minimal deps for this case
├── plot_MM_bond_time.py           # Case script (plot from cache)
├── MM_bond_time_data.npz          # ★ Original numerical product
├── MM_bond_time_data.csv          # ★ Same data, tabular
├── MM_bond_time.png / .svg        # Reference outputs
├── MM_bond_time_methods.md        # Case method notes
├── Supplementary_Methods.md       # Related method notes
└── example_gpumd_run/             # Example GPUMD inputs / thermo
```

---

## System requirements

| Item | Requirement |
|------|-------------|
| OS | Windows 10/11, macOS, or Linux |
| Python | **3.10+** (tested on 3.13) |
| GPU | **Not required** for the smoke test |
| RAM | ≥ 4 GB |

```text
numpy>=1.22
matplotlib>=3.5
```

Optional: `ovito` — only if you recompute this case from raw `dump.xyz`
(not part of the smoke test).

---

## Run the smoke test

### 1. Clone

```bash
git clone https://github.com/JiaaoWANG-ut/data-smoke-test.git
cd data-smoke-test
```

### 2. Install

```bash
python -m venv .venv
# Windows: .\.venv\Scripts\Activate.ps1
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
```

Typical install time: **1–3 minutes**.

### 3. Execute (this case)

```bash
python plot_MM_bond_time.py --plot-only
```

### 4. Expected console output

```text
Saved: .../MM_bond_time_data.csv
Saved: .../MM_bond_time.png
Saved: .../MM_bond_time.svg
```

### 5. Expected artifacts

| File | Meaning |
|------|---------|
| `MM_bond_time.png` | Raster figure |
| `MM_bond_time.svg` | Vector figure |
| `MM_bond_time_data.csv` | Long-format table regenerated from NPZ |

---

## Shipped data (this case)

### CSV columns (`MM_bond_time_data.csv`)

| Column | Type | Description |
|--------|------|-------------|
| `temperature_K` | int | Simulation temperature (1500, 1600, 1800, 2000, 2500, 3000) |
| `time_ps` | float | Frame time in picoseconds |
| `frame_index` | int | Index in the original 2500-frame trajectory |
| `n_pure` | int | Number of metal atoms counted as M–M bonded |
| `n_err` | float | Uncertainty σ = √n_pure (Poisson) |

Example (first rows are near-zero at 1500 K):

```csv
temperature_K,time_ps,frame_index,n_pure,n_err
1500,2.000000,0,0,0.000000
1500,14.000000,6,0,0.000000
```

### Quick inspect

```python
import numpy as np
d = np.load("MM_bond_time_data.npz", allow_pickle=True)
print("temperatures:", d["temperatures"])
print("3000 K n_pure max:", d["3000_n_pure"].max())
```

---

## Case science (brief)

For metal atoms M in {Fe, Co, Ni}:

- `CN_O`: O neighbours with r &lt; 2.5 Å  
- `CN_metal`: Fe/Co/Ni neighbours with r &lt; 3.0 Å  

Counted when `CN_O = 0` and `CN_metal > 0`.  
Full notes: [`MM_bond_time_methods.md`](MM_bond_time_methods.md).

### Expected trend (sanity check for this case)

| T (K) | Typical `n_pure` behaviour |
|------:|----------------------------|
| 1500–2000 | Near zero for most/all frames (oxide-dominated local shells) |
| 2500 | Rises at later times (order 10²–10³) |
| 3000 | Strong rise earlier; can reach ~2000+ by the end |

---

## CLI flags (this case)

| Flag | Role in smoke test |
|------|--------------------|
| `--plot-only` | **Use this.** Load shipped NPZ; write figure + CSV. |
| `--force` | Outside smoke test: recompute from dumps (needs OVITO + trajectories). |

---

## Troubleshooting

| Symptom | Action |
|---------|--------|
| Missing numpy/matplotlib | `pip install -r requirements.txt` |
| Missing NPZ | Restore `MM_bond_time_data.npz` from git |
| Missing ovito / dumps | Stay on `--plot-only` — that is the smoke test |

---

## Relation to the full methods package

Full original scripts (all cases) are archived on Zenodo:

- **DOI:** [10.5281/zenodo.22816324](https://doi.org/10.5281/zenodo.22816324)
- **Record:** [https://zenodo.org/records/22816324](https://zenodo.org/records/22816324)

```text
Zenodo deposit → Methods/
  entropy/              ← other cases
  contact ratio/        ← other cases
  bond angle analysis/  ← other cases
  coordination number/  ← other cases
  M-M bonds/            ← THIS smoke-test case (isolated here)
```

Use this repo to verify “cached data → script → figure” end-to-end. Add
parallel smoke tests for other cases the same way: small data product +
one command + expected outputs / runtime.

---

## Citation

If you use this smoke test or the full analysis code, please cite:

- Zenodo archive (full scripts): [10.5281/zenodo.22816324](https://doi.org/10.5281/zenodo.22816324)  
  ([https://zenodo.org/records/22816324](https://zenodo.org/records/22816324))
- The associated manuscript

---

## License

This repository is licensed under
**[Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)](LICENSE)**.

- You may share and adapt the materials for **non-commercial** purposes with attribution.
- **Commercial use is prohibited.**
- Full terms: [https://creativecommons.org/licenses/by-nc/4.0/](https://creativecommons.org/licenses/by-nc/4.0/)
