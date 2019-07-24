import cv2
import numpy as np
import math
import cmath
import multiprocessing

MAX_FEATURES = 500
GOOD_MATCH_PERCENT = 0.15

class Registration_Strategy():
    def __init__():
        self.cpus = multiprocessing.cpu_count()
        self.pool = multiprocessing.Pool(processes=self.cpus)

    def shift_frame(self, frame, previous_frame):
        '''
        Takes in transformation matrix; does homography transformation to register/align two frames
        '''
        M = self.register(previous_frame, frame)
        return (cv2.warpPerspective(previous_frame, M, (previous_frame.shape[1], previous_frame.shape[0])).astype(np.uint8), M)

    def shift_all_frames(self, target_frame, frames):
        '''
        Shifts all frames to target frame, returns list of shifted frames
        '''
        return [self.shift_frame(target_frame, f) for f in frames]

    def shift_all_frames_multiprocessing(self, target_frame, frames, pool):
        '''
        Shifts all frames to target frame, returns list of shifted frames
        '''
        return pool.map(self.shift_frame, [(target_frame, f) for f in history_frames])


class ORB_Registration_Strategy(Registration_Strategy):
    def register(self, frame1, frame2):
        '''
        Registration function to find homography transformation between two frames using ORB
        Returns list of tuples containing (warped_frame, transformation matrix)
        (Not including most recent frame)
        '''
        orb = cv2.ORB_create(MAX_FEATURES)

        keypoints1, descriptors1 = orb.detectAndCompute(frame1, None)
        keypoints2, descriptors2 = orb.detectAndCompute(frame2, None)

        # Match features.
        matcher = cv2.DescriptorMatcher_create(cv2.DESCRIPTOR_MATCHER_BRUTEFORCE_HAMMING)
        matches = matcher.match(descriptors1, descriptors2, None)

        # Sort matches by score
        matches.sort(key=lambda x: x.distance, reverse=False)

        # Remove not so good matches
        numGoodMatches = int(len(matches) * GOOD_MATCH_PERCENT)
        matches = matches[:numGoodMatches]

        # Extract location of good matches
        points1 = np.zeros((len(matches), 2), dtype=np.float32)
        points2 = np.zeros((len(matches), 2), dtype=np.float32)

        for i, match in enumerate(matches):
            points1[i, :] = keypoints1[match.queryIdx].pt
            points2[i, :] = keypoints2[match.trainIdx].pt

        # Find homography
        h, mask = cv2.findHomography(points1, points2, cv2.RANSAC)

        return h

class FFT_Registration_Strategy(Registration_Strategy):
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
        '''
        Uses Fast Fourier Transform to find transformation matrix betwen two frames
        '''
        ratio = abs(self._compute_ratio(frame1, frame2))
        arg_max = np.unravel_index(ratio.argmax(), ratio.shape)

        delta = (self._delta_x(arg_max[1], frame1.shape[1]), self._delta_y(arg_max[0], frame1.shape[0]))

        M = np.float32([[1, 0, -delta[0]], [0, 1, -delta[1]]])

        return M

registration_strategies = {
    'orb': ORB_Registration_Strategy,
    'fft': FFT_Registration_Strategy
}