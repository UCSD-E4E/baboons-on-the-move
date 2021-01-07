### old_tracking.py explained

## Usage
`python old_tracking.py bitmask srcvideo`

## Overview
This tracking algorithm uses out-of-the-box opencv techniques to get a pretty good result. Uses pre-calculated bitmask for movement, but could use opencv's background subtraction instead. Uses blob detection to get blobs, and uses trackers to persist them between frames. Each frame, each keypoint found by blob detection attaches itself to the nearest tracker object. Then, tracker objects that haven't recieved updates in a while will dissappear. This allows a baboon to be tracked even though it stays still for a short while, or if it crosses paths with another baboon. It's a stupid algorithm, but simple is good and fast.

## In the future
As brought up in the meeting, this algorithm can be used in tandem with a CNN, effectively replacing an RPN. On a simpler level, it can at least be used to generate training data for a CNN by saving images that may or may not be baboons. I expect that with a little enhancement, maybe using color or gradient features, this would be a really effective algorithm, despite the weakness of it relying initially on movement.
