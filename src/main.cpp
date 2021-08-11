#include <chrono>
#include <cstdlib>
#include <string>
#include <tuple>

#include <fmt/format.h>

#include <opencv2/core.hpp>
#include <opencv2/highgui.hpp>
#include <opencv2/imgcodecs.hpp>
#include <opencv2/videoio.hpp>

#include "pipes.h"
#include "thread_pool.h"

constexpr bool should_show = true;
void show(std::string window_name, cv::InputArray image) {
  if (!should_show)
    return;

  static std::map<std::string, bool> has_shown;
  if (!has_shown[window_name])
    cv::namedWindow(window_name, cv::WINDOW_KEEPRATIO);
  cv::imshow(window_name, image);
  if (!has_shown[window_name]) {
    cv::resizeWindow(window_name, image.cols() / 4.0, image.rows() / 4.0);
    has_shown[window_name] = true;
  }
}

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
        compute_moving_foreground{hist_frames}, apply_masks{}, erode{3},
        detect_blobs{} {}

  auto process(std::uint64_t current_frame_num, frame &&bgr_frame) {
    auto drawing_frame = bgr_frame;
    auto gray_frame = convert_bgr_to_gray.run(std::move(bgr_frame));
    auto blurred_frame = blur_gray.run(std::move(gray_frame));

    // TODO: don't return current_frame_num anymore
    auto homographies =
        compute_homography.run(current_frame_num, std::move(blurred_frame));
    if (homographies.empty())
      return std::vector<cv::Rect>{};

    auto [transformed_history_frames, transformed_masks] =
        transform_history_frames_and_masks.run(current_frame_num,
                                               std::move(homographies));
    auto transformed_rescaled_history_frames =
        rescale_transformed_history_frames.run(transformed_history_frames);
    // show("Current frame, transformed",
    // transformed_history_frames[transformed_history_frames.size() - 1]);
    // show("Current frame, transformed and rescaled",
    // transformed_rescaled_history_frames[transformed_rescaled_history_frames.size()
    // - 1]);
    auto weights = generate_weights.run(transformed_rescaled_history_frames);
    auto history_of_dissimilarity = generate_history_of_dissimilarity.run(
        transformed_history_frames, transformed_rescaled_history_frames);
    auto intersected_frames =
        intersect_frames.run(std::move(transformed_history_frames),
                             std::move(transformed_rescaled_history_frames));
    auto union_of_all =
        union_intersected_frames.run(std::move(intersected_frames));
    // show("Union of all", union_of_all);
    auto foreground = subtract_background.run(current_frame_num,
                                              std::move(union_of_all), weights);
    // show("Foreground", foreground);
    // show("History of dissimilarity", history_of_dissimilarity);
    // show("Weights", weights);
    auto moving_foreground = compute_moving_foreground.run(
        std::move(history_of_dissimilarity), std::move(foreground),
        std::move(weights));
    apply_masks.run(&moving_foreground, std::move(transformed_masks));
    erode.run(&moving_foreground);
    // show("Moving foreground", moving_foreground);
    auto blobs = detect_blobs.run(std::move(moving_foreground));
    static const auto color = cv::Scalar(255, 0, 0);
    for (auto &&blob : blobs) {
      cv::rectangle(drawing_frame, blob, color, 4);
    }
    show("Blobs on frame", drawing_frame);

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
  typename bt::erode erode;
  typename bt::detect_blobs detect_blobs;
};

int main() {
  unsigned int max_threads = 8;
  std::uint64_t max_tasks =
      15; // We can't have unlimited tasks because they keep frames around in
          // memory, which can lead to excessive memory usage if left unchecked

  cv::Mat image;
  auto hist_frames = std::make_shared<
      baboon_tracking::historical_frames_container<decltype(image)>>(
      9, max_threads);
  pipeline pl{hist_frames};

  baboon_tracking::thread_pool tp{max_tasks, max_threads};

  cv::VideoCapture vc{"./input.mp4"};
  for (std::uint64_t i = 0; vc.read(image); i++) {
    cv::waitKey();

    auto start = std::chrono::steady_clock::now();
    auto blobs = pl.process(i, image.clone());
    auto end = std::chrono::steady_clock::now();

    fmt::print(
        "Took {} ms\n",
        std::chrono::duration_cast<std::chrono::milliseconds>(end - start)
            .count());
  }

  fmt::print("finished");

  return EXIT_SUCCESS;
}
