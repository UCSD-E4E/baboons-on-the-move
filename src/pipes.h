#pragma once

#include "cv_specializations.h"
#include "historical_frame_container.h"
#include "sortable_frame.h"

#include "kalman/kalman_filter.h"

#include "ssc.h"

#include <opencv2/calib3d.hpp>
#include <opencv2/core.hpp>
#include <opencv2/features2d.hpp>
#include <opencv2/imgproc.hpp>
#include <opencv2/photo.hpp>

#include <utility>

#include <condition_variable>
#include <map>
#include <memory>
#include <set>
#include <tuple>
#include <vector>

namespace baboon_tracking {
template <typename frame> struct pipes {
  using cvs = cv_specializations<frame>;

  class convert_bgr_to_gray {
  public:
    frame run(frame &&color_frame) const {
      frame out; // XXX: why do we need this with GpuMat?
      cvs::cvtColor(color_frame, out, cv::COLOR_BGR2GRAY, 0);
      return out;
    }
  };

  class blur_gray {
  public:
    blur_gray(int kernel_size) : kernel_size{kernel_size} {};

    frame run(frame &&gray_frame) const {
      // sigma_x = sigma_y = 0 implies that the Gaussian kernel standard
      // deviation is calculated from the kernel size
      if constexpr (!cvs::is_cuda) {
        cv::GaussianBlur(gray_frame, gray_frame, {kernel_size, kernel_size}, 0,
                         0);
      } else {
        // XXX: grid size is wrong for Jetson Nano?
        // static auto filter = cv::cuda::createGaussianFilter(CV_8UC1, CV_8UC1,
        // {kernel_size, kernel_size}, 0, 0); filter->apply(gray_frame,
        // gray_frame);
      }
      return std::move(gray_frame);
    }

  private:
    int kernel_size;
  };

  class denoise {
  public:
    // denoise_strength is called 'h' by OpenCV and the original Non-Local Means
    // Denoising paper
    denoise(float denoise_strength) : denoise_strength{denoise_strength} {};

    frame run(frame &&gray_frame) const {
      // TODO: should probably add a CUDA version of this to the aliases if we
      // ever use the denoising step
      cv::fastNlMeansDenoisingColored(gray_frame, gray_frame, denoise_strength);
      return std::move(gray_frame);
    }

  private:
    float denoise_strength;
  };

  class compute_homography {
  public:
    compute_homography(
        double good_match_percent, double ransac_max_reproj_error,
        double ssc_tolerance, int ssc_num_ret_points,
        std::shared_ptr<historical_frames_container<frame>> historical_frames)
        : good_match_percent{good_match_percent},
          ransac_max_reproj_error{ransac_max_reproj_error},
          ssc_tolerance{ssc_tolerance}, ssc_num_ret_points{ssc_num_ret_points},
          historical_frames{historical_frames} {};

    std::vector<cv::Mat> run(std::uint8_t current_frame_num,
                             frame &&gray_blurred_frame) {
      historical_frames->add_historical_frame(current_frame_num,
                                              std::move(gray_blurred_frame));
      if (current_frame_num < historical_frames->max_historical_frames() - 1) {
        return {};
      }
      const auto &current_frame =
          historical_frames->get_historical_frame(current_frame_num);

      auto num_historical_frames = historical_frames->max_historical_frames();
      std::vector<cv::Mat> homographies;
      homographies.reserve(num_historical_frames);
      for (std::uint64_t i = 0; i < num_historical_frames; i++) {
        auto hom = register_and_compute_homography(
            current_frame_num - i, current_frame_num,
            historical_frames->get_historical_frame(current_frame_num - i),
            current_frame);

        homographies.push_back(hom);
      }
      return homographies;
    }

  private:
    cv::Mat register_and_compute_homography(std::uint64_t frame_one_num,
                                            std::uint64_t frame_two_num,
                                            const frame &frame_one,
                                            const frame &frame_two) {
      // Detect features and compute descriptors
      auto [keypoints_one, descriptors_one] =
          detect_features_compute_descriptors(frame_one_num, frame_one);
      auto [keypoints_two, descriptors_two] =
          detect_features_compute_descriptors(frame_two_num, frame_two);

      // Register features based on descriptors (there is a 1:1 correspondence)
      std::vector<cv::DMatch> matches;
      if (!cvs::is_cuda) {
        static auto descriptor_matcher = cv::FlannBasedMatcher(
            cv::makePtr<cv::flann::LshIndexParams>(6, 12, 1));
        descriptor_matcher.match(descriptors_one, descriptors_two, matches);
      } else {
#ifdef HAS_CUDA
        static auto descriptor_matcher =
            cv::cuda::DescriptorMatcher::createBFMatcher(
                cv::BRUTEFORCE_HAMMING);
        descriptor_matcher->match(descriptors_one, descriptors_two, matches);
#endif
      }

      // Sort matches by score
      std::sort(
          matches.begin(), matches.end(),
          [](const auto &l, const auto &r) { return l.distance < r.distance; });

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

    std::tuple<const std::vector<cv::KeyPoint> &,
               const typename cvs::cpu_or_gpu_mat &>
    detect_features_compute_descriptors(std::uint64_t frame_num,
                                        const frame &fr) {
      sortable_frame<frame> sortable_frame{frame_num, fr};

      // Check this before getting referenecs to map contents because doing so
      // will insert a new entry if one doesn't already exist
      bool already_memoized =
          memoized_keypoint_and_descriptor_map.count(sortable_frame);

      auto &ret = memoized_keypoint_and_descriptor_map[sortable_frame];
      auto &[keypoints, descriptors] = ret;
      if (!already_memoized) {
        static cv::Ptr<cv::Feature2D> fast_detector;
        static cv::Ptr<cv::Feature2D> orb_detector;
        if (!cvs::is_cuda && !fast_detector && !orb_detector) {
          fast_detector = cv::FastFeatureDetector::create();
          orb_detector = cv::ORB::create();
        } else if (!fast_detector && !orb_detector) {
#ifdef HAS_CUDA
          fast_detector = cv::cuda::FastFeatureDetector::create();
          orb_detector = cv::cuda::ORB::create();
#endif
          // TODO: we an probably turn of the GPU ORB detector's blurring
        }

        fast_detector->detect(fr, keypoints);
        keypoints = anms::ssc(keypoints, ssc_num_ret_points, ssc_tolerance,
                              fr.cols, fr.rows);
        orb_detector->compute(fr, keypoints, descriptors);
      }

      return ret;
    }

    double good_match_percent;
    double ransac_max_reproj_error;
    double ssc_tolerance;
    int ssc_num_ret_points;

    std::map<sortable_frame<frame>, std::tuple<std::vector<cv::KeyPoint>,
                                               typename cvs::cpu_or_gpu_mat>>
        memoized_keypoint_and_descriptor_map;

    std::shared_ptr<historical_frames_container<frame>> historical_frames;
  };

  // TODO: could be two parallel pipes or parallel tasks in the pipe
  class transform_history_frames_and_masks {
  public:
    transform_history_frames_and_masks(
        std::shared_ptr<historical_frames_container<frame>> historical_frames)
        : historical_frames{historical_frames} {};

    std::tuple<std::vector<frame>, std::vector<cv::Mat>>
    run(std::uint64_t current_frame_num,
        const std::vector<cv::Mat> &&homographies) {
      std::vector<frame> transformed_history_frames;
      std::vector<cv::Mat> transformed_masks;
      for (std::uint64_t i = 0; i < historical_frames->max_historical_frames();
           i++) {
        auto frame_to_transform =
            historical_frames->get_historical_frame(current_frame_num - i);
        auto frame_size = frame_to_transform.size();

        frame transformed_frame{frame_size, CV_8UC1};
        cvs::warpPerspective(frame_to_transform, transformed_frame,
                             homographies[i], frame_size);
        transformed_history_frames.emplace_back(transformed_frame);

        cv::Mat mask_to_transform = cv::Mat::ones(frame_size, CV_8UC1);
        static_assert(
            sizeof(
                std::remove_reference_t<decltype(homographies)>::size_type) >=
            sizeof(decltype(i)));
        cvs::warpPerspective(mask_to_transform, mask_to_transform,
                             homographies[i], frame_size);
        transformed_masks.emplace_back(mask_to_transform);
      }

      return std::make_tuple(std::move(transformed_history_frames),
                             std::move(transformed_masks));
    }

  private:
    std::shared_ptr<historical_frames_container<frame>> historical_frames;
  };

  class rescale_transformed_history_frames {
  public:
    rescale_transformed_history_frames(double scale_factor)
        : scale_factor{scale_factor} {};

    std::vector<frame>
    run(const std::vector<frame> &transformed_history_frames) {
      std::vector<frame> transformed_rescaled_history_frames;
      transformed_rescaled_history_frames.reserve(
          transformed_history_frames.size());

      for (auto &&transformed_frame : transformed_history_frames) {
        frame transformed_rescaled_history_frame{transformed_frame.size(),
                                                 CV_8UC1};
        cvs::multiply(
            transformed_frame,
            scale_factor /
                static_cast<double>(std::numeric_limits<std::uint8_t>::max()),
            transformed_rescaled_history_frame);
        transformed_rescaled_history_frames.emplace_back(
            transformed_rescaled_history_frame);
      }

      return transformed_rescaled_history_frames;
    }

  private:
    double scale_factor;
  };

  class generate_weights {
  public:
    cv::Mat run(const std::vector<frame> &transformed_rescaled_history_frames) {
      cv::Mat weights = cv::Mat::zeros(
          transformed_rescaled_history_frames[0].size(), CV_8UC1);
      if (transformed_rescaled_history_frames.size() >
          std::numeric_limits<std::uint8_t>::max())
        throw std::overflow_error("Number of history frames would overflow "
                                  "intermediate storage for weights");

      // Note: this static makes this not thread safe
      static cv::Mat mask{transformed_rescaled_history_frames[0].size(),
                          CV_8UC1};
      for (auto iter = std::next(transformed_rescaled_history_frames.begin());
           iter != transformed_rescaled_history_frames.end(); iter++) {
        cvs::absdiff(*iter, *std::prev(iter), mask);
        cvs::compare(mask, 1, mask, cv::CMP_LE);
        cvs::scaleAdd(
            mask,
            1 / static_cast<double>(std::numeric_limits<std::uint8_t>::max()),
            weights, weights);
      }

      return weights;
    }
  };

  class generate_history_of_dissimilarity {
  public:
    cv::Mat run(const std::vector<frame> &transformed_history_frames,
                const std::vector<frame> &transformed_rescaled_history_frames) {
      cv::Mat dissimilarity =
          cv::Mat::zeros(transformed_history_frames[0].size(), CV_32SC1);

      // Note: static storage duration makes this pipe not thread safe
      static cv::Mat mask{transformed_history_frames[0].size(), CV_8UC1};
      static cv::Mat dissimilarity_part{transformed_history_frames[0].size(),
                                        CV_8UC1};
      for (typename std::remove_reference_t<
               decltype(transformed_history_frames)>::size_type i = 0;
           i < transformed_history_frames.size(); i++) {
        if (i == 0)
          continue;

        // Note: we could use the operator overloads in MatExpr to make this
        // more readable, but that would require allocating a new Mat each loop
        // iteration. This also allows for easy CUDA support.

        cvs::absdiff(transformed_rescaled_history_frames[i],
                     transformed_history_frames[i - 1], mask);
        cvs::compare(mask, 1, mask,
                     cv::CMP_GT); // This operation should be less or equal to
                                  // than 1, but we do greater than 1 so we can
                                  // avoid a bitwise not on the mask later on

        cvs::absdiff(transformed_history_frames[i],
                     transformed_history_frames[i - 1], dissimilarity_part);
        cvs::bitwise_and(dissimilarity_part, mask, dissimilarity_part);

        cvs::add(dissimilarity, dissimilarity_part, dissimilarity,
                 cv::noArray(), CV_32SC1);
      }

      // Note: we're trying to get a count of how many times in the history
      // frames each given pixel was similar. There's a difference from the
      // Python implemenation because here true is 0xFF instead of 1; this is
      // why we divide by 255. This means that "similar" is 1 while "dissimilar"
      // is 0.
      dissimilarity.convertTo(
          dissimilarity, CV_8UC1,
          1 / (static_cast<double>(transformed_history_frames.size()) *
               std::numeric_limits<uint8_t>::max()));
      return dissimilarity;
    }
  };

  class intersect_frames {
  public:
    std::vector<frame>
    run(const std::vector<frame> &&transformed_history_frames,
        const std::vector<frame> &&transformed_rescaled_history_frames) {
      std::vector<frame> intersected_frames =
          std::move(transformed_history_frames);

      cv::Mat mask{transformed_history_frames[0].size(), CV_8UC1};
      for (typename std::remove_reference_t<
               decltype(transformed_history_frames)>::size_type i = 0;
           i < transformed_history_frames.size() - 1; i++) {
        cvs::absdiff(transformed_rescaled_history_frames[i],
                     transformed_rescaled_history_frames[i + 1], mask);
        cvs::compare(mask, 1, mask,
                     cv::CMP_GT); // This operation should be less or equal to
                                  // than 1, but we do greater than 1 so we can
                                  // avoid a bitwise not on the mask later on

        cvs::bitwise_and(intersected_frames[i], mask, intersected_frames[i]);
      }
      intersected_frames
          .pop_back(); // Because intersected_frames is being re-used from
                       // transformed_history_frames the last frame is vestigial

      return intersected_frames;
    }
  };

  class union_intersected_frames {
  public:
    frame run(const std::vector<frame> &&intersected_frames) {
      frame union_of_all = intersected_frames[0];
      for (auto &&fr : intersected_frames) {
        cvs::bitwise_or(union_of_all, fr, union_of_all);
      }

      return union_of_all;
    }
  };

  class subtract_background {
  public:
    subtract_background(
        std::shared_ptr<historical_frames_container<frame>> historical_frames)
        : historical_frames{historical_frames} {};

    frame run(std::uint64_t current_frame_num, const frame &&union_of_all,
              const cv::Mat &weights) {
      auto num_historical_frames = historical_frames->max_historical_frames();
      auto zero_weights = [num_historical_frames](const auto &image,
                                                  cv::Mat &&weights) {
        frame weights_native(weights); // Either uploads weights to the GPU or
                                       // effectively nothing on the CPU
        cvs::compare(weights_native, num_historical_frames - 1, weights_native,
                     cv::CMP_LT);
        cvs::bitwise_and(weights_native, image, weights_native);
        return weights_native;
      };

      const frame current_frame =
          historical_frames->get_historical_frame(current_frame_num);
      auto frame_new = zero_weights(current_frame, weights.clone());
      auto union_new = zero_weights(union_of_all, weights.clone());

      cvs::absdiff(frame_new, union_new, frame_new);
      return frame_new;
    }

  private:
    std::shared_ptr<historical_frames_container<frame>> historical_frames;
  };

  class compute_moving_foreground {
  public:
    compute_moving_foreground(
        std::shared_ptr<historical_frames_container<frame>> historical_frames)
        : historical_frames{historical_frames} {};

    frame run(cv::Mat &&dissimilarity, frame &&foreground_fr,
              cv::Mat &&weights) {
      // Every time we divide by uint8_max_double we're normalizing 0-255 to 0-1
      // TODO: if we're consistient everywhere and we operate on a 32-bit
      // integer then we don't have to normalize. Will need to profile to
      // determine if this is faster.
      constexpr double uint8_max_double =
          std::numeric_limits<std::uint8_t>::max();
      constexpr double third_gray = uint8_max_double / 3.0;

      auto history_frame_count = historical_frames->max_historical_frames();
      int history_frame_count_third =
          std::floor(static_cast<double>(history_frame_count) / 3.0);

      // TODO: MatExpr doesn't work on cv::cuda::GpuMats... we download to host
      // memory rn. Worth it to fix?
      auto foreground = cv::Mat(foreground_fr);

      // We use MatExpr for lazy evaluation in order avoid the allocation of
      // temporary cv::Mats

      cv::MatExpr weights_low =
          (weights <= history_frame_count_third) / uint8_max_double;
      cv::MatExpr weights_medium = ((weights < history_frame_count - 1) &
                                    (weights > history_frame_count_third)) /
                                   uint8_max_double * 2.0;
      // XXX: where is weights_high?

      cv::MatExpr weight_levels = weights_low + weights_medium;

      cv::MatExpr foreground_low =
          (foreground <= third_gray) / uint8_max_double;
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
          ((weight_levels == 2) & (foreground_levels >= dissimilarity_levels)) /
          uint8_max_double;
      moving_foreground =
          moving_foreground + ((weight_levels == 1) &
                               ((dissimilarity_levels == 1) &
                                (foreground_levels > dissimilarity_levels))) /
                                  uint8_max_double;

      // XXX: MatExpr doesn't seem to be able to write into existing memory,
      // which is what stops uses in other areas... can we do that and re-use
      // the already-allocated memory in foreground_fr?
      foreground_fr = frame(cv::Mat(moving_foreground *
                                    std::numeric_limits<std::uint8_t>::max()));
      return std::move(foreground_fr);
    }

  private:
    std::shared_ptr<historical_frames_container<frame>> historical_frames;
  };

  class apply_masks {
  public:
    void run(frame *moving_foreground, std::vector<cv::Mat> &&shifted_masks) {
      for (auto &&mask : shifted_masks) {
        cvs::multiply(*moving_foreground, mask, *moving_foreground);
      }
    }
  };

  class erode {
  public:
    erode(int erosion_size) : erosion_size{erosion_size} {};

    void run(frame *moving_foreground) {
      static cv::Mat element = cv::getStructuringElement(
          cv::MORPH_RECT, cv::Size(erosion_size, erosion_size));
      cv::erode(*moving_foreground, *moving_foreground, element);
    }

  private:
    int erosion_size;
  };

  class detect_blobs {
  public:
    std::vector<cv::Rect> run(const frame &&moving_foreground) {
      // Have to download from the GPU; there is no CUDA findContours
      auto foreground_mask = cv::Mat(moving_foreground);

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
  };

  template <int NumBaboons> class filter {
  private:
    // x = [x, y, v_x, v_y, ...]
    // y = [x_k, y_k, x_{k-1}, y_{k-1}, ...]
    // No u
    static constexpr int states_per_baboon = 4;
    static constexpr int num_states = NumBaboons * states_per_baboon;
    static constexpr int measurements_per_baboon = 4;
    static constexpr int num_measurements =
        NumBaboons * measurements_per_baboon;

  public:
    filter(std::array<double, num_states> state_std_devs,
           std::array<double, num_measurements> measurement_std_devs, double dt)
        : dt{dt} {
      // Remember: A is continuous—xdot = Ax
      Eigen::Matrix<double, states_per_baboon, states_per_baboon> A_sub;
      // clang-format off
      A_sub << 0, 0, 1, 0,
	       0, 0, 0, 1,
	       0, 0, 0, 0,
	       0, 0, 0, 0;
      // clang-format on

      Eigen::Matrix<double, num_states, num_states> A;
      for (int i = 0; i < NumBaboons; i++) {
        A.template block<states_per_baboon, states_per_baboon>(
            i * num_states, i * num_states) = A_sub;
      }
      Eigen::Matrix<double, num_states, 0> B =
          Eigen::Matrix<double, num_measurements, 0>::Zero();

      Eigen::Matrix<double, measurements_per_baboon, states_per_baboon> C_sub;
      // clang-format off
      C_sub << 1, 0, 0,  0,
	       0, 1, 0,  0,
	       0, 0, dt, 0,
	       0, 0, 0, dt;
      // clang-format on
      Eigen::Matrix<double, num_measurements, num_states> C;
      for (int i = 0; i < NumBaboons; i++) {
        C.template block<measurements_per_baboon, states_per_baboon>(
            i * num_measurements, i * num_states) = C_sub;
      }
      Eigen::Matrix<double, num_measurements, 0> D =
          Eigen::Matrix<double, num_measurements, 0>::Zero();

      kf = kalman_filter<num_states, 0, num_measurements>{
          A, B, C, D, state_std_devs, measurement_std_devs, dt};
    };

    void run(const int actual_num_baboons,
             const std::vector<cv::Rect> &current_bounding_boxes) {
      Eigen::Matrix<double, num_states, 1> x_hat_old = kf.x_hat();
      kf.predict(Eigen::Matrix<double, 0, 0>::Zero(), dt);

      Eigen::Matrix<double, num_measurements, 1> y;
      for (int i; i < actual_num_baboons; i++) {
        y.template block<measurements_per_baboon, 1>(
            i * measurements_per_baboon, 1)
            << current_bounding_boxes[i].x;
      }
      kf.correct(Eigen::Matrix<double, 0, 0>::Zero());
    }

  private:
    kalman_filter<num_states, 0, num_measurements> kf;
    double dt; // Seconds
  };
};
} // namespace baboon_tracking
