#include <chrono>
#include <cstdlib>
#include <string>
#include <tuple>

#include <fmt/core.h>

#include <opencv2/imgcodecs.hpp>
#include <opencv2/videoio.hpp>

#include "pipes.h"

class pipeline {
public:
  pipeline(
      std::shared_ptr<baboon_tracking::historical_frames_container> hist_frames)
      : convert_bgr_to_gray{}, blur_gray{3}, compute_homography{0.7, 0.2, 0.1,
                                                                1000,
                                                                hist_frames},
        transform_history_frames_and_masks{hist_frames},
        rescale_transformed_history_frames{0.5}, generate_weights{},
        generate_history_of_dissimilarity{}, intersect_frames{},
        union_intersected_frames{}, subtract_background{hist_frames},
        compute_moving_foreground{hist_frames}, apply_masks{}, detect_blobs{} {}

  auto process(baboon_tracking::frame &&bgr_frame) {
    auto gray_frame = convert_bgr_to_gray.run(std::move(bgr_frame));
    auto blurred_frame = blur_gray.run(std::move(gray_frame));

    auto [current_frame_num, homographies] =
        compute_homography.run(std::move(blurred_frame));
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
    auto blobs = detect_blobs.run(std::move(moving_foreground));

    return blobs;
  }

private:
  baboon_tracking::convert_bgr_to_gray convert_bgr_to_gray;
  baboon_tracking::blur_gray blur_gray;

  baboon_tracking::compute_homography compute_homography;
  baboon_tracking::transform_history_frames_and_masks
      transform_history_frames_and_masks;
  baboon_tracking::rescale_transformed_history_frames
      rescale_transformed_history_frames;
  baboon_tracking::generate_weights generate_weights;
  baboon_tracking::generate_history_of_dissimilarity
      generate_history_of_dissimilarity;
  baboon_tracking::intersect_frames intersect_frames;
  baboon_tracking::union_intersected_frames union_intersected_frames;
  baboon_tracking::subtract_background subtract_background;
  baboon_tracking::compute_moving_foreground compute_moving_foreground;
  baboon_tracking::apply_masks apply_masks;
  baboon_tracking::detect_blobs detect_blobs;
};

int main() {
  auto hist_frames =
      std::make_shared<baboon_tracking::historical_frames_container>(100);
  pipeline pl{hist_frames};

  // cv::VideoCapture vc{"./sample_1920x1080.avi"};
  cv::Mat image = cv::imread("./maxresdefault.jpg");
  for (std::uint64_t i = 0; /*vc.read(image)*/; i++) {
    auto start = std::chrono::steady_clock::now();
    baboon_tracking::frame fr{i, image.clone()};
    pl.process(std::move(fr));
    auto end = std::chrono::steady_clock::now();

    /*if (res.size() > 0) {
      std::string res_contents = "Result: ";
      res_contents << res[0];

      fmt::print("{}; a {}x{} cv::Mat\n", res_contents, res[0].rows,
                 res[1].cols);
    }*/
    fmt::print(
        "Took {} ms\n",
        std::chrono::duration_cast<std::chrono::milliseconds>(end - start)
            .count());
  }

  return EXIT_SUCCESS;
}
