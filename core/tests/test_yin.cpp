#include "pitch/yin.h"

#include <catch2/catch_test_macros.hpp>

#include <cmath>
#include <numbers>
#include <vector>

namespace {

constexpr float kSr = 44100.0f;
constexpr std::size_t kFrame = 2048;
constexpr float kFmin = 50.0f;
constexpr float kFmax = 1000.0f;

std::vector<float> sine(float freq, float amp = 0.5f, std::size_t n = kFrame, float sr = kSr)
{
    std::vector<float> y(n);
    const double w = 2.0 * std::numbers::pi * freq / sr;
    for (std::size_t i = 0; i < n; ++i)
        y[i] = amp * static_cast<float>(std::sin(w * static_cast<double>(i)));
    return y;
}

double cents(double est, double ref) { return 1200.0 * std::log2(est / ref); }

} // namespace

TEST_CASE("sine at 440 Hz is detected within 1 cent", "[yin]")
{
    const auto y = sine(440.0f);
    const float f0 = pitch::yin(y, kSr, kFmin, kFmax);

    INFO("f0 = " << f0 << " Hz");
    REQUIRE(std::isfinite(f0));
    CHECK(std::abs(cents(f0, 440.0)) < 1.0);
}
