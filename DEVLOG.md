# Devlog

**2026-11-10**: NumPy YIN reference (`python/yin_ref.py`) done: steps 1–5, unvoiced/silence handling; sine sweep 60–900 Hz within 0.01 c. Found librosa's +1–22 c bias: its difference function zero-pads past the frame (adds energy of the last τ samples). Added ruff.
Next: Catch2 via FetchContent, port YIN to C++ in `core/`, sine tests in ctest (B1).
Blocking: nothing.
