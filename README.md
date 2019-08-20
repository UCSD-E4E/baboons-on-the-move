# baboon-tracking
[![Build Status](https://travis-ci.org/UCSD-E4E/baboon-tracking.svg?branch=master)](https://travis-ci.org/UCSD-E4E/baboon-tracking)
This repo holds all of the [Baboon Team](http://e4e.ucsd.edu/baboons-on-the-move)'s attempted algorithms and implementations to track baboons from aerial drone footage, as well as any other code written for the project.

# Makefile Instructions
- make: builds python package, builds docker image, runs docker image
- build: build python package
- docker-build: builds docker image with tag anhdngo/baboon_tracking
- docker-run: creates and runs our baboon docker image, as well as rabbitmq docker image

# User Setup Instructions
1. Build everything and start docker container
```
make
```
2. Open localhost:8888 to access jupyter notebook inside docker container, the password is e4ebaboons
3. Navigate into utils and run ImageStreamClient to receive images from rabbitmq
```
cd utils; python3 ImageStreamClient.py
```

# Dev Setup Instructions
1. Set up pip environment
```
$ pipenv install
$ pipenv shell
```
2. Install baboon_tracking package
```
$ sudo python3 setup.py install
```
3. Test if package is installed through the python3 interpreter
```
$ python3
```
```
>>> import baboon_tracking
```
4. Run the rabbitmq docker container
```
$ docker container run -p 5672:5672 -p 15672:15672 --rm rabbitmq:3.8.0-beta.5
```
5. Run the provided sample files
```
$ python3 generate_mask.py
$ python3 detect_blobs.py
```
# Test Instructions
```
python3 -m unittest discover
```
# Included Projects
### scraper
Webscraper to download streamed videos from the San Diego Zoo's [Baboon Live Cams](https://zoo.sandiegozoo.org/cams/baboon-cam). These videos habe been determined to not be useful at the current time in the project, as drone footage has very different properties.
### kcf_tracking
Attempt to track baboons using Kernelized Correlation Filters. (TODO: Insert blurb here to explain how well this worked)
### background_subtraction
Attempt to detect baboons using simple background subtraction methods. Works well with stationary cameras, but translational and rotational background movement causes issues with this approach.
### opencv_builtin_tracking
Interactive test of various common builtin [opencv tracking methods](https://www.learnopencv.com/object-tracking-using-opencv-cpp-python/). Allows user to draw bounding box around baboon, and attempts to track it for duration of the video. Only able to track, not detect baboons.
### variable_background_tracking
Attempt to isolate moving foreground from a variable background by implementing the algorithm described in [this paper](https://arxiv.org/abs/1706.02672). At the moment, algorithm works well but is incredibly slow, as it has not been optimized for performance.
### registration_bg_subtraction
Use registration (stabilization) functions from variable_background_tracking, and apply regular background subtraction on the results
