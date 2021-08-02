#include "pipes.h"

#include <opencv2/calib3d.hpp>
#include <opencv2/cudaarithm.hpp>
#include <opencv2/imgproc.hpp>

#include <mutex>
#include <tuple>
#include <vector>

#include "ssc.h"

namespace baboon_tracking {
void historical_frames_container::add_historical_frame(
    frame &&preprocessed_frame) {
  {
    std::scoped_lock lk{mutex};
    // This is just greater than we assume the caller adds a frame before
    // accessing it
    if (historical_frames.size() > max_frames) {
      historical_frames.erase(historical_frames.begin());
    }
    historical_frames.emplace(std::move(preprocessed_frame));
  }

  frame_added_cv.notify_all();
}

// std::tuple<const frame &, std::unique_lock<std::mutex>>
frame historical_frames_container::get_historical_frame(
    std::uint64_t frame_number) {
  std::unique_lock lk{mutex};

  if (!historical_frames.count(frame_number)) {
    frame_added_cv.wait(
        lk, [&historical_frames = historical_frames, frame_number]() {
          return historical_frames.count(frame_number);
        });
  }

  auto frame = historical_frames.find(frame_number);
  return *frame;
}

bool historical_frames_container::is_full() {
  std::unique_lock lk{mutex};
  return historical_frames.size() >= max_frames;
}
} // namespace baboon_tracking

namespace baboon_tracking {
compute_homography::compute_homography(compute_homography &&old) {
  std::scoped_lock lk(old.memo_map_mutex);

  good_match_percent = old.good_match_percent;
  ransac_max_reproj_error = old.ransac_max_reproj_error;
  ssc_tolerance = old.ssc_tolerance;
  ssc_num_ret_points = old.ssc_num_ret_points;

  fast_detector = std::move(old.fast_detector);
  orb_detector = std::move(old.orb_detector);
  descriptor_matcher = std::move(old.descriptor_matcher);

  historical_frames = std::move(old.historical_frames);

  memoized_keypoint_and_descriptor_map =
      std::move(old.memoized_keypoint_and_descriptor_map);
}

std::tuple<std::uint64_t, std::vector<cv::Mat>>
compute_homography::run(frame &&gray_blurred_frame) {
  std::uint64_t current_frame_num = gray_blurred_frame.number;
  historical_frames->add_historical_frame(std::move(gray_blurred_frame));
  if (current_frame_num < historical_frames->max_historical_frames() - 1) {
    return {};
  }
  const auto current_frame =
      historical_frames->get_historical_frame(current_frame_num);

  auto num_historical_frames = historical_frames->max_historical_frames();
  std::vector<cv::Mat> homographies;
  homographies.reserve(num_historical_frames);
  for (std::uint64_t i = 0; i < num_historical_frames; i++) {
    auto hom = register_and_compute_homography(
        historical_frames->get_historical_frame(current_frame_num - i),
        current_frame);

    homographies.push_back(hom);
  }
  return std::make_tuple(
      current_frame_num,
      homographies); // NRVO means copy will almost certainly be elided
}

cv::Mat
compute_homography::register_and_compute_homography(const frame &frame_one,
                                                    const frame &frame_two) {
  // Detect features and compute descriptors
  auto [keypoints_one, descriptors_one] =
      detect_features_compute_descriptors(frame_one);
  auto [keypoints_two, descriptors_two] =
      detect_features_compute_descriptors(frame_two);

  // TODO: big area to revisit. many opportunities for algorithim optimization
  // and accuracy improvements (why not FLANN?)

  // Register features based on descriptors (there is a 1:1 correspondence)
  std::vector<cv::DMatch> matches;
  descriptor_matcher->match(descriptors_one, descriptors_two, matches);

  // Sort matches by score
  std::sort(matches.begin(), matches.end(), [](const auto &l, const auto &r) {
    return l.distance < r.distance;
  });

  // Remove worst matches
  auto num_good_matches = static_cast<decltype(matches.size())>(
      matches.size() * good_match_percent);
  matches.erase(matches.begin() + num_good_matches, matches.end());

  // Match key points into a new Mat
  auto matches_size = matches.size();
  std::vector<cv::Point2f> points_one{matches_size};
  std::vector<cv::Point2f> points_two{matches_size};
  for (decltype(matches_size) i = 0; i < matches_size; i++) {
    points_one[i] = keypoints_one[matches[i].queryIdx].pt;
    points_two[i] = keypoints_two[matches[i].trainIdx].pt;
  }

  // Compute homography with RANSAC method
  auto hom = cv::findHomography(points_one, points_two, cv::RANSAC,
                                ransac_max_reproj_error);

  return hom;
}

std::tuple<const std::vector<cv::KeyPoint> &, const cv::Mat &>
compute_homography::detect_features_compute_descriptors(const frame &frame) {
  // Check this before getting referenecs to map contents because doing so will
  // insert a new entry if one doesn't already exist
  bool already_memoized = memoized_keypoint_and_descriptor_map.count(frame);

  auto &ret = memoized_keypoint_and_descriptor_map[frame];
  auto &[keypoints, descriptors] = ret;
  if (!already_memoized) {
    fast_detector->detect(frame.image, keypoints);
    keypoints = anms::ssc(keypoints, ssc_num_ret_points, ssc_tolerance,
                          frame.image.cols, frame.image.rows);
    orb_detector->compute(frame.image, keypoints, descriptors);
  }

  return ret;
}
} // namespace baboon_tracking

