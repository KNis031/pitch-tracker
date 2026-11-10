"""Sine sweep: compare yin_ref.yin and librosa.yin against ground truth, in cents.

Run from this directory:  python check_librosa.py
"""

import librosa
import numpy as np

import yin_ref

SR = 44100
FRAME = 2048
HOP = 512
FMIN, FMAX = 50.0, 1000.0
DURATION = 0.5  # seconds per test tone


def cents(est, ref):
    return 1200.0 * np.log2(est / ref)


def frames(y):
    n = 1 + (len(y) - FRAME) // HOP
    return np.stack([y[i * HOP : i * HOP + FRAME] for i in range(n)])


def ref_f0(y):
    """Median of yin_ref over frames, or None if not implemented yet."""
    try:
        f0 = np.array([yin_ref.yin(f, SR, FMIN, FMAX) for f in frames(y)])
    except NotImplementedError:
        return None
    return np.nanmedian(f0)


def main():
    freqs = np.geomspace(60.0, 900.0, 20)
    t = np.arange(int(SR * DURATION)) / SR
    rows = []
    for f in freqs:
        y = 0.5 * np.sin(2 * np.pi * f * t)
        lib = np.nanmedian(
            librosa.yin(
                y, fmin=FMIN, fmax=FMAX, sr=SR, frame_length=FRAME, hop_length=HOP, center=False
            )
        )
        ref = ref_f0(y)
        rows.append((f, cents(lib, f), None if ref is None else cents(ref, f)))

    print(f"{'f0 [Hz]':>9} {'librosa [c]':>12} {'yin_ref [c]':>12}")
    for f, c_lib, c_ref in rows:
        ref_s = "     n/a" if c_ref is None else f"{c_ref:+12.2f}"
        print(f"{f:9.2f} {c_lib:+12.2f} {ref_s}")

    for name, col in (("librosa", 1), ("yin_ref", 2)):
        errs = np.array([r[col] for r in rows if r[col] is not None])
        if errs.size:
            print(
                f"{name}: mean |err| {np.mean(np.abs(errs)):.2f} c, "
                f"max |err| {np.max(np.abs(errs)):.2f} c"
            )
        else:
            print(f"{name}: not implemented")


if __name__ == "__main__":
    main()
