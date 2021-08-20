#pragma once

#include <cmath>

#include <eigen3/Eigen/Core>
#include <eigen3/Eigen/QR>
#include <eigen3/Eigen/src/Cholesky/LDLT.h>
#include <eigen3/Eigen/src/Eigenvalues/EigenSolver.h>

#include "util.h"
#include "discretization.h"

#include "../drake/math/discrete_algebraic_riccati_equation.h"

namespace baboon_tracking {
template <int States, int Inputs>
bool is_stabilizable(const Eigen::Matrix<double, States, States>& A,
                        const Eigen::Matrix<double, States, Inputs>& B) {
  Eigen::EigenSolver<Eigen::Matrix<double, States, States>> es(A);

  for (int i = 0; i < States; ++i) {
    if (es.eigenvalues()[i].real() * es.eigenvalues()[i].real() +
            es.eigenvalues()[i].imag() * es.eigenvalues()[i].imag() <
        1) {
      continue;
    }

    Eigen::Matrix<std::complex<double>, States, States + Inputs> E;
    E << es.eigenvalues()[i] * Eigen::Matrix<std::complex<double>, States,
                                             States>::Identity() -
             A,
        B;

    Eigen::ColPivHouseholderQR<
        Eigen::Matrix<std::complex<double>, States, States + Inputs>>
        qr(E);
    if (qr.rank() < States) {
      return false;
    }
  }
  return true;
}

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
 * We can compute an optimal steady-state Kalman gain by solving a DARE if we have constant measurement and process noise covariance (and therefore a constant set of measurements.)
 */
template <int States, int Outputs>
class steady_state_kalman_filter {
 public:
  /**
   * Constructs a state-space observer with the given plant.
   *
   * @param A                  System matrix (process model).
   * @param C                  Measurement matrix (measurement model).
   * @param stateStdDevs       Standard deviations of model states.
   * @param measurementStdDevs Standard deviations of measurements.
   * @param dt                 Nominal discretization timestep (seconds).
   */
  steady_state_kalman_filter(const Eigen::Matrix<double, States, States>& A,
		   const Eigen::Matrix<double, Outputs, States>& C,
                   const std::array<double, States>& state_std_devs,
                   const std::array<double, Outputs>& measurement_std_devs,
                   double dt) : A{A}, C{C} {
    auto cont_Q = make_cov_matrix(state_std_devs);
    auto cont_R = make_cov_matrix(measurement_std_devs);

    Eigen::Matrix<double, States, States> disc_A;
    Eigen::Matrix<double, States, States> disc_Q;
    discretize_AQ_taylor<States>(A, cont_Q, dt, &disc_A, &disc_Q);
    disc_A_nominal = disc_A;

    auto disc_R = discretize_R<Outputs>(cont_R, dt);

    // IsStabilizable(Aᵀ, Cᵀ) will tell us if the system is observable.
    bool is_observable =
        is_stabilizable<States, Outputs>(disc_A.transpose(), C.transpose());
    if (!is_observable) {
      throw std::invalid_argument(
          "The system passed to the Kalman filter is not observable!");
    }

    Eigen::Matrix<double, States, States> P =
        drake::math::DiscreteAlgebraicRiccatiEquation(
            disc_A.transpose(), C.transpose(), disc_Q, disc_R);

    // S = CPCᵀ + R
    Eigen::Matrix<double, Outputs, Outputs> S = C * P * C.transpose() + disc_R;

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
    _K = S.transpose().ldlt().solve(C * P.transpose()).transpose();

    reset();
  }

  steady_state_kalman_filter(steady_state_kalman_filter&&) = default;
  steady_state_kalman_filter& operator=(steady_state_kalman_filter&&) = default;

  /**
   * Returns the steady-state Kalman gain matrix K.
   */
  const Eigen::Matrix<double, States, Outputs>& K() const { return _K; }

  /**
   * Returns an element of the steady-state Kalman gain matrix K.
   *
   * @param i Row of K.
   * @param j Column of K.
   */
  double K(int i, int j) const { return _K(i, j); }

  /**
   * Returns the state estimate x-hat.
   */
  const Eigen::Matrix<double, States, 1>& x_hat() const { return _x_hat; }

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
  void set_x_hat(const Eigen::Matrix<double, States, 1>& x_hat) { _x_hat = x_hat; }

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
   * Project the model into the future. No control input—we assume a homogenous system.
   *
   * @param dt Timestep for prediction (seconds).
   */
  void predict(double dt) {
    // We re-discretize A if there's a varying timestep
    Eigen::Matrix<double, States, States> disc_A;
    discretize_A<States>(A, dt, &disc_A);

    _x_hat = disc_A * _x_hat;
  }

  /**
   * Project the model into the future. No control input—we assume a homogenous system. This overload is for when you have a constant dt.
   */
  void predict() {
    _x_hat = disc_A_nominal * _x_hat;
  }

  /**
   * Correct the state estimate x-hat using the measurements in y.
   *
   * @param y Measurement vector.
   */
  void correct(const Eigen::Matrix<double, Outputs, 1>& y) {
    // x̂ₖ₊₁⁺ = x̂ₖ₊₁⁻ + K(y − Cx̂ₖ₊₁⁻)
    _x_hat += _K * (y - C * _x_hat);
  }

 private:
  Eigen::Matrix<double, States, States> A;
  Eigen::Matrix<double, Outputs, States> C;

  Eigen::Matrix<double, States, States> disc_A_nominal; // A discretized for the nominal timestep

  /**
   * The steady-state Kalman gain matrix.
   */
  Eigen::Matrix<double, States, Outputs> _K;

  /**
   * The state estimate.
   */
  Eigen::Matrix<double, States, 1> _x_hat;
};
}
