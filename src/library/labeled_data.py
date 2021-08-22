"""
module for loading from labeled data.
"""
from math import ceil, floor
from xml.etree import ElementTree as ET


def _load_xml(xml_path: str):
    """
    loads XML data into python using etree package
    copied from /src/scripts/generate_velocities.py
    """
    xml_tree = ET.parse(xml_path)
    root = xml_tree.getroot()
    return root


def get_regions_from_xml(xml_path: str):
    """
    loads the specified XML and then calculates the regions of the boxes.
    """

    xml = _load_xml(xml_path)
    # uses a dict for simplicity, can be converted into array if needed.
    # key is frame, value is list of centroids
    video_frames = {}
    # iterate through each baboon
    for baboon in xml.iter("track"):
        # iterate through each labeled frame
        for box in baboon.iter("box"):
            frame = int(box.get("frame"))
            # create new list if there is none for this frame
            if video_frames.get(frame) is None:
                video_frames[frame] = []

            xtl = floor(float(box.get("xtl")))
            ytl = floor(float(box.get("ytl")))
            xbr = ceil(float(box.get("xbr")))
            ybr = ceil(float(box.get("ybr")))

            region = (xtl, ytl, xbr, ybr)
            video_frames[frame].append(region)

    return video_frames
