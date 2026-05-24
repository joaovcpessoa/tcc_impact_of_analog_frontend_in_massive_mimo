"""
Nonlinear power amplifier models.

All models implement AM-AM (and optionally AM-PM) distortion.
The gain in small-signal regime is normalised to 1.

Models
------
IDEAL : Linear passthrough (no distortion).
CLIP  : Ideal clipping amplifier – AM-AM only.
SS    : Solid-state amplifier (Rapp model) – AM-AM only.
TWT   : Travelling-wave tube amplifier (Saleh model) – AM-AM + AM-PM.
"""

from dataclasses import dataclass, field
from typing import Optional
import numpy as np


# ---------------------------------------------------------------------------
# Parameter containers
# ---------------------------------------------------------------------------

@dataclass
class ClipParams:
    A0: float = 1.0                  # saturation amplitude


@dataclass
class SSParams:
    A0: float  = 1.0                 # saturation amplitude
    rho: float = 1.0                 # smoothness parameter (p in thesis)


@dataclass
class TWTParams:
    chi_A:     float = 1.0           # AM-AM gain coefficient
    kappa_A:   float = 0.25          # AM-AM saturation coefficient
    chi_phi:   float = 0.26          # AM-PM gain coefficient
    kappa_phi: float = 0.25          # AM-PM saturation coefficient


# Default TWT parameter sets from Saleh (1981) – Table 4.1 of thesis
TWT_PARAM_SETS = [
    TWTParams(chi_A=1.6397, kappa_A=0.0618,  chi_phi=0.2038, kappa_phi=0.1332),
    TWTParams(chi_A=1.9638, kappa_A=0.9945,  chi_phi=2.5293, kappa_phi=2.8168),
    TWTParams(chi_A=2.1587, kappa_A=1.1517,  chi_phi=4.0033, kappa_phi=9.1040),
]

# Default CLIP / SS saturation levels used in thesis simulations
CLIP_SS_A0_VALUES = [0.5, 1.0, 1.5, 2.0, 2.5]


# ---------------------------------------------------------------------------
# Core amplifier functions
# ---------------------------------------------------------------------------

def amplify_ideal(x: np.ndarray) -> np.ndarray:
    """Identity (no distortion)."""
    return x.copy()


def amplify_clip(x: np.ndarray, params: ClipParams) -> np.ndarray:
    """
    Ideal clipping amplifier (AM-AM only, no AM-PM).

    f_A(A) = A         if A ≤ A0
             A0        if A > A0
    """
    A  = np.abs(x)
    A0 = params.A0
    A_out = np.minimum(A, A0)
    return A_out * np.exp(1j * np.angle(x))


def amplify_ss(x: np.ndarray, params: SSParams) -> np.ndarray:
    """
    Solid-state amplifier (Rapp model, AM-AM only).

    f_A(A) = A / (1 + (A/A0)^(2ρ))^(1/(2ρ))
    """
    A   = np.abs(x)
    A0  = params.A0
    rho = params.rho
    denom  = (1.0 + (A / A0) ** (2.0 * rho)) ** (1.0 / (2.0 * rho))
    A_out  = A / denom
    return A_out * np.exp(1j * np.angle(x))


def amplify_twt(x: np.ndarray, params: TWTParams) -> np.ndarray:
    """
    Travelling-wave tube amplifier (Saleh model, AM-AM + AM-PM).

    f_A(A)   = χ_A · A / (1 + κ_A · A²)
    f_φ(A)   = χ_φ · A² / (1 + κ_φ · A²)
    """
    A = np.abs(x)
    g_A   = (params.chi_A   * A)      / (1.0 + params.kappa_A   * A ** 2)
    g_phi = (params.chi_phi * A ** 2) / (1.0 + params.kappa_phi * A ** 2)
    return g_A * np.exp(1j * (np.angle(x) + g_phi))


# ---------------------------------------------------------------------------
# Unified dispatcher
# ---------------------------------------------------------------------------

def amplify(x: np.ndarray, amp_type: str, params=None) -> np.ndarray:
    """
    Apply an amplifier model to a complex signal.

    Parameters
    ----------
    x        : Complex signal array (any shape).
    amp_type : 'IDEAL', 'CLIP', 'SS', or 'TWT'.
    params   : Parameter object matching the amp_type, or None for IDEAL.

    Returns
    -------
    Complex array of the same shape as x.
    """
    amp_type = amp_type.upper()
    if amp_type == "IDEAL":
        return amplify_ideal(x)
    elif amp_type == "CLIP":
        return amplify_clip(x, params)
    elif amp_type == "SS":
        return amplify_ss(x, params)
    elif amp_type == "TWT":
        return amplify_twt(x, params)
    else:
        raise ValueError(f"Unknown amplifier type: '{amp_type}'")
