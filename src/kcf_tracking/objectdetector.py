import cv2
import numpy as np
from skimage import img_as_ubyte
from skimage.measure import regionprops, label

from objectregistry import ObjectModel

class ObjectDetector:
    blur_threshold = 75

    def __init__(self):
        self.subtractor = cv2.createBackgroundSubtractorKNN()

    def _compute_mask(self, frame):
        subtractor_mask = self.subtractor.apply(frame)

        cv2.imshow('Subtractor Mask', subtractor_mask)

        blurred_mask = cv2.blur(subtractor_mask, (25, 25))
        idx = blurred_mask[:,:] > self.blur_threshold

        cv2.imshow('Blurred Mask', blurred_mask)

        blurred_mask_threshold = np.zeros(blurred_mask.shape)
        blurred_mask_threshold[idx] = 1

        cv2.imshow('Blurred Mask Threshold', blurred_mask_threshold)

        contours, hierarchy = cv2.findContours(img_as_ubyte(blurred_mask_threshold), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        contours_mask = np.zeros(blurred_mask_threshold.shape)
        cv2.drawContours(contours_mask, contours, -1, (255, 255, 255), cv2.FILLED)

        cv2.imshow('Contour Mask', contours_mask)

        percentage = (np.sum(contours_mask) / 255) / (contours_mask.shape[0] * contours_mask.shape[1])

        if percentage > 0.05:
            return np.zeros(contours_mask.shape)
        else:
            return contours_mask

    def _is_baboon(self, prop):
        return prop.bbox_area >= 500

    def find_objects(self, frame):
        blur = frame.copy()
        blur = cv2.blur(frame, (5, 5))

        cv2.imshow('Blur', blur)

        mask = self._compute_mask(frame)
        label_mask = label(mask)
        props = regionprops(label_mask)

        return [ObjectModel(np.array([p.bbox[1], p.bbox[0], p.bbox[3], p.bbox[2]])) for p in props if self._is_baboon(p)]
