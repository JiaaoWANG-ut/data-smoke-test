#!/usr/bin/env python3
"""
Metal-only first-shell analysis for Fe and Co in the GPUMD trajectory.

Definition (metallic local pocket):
  CN_O(r < R_O) = 0  AND  CN_metal(r < R_M) > 0
  where metal = Fe + Co + Ni.

Outputs Nature-style figure with:
  (a) Count of metal-only Fe / Co vs time
  (b) Event timeline (when any such atom exists)
  (c) CN_O vs CN_metal at the peak frame (local environments)
"""

import os
import warnings

warnings.filterwarnings("ignore", message=".*OVITO.*PyPI")

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from ovito.data import CutoffNeighborFinder
from ovito.io import import_file

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DUMP_FILE = os.path.join(SCRIPT_DIR, "dump.xyz")
DATA_NPZ = os.path.join(SCRIPT_DIR, "FeCo_metal_coord_data.npz")
OUT_PNG = os.path.join(SCRIPT_DIR, "FeCo_metal_coord_analysis.png")

O_CUT = 2.5   # Å — upper bound of first O shell (Fe–O / Co–O peak ~1.95 Å)
MET_CUT = 3.0  # Å — metal contact shell (Fe/Co/Ni neighbors)
TIME_STEP_FS = 1.0


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


def classify_frame(data):
    """Return counts and per-atom CN arrays for Fe and Co."""
    pt = data.particles["Particle Type"]
    ptypes = data.particles.particle_types
    ids = {s: ptypes.type_by_name(s).id for s in ["Fe", "Co", "Ni", "O"]}
    metal_ids = {ids["Fe"], ids["Co"], ids["Ni"]}
    o_id = ids["O"]

    finder_o = CutoffNeighborFinder(O_CUT, data)
    finder_m = CutoffNeighborFinder(MET_CUT, data)

    def scan(sym):
        cn_o_list = []
        cn_m_list = []
        n_metal_only = 0
        for i in np.where(pt == ids[sym])[0]:
            cn_o = sum(1 for nb in finder_o.find(i) if pt[nb.index] == o_id)
            cn_m = sum(1 for nb in finder_m.find(i) if pt[nb.index] in metal_ids)
            cn_o_list.append(cn_o)
            cn_m_list.append(cn_m)
            if cn_o == 0 and cn_m > 0:
                n_metal_only += 1
        return (
            n_metal_only,
            np.array(cn_o_list, dtype=int),
            np.array(cn_m_list, dtype=int),
        )

    n_fe, cn_fe_o, cn_fe_m = scan("Fe")
    n_co, cn_co_o, cn_co_m = scan("Co")
    return n_fe, n_co, cn_fe_o, cn_fe_m, cn_co_o, cn_co_m


def analyze_trajectory():
    print(f"Scanning: {DUMP_FILE}")
    pipeline = import_file(DUMP_FILE)
    n_frames = pipeline.source.num_frames

    times_ps = np.empty(n_frames)
    n_fe_mo = np.zeros(n_frames, dtype=int)
    n_co_mo = np.zeros(n_frames, dtype=int)

    peak_score = -1
    peak_frame = 0
    peak_cn = None

    for fidx in range(n_frames):
        data = pipeline.compute(fidx)
        step_fs = float(data.attributes.get("Time", (fidx + 1) * 2000))
        times_ps[fidx] = step_fs * TIME_STEP_FS / 1000.0

        n_fe, n_co, cn_fe_o, cn_fe_m, cn_co_o, cn_co_m = classify_frame(data)
        n_fe_mo[fidx] = n_fe
        n_co_mo[fidx] = n_co

        score = n_fe + n_co
        if score > peak_score:
            peak_score = score
            peak_frame = fidx
            peak_cn = (cn_fe_o, cn_fe_m, cn_co_o, cn_co_m, times_ps[fidx])

        if fidx % 250 == 0 or fidx == n_frames - 1:
            print(
                f"  frame {fidx:5d}  t={times_ps[fidx]:8.1f} ps  "
                f"Fe={n_fe}  Co={n_co}  (metal-only shell)"
            )

    np.savez(
        DATA_NPZ,
        times_ps=times_ps,
        n_fe_metal_only=n_fe_mo,
        n_co_metal_only=n_co_mo,
        o_cut=O_CUT,
        met_cut=MET_CUT,
        peak_frame=peak_frame,
        peak_time_ps=peak_cn[4],
        peak_cn_fe_o=peak_cn[0],
        peak_cn_fe_m=peak_cn[1],
        peak_cn_co_o=peak_cn[2],
        peak_cn_co_m=peak_cn[3],
    )
    print(f"Saved: {DATA_NPZ}")
    print(f"Peak frame {peak_frame}  t={peak_cn[4]:.1f} ps  Fe={n_fe_mo[peak_frame]}  Co={n_co_mo[peak_frame]}")

    return times_ps, n_fe_mo, n_co_mo, peak_frame, peak_cn


