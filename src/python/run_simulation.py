"""
run_simulation.py
=================
Reproduces all figures from:

  "Análise de Impacto do Front-end Analógico em Sistemas Massive MIMO"
  João Vítor Correia Pessoa, CEFET/RJ, 2025

Usage
-----
  # Full simulation (matches thesis exactly, slow)
  python run_simulation.py

  # Quick smoke-test with reduced MC counts
  python run_simulation.py --quick

  # Only amplitude-characteristic figures (fast, no BER)
  python run_simulation.py --amp-only

  # Choose output directory
  python run_simulation.py --outdir results/

Reproducibility
---------------
All random draws use a seeded NumPy Generator (seed = 42).
Results are saved as .npz files so plots can be regenerated without
re-running the simulation.
"""

from __future__ import annotations

import argparse
import time
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")   # headless rendering
import matplotlib.pyplot as plt

# --------------------------------------------------------------------------- #
# Local package                                                                #
# --------------------------------------------------------------------------- #
import sys
sys.path.insert(0, str(Path(__file__).parent))

from massive_mimo_sim.amplifiers import (
    ClipParams, SSParams, TWTParams,
    TWT_PARAM_SETS, CLIP_SS_A0_VALUES,
)
from massive_mimo_sim.simulation import run_ber_simulation
from massive_mimo_sim.plotting   import (
    plot_clip_am_am, plot_ss_am_am, plot_twt_am_am_pm, plot_ber_grid,
)


# =========================================================================== #
# Simulation parameters (Table 5.2 of thesis)                                 #
# =========================================================================== #

SNR_DB       = np.arange(-10, 31, 1, dtype=float)   # −10 … 30 dB
N_BLK        = 1000          # symbols per block
B_PER_SYM    = 4             # 16-QAM
K_FACTOR_DB  = 10.0          # Rician K-factor (dB)
CELL_RADIUS  = 1000.0        # metres
RANDOM_SEED  = 42

# Antenna / user configurations
# Each entry: (M, K_values)
#   K = M/4 → low load
#   K = M/2 → medium load
#   K = M   → high load
ANTENNA_CONFIGS = [
    (64,  [16, 32, 64]),
    (128, [32, 64, 128]),
    (256, [64, 128, 256]),
]

PRECODER_TYPES = ["MF", "ZF", "MMSE"]

# TWT amp param sets (from Saleh 1981, Table 4.1)
TWT_PARAMS = TWT_PARAM_SETS          # 3 sets
TWT_LABELS = ["Conjunto 1", "Conjunto 2", "Conjunto 3"]

# CLIP / SS param sets (A0 saturation levels)
CLIP_SS_PARAMS_CLIP = [ClipParams(A0=a0) for a0 in CLIP_SS_A0_VALUES]
CLIP_SS_PARAMS_SS   = [SSParams(A0=a0, rho=1.0) for a0 in CLIP_SS_A0_VALUES]
CLIP_SS_LABELS      = [f"$A_0={a0}$" for a0 in CLIP_SS_A0_VALUES]


# =========================================================================== #
# Helper: save / load results                                                  #
# =========================================================================== #

def _results_path(outdir: Path, tag: str) -> Path:
    return outdir / f"ber_{tag}.npz"


def _save_ber(path: Path, ber_dict: dict, snr_db: np.ndarray) -> None:
    np.savez(path, snr_db=snr_db, **{
        f"{prec}_{K}": arr for (prec, K), arr in ber_dict.items()
    })
    print(f"  Saved → {path}")


def _load_ber(path: Path, precoder_list, k_list) -> dict:
    data = np.load(path)
    return {
        (prec, K): data[f"{prec}_{K}"]
        for prec in precoder_list for K in k_list
        if f"{prec}_{K}" in data
    }


# =========================================================================== #
# Amplitude-characteristic figures                                             #
# =========================================================================== #

