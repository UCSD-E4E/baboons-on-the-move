import cv2

class FramePreprocessor:
    def preprocess(self, frame):
        img_yuv = cv2.cvtColor(frame, cv2.COLOR_BGR2YUV)

        img_yuv[:,:,0] = cv2.equalizeHist(img_yuv[:,:,0])

        return cv2.cvtColor(img_yuv, cv2.COLOR_YUV2BGR)