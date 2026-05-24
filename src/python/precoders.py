"""
Downlink linear precoders for Massive MIMO.

Implements MF, ZF and MMSE precoders and the per-antenna power normalisation
that matches the MATLAB `precode_signal.m` / `normalize_precoded_signal.m`.

Precoder definitions (H ∈ ℂ^{M×K} is the uplink channel matrix):
  MF   : W = H* ./ ||h_k||²  (column-wise, matched filter)
  ZF   : W = H* (Hᵀ H*)⁻¹
  MMSE : W = H* (Hᵀ H* + (1/ρ) I_K)⁻¹   (SNR-dependent)

Normalisation (per antenna, matching the MATLAB implementation):
  For each antenna m:
      Px = ||x[m, :]||² / M          (NOTE: MATLAB uses M, not N_BLK)
      x_norm[m, :] = x[m, :] / √Px
"""

import numpy as np


# ---------------------------------------------------------------------------
# Precoder computation
# ---------------------------------------------------------------------------

def compute_precoder(
    precoder_type: str,
    H: np.ndarray,
    snr_linear: np.ndarray,
) -> np.ndarray:
    """
    Compute the downlink precoding matrix W.

    Parameters
    ----------
    precoder_type : 'MF', 'ZF', or 'MMSE'.
    H             : Channel matrix, shape (M, K), complex.
    snr_linear    : Linear SNR array, shape (N_SNR,). Used only for MMSE.

    Returns
    -------
    W : Precoder matrix.
        - 'MF'/'ZF': shape (M, K)
        - 'MMSE'   : shape (M, K, N_SNR)
    """
    M, K = H.shape
    ptype = precoder_type.upper()

    if ptype == "MF":
        # W_k = h_k* / ||h_k||²  →  column-wise
        col_norms_sq = np.sum(np.abs(H) ** 2, axis=0)      # (K,)
        return np.conj(H) / col_norms_sq[np.newaxis, :]     # (M, K)

    elif ptype == "ZF":
        # W = H* (Hᵀ H*)⁻¹
        HT_Hconj = H.T @ np.conj(H)                        # (K, K)
        return np.linalg.solve(HT_Hconj.T, np.conj(H).T).T # (M, K)

    elif ptype == "MMSE":
        N_SNR = len(snr_linear)
        W = np.zeros((M, K, N_SNR), dtype=complex)
        HT_Hconj = H.T @ np.conj(H)                        # (K, K)
        for snr_idx, snr_val in enumerate(snr_linear):
            reg = HT_Hconj + (1.0 / snr_val) * np.eye(K)  # (K, K)
            W[:, :, snr_idx] = np.linalg.solve(reg.T, np.conj(H).T).T
        return W

    else:
        raise ValueError(f"Unknown precoder type: '{precoder_type}'")


# ---------------------------------------------------------------------------
# Per-antenna power normalisation
# ---------------------------------------------------------------------------

def normalize_precoded_signal(
    precoder: np.ndarray,
    precoder_type: str,
    n_antennas: int,
    s: np.ndarray,
) -> np.ndarray:
    """
    Apply precoder and normalise each antenna's output to unit power.

    The divisor in the power estimate is M (number of antennas), matching
    the MATLAB implementation:
        Px = norm(x[m, :])² / length(x[:, m])   where length(x[:, m]) = M

    Parameters
    ----------
    precoder      : Output of compute_precoder.
    precoder_type : 'MF', 'ZF', or 'MMSE'.
    n_antennas    : M (BS antennas).
    s             : Transmitted symbols, shape (N_BLK, K), complex.

    Returns
    -------
    x_norm : Normalised precoded signal.
             - 'MF'/'ZF': shape (M, N_BLK)
             - 'MMSE'   : shape (M, N_BLK, N_SNR)
    """
    M = n_antennas
    ptype = precoder_type.upper()

    if ptype in ("MF", "ZF"):
        # s.T is (K, N_BLK)
        x = precoder @ s.T                  # (M, N_BLK)
        x_norm = _per_antenna_normalize(x, M)
        return x_norm

    elif ptype == "MMSE":
        N_SNR = precoder.shape[2]
        N_BLK = s.shape[0]
        x_norm = np.zeros((M, N_BLK, N_SNR), dtype=complex)
        for snr_idx in range(N_SNR):
            x = precoder[:, :, snr_idx] @ s.T   # (M, N_BLK)
            x_norm[:, :, snr_idx] = _per_antenna_normalize(x, M)
        return x_norm

    else:
        raise ValueError(f"Unknown precoder type: '{precoder_type}'")


def _per_antenna_normalize(x: np.ndarray, M: int) -> np.ndarray:
    """
    x : (M, N_BLK) complex
    Returns normalised x where each row has power 1
    (divisor = M, matching MATLAB `length(x[:, m])` = M).
    """
    x_norm = np.empty_like(x)
    for m in range(M):
        Px = np.linalg.norm(x[m, :]) ** 2 / M
        x_norm[m, :] = x[m, :] / np.sqrt(Px)
    return x_norm