def generate_amplitude_figures(outdir: Path) -> None:
    print("\n── Amplitude characteristic figures ─────────────────────────────")

    fig = plot_clip_am_am(A0_values=[1.0, 2.0],
                          save_path=outdir / "fig4_2_clip_am_am.png")
    plt.close(fig)
    print("  Fig 4.2: CLIP AM-AM  →", outdir / "fig4_2_clip_am_am.png")

    fig = plot_ss_am_am(A0_values=[1.0, 2.0], p_values=[1, 2, 3],
                        save_path=outdir / "fig4_3_ss_am_am.png")
    plt.close(fig)
    print("  Fig 4.3: SS AM-AM    →", outdir / "fig4_3_ss_am_am.png")

    fig = plot_twt_am_am_pm(param_sets=TWT_PARAMS,
                            save_path=outdir / "fig4_4_twt_am_am_pm.png")
    plt.close(fig)
    print("  Fig 4.4: TWT AM-AM / AM-PM →", outdir / "fig4_4_twt_am_am_pm.png")


# =========================================================================== #
# BER simulation helpers                                                       #
# =========================================================================== #

def _run_one_config(
    M, K, precoder_type, amp_type, amp_params, n_mc1, n_mc2, rng_seed
) -> np.ndarray:
    """
    Run a single (M, K, precoder, amp) BER simulation.

    The IDEAL curve is always prepended as the first column,
    so the returned array has shape (N_SNR, 1 + N_params).
    """
    rng = np.random.default_rng(rng_seed)

    # IDEAL baseline
    ber_ideal = run_ber_simulation(
        M=M, K=K, precoder_type=precoder_type,
        amp_type="IDEAL", amp_params=[None],
        snr_db=SNR_DB, n_blk=N_BLK,
        n_mc1=n_mc1, n_mc2=n_mc2,
        b_per_sym=B_PER_SYM, k_factor_db=K_FACTOR_DB,
        cell_radius=CELL_RADIUS, rng=rng,
    )   # (N_SNR, 1)

    rng = np.random.default_rng(rng_seed)   # re-seed for reproducibility

    # Non-linear amplifier
    ber_nonlin = run_ber_simulation(
        M=M, K=K, precoder_type=precoder_type,
        amp_type=amp_type, amp_params=amp_params,
        snr_db=SNR_DB, n_blk=N_BLK,
        n_mc1=n_mc1, n_mc2=n_mc2,
        b_per_sym=B_PER_SYM, k_factor_db=K_FACTOR_DB,
        cell_radius=CELL_RADIUS, rng=rng,
    )   # (N_SNR, N_params)

    return np.hstack([ber_ideal, ber_nonlin])   # (N_SNR, 1 + N_params)


def _run_and_plot(
    *,
    M:             int,
    k_list:        list,
    amp_type:      str,
    amp_params:    list,
    amp_label:     str,
    param_labels:  list,
    fig_num:       str,
    n_mc1:         int,
    n_mc2:         int,
    outdir:        Path,
    force_rerun:   bool = False,
) -> None:
    """Run BER for all (precoder, K) combos for one (M, amp) configuration."""
    npz_path = _results_path(outdir, f"{amp_type.lower()}_M{M}")

    # ── Load cached results if available ─────────────────────────────────────
    if npz_path.exists() and not force_rerun:
        print(f"  Loading cached results from {npz_path}")
        ber_results = _load_ber(npz_path, PRECODER_TYPES, k_list)
    else:
        ber_results = {}
        for precoder_type in PRECODER_TYPES:
            for K in k_list:
                tag = f"M={M}, K={K}, {precoder_type}, {amp_label}"
                print(f"  Simulating {tag} …", end="", flush=True)
                t0  = time.perf_counter()
                ber = _run_one_config(
                    M, K, precoder_type, amp_type, amp_params,
                    n_mc1, n_mc2, RANDOM_SEED,
                )
                dt  = time.perf_counter() - t0
                print(f" done ({dt:.1f}s)")
                ber_results[(precoder_type, K)] = ber
        _save_ber(npz_path, ber_results, SNR_DB)

    # ── Plot ─────────────────────────────────────────────────────────────────
    fig = plot_ber_grid(
        ber_results   = ber_results,
        snr_db        = SNR_DB,
        precoder_list = PRECODER_TYPES,
        k_list        = k_list,
        amp_label     = amp_label,
        param_labels  = param_labels,
        M             = M,
        save_path     = outdir / f"fig{fig_num}_ber_{amp_type.lower()}_M{M}.png",
    )
    plt.close(fig)
    print(f"  Fig {fig_num}: BER {amp_label} M={M} → "
          f"{outdir / f'fig{fig_num}_ber_{amp_type.lower()}_M{M}.png'}")


