import numpy as np

class ObjectModel:
    def __init__(self, bbox):
        self.bbox = bbox
        self.center = self._find_center()
        self.visible = True

    def _find_center(self):
        bbox = self.bbox

        # Find center
        return np.array([bbox[0] + (bbox[2] - bbox[0]) / 2, bbox[1] + (bbox[3] - bbox[1]) / 2])

    def tuple_bbox(self):
        return (self.bbox[0], self.bbox[1]), (self.bbox[2], self.bbox[3])

class ObjectRegistry:
    dist_threshold = 50

    def __init__(self):
        self._registry = []
        self._next_id = 0

    def _distance(self, p1, p2):
        return np.linalg.norm(np.subtract(p1, p2))

    def _find_nearest_object(self, input):
        nearest = None
        nearest_dist = None
        for obj in self._registry:
            if nearest is None:
                nearest = obj
                nearest_dist = self._distance(input.center, obj.center)
            else:
                dist = self._distance(input.center, obj.center)

                if nearest_dist > dist:
                    nearest = obj
                    nearest_dist = dist

        if nearest is None:
            return None

        if nearest_dist < self.dist_threshold:
            return nearest
        else:
            return None

    def get_objects(self):
        return self._registry

    def update(self, objects):
        for obj in self._registry:
            obj.visible = False

        for obj in objects:
            nearest = self._find_nearest_object(obj)

            if nearest is not None:
                self._registry.remove(nearest)

                obj.id = nearest.id
                obj.visible = True
            else:
                obj.id = self._next_id
                self._next_id += 1

            self._registry.append(obj)
