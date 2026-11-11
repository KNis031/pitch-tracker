#pragma once

#include <span>

namespace pitch {

// Estimate f0 of one frame with YIN (de Cheveigné & Kawahara, 2002).
// Mirrors python/yin_ref.py:yin.
//
// frame:      mono samples; frame.size() must be larger than sr / fmin.
// sr:         sample rate in Hz.
// fmin, fmax: search range in Hz.
// threshold:  absolute threshold on d'(tau), step 4.
//
// Returns f0 in Hz, or NaN if the frame is silent or unvoiced.
float yin(std::span<const float> frame, float sr, float fmin, float fmax,
          float threshold = 0.1f);

} // namespace pitch
