#pragma once

#include <eigen3/Eigen/Core>
#include <eigen3/Eigen/src/LU/PartialPivLU.h>
#include <eigen3/unsupported/Eigen/src/MatrixFunctions/MatrixExponential.h>

namespace baboon_tracking {
/**
 * Discretizes the given continuous A matrix.
 *
 * @param contA Continuous system matrix.
 * @param dt    Discretization timestep (seconds).
 * @param discA Storage for discrete system matrix.
 */
template <int States>
void discretize_A(const Eigen::Matrix<double, States, States>& contA,
                 double dt,
                 Eigen::Matrix<double, States, States>* discA) {
  *discA = (contA * dt).exp();
}

/**
 * Discretizes the given continuous A and Q matrices.
 *
 * @param contA Continuous system matrix.
 * @param contQ Continuous process noise covariance matrix.
 * @param dt    Discretization timestep (seconds).
 * @param discA Storage for discrete system matrix.
 * @param discQ Storage for discrete process noise covariance matrix.
 */
template <int States>
void discretize_AQ(const Eigen::Matrix<double, States, States>& cont_A,
                  const Eigen::Matrix<double, States, States>& cont_Q,
                  double dt,
                  Eigen::Matrix<double, States, States>* disc_A,
                  Eigen::Matrix<double, States, States>* disc_Q) {
  // Make continuous Q symmetric if it isn't already
  Eigen::Matrix<double, States, States> Q = (cont_Q + cont_Q.transpose()) / 2.0;

  // Set up the matrix M = [[-A, Q], [0, A.T]]
  Eigen::Matrix<double, 2 * States, 2 * States> M;
  M.template block<States, States>(0, 0) = -cont_A;
  M.template block<States, States>(0, States) = Q;
  M.template block<States, States>(States, 0).setZero();
  M.template block<States, States>(States, States) = cont_A.transpose();

  Eigen::Matrix<double, 2 * States, 2 * States> phi =
      (M * dt).exp();

  // Phi12 = phi[0:States,        States:2*States]
  // Phi22 = phi[States:2*States, States:2*States]
  Eigen::Matrix<double, States, States> phi12 =
      phi.block(0, States, States, States);
  Eigen::Matrix<double, States, States> phi22 =
      phi.block(States, States, States, States);

  *disc_A = phi22.transpose();

  Q = *disc_A * phi12;

  // Make discrete Q symmetric if it isn't already
  *disc_Q = (Q + Q.transpose()) / 2.0;
}

/**
 * Discretizes the given continuous A and Q matrices.
 *
 * Rather than solving a 2N x 2N matrix exponential like in DiscretizeAQ()
 * (which is expensive), we take advantage of the structure of the block matrix
 * of A and Q.
 *
 * 1) The exponential of A*t, which is only N x N, is relatively cheap.
 * 2) The upper-right quarter of the 2N x 2N matrix, which we can approximate
 *    using a taylor series to several terms and still be substantially cheaper
 *    than taking the big exponential.
 *
 * @param contA Continuous system matrix.
 * @param contQ Continuous process noise covariance matrix.
 * @param dt    Discretization timestep (double).
 * @param discA Storage for discrete system matrix.
 * @param discQ Storage for discrete process noise covariance matrix.
 */
template <int States>
void discretize_AQ_taylor(const Eigen::Matrix<double, States, States>& cont_A,
                        const Eigen::Matrix<double, States, States>& cont_Q,
                        double dt,
                        Eigen::Matrix<double, States, States>* disc_A,
                        Eigen::Matrix<double, States, States>* disc_Q) {
  // Make continuous Q symmetric if it isn't already
  Eigen::Matrix<double, States, States> Q = (cont_Q + cont_Q.transpose()) / 2.0;

  Eigen::Matrix<double, States, States> last_term = Q;
  double last_coeff = dt;

  // Aᵀⁿ
  Eigen::Matrix<double, States, States> Atn = cont_A.transpose();

  Eigen::Matrix<double, States, States> phi12 = last_term * last_coeff;

  // i = 6 i.e. 5th order should be enough precision
  for (int i = 2; i < 6; ++i) {
    last_term = -cont_A * last_term + Q * Atn;
    last_coeff *= dt / static_cast<double>(i);

    phi12 += last_term * last_coeff;

    Atn *= cont_A.transpose();
  }

  discretize_A<States>(cont_A, dt, disc_A);
  Q = *disc_A * phi12;

  // Make discrete Q symmetric if it isn't already
  *disc_Q = (Q + Q.transpose()) / 2.0;
}

/**
 * Returns a discretized version of the provided continuous measurement noise
 * covariance matrix.
 *
 * @param R  Continuous measurement noise covariance matrix.
 * @param dt Discretization timestep.
 */
template <int Outputs>
Eigen::Matrix<double, Outputs, Outputs> discretize_R(
    const Eigen::Matrix<double, Outputs, Outputs>& R, double dt) {
  return R / dt;
}
}
