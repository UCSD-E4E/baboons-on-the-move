#pragma once

#include "kalman/kalman_filter.h"
#include <opencv2/core/types.hpp>

namespace baboon_tracking {
// TODO: dynamic-sized matrices would *probably* be more efficient, but it's
// also much more of a pain
template <int MaxBaboons> class constant_velocity_kalman_filter {
private:
  // x = [x, y, v_x, v_y, ...]
  // y = [x_k, y_k, x_{k-1}, y_{k-1}, ...]
  // No u
  static constexpr int states_per_baboon = 4;
  static constexpr int num_states = MaxBaboons * states_per_baboon;
  static constexpr int measurements_per_baboon = 4;
  static constexpr int num_measurements = MaxBaboons * measurements_per_baboon;

  static Eigen::Matrix<double, num_states, num_states> make_A() {
    // Remember: A is continuous—xdot = Ax
    Eigen::Matrix<double, states_per_baboon, states_per_baboon> A_sub;
    // clang-format off
      A_sub << 0, 0, 1, 0,
	       0, 0, 0, 1,
	       0, 0, 0, 0,
	       0, 0, 0, 0;
    // clang-format on

    Eigen::Matrix<double, num_states, num_states> A;
    for (int i = 0; i < MaxBaboons; i++) {
      A.template block<states_per_baboon, states_per_baboon>(
          i * num_states, i * num_states) = A_sub;
    }

    return A;
  }

  static Eigen::Matrix<double, num_measurements, num_states> make_C(double dt) {
    Eigen::Matrix<double, measurements_per_baboon, states_per_baboon> C_sub;
    // clang-format off
      C_sub << 1, 0, 0,   0,
	       0, 1, 0,   0,
	       1, 0, -dt, 0,
	       0, 1, 0, -dt;
    // clang-format on
    Eigen::Matrix<double, num_measurements, num_states> C;
    for (int i = 0; i < MaxBaboons; i++) {
      C.template block<measurements_per_baboon, states_per_baboon>(
          i * num_measurements, i * num_states) = C_sub;
    }

    return C;
  }

public:
  constant_velocity_kalman_filter(
      std::array<double, num_states> state_std_devs,
      std::array<double, num_measurements> measurement_std_devs, double dt)
      : kf{make_A(), make_C(dt), state_std_devs, measurement_std_devs, dt},
        dt{dt} {}

  Eigen::Matrix<double, num_states, 1>
  run(const int actual_num_baboons,
      const std::vector<cv::Rect> &current_bounding_boxes) {
    if (actual_num_baboons > MaxBaboons)
      throw std::range_error{"You have more baboons than the compiled-in "
                             "maximum number of baboons"};

    Eigen::Matrix<double, num_states, 1> x_hat_old = kf.x_hat();
    kf.predict();

    Eigen::Matrix<double, num_measurements, 1> y;
    for (int i = 0; i < actual_num_baboons; i++) {
      Eigen::Vector2d predicted_baboon_center =
          kf.x_hat().template block<2, 1>(i * states_per_baboon, 0);

      auto smallest_distance = std::numeric_limits<double>::infinity();
      Eigen::Vector2d closest_bounding_box_center;
      for (auto &&bounding_box : current_bounding_boxes) {
        Eigen::Vector2d bounding_box_center{bounding_box.x, bounding_box.y};

        auto distance =
            (predicted_baboon_center - bounding_box_center).hypotNorm();
        if (distance < smallest_distance) {
          smallest_distance = distance;
          closest_bounding_box_center = bounding_box_center;
        }
      }
      // TODO: the above loop could be made way faster by putting all the
      // bounding box centers into a Matrix and then finding the columnwise
      // Euclidian norm and taking the minimum of the result of that reduction
      y.template block<measurements_per_baboon, 1>(i * measurements_per_baboon,
                                                   0)
          << closest_bounding_box_center,
          x_hat_old.template block<2, 1>(i * states_per_baboon, 0);
    }
    kf.correct(y);

    return kf.x_hat();
  }

  void set_x_hat(int i, double value) { kf.set_x_hat(i, value); }

private:
  kalman_filter<num_states, num_measurements> kf;
  double dt; // Seconds
};
} // namespace baboon_tracking