def load_or_analyze():
    if os.path.isfile(DATA_NPZ):
        print(f"Loading: {DATA_NPZ}")
        d = np.load(DATA_NPZ)
        peak_frame = int(d["peak_frame"])
        peak_cn = (
            d["peak_cn_fe_o"],
            d["peak_cn_fe_m"],
            d["peak_cn_co_o"],
            d["peak_cn_co_m"],
            float(d["peak_time_ps"]),
        )
        return d["times_ps"], d["n_fe_metal_only"], d["n_co_metal_only"], peak_frame, peak_cn
    return analyze_trajectory()


def plot_analysis(times_ps, n_fe_mo, n_co_mo, peak_frame, peak_cn):
    apply_nature_style()
    cn_fe_o, cn_fe_m, cn_co_o, cn_co_m, peak_t = peak_cn

    fig = plt.figure(figsize=(5.0, 6.2))
    gs = fig.add_gridspec(3, 1, height_ratios=[1.1, 0.55, 1.15], hspace=0.42)
    ax_count = fig.add_subplot(gs[0, 0])
    ax_event = fig.add_subplot(gs[1, 0])
    ax_cn = fig.add_subplot(gs[2, 0])

    # (a) Count vs time
    ax_count.plot(times_ps, n_fe_mo, color="#0072B2", lw=1.0, label="Fe (metal-only shell)")
    ax_count.plot(times_ps, n_co_mo, color="#009E73", lw=1.0, label="Co (metal-only shell)")
    ax_count.axvline(peak_t, color="#999999", ls=":", lw=0.8, alpha=0.9)
    ax_count.set_xlim(times_ps[0], times_ps[-1])
    ax_count.set_ylim(-0.2, max(3.5, n_fe_mo.max() + 0.5, n_co_mo.max() + 0.5))
    ax_count.set_xlabel("Time (ps)", labelpad=3)
    ax_count.set_ylabel("Atom count", labelpad=3)
    ax_count.set_title(
        f"(a) Atoms with O-free, metal-only local shell  "
        f"(O cutoff {O_CUT:.1f} Å, metal cutoff {MET_CUT:.1f} Å)",
        loc="left",
        pad=8,
    )
    ax_count.legend(frameon=False, loc="upper right")
    apply_nature_spines(ax_count)

    # (b) Event timeline
    fe_events = times_ps[n_fe_mo > 0]
    co_events = times_ps[n_co_mo > 0]
    ax_event.scatter(
        fe_events,
        np.full(fe_events.size, 1.0),
        s=12,
        color="#0072B2",
        marker="|",
        linewidths=1.2,
        label="Fe event",
    )
    ax_event.scatter(
        co_events,
        np.full(co_events.size, 0.0),
        s=12,
        color="#009E73",
        marker="|",
        linewidths=1.2,
        label="Co event",
    )
    ax_event.set_xlim(times_ps[0], times_ps[-1])
    ax_event.set_ylim(-0.6, 1.6)
    ax_event.set_yticks([0, 1], ["Co", "Fe"])
    ax_event.set_xlabel("Time (ps)", labelpad=3)
    ax_event.set_title(
        f"(b) Transient metal-only events  "
        f"({fe_events.size} Fe-frame, {co_events.size} Co-frame hits)",
        loc="left",
        pad=8,
    )
    ax_event.legend(frameon=False, loc="upper right", ncol=2)
    apply_nature_spines(ax_event)

    # (c) CN scatter at peak frame
    ax_cn.axvspan(-0.2, 0.45, alpha=0.10, color="#0072B2", zorder=0)
    ax_cn.axvline(0.5, color="#666666", ls="--", lw=0.7, alpha=0.8)
    ax_cn.axhline(0.5, color="#666666", ls="--", lw=0.7, alpha=0.8)

    fe_mask = (cn_fe_o == 0) & (cn_fe_m > 0)
    co_mask = (cn_co_o == 0) & (cn_co_m > 0)

    ax_cn.scatter(
        cn_fe_o[~fe_mask],
        cn_fe_m[~fe_mask],
        s=8,
        c="#0072B2",
        alpha=0.25,
        marker="o",
        linewidths=0,
        label="Fe (oxide-coordinated)",
    )
    ax_cn.scatter(
        cn_co_o[~co_mask],
        cn_co_m[~co_mask],
        s=8,
        c="#009E73",
        alpha=0.25,
        marker="s",
        linewidths=0,
        label="Co (oxide-coordinated)",
    )
    if np.any(fe_mask):
        ax_cn.scatter(
            cn_fe_o[fe_mask],
            cn_fe_m[fe_mask],
            s=36,
            facecolors="none",
            edgecolors="#0072B2",
            linewidths=1.0,
            marker="o",
            label="Fe (metal-only shell)",
        )
    if np.any(co_mask):
        ax_cn.scatter(
            cn_co_o[co_mask],
            cn_co_m[co_mask],
            s=36,
            facecolors="none",
            edgecolors="#009E73",
            linewidths=1.0,
            marker="s",
            label="Co (metal-only shell)",
        )

    ax_cn.set_xlim(-0.2, min(12, max(cn_fe_o.max(), cn_co_o.max()) + 1))
    ax_cn.set_ylim(-0.2, min(16, max(cn_fe_m.max(), cn_co_m.max()) + 1))
    ax_cn.set_xlabel(f"CN_O (r < {O_CUT:.1f} Å)", labelpad=3)
    ax_cn.set_ylabel(f"CN_metal (r < {MET_CUT:.1f} Å)", labelpad=3)
    ax_cn.set_title(
        f"(c) Coordination at peak frame  (t = {peak_t:.0f} ps, frame {peak_frame})",
        loc="left",
        pad=8,
    )
    ax_cn.legend(frameon=False, loc="upper right", fontsize=6)
    apply_nature_spines(ax_cn)

    note = (
        f"Criterion: no O within {O_CUT:.1f} A and >=1 metal neighbor (Fe/Co/Ni) within {MET_CUT:.1f} A. "
        f"Peak: {int(n_fe_mo[peak_frame])} Fe + {int(n_co_mo[peak_frame])} Co; "
        f"total event frames: Fe {fe_events.size}, Co {co_events.size} / {len(times_ps)}."
    )
    fig.text(0.08, 0.015, note, ha="left", va="center", fontsize=6.3)

    fig.subplots_adjust(top=0.97, bottom=0.07, left=0.14, right=0.97)
    fig.savefig(OUT_PNG)
    plt.close(fig)
    print(f"Saved: {OUT_PNG}")


def main():
    times_ps, n_fe_mo, n_co_mo, peak_frame, peak_cn = load_or_analyze()
    plot_analysis(times_ps, n_fe_mo, n_co_mo, peak_frame, peak_cn)


if __name__ == "__main__":
    main()
