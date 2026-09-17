#!/usr/bin/env python3
"""
Metal–metal (M–M) bond statistics vs time for six temperatures.

For each GPUMD dump.xyz trajectory, uniformly sample 400 frames and count
metal atoms (Fe/Co/Ni) whose first shell is O-free and M-coordinated:
  CN_O(r < R_O) = 0  and  CN_metal(r < R_M) > 0.

Error bands show ± sqrt(N) (Poisson) at each sampled frame.

Outputs (Nature-style): MM_bond_time.png, MM_bond_time.svg
"""

import os
import warnings

warnings.filterwarnings("ignore", message=".*OVITO.*PyPI")

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import cm
from matplotlib.colors import Normalize

ROOT = os.path.dirname(os.path.abspath(__file__))
N_SAMPLE = 400
O_CUT = 2.5   # Å — upper bound of first O shell
MET_CUT = 3.0  # Å — first-shell metal contact
METALS = ("Fe", "Co", "Ni")
TIME_STEP_FS = 1.0
TEMPERATURES = (1500, 1600, 1800, 2000, 2500, 3000)
DATA_NPZ = os.path.join(ROOT, "MM_bond_time_data.npz")
OUT_CSV = os.path.join(ROOT, "MM_bond_time_data.csv")
OUT_PNG = os.path.join(ROOT, "MM_bond_time.png")
OUT_SVG = os.path.join(ROOT, "MM_bond_time.svg")
ERR_BAND_ALPHA = 0.42


def dump_path(temp_k: int) -> str:
    gpumd = os.path.join(ROOT, f"{temp_k}K", "gpumd")
    for name in ("dump.xyz", "dump.xyz.gz"):
        path = os.path.join(gpumd, name)
        if os.path.isfile(path):
            return path
    raise FileNotFoundError(f"No dump file for {temp_k} K under {gpumd}")


def apply_nature_style():
    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
            "font.size": 7,
            "axes.labelsize": 8,
            "axes.titlesize": 8,
            "xtick.labelsize": 7,
            "ytick.labelsize": 7,
            "legend.fontsize": 6.5,
            "axes.linewidth": 0.6,
            "xtick.major.width": 0.6,
            "ytick.major.width": 0.6,
            "xtick.major.size": 3,
            "ytick.major.size": 3,
            "lines.linewidth": 1.0,
            "figure.dpi": 150,
            "savefig.dpi": 600,
            "savefig.bbox": "tight",
            "savefig.pad_inches": 0.02,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )


def apply_nature_spines(ax):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_linewidth(0.6)
    ax.tick_params(axis="both", direction="in", length=3, width=0.6)


def sample_frame_indices(n_frames: int, n_sample: int = N_SAMPLE) -> np.ndarray:
    if n_frames <= n_sample:
        return np.arange(n_frames, dtype=int)
    return np.unique(np.round(np.linspace(0, n_frames - 1, n_sample)).astype(int))


def frame_time_ps(data, fidx: int) -> float:
    step_fs = float(data.attributes.get("Time", (fidx + 1) * 2000))
    return step_fs * TIME_STEP_FS / 1000.0


def metal_mm_stats(data):
    """Count M atoms with O-free first shell and at least one M neighbor."""
    from ovito.data import CutoffNeighborFinder

    pt = data.particles["Particle Type"]
    ptypes = data.particles.particle_types
    metal_ids = {ptypes.type_by_name(s).id for s in METALS}
    o_id = ptypes.type_by_name("O").id
    metal_idx = np.where(np.isin(pt, list(metal_ids)))[0]
    if len(metal_idx) == 0:
        return 0.0, 0.0

    finder_o = CutoffNeighborFinder(O_CUT, data)
    finder_m = CutoffNeighborFinder(MET_CUT, data)
    n_pure = 0
    for i in metal_idx:
        cn_o = sum(1 for nb in finder_o.find(i) if pt[nb.index] == o_id)
        if cn_o > 0:
            continue
        cn_m = sum(1 for nb in finder_m.find(i) if pt[nb.index] in metal_ids)
        if cn_m > 0:
            n_pure += 1

    err = float(np.sqrt(n_pure)) if n_pure > 0 else 0.0
    return float(n_pure), err


def analyze_temperature(temp_k: int):
    from ovito.io import import_file

    path = dump_path(temp_k)
    print(f"\n[{temp_k} K] {path}")
    pipeline = import_file(path)
    n_frames = pipeline.source.num_frames
    frame_indices = sample_frame_indices(n_frames)
    sample_set = set(int(i) for i in frame_indices)
    sequential = path.endswith(".gz")
    print(
        f"  total frames: {n_frames}, sampled: {len(frame_indices)}, "
        f"mode: {'sequential' if sequential else 'indexed'}"
    )

    times = []
    n_pure = []
    n_err = []
    kept_indices = []

    def process_frame(fidx, data):
        t_ps = frame_time_ps(data, fidx)
        count, err = metal_mm_stats(data)
        kept_indices.append(fidx)
        times.append(t_ps)
        n_pure.append(count)
        n_err.append(err)
        k = len(times)
        if k % 50 == 0 or k == len(frame_indices):
            print(
                f"  [{k:3d}/{len(frame_indices)}]  t={t_ps:8.2f} ps  "
                f"N={count:.0f} ± {err:.1f}"
            )

    if sequential:
        for fidx in range(n_frames):
            data = pipeline.compute(fidx)
            if fidx in sample_set:
                process_frame(fidx, data)
    else:
        for fidx in sorted(sample_set):
            data = pipeline.compute(fidx)
            process_frame(fidx, data)

    return {
        "temp_k": temp_k,
        "times_ps": np.asarray(times, dtype=float),
        "n_pure": np.asarray(n_pure, dtype=float),
        "n_err": np.asarray(n_err, dtype=float),
        "frame_indices": np.asarray(kept_indices, dtype=int),
        "dump_path": path,
    }


