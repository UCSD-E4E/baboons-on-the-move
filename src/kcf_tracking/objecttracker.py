import cv2

from objectregistry import ObjectModel

class ObjectTracker:
    def __init__(self, object_registry):
        self._object_registry = object_registry
        self._tracker_created = set()

        self._multitracker = cv2.MultiTracker_create()

    def find_objects(self, frame):
        objects = self._object_registry.get_objects()

        for obj in objects:
            if obj.id in self._tracker_created:
                continue

            self._multitracker.add(cv2.TrackerKCF_create(), frame, (obj.bbox[0], obj.bbox[1], obj.bbox[2], obj.bbox[3]))
            self._tracker_created.add(obj.id)

        success, boxes = self._multitracker.update(frame)
        self._object_registry.update([ObjectModel(b) for b in boxes])

        print(success)

        return self._object_registry.get_objects()