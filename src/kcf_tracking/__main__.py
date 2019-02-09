import cv2

from objectdetector import ObjectDetector
from objecttracker import ObjectTracker
from objectregistry import ObjectRegistry

def main():
    font = cv2.FONT_HERSHEY_SIMPLEX

    object_detector = ObjectDetector()
    object_tracker = ObjectTracker()
    object_registry = ObjectRegistry()

    cap = cv2.VideoCapture('video.avi')
    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    out = cv2.VideoWriter('output.avi',fourcc, 20.0, (800,480))

    prev_frame = None
    prev_boxes = None
    boxes2 = []
    while True:
        # Get the frame from video file
        ret, frame = cap.read()

        if ret == True:
            objects_from_bkg_sub = object_detector.find_objects(frame)

            object_registry.update(objects_from_bkg_sub)

            objects = object_registry.get_objects()

            # if prev_frame is not None and prev_boxes is not None:
            #     boxes2 = object_tracker.find_boxes((prev_frame, prev_boxes), (frame, boxes))

            # if len(boxes2) == 0:
            #     boxes2 = boxes

            bounding_boxes = frame.copy()

            for obj in objects:
                if not obj.visible:
                    continue

                cv2.rectangle(bounding_boxes, (obj.bbox[0], obj.bbox[1]), (obj.bbox[2], obj.bbox[3]), (255, 0, 0))

                cv2.circle(bounding_boxes, (int(obj.center[0]), int(obj.center[1])), 2, (255, 0, 0), cv2.FILLED)
                cv2.putText(bounding_boxes, str(obj.id), (int(obj.center[0]) - 2, int(obj.center[1]) - 5), font, 0.5, (255, 0, 0), 1, cv2.LINE_AA)

            # for box in boxes2:
            #     cv2.rectangle(bounding_boxes, (box[0], box[1]), (box[2], box[3]), (0, 0, 255))

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