#pragma once

#include <opencv2/core.hpp>

namespace baboon_tracking {
struct frame {
  std::uint64_t number;
  cv::Mat image;

  // frame(std::uint64_t number) : number{number} {};

  // Makes this a Compare type
  friend bool operator<(const frame &l, const frame &r) {
    return l.number < r.number;
  }

  friend bool operator<(const frame &l, const std::uint64_t &r) {
    return l.number < r;
  }

  friend bool operator<(const std::uint64_t &l, const frame &r) {
    return l < r.number;
  }
};
} // namespace baboon_tracking
