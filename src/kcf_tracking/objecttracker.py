import cv2

class ObjectTracker:
    def __init__(self):
        self.tracker = cv2.TrackerKCF_create()

    def _filter_duplicates(self, boxes):
        return boxes

    def find_boxes(self, prev_frame, frame):
        prev_boxes = prev_frame[1]
        prev_frame = prev_frame[0]

        boxes = []# frame[1]
        frame = frame[0]

        for prev_box in prev_boxes:
            self.tracker = cv2.TrackerKCF_create()
            self.tracker.init(prev_frame, prev_box)

            ret, bbox = self.tracker.update(frame)
            
            if ret:
                boxes.append((int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])))

        return boxes