def build_dataset(force: bool = False):
    if os.path.isfile(DATA_NPZ) and not force:
        print(f"Loading cached data: {DATA_NPZ}")
        return np.load(DATA_NPZ, allow_pickle=True)

    results = {}
    for temp_k in TEMPERATURES:
        results[str(temp_k)] = analyze_temperature(temp_k)

    payload = {"temperatures": np.array(TEMPERATURES)}
    for key, res in results.items():
        for field, val in res.items():
            payload[f"{key}_{field}"] = val

    np.savez(DATA_NPZ, **payload)
    print(f"\nSaved: {DATA_NPZ}")
    return payload


def temp_color(temp_k: float, t_min: float, t_max: float):
    norm = Normalize(vmin=t_min, vmax=t_max)
    rgba = cm.coolwarm(norm(temp_k))
    return rgba


def export_raw_csv(data):
    """Write long-format CSV with all sampled frames."""
    rows = ["temperature_K,time_ps,frame_index,n_pure,n_err"]
    for temp_k in TEMPERATURES:
        key = str(temp_k)
        times = np.asarray(data[f"{key}_times_ps"], dtype=float)
        counts = np.asarray(data[f"{key}_n_pure"], dtype=float)
        errs = np.asarray(data[f"{key}_n_err"], dtype=float)
        frames = np.asarray(data[f"{key}_frame_indices"], dtype=int)
        for t, fidx, n, e in zip(times, frames, counts, errs):
            rows.append(f"{temp_k},{t:.6f},{fidx},{n:.0f},{e:.6f}")

    with open(OUT_CSV, "w", encoding="utf-8") as fh:
        fh.write("\n".join(rows) + "\n")
    print(f"Saved: {OUT_CSV}")


def plot_mm_bond(data):
    export_raw_csv(data)
    apply_nature_style()
    temps = TEMPERATURES
    t_min, t_max = min(temps), max(temps)

    fig, ax = plt.subplots(figsize=(4.6, 2.8))

    for temp_k in temps:
        key = str(temp_k)
        times = np.asarray(data[f"{key}_times_ps"], dtype=float)
        if f"{key}_n_pure" in data:
            counts = np.asarray(data[f"{key}_n_pure"], dtype=float)
            errs = np.asarray(data[f"{key}_n_err"], dtype=float)
        else:
            counts = np.asarray(data[f"{key}_cn_mean"], dtype=float)
            errs = np.asarray(data[f"{key}_cn_sem"], dtype=float)
        color = temp_color(temp_k, t_min, t_max)

        order = np.argsort(times)
        times = times[order]
        counts = counts[order]
        errs = errs[order]

        plot_y = counts
        y_lo = np.maximum(counts - errs, 0.0)
        y_hi = counts + errs

        ax.plot(times, plot_y, color=color, lw=1.1, label=f"{temp_k} K", zorder=3)
        ax.fill_between(
            times,
            y_lo,
            y_hi,
            color=color,
            alpha=ERR_BAND_ALPHA,
            linewidth=0,
            zorder=2,
        )

    ax.set_xscale("log")
    ax.set_xlabel("Time (ps)", labelpad=3)
    ax.set_ylabel("M–M bond count", labelpad=3)
    ax.set_title(
        "M–M bonding vs time  (400 frames per trajectory)",
        loc="left",
        pad=8,
    )
    ax.legend(
        frameon=False,
        loc="upper left",
        handlelength=1.4,
        borderpad=0.3,
        labelspacing=0.25,
    )
    apply_nature_spines(ax)
    fig.subplots_adjust(top=0.90, bottom=0.14, left=0.14, right=0.97)

    fig.savefig(OUT_PNG)
    fig.savefig(OUT_SVG)
    plt.close(fig)
    print(f"Saved: {OUT_PNG}")
    print(f"Saved: {OUT_SVG}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Plot M–M bond vs time for six temperatures.")
    parser.add_argument("--force", action="store_true", help="Recompute trajectory statistics.")
    parser.add_argument("--plot-only", action="store_true", help="Plot from cached NPZ only.")
    args = parser.parse_args()

    if args.plot_only:
        if not os.path.isfile(DATA_NPZ):
            raise SystemExit(f"Missing cache: {DATA_NPZ}")
        data = np.load(DATA_NPZ, allow_pickle=True)
    else:
        data = build_dataset(force=args.force)

    plot_mm_bond(data)


if __name__ == "__main__":
    main()
