#pragma once

#include "frame.h"

#include <opencv2/features2d.hpp>

#include <fmt/core.h>

#include <condition_variable>
#include <map>
#include <memory>
#include <set>
#include <tuple>
#include <vector>

namespace baboon_tracking {
class convert_bgr_to_gray {
public:
  frame run(frame &&color_frame) const;
};

class blur_gray {
public:
  blur_gray(int kernel_size) : kernel_size{kernel_size} {};

  frame run(frame &&gray_frame) const;

private:
  int kernel_size;
};

class denoise {
public:
  // denoise_strength is called 'h' by OpenCV and the original Non-Local Means
  // Denoising paper
  denoise(float denoise_strength) : denoise_strength{denoise_strength} {};

  frame run(frame &&gray_frame) const;

private:
  float denoise_strength;
};
} // namespace baboon_tracking

namespace baboon_tracking {
class historical_frames_container {
public:
  // Need to add a parameter for max number of threads and then we'll reserve
  // that amount as extra
  historical_frames_container(std::set<frame>::size_type max_historical_frames)
      : max_frames{max_historical_frames} {};

  void add_historical_frame(frame &&preprocessed_frame);

  // If the numbered frame is not yet available this will block until that frame
  // is added Why do we copy frame here and nowhere else? In other cases it's
  // easy to just move frame and better indicates intent, but in this case
  // returning a reference to frame would require holding the lock for the
  // duration of its use because it's possible that the frame gets removed from
  // the set when another thread adds a frame and old frames get cleaned up.
  // Copying the frame does *not* cause a copy of the frame's cv::Mat's
  // underlying data, because cv::Mat is effectively a std::shared_ptr (it does
  // reference counting.)
  frame get_historical_frame(std::uint64_t frame_number);

  bool is_full();

  std::set<frame>::size_type max_historical_frames() const {
    return max_frames;
  }

private:
  std::mutex mutex;
  std::condition_variable frame_added_cv;

  std::set<frame, std::less<>> historical_frames;
  std::set<frame>::size_type max_frames;
};

class store_history_frame {
public:
  store_history_frame(
      std::shared_ptr<historical_frames_container> historical_frames)
      : historical_frames{historical_frames} {};

  frame run(frame &&gray_blurred_frame);

private:
  std::shared_ptr<historical_frames_container> historical_frames;
};

class compute_homography {
public:
  compute_homography(
      double good_match_percent, double ransac_max_reproj_error,
      double ssc_tolerance, int ssc_num_ret_points,
      std::shared_ptr<historical_frames_container> historical_frames)
      : good_match_percent{good_match_percent},
        ransac_max_reproj_error{ransac_max_reproj_error},
        ssc_tolerance{ssc_tolerance}, ssc_num_ret_points{ssc_num_ret_points},
        historical_frames{historical_frames} {};

  compute_homography(compute_homography &&old);

  std::tuple<std::uint64_t, std::vector<cv::Mat>>
  run(frame &&gray_blurred_frame);

  bool should_break() {
    if (!historical_frames->is_full()) fmt::print("Skipping in break\n");
    return !historical_frames->is_full();
  } // TODO: fix this race condition

private:
  cv::Mat register_and_compute_homography(const frame &frame_one,
                                          const frame &frame_two);
  std::tuple<const std::vector<cv::KeyPoint> &, const cv::Mat &>
  detect_features_compute_descriptors(const frame &frame);

  double good_match_percent;
  double ransac_max_reproj_error;
  double ssc_tolerance;
  int ssc_num_ret_points;

  // TODO: calls into these objects are likely not thread safe, however locking
  // on accesses to them would defeat the purpose of running multiple pipeline
  // threads; we could have multiple instances or even duplicate the entire
  // pipeline (which solves some other problems, but also is potentially
  // counterintuitive)
  cv::Ptr<cv::FastFeatureDetector> fast_detector =
      cv::FastFeatureDetector::create();
  cv::Ptr<cv::ORB> orb_detector = cv::ORB::create();
  cv::Ptr<cv::DescriptorMatcher> descriptor_matcher =
      cv::DescriptorMatcher::create(
          cv::DescriptorMatcher::MatcherType::BRUTEFORCE_HAMMING);

  std::shared_ptr<historical_frames_container> historical_frames;

  std::mutex memo_map_mutex;
  std::map<frame, std::tuple<std::vector<cv::KeyPoint>, cv::Mat>>
      memoized_keypoint_and_descriptor_map;
};

// TODO: could be two parallel pipes or parallel tasks in the pipe
class transform_history_frames_and_masks {
public:
  transform_history_frames_and_masks(
      std::shared_ptr<historical_frames_container> historical_frames)
      : historical_frames{historical_frames} {};

  std::tuple<std::uint64_t, std::vector<frame>, std::vector<cv::Mat>>
  run(std::uint64_t current_frame_num, std::vector<cv::Mat>&& homographies);

private:
  std::shared_ptr<historical_frames_container> historical_frames;
};

class rescale_transformed_history_frames {
public:
  rescale_transformed_history_frames(double scale_factor)
      : scale_factor{scale_factor} {};

  std::tuple<std::uint64_t, std::vector<frame>, std::vector<cv::Mat>, std::vector<frame>>
  run(std::uint64_t current_frame_num, std::vector<frame>&& transformed_history_frames, std::vector<cv::Mat>&& transformed_masks);

private:
  double scale_factor;
};

class generate_weights {
public:
  std::tuple<std::uint64_t, std::vector<frame>, std::vector<cv::Mat>, std::vector<frame>, cv::Mat>
  run(std::uint64_t current_frame_num, std::vector<frame>&& transformed_history_frames, std::vector<cv::Mat>&& transformed_masks, std::vector<frame>&& transformed_rescaled_history_frames);
};

class generate_history_of_dissimilarity {
public:
  std::tuple<std::uint64_t, std::vector<cv::Mat>, std::vector<frame>, std::vector<frame>, cv::Mat, cv::Mat>
  run(std::uint64_t current_frame_num, std::vector<frame>&& transformed_history_frames, std::vector<cv::Mat>&& transformed_masks, std::vector<frame>&& transformed_rescaled_history_frames, cv::Mat&& weights) ;
};

class group_transformed_rescaled_frames {
public:
  std::tuple<std::uint64_t, cv::Mat, std::vector<std::tuple<frame, frame>>, std::vector<std::tuple<frame, frame>>>
  run(std::uint64_t current_frame_num, std::vector<frame>&& transformed_history_frames, std::vector<cv::Mat>&& transformed_masks, std::vector<frame>&& transformed_rescaled_history_frames, cv::Mat&& weights, cv::Mat&& hist_of_dissimilarity);
};

class intersect_frames {
public:
  std::tuple<std::uint64_t, cv::Mat, std::vector<cv::Mat>>
  run(std::uint64_t current_frame_num, cv::Mat&& weights, std::vector<std::tuple<frame, frame>> grouped_transformed_frames, std::vector<std::tuple<frame, frame>> grouped_transformed_rescaled_frames);
};

class union_intersected_frames {
public:
  std::tuple<std::uint64_t, cv::Mat, cv::Mat>
  run(std::uint64_t current_frame_num, cv::Mat&& weights, std::vector<cv::Mat>);
};

class subtract_background {
public:
  subtract_background(std::shared_ptr<historical_frames_container> historical_frames) : historical_frames{historical_frames} {};

  std::tuple<std::uint64_t, frame>
  run(std::uint64_t current_frame_num, cv::Mat&& weights, cv::Mat&& background);

private:
  std::shared_ptr<historical_frames_container> historical_frames;
};
} // namespace baboon_tracking
