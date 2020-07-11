# baboon-tracking

[[![Build Status](https://travis-ci.org/UCSD-E4E/baboon-tracking.svg?branch=master)](https://travis-ci.org/UCSD-E4E/baboon-tracking)](https://travis-ci.org/UCSD-E4E/baboon-tracking)
This repo holds all of the [Baboon Team](http://e4e.ucsd.edu/baboons-on-the-move)'s attempted algorithms and implementations to track baboons from aerial drone footage, as well as any other code written for the project.

# User Setup Instructions

1. Build everything and start docker container

```
make
```

2. Open localhost:8888 to access jupyter notebook inside docker container, the password is ucsde4e
3. Navigate into utils and run ImageStreamClient to receive images from rabbitmq

```
cd utils; python3 ImageStreamClient.py
```

# Dev Setup Instructions, python 3.8 needed (conda environment recommended)

1. Set up python virtual environment
   conda (uses the conda_requirements.txt):

```
(base) $ conda create --name py38 python=3.8
(base) $ conda activate py38
(py38) $ conda install --file conda_requirements.txt
```

pipenv (uses the Pipfile):

```
$ pipenv install
$ pipenv shell
```

venv (just don't, but if you really wanted to...):

```
$ pip install -r requirements.txt
```

2. Add "baboon_tracking" to be importable
   cd into the directory at which the baboon-tracking on your local directory  
   pwd (to get the full path of where the directory lives)  
   add the following line (but your path found in the previous step) to your ~/.bashrc (or ~/.zshrc if you're a ninja)  
   restart your terminal session (or use the command "source ~/.zshrc", if you're a ninja of course)

```
export PYTHONPATH="/Users/joshuakang/git/baboon-tracking:$PYTHONPATH"
```

3. Test if package is accessible by the python path

```
$ python3
>>> import baboon_tracking
```

4. Add a video dataset to the /data directory named "input.mp4"
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

Webscraper to download streamed videos from the San Diego Zoo's [Baboon Live Cams](https://zoo.sandiegozoo.org/cams/baboon-cam). These videos have been determined to not be useful at the current time in the project, as drone footage has very different properties.

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