namespace baboon_tracking {
std::tuple<std::vector<frame>, std::vector<cv::Mat>>
transform_history_frames_and_masks::run(
    std::uint64_t current_frame_num,
    const std::vector<cv::Mat> &&homographies) {
  std::vector<frame> transformed_history_frames;
  std::vector<cv::Mat> transformed_masks;
  for (std::uint64_t i = 0; i < historical_frames->max_historical_frames();
       i++) {
    auto frame_to_transform =
        historical_frames->get_historical_frame(current_frame_num - i);
    auto image_size = frame_to_transform.image.size();

    cv::Mat transformed_image;
    cv::warpPerspective(frame_to_transform.image, transformed_image,
                        homographies[i], image_size);
    transformed_history_frames.emplace_back(
        frame{frame_to_transform.number, transformed_image});

    cv::Mat mask_to_transform = cv::Mat::ones(image_size, CV_8UC1) *
                                std::numeric_limits<std::uint8_t>::max();

    static_assert(
        sizeof(std::remove_reference_t<decltype(homographies)>::size_type) >=
        sizeof(decltype(i)));
    cv::warpPerspective(mask_to_transform, mask_to_transform, homographies[i],
                        image_size);
    transformed_masks.emplace_back(mask_to_transform);
  }

  return std::make_tuple(std::move(transformed_history_frames),
                         std::move(transformed_masks));
}
} // namespace baboon_tracking

namespace baboon_tracking {
std::vector<frame> rescale_transformed_history_frames::run(
    const std::vector<frame> &transformed_history_frames) {
  std::vector<frame> transformed_rescaled_history_frames;
  transformed_rescaled_history_frames.reserve(
      transformed_history_frames.size());

  for (auto &&transformed_frame : transformed_history_frames) {
    transformed_rescaled_history_frames.emplace_back(
        frame{transformed_frame.number,
              transformed_frame.image.clone() * (scale_factor / 255.0)});
  }

  return transformed_rescaled_history_frames;
}
} // namespace baboon_tracking

namespace baboon_tracking {
cv::Mat generate_history_of_dissimilarity::run(
    const std::vector<frame> &transformed_history_frames,
    const std::vector<frame> &transformed_rescaled_history_frames) {
  cv::Mat dissimilarity{transformed_history_frames[0].image.size(), CV_32SC1};

  cv::Mat mask{transformed_history_frames[0].image.size(), CV_8UC1};
  cv::Mat dissimilarity_part{transformed_history_frames[0].image.size(),
                             CV_8UC1};
  for (std::remove_reference_t<decltype(transformed_history_frames)>::size_type
           i = 0;
       i < transformed_history_frames.size(); i++) {
    if (i == 0)
      continue;

    // Note: we could use the operator overloads in MatExpr to make this more
    // readable, but that would require allocating a new Mat each loop iteration

    cv::absdiff(transformed_rescaled_history_frames[i].image,
                transformed_history_frames[i - 1].image, mask);
    cv::compare(mask, 1, mask,
                cv::CMP_GT); // This operation should be less or equal to than
                             // 1, but we do greater than 1 so we can avoid a
                             // bitwise not on the mask later on

    cv::absdiff(transformed_history_frames[i].image,
                transformed_history_frames[i - 1].image, dissimilarity_part);
    cv::bitwise_and(dissimilarity_part, mask, dissimilarity_part);

    dissimilarity += dissimilarity_part;
  }

  // Note: we're trying to get a count of how many times in the history frames
  // each given pixel was similar. There's a difference from the Python
  // implemenation because here true is 0xFF instead of 1; this is why we divide
  // by 255. This means that "similar" is 1 while "dissimilar" is 0.
  dissimilarity.convertTo(
      dissimilarity, CV_8UC1,
      1 / (static_cast<double>(transformed_history_frames.size()) *
           std::numeric_limits<uint8_t>::max()));
  return dissimilarity;
}

std::vector<frame> intersect_frames::run(
    const std::vector<frame> &&transformed_history_frames,
    const std::vector<frame> &&transformed_rescaled_history_frames) {
  std::vector<frame> intersected_frames = std::move(transformed_history_frames);

  cv::Mat mask{transformed_history_frames[0].image.size(), CV_8UC1};
  for (std::remove_reference_t<decltype(transformed_history_frames)>::size_type
           i = 0;
       i < transformed_history_frames.size() - 1; i++) {
    cv::absdiff(transformed_rescaled_history_frames[i].image,
                transformed_rescaled_history_frames[i + 1].image, mask);
    cv::compare(mask, 1, mask,
                cv::CMP_GT); // This operation should be less or equal to than
                             // 1, but we do greater than 1 so we can avoid a
                             // bitwise not on the mask later on

    cv::bitwise_and(intersected_frames[i].image, mask,
                    intersected_frames[i].image);
  }
  intersected_frames
      .pop_back(); // Because intersected_frames is being re-used from
                   // transformed_history_frames the last frame is vestigial

  return intersected_frames;
}

frame union_intersected_frames::run(
    const std::vector<frame> &&intersected_frames) {
  frame union_of_all = intersected_frames[0];
  for (auto &&frame : intersected_frames) {
    cv::bitwise_or(union_of_all.image, frame.image, union_of_all.image);
  }

  return union_of_all;
}

frame subtract_background::run(std::uint64_t current_frame_num,
                               const frame &&union_of_all,
                               const cv::Mat &weights) {
  auto num_historical_frames = historical_frames->max_historical_frames();
  auto zero_weights = [num_historical_frames](const cv::Mat &image,
                                              cv::Mat &&weights) {
    cv::compare(weights, num_historical_frames - 1, weights, cv::CMP_LT);
    cv::bitwise_and(weights, image, weights);
    return std::move(weights);
  };

  const frame current_frame =
      historical_frames->get_historical_frame(current_frame_num);
  auto frame_new = zero_weights(current_frame.image, weights.clone());
  auto union_new = zero_weights(union_of_all.image, weights.clone());

  cv::absdiff(frame_new, union_new, frame_new);
  return {current_frame_num, frame_new};
}
} // namespace baboon_tracking

