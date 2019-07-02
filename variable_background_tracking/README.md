# Variable Background Tracking
Implementation of [Kumar S. Ray, Soma Chakraborty](https://arxiv.org/abs/1706.02672)'s paper  
Instead of using Fourier Transforms for image registration, we are using [OpenCV Image Alignment](https://www.learnopencv.com/image-alignment-feature-based-using-opencv-c-python/)
For defining blobs, we use [OpenCV Morphological Transforms](https://docs.opencv.org/3.0-beta/doc/py_tutorials/py_imgproc/py_morphological_ops/py_morphological_ops.html) instead of the equation given on the paper

## How To Run
1. Move DJI_0769.MP4 into current directory
2. Install dependencies (TODO CREATE PIPENV)
3. To run main code:
```
python3 __init__.py
```
4. To run benchmarking code:
```
python3 bencmark.py
```
5. To run blob detection code only, first move first_attempt_at_using_image_registration into current directory, and then:
```
python3 test_dilate.py
```
