#include "pipes.h"

#include <opencv2/calib3d.hpp>

#include <iostream>

#include <mutex>
#include <opencv2/imgproc.hpp>
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
  if (current_frame_num < historical_frames->max_historical_frames()) {
    return {};
  }
  const auto current_frame =
      historical_frames->get_historical_frame(current_frame_num);

  auto num_historical_frames = historical_frames->max_historical_frames();
  std::vector<cv::Mat> homographies;
  homographies.reserve(num_historical_frames);
  for (std::uint64_t i = 0; i <= num_historical_frames; i++) {
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
  /*auto matches_size = matches.size();
  if (matches_size > std::numeric_limits<int>::max())
    throw std::runtime_error{
        "Number of matches would overflow a signed integer"};

  cv::Mat points_one{static_cast<int>(matches_size), 1, CV_32FC2};
  cv::Mat points_two{static_cast<int>(matches_size), 1, CV_32FC2};

  // We take great care here so that the compiler will autovectorize this loop
  float *points_one_data = points_one.ptr<float>();
  float *points_two_data = points_two.ptr<float>();
  const cv::DMatch *matches_data = matches.data();
  const cv::KeyPoint *keypoints_one_data = keypoints_one.data();
  const cv::KeyPoint *keypoints_two_data = keypoints_two.data();
  for (decltype(matches_size) i = 0; i < matches_size; i++) {
    points_one_data[i] = keypoints_one_data[matches_data[i].queryIdx].pt.x;
    points_one_data[i + 1] = keypoints_one_data[matches_data[i].queryIdx].pt.y;

    points_two_data[i] = keypoints_two_data[matches_data[i].trainIdx].pt.x;
    points_two_data[i + 1] = keypoints_two_data[matches_data[i].trainIdx].pt.y;
  }*/
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
std::tuple<std::uint64_t, std::vector<frame>, std::vector<cv::Mat>>
transform_history_frames_and_masks::run(std::uint64_t current_frame_num,
                                        std::vector<cv::Mat> homographies) {
  std::vector<frame> transformed_history_frames;
  std::vector<cv::Mat> transformed_masks;
  for (std::uint64_t i = 0; i < historical_frames->max_historical_frames();
       i++) {
    auto frame_to_transform =
        historical_frames->get_historical_frame(current_frame_num - i);
    auto image_size =
        cv::Size(frame_to_transform.image.cols, frame_to_transform.image.rows);

    cv::Mat transformed_image;
    cv::warpPerspective(frame_to_transform.image, transformed_image,
                        homographies[i], image_size);
    transformed_history_frames.emplace_back(transformed_image,
                                            frame_to_transform.number);

    cv::Mat mask_to_transform = cv::Mat::ones(image_size, CV_8UC1) *
                                std::numeric_limits<std::uint8_t>::max();
    cv::warpPerspective(mask_to_transform, mask_to_transform, homographies[i],
                        image_size);
    transformed_masks.emplace_back(mask_to_transform);
  }

  return std::make_tuple(current_frame_num,
                         std::move(transformed_history_frames),
                         transformed_masks);
}
} // namespace baboon_tracking
