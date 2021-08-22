#pragma once

#ifdef USE_CUDA
#include <opencv2/cudaarithm.hpp>
#include <opencv2/cudafeatures2d.hpp>
#include <opencv2/cudafilters.hpp>
#include <opencv2/cudaimgproc.hpp>
#include <opencv2/cudawarping.hpp>
#else
#include <opencv2/core.hpp>
#include <opencv2/imgproc.hpp>
#endif

namespace baboon_tracking {
template <typename frame> struct cv_specializations {
  // This typedef will have the same type as frame, but frame has a different
  // meaning and isn't appropriate for some places where we'd like to use either
  // CPU or GPU Mats
  using cpu_or_gpu_mat = cv::Mat;
  static constexpr bool is_cuda = false;

  static constexpr auto cvtColor = cv::cvtColor;
  static constexpr auto compare = cv::compare;
  static constexpr auto add = cv::add;
  static constexpr auto scaleAdd = cv::scaleAdd;
  static constexpr auto absdiff = cv::absdiff;
  static constexpr auto multiply = [](auto a, auto b, auto c, double scale = 1,
                                      int dtype = -1) {
    cv::multiply(a, b, c, scale, dtype);
  };
  static constexpr auto bitwise_or = [](auto a, auto b, auto c) {
    cv::bitwise_or(a, b, c);
  }; // I guess I'll reproduce OpenCV's painfully inconsistient naming
     // conventions in the alias names?
  static constexpr auto bitwise_and = [](auto a, auto b, auto c) {
    cv::bitwise_and(a, b, c);
  };
  static constexpr auto warpPerspective = [](auto a, auto b, auto c, auto d) {
    cv::warpPerspective(a, b, c, d);
  };
  static constexpr auto erode = cv::erode;
};

#ifdef USE_CUDA
template <> struct cv_specializations<cv::cuda::GpuMat> {
  using cpu_or_gpu_mat = cv::cuda::GpuMat;
  static constexpr bool is_cuda = true;

  // Unfortunately aliasing functions this way requires us to do this lambda
  // trick if one of CUDA functions takes more arguments (even if those
  // arguments are optional.) This means we have to do this in almost every case
  // because pretty much every CUDA function takes an extra cv::cuda::Stream
  // argument.
  static constexpr auto cvtColor = [](auto a, auto b, auto c, auto d) {
    cv::cuda::cvtColor(a, b, c, d);
  };
  static constexpr auto compare = [](auto a, auto b, auto c, auto d) {
    cv::cuda::compare(a, b, c, d);
  };
  static constexpr auto add = [](auto a, auto b, auto c, auto d, auto e) {
    cv::cuda::add(a, b, c, d, e);
  };
  static constexpr auto scaleAdd = [](auto a, auto b, auto c, auto d) {
    cv::cuda::scaleAdd(a, b, c, d);
  };
  static constexpr auto absdiff = [](auto a, auto b, auto c) {
    cv::cuda::absdiff(a, b, c);
  };
  static constexpr auto multiply = [](auto a, auto b, auto c, double scale = 1,
                                      int dtype = -1) {
    cv::cuda::multiply(a, b, c, scale, dtype);
  };
  static constexpr auto bitwise_or = [](auto a, auto b, auto c) {
    cv::cuda::bitwise_or(a, b, c);
  };
  static constexpr auto bitwise_and = [](auto a, auto b, auto c) {
    cv::cuda::bitwise_and(a, b, c);
  };
  static constexpr auto warpPerspective = [](auto a, auto b, auto c, auto d) {
    cv::cuda::warpPerspective(a, b, c, d);
  };
};
#endif
} // namespace baboon_tracking
