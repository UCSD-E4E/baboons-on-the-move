#pragma once

#include <cmath>

#include <eigen3/Eigen/Core>
#include <eigen3/Eigen/src/Cholesky/LDLT.h>

#include "discretization.h"
#include "util.h"

namespace baboon_tracking {
/**
 * A Kalman filter combines predictions from a model and measurements to give an
 * estimate of the true system state. This is useful because many states cannot
 * be measured directly as a result of sensor noise, or because the state is
 * "hidden".
 *
 * Kalman filters use a K gain matrix to determine whether to trust the model or
 * measurements more. Kalman filter theory uses statistics to compute an optimal
 * K gain which minimizes the sum of squares error in the state estimate. This K
 * gain is used to correct the state estimate by some amount of the difference
 * between the actual measurements and the measurements predicted by the model.
 *
 * We do not compute an optimal steady-state Kalman gain because this Kalman
 * filter is designed to work with varying sets of measurements and varying
 * measurement covariance.
 */
template <int States> class kalman_filter {
public:
  /**
   * Constructs a state-space observer with the given plant.
   *
   * @param A                  Continuous system matrix (process model).
   * @param stateStdDevs       Standard deviations of continuous model states.
   * @param dt                 Nominal discretization timestep (seconds).
   */
  kalman_filter(const Eigen::Matrix<double, States, States> &A,
                const std::array<double, States> &state_std_devs, double dt)
      : A{A}, dt_nominal{dt} {
    auto cont_Q = make_cov_matrix(state_std_devs);
    discretize_AQ_taylor<States>(A, cont_Q, dt, &disc_A_nominal,
                                 &disc_Q_nominal);

    reset();
  }

  kalman_filter(kalman_filter &&) = default;
  kalman_filter &operator=(kalman_filter &&) = default;

  /**
   * Returns the state estimate x-hat.
   */
  const Eigen::Matrix<double, States, 1> &x_hat() const { return _x_hat; }

  /**
   * Returns the error covariance P.
   */
  const Eigen::Matrix<double, States, States> &P() const { return _P; }

  /**
   * Returns an element of the state estimate x-hat.
   *
   * @param i Row of x-hat.
   */
  double x_hat(int i) const { return _x_hat(i); }

  /**
   * Set initial state estimate x-hat.
   *
   * @param xHat The state estimate x-hat.
   */
  void set_x_hat(const Eigen::Matrix<double, States, 1> &x_hat) {
    _x_hat = x_hat;
  }

  /**
   * Set an element of the initial state estimate x-hat.
   *
   * @param i     Row of x-hat.
   * @param value Value for element of x-hat.
   */
  void set_x_hat(int i, double value) { _x_hat(i) = value; }

  /**
   * Resets the observer.
   */
  void reset() { _x_hat.setZero(); }

  /**
   * Project the model into the future. No control input—we assume a homogenous
   * system.
   *
   * @param dt Timestep for prediction (seconds).
   */
  void predict(const double dt) {
    // We re-discretize A if there's a varying timestep
    Eigen::Matrix<double, States, States> disc_A;
    Eigen::Matrix<double, States, States> disc_Q;
    discretize_AQ_taylor<States>(A, Q, dt, &disc_A, &disc_Q);

    _x_hat = disc_A * _x_hat;
    _P = disc_A * _P * disc_A.transpose() + disc_Q;
  }

  /**
   * Project the model into the future. No control input—we assume a homogenous
   * system. This overload is for when you have a constant dt (so you don't have
   * the cost of discretizing at each timestep).
   */
  void predict() {
    _x_hat = disc_A_nominal * _x_hat;
    _P = disc_A_nominal * _P * disc_A_nominal.transpose() + disc_Q_nominal;
  }

  /**
   * Correct the state estimate x-hat using the measurements in y.
   *
   * @param y Measurement vector.
   * @param C Output matrix (measurement model).
   * @param measurement_std_devs Standard deviations of measurement noise.
   */
  template <int Outputs, std::size_t OutputsLong = Outputs>
  void correct(const Eigen::Matrix<double, Outputs, 1> &y,
               const Eigen::Matrix<double, Outputs, States> &C,
               const Eigen::Matrix<double, Outputs, Outputs> &disc_R) {
    Eigen::Matrix<double, Outputs, Outputs> S = C * _P * C.transpose() + disc_R;

    // We want to put K = PCᵀS⁻¹ into Ax = b form so we can solve it more
    // efficiently.
    //
    // K = PCᵀS⁻¹
    // KS = PCᵀ
    // (KS)ᵀ = (PCᵀ)ᵀ
    // SᵀKᵀ = CPᵀ
    //
    // The solution of Ax = b can be found via x = A.solve(b).
    //
    // Kᵀ = Sᵀ.solve(CPᵀ)
    // K = (Sᵀ.solve(CPᵀ))ᵀ
    Eigen::Matrix<double, States, Outputs> K =
        S.transpose().ldlt().solve(C * _P.transpose()).transpose();

    // x̂ₖ₊₁⁺ = x̂ₖ₊₁⁻ + K(y − h(x̂ₖ₊₁⁻, uₖ₊₁))
    _x_hat += K * (y - C * _x_hat);

    // Pₖ₊₁⁺ = (I − KC)Pₖ₊₁⁻
    _P = (Eigen::Matrix<double, States, States>::Identity() - K * C) * _P;
  }

private:
  Eigen::Matrix<double, States, States> A;
  Eigen::Matrix<double, States, States>
      disc_A_nominal; // A discretized for the nominal timestep

  Eigen::Matrix<double, States, States> Q;
  Eigen::Matrix<double, States, States>
      disc_Q_nominal; // Q discretized for the nominal timestep

  double dt_nominal;

  /**
   * The state estimate.
   */
  Eigen::Matrix<double, States, 1> _x_hat;

  /**
   * The error covariance.
   */
  Eigen::Matrix<double, States, States> _P =
      Eigen::Matrix<double, States, States>::Zero();
};
} // namespace baboon_tracking
