import cv2

from objectdetector import ObjectDetector
from objecttracker import ObjectTracker

def main():
    object_detector = ObjectDetector()
    object_tracker = ObjectTracker()

    cap = cv2.VideoCapture('video.avi')
    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    out = cv2.VideoWriter('output.avi',fourcc, 20.0, (800,480))

    prev_frame = None
    prev_boxes = None
    while True:
        ret, frame = cap.read()

        if ret == True:
            boxes = object_detector.find_boxes(frame)

            if prev_frame is not None and prev_boxes is not None:
                boxes2 = object_tracker.find_boxes((prev_frame, prev_boxes), (frame, boxes))

            if len(boxes2) == 0:
                boxes2 = boxes

            bounding_boxes = frame.copy()

            for box in boxes:
                cv2.rectangle(bounding_boxes, (box[0], box[1]), (box[2], box[3]), (255, 0, 0))

            for box in boxes2:
                cv2.rectangle(bounding_boxes, (box[0], box[1]), (box[2], box[3]), (0, 0, 255))

            cv2.imshow('Input',frame)
            cv2.imshow('Bounding Boxes', bounding_boxes)
            out.write(bounding_boxes)
            k = cv2.waitKey(30) & 0xff
            if k == 27:
                break

            prev_frame = frame.copy()
            prev_boxes = boxes2
        else:
            break

    out.release()
    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()