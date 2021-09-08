#include <chrono>
#include <cstdlib>
#include <string>
#include <tuple>

#include <fmt/format.h>

#include <opencv2/core.hpp>
#ifdef DEBUG_DRAW
#include <opencv2/highgui.hpp>
#endif
#ifdef USE_CUDA
#include <opencv2/cudacodec.hpp>
#else
#include <opencv2/imgcodecs.hpp>
#endif
#include <opencv2/videoio.hpp>

#include "constant_velocity_kalman_filter.h"
#include "pipes.h"

#ifdef DEBUG_DRAW
void show(std::string window_name, cv::InputArray image) {
    static std::map<std::string, bool> has_shown;
    if (!has_shown[window_name])
      cv::namedWindow(window_name, cv::WINDOW_KEEPRATIO);
    cv::imshow(window_name, image);
    if (!has_shown[window_name]) {
      // Frame is too big to display on my screen
      cv::resizeWindow(window_name, image.cols() / 4.0, image.rows() / 4.0);
      has_shown[window_name] = true;
    }
}
#endif

template <typename frame> class pipeline {
private:
  using bt = baboon_tracking::pipes<frame>;

public:
  pipeline(std::shared_ptr<baboon_tracking::historical_frames_container<frame>>
               hist_frames)
      : convert_bgr_to_gray{}, blur_gray{3}, compute_homography{0.27, 4.96,
                                                                0.13, 10001,
                                                                hist_frames},
        transform_history_frames_and_masks{hist_frames},
        rescale_transformed_history_frames{48}, generate_weights{},
        generate_history_of_dissimilarity{}, intersect_frames{},
        union_intersected_frames{}, subtract_background{hist_frames},
        compute_moving_foreground{hist_frames}, apply_masks{},
        erode_dialate{5, 10}, detect_blobs{} {}

  auto process(std::uint64_t current_frame_num, frame &&bgr_frame) {
    auto drawing_frame = bgr_frame.clone();
    auto gray_frame = convert_bgr_to_gray.run(std::move(bgr_frame));
    auto blurred_frame = blur_gray.run(std::move(gray_frame));

    auto homographies =
        compute_homography.run(current_frame_num, std::move(blurred_frame));
    if (homographies.empty())
      return std::vector<cv::Rect>{};

    auto [transformed_history_frames, transformed_masks] =
        transform_history_frames_and_masks.run(current_frame_num,
                                               std::move(homographies));
    auto transformed_rescaled_history_frames =
        rescale_transformed_history_frames.run(transformed_history_frames);
    auto weights = generate_weights.run(transformed_rescaled_history_frames);
    auto history_of_dissimilarity = generate_history_of_dissimilarity.run(
        transformed_history_frames, transformed_rescaled_history_frames);
    auto intersected_frames =
        intersect_frames.run(std::move(transformed_history_frames),
                             std::move(transformed_rescaled_history_frames));
    auto union_of_all =
        union_intersected_frames.run(std::move(intersected_frames));
    auto foreground = subtract_background.run(current_frame_num,
                                              std::move(union_of_all), weights);
    auto moving_foreground = compute_moving_foreground.run(
        std::move(history_of_dissimilarity), std::move(foreground),
        std::move(weights));
    apply_masks.run(&moving_foreground, std::move(transformed_masks));
    erode_dialate.run(&moving_foreground);
    auto blobs = detect_blobs.run(std::move(moving_foreground));

    fmt::print("{} done\n", current_frame_num);

    return blobs;
  }

private:
  typename bt::convert_bgr_to_gray convert_bgr_to_gray;
  typename bt::blur_gray blur_gray;

  typename bt::compute_homography compute_homography;
  typename bt::transform_history_frames_and_masks
      transform_history_frames_and_masks;
  typename bt::rescale_transformed_history_frames
      rescale_transformed_history_frames;
  typename bt::generate_weights generate_weights;
  typename bt::generate_history_of_dissimilarity
      generate_history_of_dissimilarity;
  typename bt::intersect_frames intersect_frames;
  typename bt::union_intersected_frames union_intersected_frames;
  typename bt::subtract_background subtract_background;
  typename bt::compute_moving_foreground compute_moving_foreground;
  typename bt::apply_masks apply_masks;
  typename bt::erode_dilate erode_dialate;
  typename bt::detect_blobs detect_blobs;
};

int main() {
  constexpr unsigned int max_threads = 8; // TODO: put the thread pool back optionally
  constexpr auto input_file_name = "./input.mp4";

  // TODO: we're using USE_CUDA elsewhere to mean that CUDA headers are
  // available (an unfortunate kludge that happens because some builds of OpenCV
  // don't even come with the OpenCV CUDA headers even though those headers have
  // appropriate stubbed functions). This is not with the spirit of the meaning
  // of USE_CUDA (i.e. USE_CUDA should probably only be touched here, while
  // HAS_CUDA should maybe be used elsewhere?)
  cv::Mat frame_host;
#ifdef USE_CUDA
  cv::cuda::GpuMat frame;
#else
  cv::Mat frame = frame_host;
#endif

  cv::VideoCapture vc{};
  if (!vc.open(input_file_name, cv::CAP_FFMPEG)) {
    throw std::runtime_error{fmt::format("Couldn't open {}", input_file_name)};
  }
  const auto fps = vc.get(cv::CAP_PROP_FPS);

  auto hist_frames = std::make_shared<
      baboon_tracking::historical_frames_container<decltype(frame)>>(
      9, max_threads);
  pipeline pl{hist_frames};


  baboon_tracking::constant_velocity_kalman_filter<20> kf{
      {9, 9, 2, 2}, // Units are pixels, pixels, pixels/s, pixels/s respectively
      {2, 2, 5, 5}, // Units are all pixels
      30,           // Units are pixels
      1.0 / fps // s/frame
  };
  static constexpr int actual_num_baboons = 1;
  kf.set_x_hat(0, 2920);
  kf.set_x_hat(1, 1210);

  for (std::uint64_t i = 0; vc.read(frame_host) && !frame_host.empty(); i++) {
#ifdef USE_CUDA
    frame.upload(frame_host);
#endif

#ifdef DEBUG_DRAW
    auto drawing_frame = cv::Mat{frame}.clone();
#endif

    auto start = std::chrono::steady_clock::now();
    auto bounding_boxes = pl.process(i, std::move(frame));
    auto end = std::chrono::steady_clock::now();

    frame = decltype(frame){};

    fmt::print(
        "Took {} ms\n",
        std::chrono::duration_cast<std::chrono::milliseconds>(end - start)
            .count());

    if (!bounding_boxes.empty()) {
      auto x_hat = kf.run(actual_num_baboons, bounding_boxes);

#ifdef DEBUG_DRAW
      static const auto bounding_box_color = cv::Scalar(255, 0, 0);
      for (auto &&bounding_box : bounding_boxes) {
        cv::rectangle(drawing_frame, bounding_box, bounding_box_color, 4);
      }

      for (int j = 0; j < kf.states_per_baboon * actual_num_baboons;
           j += kf.states_per_baboon) {
        cv::circle(drawing_frame,
                   {static_cast<int>(std::round(x_hat[j + 0])),
                    static_cast<int>(std::round(x_hat[j + 1]))},
                   3, {0, 255, 0}, 5);
        fmt::print("kf estimate at ({}, {}) with velocity of ({}, {})\n",
                   x_hat[j + 0], x_hat[j + 1], x_hat[j + 2], x_hat[j + 3]);
      }

      show("Blobs on frame", drawing_frame);
      cv::waitKey();
#endif
    }
  }

  fmt::print("finished\n");

  return EXIT_SUCCESS;
}
