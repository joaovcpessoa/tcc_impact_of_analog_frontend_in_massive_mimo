"""
Plotting functions for all figures in the thesis.

Figures generated
-----------------
  plot_clip_am_am      : Fig 4.2 – CLIP AM-AM curve
  plot_ss_am_am        : Fig 4.3 – SS AM-AM curves (multi p, multi A0)
  plot_twt_am_am_pm    : Fig 4.4 – TWT AM-AM and AM-PM curves
  plot_ber_grid        : Figs 5.1-5.9 – 3×3 BER subplot grid
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from pathlib import Path

from .amplifiers import (
    amplify_clip, amplify_ss, amplify_twt,
    ClipParams, SSParams, TWTParams, TWT_PARAM_SETS,
)

# ── Consistent colour palette (matches MATLAB default colour order) ──────────
COLORS = [
    (0.0000, 0.0000, 0.0000),   # black
    (0.0000, 0.4470, 0.7410),   # blue
    (0.8500, 0.3250, 0.0980),   # orange-red
    (0.9290, 0.6940, 0.1250),   # yellow
    (0.4940, 0.1840, 0.5560),   # purple
    (0.4660, 0.6740, 0.1880),   # green
    (0.6350, 0.0780, 0.1840),   # dark-red
    (0.3010, 0.7450, 0.9330),   # light-blue
]

FONT_SIZE  = 14
LINE_WIDTH = 2


def _style_ax(ax: plt.Axes, xlabel: str, ylabel: str, fontsize: int = FONT_SIZE) -> None:
    ax.set_xlabel(xlabel, fontsize=fontsize)
    ax.set_ylabel(ylabel, fontsize=fontsize)
    ax.tick_params(labelsize=fontsize - 2)
    ax.legend(fontsize=fontsize - 2, frameon=False)


# ---------------------------------------------------------------------------
# Fig 4.2 – CLIP AM-AM
# ---------------------------------------------------------------------------

def plot_clip_am_am(
    A0_values: list = (1.0, 2.0),
    save_path: Path | None = None,
) -> plt.Figure:
    amp_in = np.linspace(0, 10, 300)
    fig, ax = plt.subplots(figsize=(6, 5))

    for i, A0 in enumerate(A0_values):
        params  = ClipParams(A0=A0)
        amp_out = np.abs(amplify_clip(amp_in.astype(complex), params))
        ax.plot(amp_in, amp_out, color=COLORS[i + 1], linewidth=LINE_WIDTH,
                label=f"$A_0 = {A0}$")

    ax.set_xlim(0, 2.5)
    ax.set_ylim(0, 2.5)
    _style_ax(ax, "Amplitude de entrada", "Amplitude de saída")
    ax.legend(loc="lower right", frameon=False, fontsize=FONT_SIZE - 2)
    fig.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=150)
    return fig


# ---------------------------------------------------------------------------
# Fig 4.3 – SS AM-AM
# ---------------------------------------------------------------------------

def plot_ss_am_am(
    A0_values: list = (1.0, 2.0),
    p_values:  list = (1, 2, 3),
    save_path: Path | None = None,
) -> plt.Figure:
    amp_in = np.linspace(0, 5, 300)
    fig, ax = plt.subplots(figsize=(6, 5))

    color_idx = 1
    for A0 in A0_values:
        for p in p_values:
            params  = SSParams(A0=A0, rho=float(p))
            amp_out = np.abs(amplify_ss(amp_in.astype(complex), params))
            ax.plot(amp_in, amp_out, color=COLORS[color_idx % len(COLORS)],
                    linewidth=LINE_WIDTH, label=f"$p={p},\\ A_0={A0}$")
            color_idx += 1

    ax.set_xlim(0, 5)
    ax.set_ylim(0, 2)
    _style_ax(ax, "Amplitude de entrada", "Amplitude de saída")
    ax.legend(loc="lower right", frameon=False, fontsize=FONT_SIZE - 3, ncols=2)
    fig.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=150)
    return fig


# ---------------------------------------------------------------------------
# Fig 4.4 – TWT AM-AM and AM-PM
# ---------------------------------------------------------------------------

def plot_twt_am_am_pm(
    param_sets: list | None = None,
    save_path:  Path | None = None,
) -> plt.Figure:
    if param_sets is None:
        param_sets = TWT_PARAM_SETS

    amp_in = np.linspace(0, 5, 400)
    fig, (ax_am, ax_pm) = plt.subplots(1, 2, figsize=(11, 5))

    labels = [r"$\mathcal{C}_1$", r"$\mathcal{C}_2$", r"$\mathcal{C}_3$"]
    for i, params in enumerate(param_sets):
        y        = amplify_twt(amp_in.astype(complex), params)
        amp_out  = np.abs(y)
        phase_out = np.angle(y) * 180 / np.pi

        ax_am.plot(amp_in, amp_out,   color=COLORS[i + 1], linewidth=LINE_WIDTH,
                   label=labels[i])
        ax_pm.plot(amp_in, phase_out, color=COLORS[i + 1], linewidth=LINE_WIDTH,
                   label=labels[i])

    ax_am.set_xlim(0, 3.5);  ax_am.set_ylim(0, 3.5)
    _style_ax(ax_am, "Amplitude de entrada", "Amplitude de saída")
    ax_am.legend(loc="upper left", frameon=False, fontsize=FONT_SIZE - 2)

    ax_pm.set_xlim(0, 5)
    _style_ax(ax_pm, "Amplitude de entrada", "Fase de saída (°)")
    ax_pm.legend(loc="upper left", frameon=False, fontsize=FONT_SIZE - 2)

    fig.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=150)
    return fig


# ---------------------------------------------------------------------------
# Figs 5.1-5.9 – BER vs SNR (3×3 grid: precoders × K values)
# ---------------------------------------------------------------------------

def plot_ber_grid(
    ber_results:  dict,   # {(precoder, K): np.ndarray shape (N_SNR, N_params+1)}
    snr_db:       np.ndarray,
    precoder_list: list,
    k_list:        list,
    amp_label:     str,
    param_labels:  list,
    M:             int,
    save_path:     Path | None = None,
) -> plt.Figure:
    """
    Plot a 3×3 BER grid (rows = K values, columns = precoders).

    ber_results : maps (precoder_type, K) → np.ndarray (N_SNR, N_params)
                  Column 0 = IDEAL, columns 1..N_params = nonlinear sets.
    param_labels : legend labels for the non-ideal curves (len = N_params - 1).
    """
    n_k      = len(k_list)
    n_prec   = len(precoder_list)

    fig, axes = plt.subplots(n_k, n_prec, figsize=(5 * n_prec, 4 * n_k), squeeze=False)

    for row, K in enumerate(k_list):
        for col, prec in enumerate(precoder_list):
            ax  = axes[row, col]
            key = (prec, K)

            if key not in ber_results:
                ax.set_visible(False)
                continue

            ber = ber_results[key]   # (N_SNR, N_params)

            # IDEAL (column 0)
            ax.semilogy(snr_db, np.maximum(ber[:, 0], 1e-7),
                        color=COLORS[1], linewidth=LINE_WIDTH, label="Ideal")

            # Non-ideal curves
            for p_idx in range(1, ber.shape[1]):
                label = param_labels[p_idx - 1] if p_idx - 1 < len(param_labels) else f"Set {p_idx}"
                ax.semilogy(snr_db, np.maximum(ber[:, p_idx], 1e-7),
                            color=COLORS[(p_idx + 1) % len(COLORS)],
                            linewidth=LINE_WIDTH, label=label)

            ax.set_xlim(snr_db[0], snr_db[-1])
            ax.set_xlabel("SNR (dB)", fontsize=FONT_SIZE - 2)
            ax.set_ylabel("BER",      fontsize=FONT_SIZE - 2)
            ax.set_title(f"{prec} com $K={K}$", fontsize=FONT_SIZE - 1)
            ax.tick_params(labelsize=FONT_SIZE - 3)
            ax.legend(loc="lower left", frameon=False, fontsize=FONT_SIZE - 4)
            ax.grid(True, which="both", linestyle="--", alpha=0.4)

    fig.suptitle(
        f"BER vs SNR – $M={M}$, amplificador: {amp_label}",
        fontsize=FONT_SIZE + 1, y=1.01,
    )
    fig.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
    return fig
