import cv2
import numpy as np
import math
import cmath
import multiprocessing

from .Registration import Registration


class FFT_Registration(Registration):
    def _delta_x(self, x_bar, M):
        if x_bar > M / 2:
            return x_bar - M
        else:
            return x_bar

    def _delta_y(self, y_bar, N):
        if y_bar > N / 2:
            return y_bar - N
        else:
            return y_bar

    def _compute_ratio(self, frame, previous_frame):
        frame_star = np.conj(frame)

        num = np.multiply(previous_frame, frame_star)

        return np.fft.ifft2(num)

    def _exp(self, m, n, M, N, delta):
        return cmath.exp(-1j * 2 * math.pi * ((m * delta[1]) / M + (n * delta[0]) / N))

    def register(self, frame1, frame2):
        """
        Uses Fast Fourier Transform to find transformation matrix betwen two frames
        """
        ratio = abs(self._compute_ratio(frame1, frame2))
        arg_max = np.unravel_index(ratio.argmax(), ratio.shape)

        delta = (
            self._delta_x(arg_max[1], frame1.shape[1]),
            self._delta_y(arg_max[0], frame1.shape[0]),
        )

        M = np.float32([[1, 0, -delta[0]], [0, 1, -delta[1]], [0, 0, 1]])

        return M
