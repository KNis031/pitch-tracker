"""NumPy reference implementation of YIN.

de Cheveigné & Kawahara (2002), "YIN, a fundamental frequency estimator
for speech and music", JASA 111(4).

Used as a readable ground truth for the C++ implementation in core/,
not for speed.
"""

import numpy as np

# Frame is unvoiced if the best d'(tau) >= UNVOICED_RATIO * threshold.
# Own heuristic, not from the paper (which always returns an estimate).
UNVOICED_RATIO = 3


def difference(frame: np.ndarray, tau: int, w_length: int) -> float:
    """Difference function d(tau), eq. (6), with a fixed window of w_length samples.

    Compares frame[0:W] with frame[tau:tau+W]; the frame must hold W + tau samples.
    """
    return np.sum(np.square(frame[:w_length] - frame[tau : tau + w_length]))


def parabolic_interpolation(x: int, y_left: float, y_mid: float, y_right: float) -> float:
    """Vertex abscissa of the parabola through (x-1, y_left), (x, y_mid), (x+1, y_right).

    Step 5 (Sec. II.E): refines integer lag x to sub-sample precision.
    Returns x unchanged if the parabola is not convex (no minimum) or the
    vertex lies >= 1 sample from x (the points do not bracket a minimum).
    """
    denom = y_left - 2 * y_mid + y_right
    if denom <= 0:
        return float(x)
    shift = 0.5 * (y_left - y_right) / denom
    return x + shift if abs(shift) < 1 else float(x)


def yin(frame: np.ndarray, sr: int, fmin: float, fmax: float, threshold: float = 0.1) -> float:
    """Estimate f0 of a single frame with YIN.

    d(tau) is computed for tau_min-1 .. tau_max+1: one extra lag on each side,
    so every candidate in [tau_min, tau_max] has two neighbours for the
    local-minimum test and the interpolation. This costs one extra sample.

    Args:
        frame: mono audio samples, len(frame) >= tau_max + 2.
            Window length W = len(frame) - (tau_max + 1).
        sr: sample rate in Hz, sr >= 2 * fmax.
        fmin, fmax: search range in Hz; tau_min = sr // fmax, tau_max = ceil(sr / fmin).
        threshold: absolute threshold on d'(tau) for step 4 (paper uses 0.1).

    Returns:
        f0 in Hz, or np.nan if
          - the window is silent (all zeros),
          - the best d' >= UNVOICED_RATIO * threshold (unvoiced),
          - the best minimum is at an extra lag (f0 outside [fmin, fmax]).
    """
    assert sr >= 2 * fmax, "fmax must be at most sr / 2 (Nyquist)"
    tau_min = int(sr // fmax)
    tau_max = int(np.ceil(sr / fmin))

    assert len(frame) > tau_max + 1, "frame must have at least tau_max + 2 samples"
    # tau_min-1 .. tau_max+1 (see docstring).
    extended_lags = np.arange(tau_min - 1, tau_max + 2, 1)
    w_length = len(frame) - extended_lags[-1]

    # Silent window: d = 0 for all lags, d' = 0/0.
    if not np.any(frame[:w_length]):
        return np.nan

    # Sum of d(j) for 1 <= j < tau_min - 1: the cumulative mean in eq. (8) starts at j = 1.
    pre_lag_sum = np.sum([difference(frame, j, w_length) for j in range(1, extended_lags[0])])

    # Step 3: cumulative mean normalized difference d'(tau), eq. (8).
    d = np.array([difference(frame, tau, w_length) for tau in extended_lags])
    d_prime = d * extended_lags / (pre_lag_sum + np.cumsum(d))

    # Step 4 (absolute threshold): first local min of d' below threshold, tested on the
    # inner lags [1:-1] against both neighbours. If none, fall back to the global min.
    condition = (
        (d_prime[1:-1] <= d_prime[2:])
        & (d_prime[1:-1] < d_prime[:-2])
        & (d_prime[1:-1] < threshold)
    )
    dip_indices = np.where(condition)[0]
    if dip_indices.size:
        best = dip_indices[0] + 1
    else:
        best = np.nanargmin(d_prime)

    if d_prime[best] >= UNVOICED_RATIO * threshold:
        return np.nan

    # Global min at an extra lag: d' still falling at the edge, f0 outside [fmin, fmax].
    if best == 0 or best == extended_lags.shape[0] - 1:
        return np.nan

    # Step 5: interpolate on raw d, not d', since d' biases the vertex (Sec. II.E).
    tau0 = parabolic_interpolation(extended_lags[best], d[best - 1], d[best], d[best + 1])

    return sr / tau0
