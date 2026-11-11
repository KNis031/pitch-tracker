#include "pitch/yin.h"

#include <limits>

namespace pitch {

float yin(std::span<const float> frame, float sr, float fmin, float fmax, float threshold)
{
    // TODO(Karl): implement, see python/yin_ref.py.
    (void)frame; (void)sr; (void)fmin; (void)fmax; (void)threshold;
    return std::numeric_limits<float>::quiet_NaN();
}

} // namespace pitch
