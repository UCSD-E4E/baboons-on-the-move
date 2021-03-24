from setuptools import setup, Extension
from Cython.Build import cythonize
import numpy

extensions = [
    Extension("foreground_c", ["./src/baboon_tracking/stages/motion_detector/generate_mask_subcomponents/foreground/foreground_c.pyx"]),
    Extension("generate_history_of_dissimilarity_c", ["./src/baboon_tracking/stages/motion_detector/generate_mask_subcomponents/generate_history_of_dissimilarity_c.pyx"]),
    Extension("generate_weights_c", ["./src/baboon_tracking/stages/motion_detector/generate_weights_c.pyx"]),
]
setup(
    ext_modules = cythonize(extensions, 
            annotate=True),
    include_dirs=[numpy.get_include()]
)
