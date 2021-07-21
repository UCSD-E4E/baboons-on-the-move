#include "pipes.h"

#include <fmt/core.h>

#include <opencv2/core.hpp>
#include <opencv2/imgproc.hpp>
#include <opencv2/photo.hpp>

#include <utility>

namespace baboon_tracking {
frame convert_bgr_to_gray::run(frame &&color_frame) const {
  cv::cvtColor(color_frame.image, color_frame.image, cv::COLOR_BGR2GRAY);
  return std::move(color_frame);
}

frame blur_gray::run(frame &&gray_frame) const {
  // sigma_x = sigma_y = 0 implies that the Gaussian kernel standard deviation
  // is calculated from the kernel size
  cv::GaussianBlur(gray_frame.image, gray_frame.image,
                   {kernel_size, kernel_size}, 0, 0);
  return std::move(gray_frame);
}

frame denoise::run(frame &&gray_frame) const {
  cv::fastNlMeansDenoisingColored(gray_frame.image, gray_frame.image,
                                  denoise_strength);
  return std::move(gray_frame);
}
} // namespace baboon_tracking
