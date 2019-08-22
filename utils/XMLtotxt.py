#import lxml package
from lxml import etree
#set and parse xml file
input_file = 'input_mp4.xml'
root = etree.parse(input_file).getroot()

#set other path variable
#folder to send output txt files to:
outputfolder = "groundtruth_txt/"

#iterate through all the frames you want to get ground truth measurements for
#set which frames by changing range values
for num in range(81,111,1):
#go through all of the tracked baboons, and find any instance in which the frame is equal to frame selected (ie 81)
    for trackedbaboon in root.findall(".//box[@frame='{:d}']".format(num)):
        index = []
        left = trackedbaboon.get('xtl')
        top = trackedbaboon.get('ytl')
        width = str(abs(float(trackedbaboon.get('xtl')) -  float(trackedbaboon.get('xbr'))))
        height =  str(abs(float(trackedbaboon.get('ytl')) -  float(trackedbaboon.get('ybr'))))
        index.append(["baboon", left, top, width, height])

        outputXML = outputfolder+"frame"+str(num)+".txt"
        with open(outputXML, "a+") as txt_file: #+ will create a file with the right name, if it doesn't exist
            for line in index:
                txt_file.write(" ".join(line) + "\n")
