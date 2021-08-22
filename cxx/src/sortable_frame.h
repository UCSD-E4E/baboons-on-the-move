#pragma once
#include <cstdint>

template <typename frame_type> struct sortable_frame {
  std::uint64_t number;
  frame_type frame;

  // Makes this a Compare type
  friend bool operator<(const sortable_frame &l, const sortable_frame &r) {
    return l.number < r.number;
  }

  friend bool operator<(const sortable_frame &l, const std::uint64_t &r) {
    return l.number < r;
  }

  friend bool operator<(const std::uint64_t &l, const sortable_frame &r) {
    return l < r.number;
  }
};
