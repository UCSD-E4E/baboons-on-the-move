"""
module for loading from labeled data.
"""
from xml.etree import ElementTree as ET
import argparse


def _load_xml(xml_path: str):
    """
    loads XML data into python using etree package
    copied from /src/scripts/generate_velocities.py
    """
    xml_tree = ET.parse(xml_path)
    root = xml_tree.getroot()
    return root


def _get_centroid(box_element: ET.Element):
    """
    returns centroid to be the point between top left and bottom right points
    copied then modified from /src/scripts/generate_velocities.py
    """
    xtl = float(box_element.get("xtl"))
    ytl = float(box_element.get("ytl"))
    xbr = float(box_element.get("xbr"))
    ybr = float(box_element.get("ybr"))
    centroid_x = xtl + ((xbr - xtl) / 2)
    centroid_y = ytl + ((ybr - ytl) / 2)
    diameter = xbr - xtl
    return centroid_x, centroid_y, diameter


def get_centroids_from_xml(xml_path: str):
    """
    loads the specified XML and then calculates the centroids of the boxes.
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

            centroid = _get_centroid(box)
            centroidx = centroid[0]
            centroidy = centroid[1]
            diameter = centroid[2]
            # stores each centroid in the form ((float)x, (float)y, (float)diameter)
            video_frames[frame].append((centroidx, centroidy, diameter))

    return video_frames


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse labeled data XML by frame")
    parser.add_argument(
        "XML_file_path", metavar="path", type=str, help="path to the XML file"
    )
    args = parser.parse_args()
    centroidsByFrame = get_centroids_from_xml(args.XML_file_path)
    print(centroidsByFrame)
