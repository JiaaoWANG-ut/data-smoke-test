# Hands-on Tutorial: M–M Bond Analysis from GPUMD Trajectories

> **Purpose of this repository**  
> A self-contained **demo** that shows exactly how to use `plot_MM_bond_time.py`
> to reproduce the metal–metal (M–M) bonding vs time figure.  
> You can regenerate the publication-style plot from the **shipped original
> numerical data** in ~1–3 seconds — no GPU, no OVITO, no full MD dumps required.

---

## What you will get

After following this tutorial you will:

1. Install a minimal Python environment
2. Run the analysis script in **plot-only** mode
3. Regenerate `MM_bond_time.png` / `.svg` / `.csv` from the original NPZ data
4. Understand what each column / key means
5. Know how to recompute from raw `dump.xyz` trajectories (advanced)

**Reference figure** (already included; your run should recreate it):

![M–M bonding vs time](MM_bond_time.png)

---

## Repository contents

```text
mm-bond-hands-on-tutorial/
├── README.md                      # This tutorial
├── requirements.txt               # Minimal Python dependencies
├── plot_MM_bond_time.py           # Main analysis / plotting script
│
├── MM_bond_time_data.npz          # ★ Original numerical results (binary)
├── MM_bond_time_data.csv          # ★ Same data as long-format CSV (human-readable)
├── MM_bond_time.png               # Reference PNG figure (600 dpi)
├── MM_bond_time.svg               # Reference SVG figure
│
├── MM_bond_time_methods.md        # Detailed method notes (Chinese)
├── Supplementary_Methods.md       # Related entropy method notes
│
└── example_gpumd_run/             # Example GPUMD inputs / thermo (not dumps)
    ├── model.xyz.gz               # Example initial structure
    ├── run.in                     # Example GPUMD input
    ├── gpumd.slurm                # Example Slurm submit script
    ├── thermo.out                 # Example thermodynamics output
    ├── neighbor.out               # Neighbor list output
    └── analyze_metal_coordination.py
```

### What “original data” means here

| File | Role |
|------|------|
| `MM_bond_time_data.npz` | Cached statistics for **6 temperatures × 400 frames** (2400 points). This is the primary original result used by the demo. |
| `MM_bond_time_data.csv` | Identical content in CSV form for Excel / pandas. |
| `example_gpumd_run/` | Example **simulation inputs** and thermo logs used to set up / check runs. |

