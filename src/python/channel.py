import numpy as np

def user_position_generator(n_users: int, cell_radius: float, rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray]:
    """
    Place K users randomly inside a hexagonal cell.
    The hexagon is divided into 3 sectors (rhombuses).  Users are assigned to
    sectors uniformly at random, then placed uniformly within each sector
    Replicates the MATLAB `user_position_generator.m` exactly

    Parameters:
        n_users     : Number of users K
        cell_radius : Cell radius R (metres)
        rng         : NumPy random Generator (for reproducibility)

    Returns: x, y : Arrays of shape (K,) with user coordinates in metres.
    """
    r = np.sqrt(3) / 2 * cell_radius          # apothem

    aux = rng.random(n_users)
    k1 = int(np.sum(aux < 1 / 3))
    k2 = int(np.sum((aux >= 1 / 3) & (aux < 2 / 3)))
    # k3 = n_users - k1 - k2

    u = rng.random(n_users)
    v = rng.random(n_users)

    u1, v1 = u[:k1],         v[:k1]
    u2, v2 = u[k1:k1 + k2],  v[k1:k1 + k2]
    u3, v3 = u[k1 + k2:],    v[k1 + k2:]

    # Sector 1
    x1 = -cell_radius / 2 * u1 + cell_radius * v1
    y1 =  r * u1

    # Sector 2
    x2 = -cell_radius / 2 * u2 - cell_radius / 2 * v2
    y2 = -r * u2 + r * v2

    # Sector 3
    x3 =  cell_radius * u3 - cell_radius / 2 * v3
    y3 = -r * v3

    x = np.concatenate([x1, x2, x3])
    y = np.concatenate([y1, y2, y3])
    return x, y

def rician_channel(n_antennas: int, n_users: int, k_factor: float, theta_users: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """
    Generate a Rician flat-fading channel matrix H ∈ C^{MxK}
    H = sqrt(K/(1+K)) * H_LoS  +  sqrt(1/(1+K)) * H_NLoS
    H_LoS is built from ULA steering vectors (half-wavelength spacing)
    H_NLoS ~ CN(0, I_M ⊗ I_K)  (spatial correlation R = I_M)
    Parameters:
        n_antennas  : Number of BS antennas M.
        n_users     : Number of single-antenna users K.
        k_factor    : Rician K-factor (linear, not dB).
        theta_users : AoA for each user, shape (K,), radians.
        rng         : NumPy random Generator.
    Returns: H : np.ndarray, shape (M, K), complex.
    """
    M, K = n_antennas, n_users
    m_idx = np.arange(M)[:, np.newaxis]            # (M, 1)

    # LoS component: ULA steering matrix
    A_los = np.exp(
        1j * 2 * np.pi * m_idx * 0.5 * np.sin(theta_users)[np.newaxis, :]
    )                                               # (M, K)
    H_los = np.sqrt(k_factor / (1.0 + k_factor)) * A_los

    # NLoS component (R = I_M, so sqrtm(R) = I_M)
    H_nlos = (rng.standard_normal((M, K)) + 1j * rng.standard_normal((M, K))) / np.sqrt(2)

    return H_los + np.sqrt(1.0 / (1.0 + k_factor)) * H_nlos
