from xml.etree import ElementTree as ET
import argparse
# loads XML data into python using etree package
# copied from /src/scripts/generate_velocities.py

def loadXML(xmlPath):
    XMLtree = ET.parse(xmlPath)
    root = XMLtree.getroot()
    return root

# returns centroid to be the point between top left and bottom right points
# copied from /src/scripts/generate_velocities.py
def getCentroid(boxElement):
    xtl = float(boxElement.get("xtl"))
    ytl = float(boxElement.get("ytl"))
    xbr = float(boxElement.get("xbr"))
    ybr = float(boxElement.get("ybr"))
    centroid_x = xtl + ((xbr - xtl) / 2)
    centroid_y = ytl + ((ybr - ytl) / 2)
    return centroid_x, centroid_y

def listCentroidsFromXML(xmlPath):
    XML = loadXML(xmlPath)
    # uses a dict for simplicity, can be converted into array if needed.
    # key is frame, value is list of centroids
    videoFrames = {}
    #iterate through each baboon 
    for baboon in XML.iter("track"):
        id = int(baboon.get("id"))
        #iterate through each labeled frame
        for box in baboon.iter("box"):
            frame = int(box.get("frame"))
            # create new list if there is none for this frame
            if videoFrames.get(frame) is None:
                videoFrames[frame] = []

            centroid = getCentroid(box)
            centroidx = centroid[0]
            centroidy = centroid[1]
            # stores each centroid in the form {(int)id, (float)x, (float)y}
            videoFrames[frame].append({'id': id, 'x': centroidx, 'y': centroidy})

    return videoFrames

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Parse labeled data XML by frame')
    parser.add_argument('XML_file_path', metavar='path', type=str,
                            help='path to the XML file')
    args = parser.parse_args()
    centroidsByFrame = listCentroidsFromXML(args.XML_file_path)
    print(centroidsByFrame)