# =========================================================================== #
# Main                                                                         #
# =========================================================================== #

def main() -> None:
    parser = argparse.ArgumentParser(description="Massive MIMO BER simulation")
    parser.add_argument("--quick",    action="store_true",
                        help="Use n_mc1=n_mc2=3 for a fast smoke-test")
    parser.add_argument("--amp-only", action="store_true",
                        help="Only generate amplitude-characteristic figures")
    parser.add_argument("--outdir",   default="simulation_results",
                        help="Output directory for figures and .npz caches")
    parser.add_argument("--force",    action="store_true",
                        help="Re-run simulation even if .npz cache exists")
    args = parser.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    n_mc1 = 3 if args.quick else 10
    n_mc2 = 3 if args.quick else 10

    print("=" * 60)
    print("Massive MIMO Nonlinear Front-end BER Simulation")
    print(f"  SNR range : {SNR_DB[0]:.0f} … {SNR_DB[-1]:.0f} dB "
          f"({len(SNR_DB)} points)")
    print(f"  N_BLK     : {N_BLK}")
    print(f"  N_MC1     : {n_mc1}  (user positions)")
    print(f"  N_MC2     : {n_mc2}  (small-scale fading)")
    print(f"  Seed      : {RANDOM_SEED}")
    print(f"  Output    : {outdir.resolve()}")
    print("=" * 60)

    # ── Amplitude characteristic figures (fast) ──────────────────────────────
    generate_amplitude_figures(outdir)

    if args.amp_only:
        print("\nDone (amplitude figures only).")
        return

    # ── BER simulations ───────────────────────────────────────────────────────
    # Figure numbering matches thesis sections 5.2 / 5.3 / 5.4
    #   CLIP : Figs 5.1, 5.2, 5.3  (M = 64, 128, 256)
    #   SS   : Figs 5.4, 5.5, 5.6
    #   TWT  : Figs 5.7, 5.8, 5.9

    amp_configs = [
        # (amp_type, amp_params_list, amp_label, param_labels, fig_offset)
        ("CLIP", CLIP_SS_PARAMS_CLIP, "CLIP", CLIP_SS_LABELS, "5.{idx}"),
        ("SS",   CLIP_SS_PARAMS_SS,   "SS",   CLIP_SS_LABELS, "5.{idx}"),
        ("TWT",  TWT_PARAMS,          "TWT",  TWT_LABELS,     "5.{idx}"),
    ]

    fig_offsets = {
        "CLIP": [1, 2, 3],
        "SS":   [4, 5, 6],
        "TWT":  [7, 8, 9],
    }

    for amp_type, amp_params, amp_label, param_labels, _ in amp_configs:
        print(f"\n{'─'*60}")
        print(f"Amplifier: {amp_label}")
        print(f"{'─'*60}")
        for ant_idx, (M, k_list) in enumerate(ANTENNA_CONFIGS):
            fig_num = f"5.{fig_offsets[amp_type][ant_idx]}"
            _run_and_plot(
                M            = M,
                k_list       = k_list,
                amp_type     = amp_type,
                amp_params   = amp_params,
                amp_label    = amp_label,
                param_labels = param_labels,
                fig_num      = fig_num,
                n_mc1        = n_mc1,
                n_mc2        = n_mc2,
                outdir       = outdir,
                force_rerun  = args.force,
            )

    print(f"\n{'='*60}")
    print(f"All figures saved to: {outdir.resolve()}")
    print("=" * 60)


if __name__ == "__main__":
    main()
