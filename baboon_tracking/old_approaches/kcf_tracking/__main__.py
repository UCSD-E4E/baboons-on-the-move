import cv2
import copy

from framepreprocessor import FramePreprocessor
from objectdetector import ObjectDetector
from objecttracker import ObjectTracker
from objectregistry import ObjectRegistry

def display_object(img, obj, color, size):
    if not obj.visible:
        return

    cv2.rectangle(img, (int(obj.bbox[0]), int(obj.bbox[1])), (int(obj.bbox[2]), int(obj.bbox[3])), color, size)

    cv2.circle(img, (int(obj.center[0]), int(obj.center[1])), 2, color, cv2.FILLED)
    cv2.putText(img, str(obj.id), (int(obj.center[0]) - 2, int(obj.center[1]) - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1, cv2.LINE_AA)

def main():
    frame_preprocessor = FramePreprocessor()

    object_detector = ObjectDetector()
    object_registry = ObjectRegistry()
    object_tracker = ObjectTracker(object_registry)

    cap = cv2.VideoCapture('video.avi')
    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    out = cv2.VideoWriter('output.avi',fourcc, 20.0, (800,480))

    while True:
        # Get the frame from video file
        ret, frame = cap.read()

        if ret == True:
            preprocessed_frame = frame_preprocessor.preprocess(frame)

            objects_from_bkg_sub = object_detector.find_objects(frame)
            object_registry.update(objects_from_bkg_sub)

            objects_from_registry = copy.deepcopy(object_registry.get_objects())
            objects_from_tracker = object_tracker.find_objects(frame)

            bounding_boxes = frame.copy()

            for obj in objects_from_registry: # Blue
                display_object(bounding_boxes, obj, (255, 0,0 ), 1)

            for obj in objects_from_tracker: # Red
                display_object(bounding_boxes, obj, (0, 0, 255), 1)

            cv2.imshow('Input',frame)
            cv2.imshow('Preprocessed Frame', preprocessed_frame)
            cv2.imshow('Bounding Boxes', bounding_boxes)
            out.write(bounding_boxes)
            k = cv2.waitKey(30) & 0xff
            if k == 27:
                break
        else:
            break

    out.release()
    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()