namespace baboon_tracking {
frame compute_moving_foreground::run(cv::Mat &&dissimilarity,
                                     frame &&foreground_fr, cv::Mat &&weights) {
  // Every time we divide by uint8_max_double we're normalizing 0-255 to 0-1
  // TODO: if we're consistient everywhere and we operate on a 32-bit integer
  // then we don't have to normalize. Will need to profile to determine if this
  // is faster.
  constexpr double uint8_max_double = std::numeric_limits<std::uint8_t>::max();
  constexpr double third_gray = uint8_max_double / 3.0;

  auto history_frame_count = historical_frames->max_historical_frames();
  int history_frame_count_third =
      std::floor(static_cast<double>(history_frame_count) / 3.0);

  auto foreground = foreground_fr.image;

  // We use MatExpr for lazy evaluation in order avoid the allocation of
  // temporary cv::Mats

  cv::MatExpr weights_low =
      (weights <= history_frame_count_third) / uint8_max_double;
  cv::MatExpr weights_medium = ((weights < history_frame_count - 1) &
                                (weights > history_frame_count_third)) /
                               uint8_max_double * 2.0;
  // XXX: where is weights_high?

  cv::MatExpr weight_levels = weights_low + weights_medium;

  cv::MatExpr foreground_low = (foreground <= third_gray) / uint8_max_double;
  cv::MatExpr foreground_medium =
      ((foreground > third_gray) / uint8_max_double +
       (foreground < (2.0 * third_gray)) / uint8_max_double) *
      2.0;
  cv::MatExpr foreground_high =
      (foreground >= (2.0 * third_gray)) / uint8_max_double * 3.0;

  cv::MatExpr foreground_levels =
      foreground_low + foreground_medium + foreground_high;

  cv::MatExpr dissimilarity_low =
      (dissimilarity <= third_gray) / uint8_max_double;
  cv::MatExpr dissimilarity_medium =
      ((dissimilarity > third_gray) / uint8_max_double +
       (dissimilarity < (2.0 * third_gray)) / uint8_max_double) *
      2.0;
  cv::MatExpr dissimilairy_high =
      (dissimilarity >= (2.0 * third_gray)) / uint8_max_double * 3.0;

  cv::MatExpr dissimilarity_levels =
      dissimilarity_low + dissimilarity_medium + dissimilairy_high;

  cv::MatExpr moving_foreground =
      (weight_levels == 2 & foreground_levels >= dissimilarity_levels) /
      uint8_max_double;
  moving_foreground =
      moving_foreground +
      (weight_levels == 1 & (dissimilarity_levels == 1 &
                             (foreground_levels > dissimilarity_levels))) /
          uint8_max_double;

  // XXX: MatExpr doesn't seem to be able to write into existing memory, which
  // is what stops uses in other areas... can we do that and re-use the
  // already-allocated memory in foreground_fr?
  foreground_fr.image = moving_foreground * 255;
  return std::move(foreground_fr);
}

void apply_masks::run(frame *moving_foreground,
                      std::vector<cv::Mat> &&shifted_masks) {
  for (auto &&mask : shifted_masks) {
    cv::multiply(moving_foreground->image, mask, moving_foreground->image);
  }
}
} // namespace baboon_tracking

namespace baboon_tracking {
std::vector<cv::Rect> detect_blobs::run(const frame &&moving_foreground) {
  auto foreground_mask = moving_foreground.image;

  std::vector<std::vector<cv::Point>> contours;
  cv::findContours(foreground_mask, contours, cv::RETR_LIST,
                   cv::CHAIN_APPROX_SIMPLE);

  std::vector<cv::Rect> rectangles;
  rectangles.reserve(contours.size());
  for (auto &&contour : contours) {
    rectangles.push_back(cv::boundingRect(contour));
  }

  return rectangles;
}
} // namespace baboon_tracking
