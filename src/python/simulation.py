"""
Downlink BER simulation via Monte Carlo.

Matches the simulation loop in MATLAB's `dl_ber.m`:

  Outer MC  : user positions (N_MC1 realisations)
  Inner MC  : small-scale Rician fading (N_MC2 realisations)
  Inner loop: sweep over SNR × amplifier parameter sets

Transmission model (downlink):
  y = Hᵀ f(√ρ · x_norm) + v_norm      ∈ ℂ^{K × N_BLK}

where f(·) is the amplifier nonlinearity, x_norm is the per-antenna-normalised
precoded signal, and v_norm is unit-power complex Gaussian noise.
"""

from __future__ import annotations

import numpy as np

from .amplifiers import amplify, ClipParams, SSParams, TWTParams
from .channel    import rician_channel, user_position_generator
from .precoders  import compute_precoder, normalize_precoded_signal
from .qam        import qammod, qamdemod


# ---------------------------------------------------------------------------
# BER simulation for one (M, K, precoder_type) configuration
# ---------------------------------------------------------------------------

def run_ber_simulation(
    *,
    M:            int,
    K:            int,
    precoder_type: str,
    amp_type:     str,
    amp_params:   list,          # list of ClipParams / SSParams / TWTParams
    snr_db:       np.ndarray,    # shape (N_SNR,)
    n_blk:        int   = 1000,
    n_mc1:        int   = 10,
    n_mc2:        int   = 10,
    b_per_sym:    int   = 4,
    k_factor_db:  float = 10.0,
    cell_radius:  float = 1000.0,
    rng:          np.random.Generator | None = None,
) -> np.ndarray:
    """
    Run Monte Carlo BER simulation.

    Returns
    -------
    ber : np.ndarray, shape (N_SNR, N_amp_params)
        Average BER across all users and MC realisations.
    """
    if rng is None:
        rng = np.random.default_rng(42)

    snr_lin  = 10.0 ** (snr_db / 10.0)
    n_snr    = len(snr_db)
    n_params = len(amp_params)
    m_qam    = 2 ** b_per_sym
    k_factor = 10.0 ** (k_factor_db / 10.0)

    # Accumulates (K, N_SNR, N_params, N_MC1, N_MC2)
    ber_all = np.zeros((K, n_snr, n_params, n_mc1, n_mc2))

    for mc1 in range(n_mc1):
        # ── User positions & LoS channel ──────────────────────────────────
        x_pos, y_pos = user_position_generator(K, cell_radius, rng)
        theta = np.arctan2(y_pos, x_pos)   # (K,)

        for mc2 in range(n_mc2):
            # ── Channel matrix ────────────────────────────────────────────
            H = rician_channel(M, K, k_factor, theta, rng)   # (M, K)

            # ── Symbols ───────────────────────────────────────────────────
            bits    = rng.integers(0, 2, (b_per_sym * n_blk, K))  # (B*N, K)
            s       = qammod(bits, m_qam)                          # (N, K)
            Ps      = np.linalg.norm(s, axis=0) ** 2 / n_blk      # (K,)

            # ── Precoder & normalised signal ──────────────────────────────
            precoder = compute_precoder(precoder_type, H, snr_lin)
            x_norm   = normalize_precoded_signal(precoder, precoder_type, M, s)

            # ── Noise (unit power per user, averaged over N_BLK samples) ─
            v     = np.sqrt(0.5) * (
                rng.standard_normal((K, n_blk))
                + 1j * rng.standard_normal((K, n_blk))
            )
            Pv    = (np.linalg.norm(v, axis=1, keepdims=True) ** 2) / n_blk
            v_norm = v / np.sqrt(Pv)                               # (K, N_BLK)

            # ── Sweep SNR and amplifier parameters ────────────────────────
            for snr_idx, snr_val in enumerate(snr_lin):
                # Select correct x_norm slice for MMSE
                if precoder_type.upper() == "MMSE":
                    x_tx = x_norm[:, :, snr_idx]   # (M, N_BLK)
                else:
                    x_tx = x_norm                   # (M, N_BLK)

                for p_idx, params in enumerate(amp_params):
                    # Amplify
                    x_amp = amplify(
                        np.sqrt(snr_val) * x_tx, amp_type, params
                    )                                              # (M, N_BLK)

                    # Receive: y = Hᵀ x_amp + noise
                    y = H.T @ x_amp + v_norm                      # (K, N_BLK)

                    # Demodulate all users at once
                    ber_all[:, snr_idx, p_idx, mc1, mc2] = _demod_all_users(
                        y, Ps, bits, m_qam, b_per_sym, n_blk, K
                    )

    # Average over users, MC1 and MC2
    # ber_all: (K, N_SNR, N_params, N_MC1, N_MC2)
    return ber_all.mean(axis=(0, 3, 4))   # (N_SNR, N_params)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _demod_all_users(
    y:        np.ndarray,   # (K, N_BLK)
    Ps:       np.ndarray,   # (K,) – transmitted symbol power per user
    bits_ref: np.ndarray,   # (B*N_BLK, K) – transmitted bits
    m_qam:    int,
    b_per_sym: int,
    n_blk:    int,
    K:        int,
) -> np.ndarray:
    """
    Demodulate received signal for all K users and return BER per user.

    Returns
    -------
    ber_k : np.ndarray, shape (K,)
    """
    ber_k = np.zeros(K)
    for k in range(K):
        s_recv    = y[k, :]                                         # (N_BLK,)
        Ps_recv   = np.linalg.norm(s_recv) ** 2 / n_blk
        s_scaled  = np.sqrt(Ps[k] / Ps_recv) * s_recv

        bits_recv = qamdemod(s_scaled, m_qam)                       # (B*N_BLK,)
        n_errors  = int(np.sum(bits_recv != bits_ref[:, k]))
        ber_k[k]  = n_errors / (b_per_sym * n_blk)
    return ber_k
