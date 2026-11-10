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


def parabolic_interpolation(x: float, y_left: float, y_mid: float, y_right: float) -> float:
    """Abscissa of the vertex of the parabola through (x-1, y_left), (x, y_mid), (x+1, y_right).

    Step 5 of the paper (Sec. II.E): refines an integer lag to sub-sample precision.
    """
    return x + (1 / 2) * (y_left - y_right) / (y_left - 2 * y_mid + y_right)


def yin(frame: np.ndarray, sr: int, fmin: float, fmax: float, threshold: float = 0.1) -> float:
    """Estimate f0 of a single frame with YIN.

    Args:
        frame: mono audio samples. Must be longer than sr / fmin; the window
            length is W = len(frame) - tau_max.
        sr: sample rate in Hz.
        fmin, fmax: search range in Hz; sets the lag range tau_min..tau_max.
        threshold: absolute threshold on d'(tau) for step 4 (paper uses 0.1).

    Returns:
        f0 in Hz, or np.nan if the frame is silent or unvoiced.
    """
    tau_min = int(sr // fmax)
    tau_max = int(np.ceil(sr / fmin))
    assert len(frame) > tau_max, "frame must be longer than the period of fmin"

    lags = np.arange(tau_min, tau_max, 1)
    w_length = len(frame) - lags[-1]

    # Silent window: d(tau) would be 0 for all lags and d' undefined (0/0).
    if not np.any(frame[:w_length]):
        return np.nan

    # Sum of d(j) for j < tau_min, needed for the cumulative mean in eq. (8).
    pre_lag_sum = np.sum([difference(frame, j, w_length) for j in range(1, lags[0])])

    # Step 3: cumulative mean normalized difference d'(tau), eq. (8).
    d = np.array([difference(frame, tau, w_length) for tau in lags])
    d_prime = d * lags / (pre_lag_sum + np.cumsum(d))

    # Step 4 (absolute threshold): take the first dip of d' below threshold;
    # if there is none, fall back to the global minimum.
    indices = np.where((d_prime[1:-1] < threshold) & (d_prime[2:] > d_prime[1:-1]))[0]
    if indices.size:
        best = indices[0] + 1
    else:
        best = np.nanargmin(d_prime)

    if d_prime[best] >= UNVOICED_RATIO * threshold:
        return np.nan

    # No neighbours on both sides at the edges of the lag range: skip interpolation.
    if best == 0 or best == lags.shape[0] - 1:
        return (1 / lags[best]) * sr

    # Step 5: interpolate on raw d, not d', since d' biases the vertex (Sec. II.E).
    d_left, d_mid, d_right = [difference(frame, lags[best + i], w_length) for i in range(-1, 2)]
    tau0 = parabolic_interpolation(lags[best], d_left, d_mid, d_right)

    return (1 / tau0) * sr
