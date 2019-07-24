import numpy as np
import math
import cmath

def delta_x(x_bar, M):
    if x_bar > M / 2:
        return x_bar - M
    else:
        return x_bar

def delta_y(y_bar, N):
    if y_bar > N / 2:
        return y_bar - N
    else:
        return y_bar

def compute_ratio(frame, previous_frame):
    frame_star = np.conj(frame)

    num = np.multiply(previous_frame, frame_star)

    return np.fft.ifft2(num)

def exp(m, n, M, N, delta):
    return cmath.exp(-1j * 2 * math.pi * ((m * delta[1]) / M + (n * delta[0]) / N))

def register(frame1, frame2):
    ratio = abs(compute_ratio(frame1, frame2))
    arg_max = np.unravel_index(ratio.argmax(), ratio.shape)

    delta = (delta_x(arg_max[1], frame1.shape[1]), delta_y(arg_max[0], frame1.shape[0]))

    M = np.float32([[1, 0, -delta[0]], [0, 1, -delta[1]]])

    return M