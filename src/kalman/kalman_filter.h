#pragma once

#include <cmath>

#include <eigen3/Eigen/Core>
#include <eigen3/Eigen/src/Cholesky/LDLT.h>
#include <eigen3/Eigen/src/Eigenvalues/EigenSolver.h>

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
 * Discretizes the given continuous A and B matrices.
 *
 * @param contA Continuous system matrix.
 * @param contB Continuous input matrix.
 * @param dt    Discretization timestep (seconds).
 * @param discA Storage for discrete system matrix.
 * @param discB Storage for discrete input matrix.
 */
template <int States, int Inputs>
void discretize_AB(const Eigen::Matrix<double, States, States>& cont_A,
                  const Eigen::Matrix<double, States, Inputs>& cont_B,
                  double dt,
                  Eigen::Matrix<double, States, States>* disc_A,
                  Eigen::Matrix<double, States, Inputs>* disc_B) {
  // Matrices are blocked here to minimize matrix exponentiation calculations
  Eigen::Matrix<double, States + Inputs, States + Inputs> M_cont;
  M_cont.setZero();
  M_cont.template block<States, States>(0, 0) = cont_A * dt;
  M_cont.template block<States, Inputs>(0, States) = cont_B * dt;

  // Discretize A and B with the given timestep
  Eigen::Matrix<double, States + Inputs, States + Inputs> Mdisc = M_cont.exp();
  *disc_A = Mdisc.template block<States, States>(0, 0);
  *disc_B = Mdisc.template block<States, Inputs>(0, States);
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
 * For more on the underlying math, read
 * https://file.tavsys.net/control/controls-engineering-in-frc.pdf chapter 9
 * "Stochastic control theory".
 */
template <int States, int Inputs, int Outputs>
class kalman_filter {
 public:
  /**
   * Constructs a state-space observer with the given plant.
   *
   * @param plant              The plant used for the prediction step.
   * @param stateStdDevs       Standard deviations of model states.
   * @param measurementStdDevs Standard deviations of measurements.
   * @param dt                 Nominal discretization timestep (seconds).
   */
  kalman_filter(const Eigen::Matrix<double, States, States>& A,
		   const Eigen::Matrix<double, States, Inputs>& B,
		   const Eigen::Matrix<double, Outputs, States>& C,
		   const Eigen::Matrix<double, Outputs, Inputs>& D,
                   const std::array<double, States>& state_std_devs,
                   const std::array<double, Outputs>& measurement_std_devs,
                   double dt) : A{A}, B{B}, C{C}, D{D} {
    auto cont_Q = MakeCovMatrix(state_std_devs);
    auto cont_R = MakeCovMatrix(measurement_std_devs);

    Eigen::Matrix<double, States, States> disc_A;
    Eigen::Matrix<double, States, States> disc_Q;
    discretize_AQ_taylor<States>(A, cont_Q, dt, &disc_A, &disc_Q);

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

  kalman_filter(kalman_filter&&) = default;
  kalman_filter& operator=(kalman_filter&&) = default;

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
   * Project the model into the future with a new control input u.
   *
   * @param u  New control input from controller.
   * @param dt Timestep for prediction (seconds).
   */
  void predict(const Eigen::Matrix<double, Inputs, 1>& u, double dt) {
    Eigen::Matrix<double, States, States> discA;
    Eigen::Matrix<double, States, Inputs> discB;
    discretize_AB<States, Inputs>(A, B, dt, &discA, &discB);

    _x_hat = discA * _x_hat + discB * u;
  }

  /**
   * Correct the state estimate x-hat using the measurements in y.
   *
   * @param u Same control input used in the last predict step.
   * @param y Measurement vector.
   */
  void correct(const Eigen::Matrix<double, Inputs, 1>& u,
               const Eigen::Matrix<double, Outputs, 1>& y) {
    // x̂ₖ₊₁⁺ = x̂ₖ₊₁⁻ + K(y − (Cx̂ₖ₊₁⁻ + Duₖ₊₁))
    _x_hat += _K * (y - (C * _x_hat + D * u));
  }

 private:
  Eigen::Matrix<double, States, States> A;
  Eigen::Matrix<double, States, Inputs> B;
  Eigen::Matrix<double, Outputs, States> C;
  Eigen::Matrix<double, Outputs, Inputs> D;

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
