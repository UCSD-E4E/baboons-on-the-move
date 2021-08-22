#pragma once

#include <algorithm>

#include "kalman/discretization.h"
#include "kalman/kalman_filter.h"
#include "kalman/util.h"

#include <opencv2/core/types.hpp>

namespace baboon_tracking {
// TODO: dynamic-sized matrices would *probably* be more efficient, but it's
// also much more of a pain
template <int MaxBaboons> class constant_velocity_kalman_filter {
public:
  // x = [x, y, v_x, v_y, ...]
  // y = [x_k, y_k, x_{k-1}, y_{k-1}, ...]
  // No u
  static constexpr int states_per_baboon = 4;
  static constexpr int num_states = MaxBaboons * states_per_baboon;
  static constexpr int measurements_per_baboon = 4;

private:
  static Eigen::Matrix<double, num_states, num_states> make_A() {
    // Remember: A is continuous—xdot = Ax
    Eigen::Matrix<double, states_per_baboon, states_per_baboon> A_sub;
    // clang-format off
      A_sub << 0, 0, 1, 0,
	       0, 0, 0, 1,
	       0, 0, 0, 0,
	       0, 0, 0, 0;
    // clang-format on

    Eigen::Matrix<double, num_states, num_states> A =
        Eigen::Matrix<double, num_states, num_states>::Zero();
    for (int i = 0; i < MaxBaboons; i++) {
      A.template block<states_per_baboon, states_per_baboon>(
          i * states_per_baboon, i * states_per_baboon) = A_sub;
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
    Eigen::Matrix<double, measurements_per_baboon, num_states> C =
        Eigen::Matrix<double, measurements_per_baboon, num_states>::Zero();
    C.template block<measurements_per_baboon, states_per_baboon>(
        0, baboon_idx * states_per_baboon) = C_sub;

    return C;
  }

  static constexpr std::array<double, num_states>
  make_Q(std::array<double, states_per_baboon> per_baboon_state_std_devs) {
    std::array<double, num_states> state_std_devs;
    for (int i = 0; i < num_states; i++) {
      state_std_devs[i] = per_baboon_state_std_devs[i % states_per_baboon];
    }
    return state_std_devs;
  }

public:
  constant_velocity_kalman_filter(
      std::array<double, states_per_baboon> per_baboon_state_std_devs,
      std::array<double, measurements_per_baboon> measurement_std_devs,
      double max_bounding_box_distance, double dt)
      : kf{make_A(), make_Q(per_baboon_state_std_devs), dt},
        measurement_std_devs{measurement_std_devs},
        max_bounding_box_distance{max_bounding_box_distance}, dt{dt} {}

  const Eigen::Matrix<double, num_states, 1> &
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
    Eigen::VectorXd bounding_boxes_radii{current_bounding_boxes.size()};
    for (std::remove_reference_t<decltype(current_bounding_boxes)>::size_type
             i = 0;
         i < current_bounding_boxes.size(); i++) {
      const auto &bb = current_bounding_boxes[i];
      bounding_boxes.template block<2, 1>(0, i) << bb.x + bb.width / 2.0,
          bb.y + bb.width / 2.0;
      bounding_boxes_radii[i] = std::max(bb.width, bb.height) / 2.0;
    }

    for (int i = 0; i < actual_num_baboons; i++) {
      Eigen::Vector2d predicted_baboon_center =
          kf.x_hat().template block<2, 1>(i * states_per_baboon, 0);

      Eigen::VectorXd distances =
          (((-bounding_boxes).colwise() + predicted_baboon_center)
               .colwise()
               .hypotNorm()
               .transpose() -
           bounding_boxes_radii)
              .unaryExpr([](double a) { return std::max(0.0, a); });

      Eigen::Matrix<double, measurements_per_baboon, 1> y;
      for (int j = 0; j < distances.rows(); j++) {
        if (distances[j] <= max_bounding_box_distance) {
          y << bounding_boxes.template block<2, 1>(0, j),
              x_hat_old.template block<2, 1>(i * states_per_baboon, 0);

          Eigen::Matrix<double, measurements_per_baboon,
                        measurements_per_baboon>
              disc_R_scaled =
                  disc_R + disc_R * (distances[j] / max_bounding_box_distance);
          kf.correct(y, make_C(i, dt), disc_R_scaled);
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
