#include "constant_velocity_kalman_filter.h"

filter::filter(std::array<double, num_states> state_std_devs,
               std::array<double, num_measurements> measurement_std_devs,
               double dt)
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
}

void filter::run(const int actual_num_baboons,
                 const std::vector<cv::Rect> &current_bounding_boxes) {
  Eigen::Matrix<double, num_states, 1> x_hat_old = kf.x_hat();
  kf.predict(Eigen::Matrix<double, 0, 0>::Zero(), dt);

  Eigen::Matrix<double, num_measurements, 1> y;
  for (int i = 0; i < actual_num_baboons; i++) {
    Eigen::Matrix<double, states_per_baboon, 1> predicted_baboon =
        kf.x_hat().template block<states_per_baboon, 1>(i * states_per_baboon);

    auto smallest_distance = std::numeric_limits<double>::infinity();
    Eigen::Vector2f closest_bounding_box_center;
    for (auto &&bounding_box : current_bounding_boxes) {
      Eigen::Vector2f bounding_box_center{bounding_box.x, bounding_box.y};

      auto distance =
          (bounding_box_center - closest_bounding_box_center).hypotNorm();
      if (distance < smallest_distance) {
        smallest_distance = distance;
        closest_bounding_box_center = bounding_box_center;
      }
    }
    // TODO: the above loop could be made way faster by putting all the bounding
    // box centers into a Matrix and then finding the columnwise Euclidian norm
    // and taking the minimum of the result of that reduction
    y.template block<measurements_per_baboon, 1>(i * measurements_per_baboon, 1)
        << closest_bounding_box_center,
        x_hat_old.template block<2, 1>(i * states_per_baboon);
  }
  kf.correct(y);
}