> **Note:** Full multi-temperature `dump.xyz` trajectories are large and are
> **not** shipped in this demo repo. The NPZ/CSV already contain the
> post-processed counts needed to remake the figure. To recompute from
> trajectories, see [Advanced: recompute from dumps](#advanced-recompute-from-dumps).

---

## System requirements

| Item | Requirement |
|------|-------------|
| OS | Windows 10/11, macOS, or Linux |
| Python | **3.10+** (tested on 3.13) |
| RAM | ≥ 4 GB (demo needs far less) |
| GPU | **Not required** for this demo |
| Disk | ~50 MB |

### Python packages

```text
numpy>=1.22
matplotlib>=3.5
```

(`scipy`, `Pillow`, `openpyxl` are listed in `requirements.txt` for consistency
with the parent methods package; the demo script itself only needs **numpy** and
**matplotlib**.)

Optional (only for recomputing from `dump.xyz`):

```text
ovito   # OVITO Python module
```

---

## Quick start (recommended path — ~2 minutes)

### Step 1 — Clone the repository

```bash
git clone https://github.com/JiaaoWANG-ut/mm-bond-hands-on-tutorial.git
cd mm-bond-hands-on-tutorial
```

### Step 2 — Create a virtual environment (recommended)

**Windows (PowerShell):**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**Linux / macOS:**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Typical install time on a normal desktop: **1–3 minutes**.

### Step 3 — Run the demo

```bash
python plot_MM_bond_time.py --plot-only
```

### Step 4 — Check the outputs

You should see console lines like:

```text
Saved: .../MM_bond_time_data.csv
Saved: .../MM_bond_time.png
Saved: .../MM_bond_time.svg
```

Open `MM_bond_time.png`. You should see **six temperature curves**
(1500–3000 K), log-scaled time axis, and shaded Poisson error bands.
Expected runtime: **about 1–3 seconds**.

---

## Command-line options

```bash
python plot_MM_bond_time.py --plot-only   # Use shipped NPZ only (demo)
python plot_MM_bond_time.py              # Prefer NPZ if present; else compute
python plot_MM_bond_time.py --force      # Recompute from dump.xyz (needs OVITO + dumps)
```

| Flag | Meaning |
|------|---------|
| `--plot-only` | **Demo mode.** Load `MM_bond_time_data.npz` and write figure + CSV. Fails if NPZ is missing. |
| `--force` | Ignore cache; re-analyse trajectories under `{T}K/gpumd/dump.xyz[.gz]`. |
| *(none)* | If NPZ exists, load it; otherwise try to analyse dumps. |

---

## Understanding the original data

### CSV columns (`MM_bond_time_data.csv`)

| Column | Type | Description |
|--------|------|-------------|
| `temperature_K` | int | Simulation temperature (1500, 1600, 1800, 2000, 2500, 3000) |
| `time_ps` | float | Frame time in picoseconds |
| `frame_index` | int | Index in the original 2500-frame trajectory |
| `n_pure` | int | Number of metal atoms counted as M–M bonded |
| `n_err` | float | Uncertainty \(\sigma = \sqrt{n_\mathrm{pure}}\) (Poisson) |

Example (first rows are near-zero at 1500 K):

```csv
temperature_K,time_ps,frame_index,n_pure,n_err
1500,2.000000,0,0,0.000000
1500,14.000000,6,0,0.000000
```

### Inspect with Python

```python
import numpy as np
import pandas as pd

# NPZ
d = np.load("MM_bond_time_data.npz", allow_pickle=True)
print(list(d.files))
print("temperatures:", d["temperatures"])
print("3000 K times:", d["3000_times_ps"][:5])
print("3000 K counts:", d["3000_n_pure"][:5])

# CSV
df = pd.read_csv("MM_bond_time_data.csv")
print(df.groupby("temperature_K")["n_pure"].agg(["min", "max", "mean"]))
```

### NPZ keys (per temperature `T`)

For each `T` in `{1500,1600,1800,2000,2500,3000}`:

| Key | Content |
|-----|---------|
| `{T}_times_ps` | Sampled times (ps), length 400 |
| `{T}_n_pure` | M–M bond counts |
| `{T}_n_err` | Poisson errors |
| `{T}_frame_indices` | Frame indices in the dump |
| `{T}_dump_path` | Original dump path on the analysis machine (informational) |
| `{T}_temp_k` | Temperature scalar |

Plus global key `temperatures`.

---

## What the script computes (science summary)

**System:** ternary Fe–Co–Ni–O nanoparticle (`ternay-FeCoNi-2`).

For each metal atom \(M \in \{\mathrm{Fe},\mathrm{Co},\mathrm{Ni}\}\):

| Quantity | Cutoff | Meaning |
|----------|--------|---------|
| \(\mathrm{CN_O}\) | \(r < 2.5\) Å | O neighbours in the first shell |
| \(\mathrm{CN_{metal}}\) | \(r < 3.0\) Å | Fe/Co/Ni neighbours |

An atom contributes to the M–M bond count if:

```text
CN_O = 0   AND   CN_metal > 0
```

i.e. an **oxygen-free** first shell that still has at least one metal neighbour.
Per-frame count \(N = n_\mathrm{pure}\); error band \(\pm\sqrt{N}\).

Trajectory protocol (when dumps are available):

- GPUMD dumps, 2500 frames, 2 ps spacing → **2–5000 ps**
- Uniform subsample of **400 frames** per temperature
- PBC-aware neighbour search (OVITO `CutoffNeighborFinder`)

More detail: [`MM_bond_time_methods.md`](MM_bond_time_methods.md).

---

## Expected scientific trend (sanity check)

| T (K) | Typical `n_pure` behaviour |
|------:|----------------------------|
| 1500–2000 | Near zero for most/all frames (oxide-dominated local shells) |
| 2500 | Rises at later times (order \(10^2\)–\(10^3\)) |
| 3000 | Strong rise earlier; can reach ~2000+ by the end |

If your remade figure matches the shipped PNG and shows this trend, the demo succeeded.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `ModuleNotFoundError: numpy` / `matplotlib` | Activate venv and `pip install -r requirements.txt` |
| `Missing cache: ... MM_bond_time_data.npz` | You used `--plot-only` but NPZ is missing — restore it from git |
| `No module named 'ovito'` with `--force` | Install OVITO Python **or** stay on `--plot-only` |
| `No dump file for XXX K` | Full dumps are not in this repo; use `--plot-only` |
| Figure fonts look different | Script falls back to DejaVu Sans if Arial/Helvetica are absent — curves/data are unchanged |
| PowerShell blocks `Activate.ps1` | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once, then retry |

---

## Advanced: recompute from dumps

1. Install OVITO Python: `pip install ovito`
2. Place trajectories next to the script as:

   ```text
   1500K/gpumd/dump.xyz.gz
   1600K/gpumd/dump.xyz.gz
   ...
   3000K/gpumd/dump.xyz
   ```

3. Run:

   ```bash
   python plot_MM_bond_time.py --force
   ```

This overwrites `MM_bond_time_data.npz` and regenerates figures. Runtime depends
on dump size (often several minutes per temperature on a desktop).

Example GPUMD `run.in` / structure files are under [`example_gpumd_run/`](example_gpumd_run/).
Edit the `potential` path before submitting real jobs.

---

## How this demo maps to the full methods package

In the full manuscript code deposit, this material lives under:

```text
Methods/M-M bonds/
```

This repository isolates that workflow as a **standalone teaching / software
demo**: minimal dependencies, shipped numerical data, and a one-command figure
reproduction path suitable for software checklists (system requirements,
installation, demo, instructions for use).

---

## Citation

If you use this script or data in a publication, please cite the associated
manuscript and the archival code deposit (e.g. Zenodo DOI when published).

---

## License

Code and demo data in this repository are provided for research reproducibility.
See the manuscript / Zenodo record for the formal license statement
(default intent: **CC-BY-4.0** for accompanying materials unless otherwise noted).
