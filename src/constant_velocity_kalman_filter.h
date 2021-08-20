#pragma once

#include "kalman/discretization.h"
#include "kalman/kalman_filter.h"
#include "kalman/util.h"

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

  static Eigen::Matrix<double, num_states, num_states> make_A() {
    // Remember: A is continuous—xdot = Ax
    Eigen::Matrix<double, states_per_baboon, states_per_baboon> A_sub;
    // clang-format off
      A_sub << 0, 0, 1, 0,
	       0, 0, 0, 1,
	       0, 0, -1, 0,
	       0, 0, 0, -1;
    // clang-format on

    Eigen::Matrix<double, num_states, num_states> A;
    for (int i = 0; i < MaxBaboons; i++) {
      A.template block<states_per_baboon, states_per_baboon>(
          i * num_states, i * num_states) = A_sub;
    }

    return A;
  }

  static Eigen::Matrix<double, measurements_per_baboon, num_states>
  make_C(int baboon_idx, double dt) {
    Eigen::Matrix<double, measurements_per_baboon, states_per_baboon> C_sub;
    // clang-format off
      C_sub << 1, 0, 0,   0,
	       0, 1, 0,   0,
	       1, 0, -dt, 0,
	       0, 1, 0, -dt;
    // clang-format on
    Eigen::Matrix<double, measurements_per_baboon, num_states> C;
    C.template block<measurements_per_baboon, states_per_baboon>(
        0, baboon_idx * states_per_baboon) = C_sub;

    return C;
  }

public:
  constant_velocity_kalman_filter(
      std::array<double, num_states> state_std_devs,
      std::array<double, measurements_per_baboon> measurement_std_devs,
      double max_bounding_box_distance, double dt)
      : kf{make_A(), state_std_devs, dt},
        measurement_std_devs{measurement_std_devs},
        max_bounding_box_distance{max_bounding_box_distance}, dt{dt} {}

  Eigen::Matrix<double, num_states, 1>
  run(const int actual_num_baboons,
      const std::vector<cv::Rect> &current_bounding_boxes) {
    if (actual_num_baboons > MaxBaboons)
      throw std::range_error{"You have more baboons than the compiled-in "
                             "maximum number of baboons"};

    Eigen::Matrix<double, num_states, 1> x_hat_old = kf.x_hat();
    kf.predict();

    static const Eigen::Matrix<double, measurements_per_baboon,
                               measurements_per_baboon>
        R = make_cov_matrix(measurement_std_devs);
    static const Eigen::Matrix<double, measurements_per_baboon,
                               measurements_per_baboon>
        disc_R = discretize_R(R, dt);

    Eigen::Matrix<double, 2, Eigen::Dynamic> bounding_boxes{
        2, current_bounding_boxes.size()};
    for (std::remove_reference_t<decltype(current_bounding_boxes)>::size_type
             i = 0;
         i < current_bounding_boxes.size(); i++) {
      bounding_boxes.template block<2, 1>(0, i) << current_bounding_boxes[i].x,
          current_bounding_boxes[i].y;
      // TODO: could add a third dimension corresponding to bounding box area,
      // and then we could be comparing along that dimension with a "normal"
      // baboon bounding box size
    }

    for (int i = 0; i < actual_num_baboons; i++) {
      Eigen::Vector2d predicted_baboon_center =
          kf.x_hat().template block<2, 1>(i * states_per_baboon, 0);

      Eigen::VectorXd distances =
          ((-bounding_boxes).colwise() + predicted_baboon_center)
              .colwise()
              .hypotNorm()
              .transpose();

      Eigen::Matrix<double, measurements_per_baboon, 1> y;
      for (int j = 0; j < distances.rows(); j++) {
        if (distances[j] <= max_bounding_box_distance) {
          y << bounding_boxes.template block<2, 1>(0, j),
              x_hat_old.template block<2, 1>(i * states_per_baboon, 0);
          kf.correct(y, make_C(i, dt), disc_R);
        }
      }
    }

    return kf.x_hat();
  }

  void set_x_hat(int i, double value) { kf.set_x_hat(i, value); }

private:
  kalman_filter<num_states> kf;
  std::array<double, measurements_per_baboon> measurement_std_devs;

  double max_bounding_box_distance; // Pixels
  double dt;                        // Seconds
};
} // namespace baboon_tracking
