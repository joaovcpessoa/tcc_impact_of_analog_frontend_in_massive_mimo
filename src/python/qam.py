"""
Gray-coded QAM modulation/demodulation.

Replicates MATLAB's qammod/qamdemod with 'InputType','bit' and 'OutputType','bit'.
For M=16 (16-QAM, B=4 bits/symbol):
  - First B/2 bits → I (real) component via 4-PAM Gray mapping
  - Last  B/2 bits → Q (imag) component via 4-PAM Gray mapping
  - 4-PAM levels: {-3, -1, +1, +3}
  - Gray mapping: 00→-3, 01→-1, 11→+1, 10→+3
"""

import numpy as np


def _gray_inverse_table(sqrt_m: int) -> np.ndarray:
    """Return a lookup table: gray_code_value → natural index."""
    table = np.zeros(sqrt_m, dtype=int)
    for nat_idx in range(sqrt_m):
        gray_val = nat_idx ^ (nat_idx >> 1)
        table[gray_val] = nat_idx
    return table


def _pam_levels(sqrt_m: int) -> np.ndarray:
    """PAM constellation levels: [-(sqrt_m-1), ..., -1, 1, ..., (sqrt_m-1)]."""
    return np.arange(-(sqrt_m - 1), sqrt_m, 2, dtype=float)


def qammod(bits: np.ndarray, m_order: int) -> np.ndarray:
    """
    Gray-coded QAM modulation.

    Parameters
    ----------
    bits : np.ndarray, shape (B*N_symbols, K)
        Binary bit matrix (values 0 or 1).
    m_order : int
        Modulation order (e.g., 16 for 16-QAM).

    Returns
    -------
    symbols : np.ndarray, shape (N_symbols, K), complex
        Complex QAM symbols.
    """
    b_per_sym = int(np.log2(m_order))
    sqrt_m = int(np.sqrt(m_order))
    b_half = b_per_sym // 2

    total_bits, n_users = bits.shape
    n_symbols = total_bits // b_per_sym

    bits_3d = bits.reshape(n_symbols, b_per_sym, n_users)  # (N, B, K)
    bits_i = bits_3d[:, :b_half, :]    # first B/2 bits → I
    bits_q = bits_3d[:, b_half:, :]    # last  B/2 bits → Q

    gray_inv = _gray_inverse_table(sqrt_m)
    levels   = _pam_levels(sqrt_m)

    def bits_to_pam(b_chunk: np.ndarray) -> np.ndarray:
        """b_chunk: (N, b_half, K) → PAM level (N, K)."""
        powers = 2 ** np.arange(b_half - 1, -1, -1)   # MSB first
        gray_idx = np.einsum("nbk,b->nk", b_chunk.astype(int), powers)
        nat_idx  = gray_inv[gray_idx]
        return levels[nat_idx]

    sym_i = bits_to_pam(bits_i)
    sym_q = bits_to_pam(bits_q)
    return sym_i + 1j * sym_q


def qamdemod(symbols: np.ndarray, m_order: int) -> np.ndarray:
    """
    Gray-coded QAM demodulation.

    Parameters
    ----------
    symbols : np.ndarray, shape (N_symbols,) or (N_symbols, K), complex
        Received complex symbols.
    m_order : int
        Modulation order (e.g., 16).

    Returns
    -------
    bits : np.ndarray of int, shape (B*N_symbols,) or (B*N_symbols, K)
        Decoded bit matrix.
    """
    b_per_sym = int(np.log2(m_order))
    sqrt_m = int(np.sqrt(m_order))
    b_half = b_per_sym // 2

    flat = symbols.ndim == 1
    if flat:
        symbols = symbols[:, np.newaxis]

    n_symbols, n_users = symbols.shape
    levels = _pam_levels(sqrt_m)    # shape (sqrt_m,)

    def pam_to_bits(x: np.ndarray) -> np.ndarray:
        """x: (N, K) real component → bits (N, b_half, K)."""
        # Nearest neighbour decision
        diffs   = np.abs(x[:, :, np.newaxis] - levels[np.newaxis, np.newaxis, :])
        nat_idx = np.argmin(diffs, axis=2)                   # (N, K)
        gray_idx = nat_idx ^ (nat_idx >> 1)                  # (N, K)
        out_bits = np.zeros((n_symbols, b_half, n_users), dtype=int)
        for bit_pos in range(b_half):
            out_bits[:, b_half - 1 - bit_pos, :] = (gray_idx >> bit_pos) & 1
        return out_bits                                       # (N, b_half, K)

    bits_i = pam_to_bits(np.real(symbols))  # (N, b_half, K)
    bits_q = pam_to_bits(np.imag(symbols))  # (N, b_half, K)

    # Concatenate along bit axis: I bits first, Q bits after → (N, B, K)
    bits_3d = np.concatenate([bits_i, bits_q], axis=1)       # (N, B, K)

    # Reshape to (B*N, K) to match MATLAB column layout
    bits_out = bits_3d.transpose(0, 2, 1)   # (N, K, B)
    bits_out = bits_out.reshape(n_symbols, n_users, b_per_sym)  # (N, K, B)
    bits_out = bits_out.transpose(0, 2, 1)  # (N, B, K)
    bits_out = bits_out.reshape(n_symbols * b_per_sym, n_users)

    return bits_out[:, 0] if flat else bits_out
