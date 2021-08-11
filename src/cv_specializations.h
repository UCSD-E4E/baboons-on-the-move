#pragma once

#ifdef USE_CUDA
#include <opencv2/cudaarithm.hpp>
#include <opencv2/cudafeatures2d.hpp>
#include <opencv2/cudafilters.hpp>
#include <opencv2/cudaimgproc.hpp>
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
};

#ifdef HAS_CUDA
template <> struct cv_specializations<cv::cuda::GpuMat> {
  using cpu_or_gpu_mat = cv::cuda::GpuMat;
  static constexpr bool is_cuda = true;

  static constexpr auto cvtColor = [](auto a, auto b, auto c, auto d) {
    cv::cuda::cvtColor(a, b, c, d);
  };
};
#endif
} // namespace baboon_tracking
