#pragma once

#include "cv_specializations.h"
#include "historical_frame_container.h"
#include "sortable_frame.h"

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
      frame out{color_frame.size(),
                CV_8UC1}; // XXX: why do we need this with GpuMat?
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
#ifdef USE_CUDA
        // OpenCV Gaussian blur seems to have problems on the Jetson Nano... we
        // could manually convolve with a Gaussian kernel, but that only accepts
        // float32 images. A box blur is probably close enough.
        static auto filter = cv::cuda::createBoxFilter(
            CV_8UC1, CV_8UC1, {kernel_size, kernel_size});
        filter->apply(gray_frame, gray_frame);
#endif
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
#ifdef USE_CUDA
        static auto descriptor_matcher =
            cv::cuda::DescriptorMatcher::createBFMatcher(cv::NORM_HAMMING);
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
#ifdef USE_CUDA
          fast_detector = cv::cuda::FastFeatureDetector::create(
              40, true, cv::FastFeatureDetector::TYPE_9_16, 10'000);
          orb_detector = cv::cuda::ORB::create();
          orb_detector.staticCast<cv::cuda::ORB>()->setBlurForDescriptor(
              false); // We pre-blur the image
#endif
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

  class transform_history_frames_and_masks {
  public:
    transform_history_frames_and_masks(
        std::shared_ptr<historical_frames_container<frame>> historical_frames)
        : historical_frames{historical_frames} {};

    std::tuple<std::vector<frame>, std::vector<typename cvs::cpu_or_gpu_mat>>
    run(std::uint64_t current_frame_num,
        const std::vector<cv::Mat> &&homographies) {
      std::vector<frame> transformed_history_frames;
      std::vector<typename cvs::cpu_or_gpu_mat> transformed_masks;
      transformed_history_frames.reserve(
          historical_frames->max_historical_frames());
      transformed_masks.reserve(historical_frames->max_historical_frames());

      for (std::uint64_t i = 0; i < historical_frames->max_historical_frames();
           i++) {
        auto frame_to_transform =
            historical_frames->get_historical_frame(current_frame_num - i);
        auto frame_size = frame_to_transform.size();

        frame transformed_frame{frame_size, CV_8UC1};
        cvs::warpPerspective(frame_to_transform, transformed_frame,
                             homographies[i], frame_size);
        transformed_history_frames.emplace_back(transformed_frame);

        typename cvs::cpu_or_gpu_mat mask_to_transform{frame_size, CV_8UC1, 1};
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
    typename cvs::cpu_or_gpu_mat
    run(const std::vector<frame> &transformed_rescaled_history_frames) {
      typename cvs::cpu_or_gpu_mat weights{
          transformed_rescaled_history_frames[0].size(), 0, CV_8UC1};
      if (transformed_rescaled_history_frames.size() >
          std::numeric_limits<std::uint8_t>::max())
        throw std::overflow_error("Number of history frames would overflow "
                                  "intermediate storage for weights");

      // Note: static storage duration makes this not thread safe
      static typename cvs::cpu_or_gpu_mat mask{
          transformed_rescaled_history_frames[0].size(), CV_8UC1};
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
    typename cvs::cpu_or_gpu_mat
    run(const std::vector<frame> &transformed_history_frames,
        const std::vector<frame> &transformed_rescaled_history_frames) {
      typename cvs::cpu_or_gpu_mat dissimilarity{
          transformed_history_frames[0].size(), 0, CV_32SC1};

      // Note: static storage duration makes this pipe not thread safe
      static typename cvs::cpu_or_gpu_mat mask{
          transformed_history_frames[0].size(), CV_8UC1};
      static typename cvs::cpu_or_gpu_mat dissimilarity_part{
          transformed_history_frames[0].size(), CV_8UC1};
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

      typename cvs::cpu_or_gpu_mat mask{intersected_frames[0].size(), CV_8UC1};
      for (typename std::remove_reference_t<decltype(
               intersected_frames)>::size_type i = 0;
           i < intersected_frames.size() - 1; i++) {
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
              const typename cvs::cpu_or_gpu_mat &weights) {
      auto num_historical_frames = historical_frames->max_historical_frames();
      auto zero_weights = [num_historical_frames](
                              const frame &fr,
                              typename cvs::cpu_or_gpu_mat &&weights) {
        cvs::compare(weights, num_historical_frames - 1, weights, cv::CMP_LT);
        cvs::bitwise_and(weights, fr, weights);
        return frame(weights);
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

    frame run(typename cvs::cpu_or_gpu_mat &&dissimilarity,
              frame &&foreground_fr, typename cvs::cpu_or_gpu_mat &&weights) {
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
      auto dissimilarity_host = cv::Mat(dissimilarity);
      auto weights_host = cv::Mat(weights);

      // We use MatExpr for lazy evaluation in order avoid the allocation of
      // temporary cv::Mats

      cv::MatExpr weights_low =
          (weights_host <= history_frame_count_third) / uint8_max_double;
      cv::MatExpr weights_medium =
          ((weights_host < history_frame_count - 1) &
           (weights_host > history_frame_count_third)) /
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
          (dissimilarity_host <= third_gray) / uint8_max_double;
      cv::MatExpr dissimilarity_medium =
          ((dissimilarity_host > third_gray) / uint8_max_double +
           (dissimilarity_host < (2.0 * third_gray)) / uint8_max_double) *
          2.0;
      cv::MatExpr dissimilairy_high =
          (dissimilarity_host >= (2.0 * third_gray)) / uint8_max_double * 3.0;

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
    void run(frame *moving_foreground,
             std::vector<typename cvs::cpu_or_gpu_mat> &&shifted_masks) {
      for (auto &&mask : shifted_masks) {
        cvs::multiply(*moving_foreground, mask, *moving_foreground);
      }
    }
  };

  class erode_dilate {
  public:
    erode_dilate(int erosion_size, int dilation_size)
        : erosion_size{erosion_size}, dilation_size{dilation_size} {};

    void run(frame *moving_foreground) {
      const static cv::Mat erode_element = cv::getStructuringElement(
          cv::MORPH_ELLIPSE, {erosion_size, erosion_size});
      const static cv::Mat dilate_element = cv::getStructuringElement(
          cv::MORPH_ELLIPSE, {dilation_size, dilation_size});
      if (!cvs::is_cuda) {
        cv::erode(*moving_foreground, *moving_foreground, erode_element);
        cv::dilate(*moving_foreground, *moving_foreground, dilate_element);
      } else {
#ifdef USE_CUDA
        static auto erode = cv::cuda::createMorphologyFilter(
            cv::MORPH_ERODE, CV_8UC1, erode_element);
        static auto dilate = cv::cuda::createMorphologyFilter(
            cv::MORPH_DILATE, CV_8UC1, dilate_element);
        erode->apply(*moving_foreground, *moving_foreground);
        dilate->apply(*moving_foreground, *moving_foreground);
#endif
      }
    }

  private:
    int erosion_size, dilation_size;
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
};
} // namespace baboon_tracking
