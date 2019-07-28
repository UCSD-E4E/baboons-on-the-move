import cv2
import sys

(major_ver, minor_ver, subminor_ver) = (cv2.__version__).split('.')

video_fps = 20
if( len(sys.argv) < 2):
    print("Usage: python3 " + sys.argv[0] + " [infilename]")
    exit()

infilename = sys.argv[1]
print(infilename)
outfilename = "output_" + infilename

if __name__ == '__main__' :

    # Set up tracker.
    # Instead of MIL, you can also use

    tracker_types = ['BOOSTING', 'MIL','KCF', 'TLD', 'MEDIANFLOW', 'GOTURN', 'MOSSE', 'CSRT']
    #tracker_type = tracker_types[2]
    '''
    if int(minor_ver) < 3:
        pass
        #tracker = cv2.Tracker_create(tracker_type)
    else:
        if tracker_type == 'BOOSTING':
            tracker = cv2.TrackerBoosting_create()
        if tracker_type == 'MIL':
            tracker = cv2.TrackerMIL_create()
        if tracker_type == 'KCF':
            tracker = cv2.TrackerKCF_create()
        if tracker_type == 'TLD':
            tracker = cv2.TrackerTLD_create()
        if tracker_type == 'MEDIANFLOW':
            tracker = cv2.TrackerMedianFlow_create()
        if tracker_type == 'GOTURN':
            tracker = cv2.TrackerGOTURN_create()
        if tracker_type == 'MOSSE':
            tracker = cv2.TrackerMOSSE_create()
        if tracker_type == "CSRT":
            tracker = cv2.TrackerCSRT_create()
    '''
    # populates trackers dict with all types of trackers
    trackers = {}
    trackers["BOOSTING"] = cv2.TrackerBoosting_create()
    trackers["MIL"] = cv2.TrackerMIL_create()
    trackers["KCF"] = cv2.TrackerKCF_create()
    trackers["TLD"] = cv2.TrackerTLD_create()
    trackers["MEDIANFLOW"] = cv2.TrackerMedianFlow_create()
    trackers["MOSSE"] = cv2.TrackerMOSSE_create()
    trackers["CSRT"] = cv2.TrackerCSRT_create()
    #trackers = cv2.TrackerGOTURN_create()

    tracker = cv2.TrackerBoosting_create()

    # Read video
    video = cv2.VideoCapture(infilename)

    # Write video
    fourcc = cv2.VideoWriter_fourcc('D', 'I', 'V', 'X')
    out = cv2.VideoWriter(outfilename, fourcc, video_fps, (int(video.get(3)), int(video.get(4))), True)

    # Exit if video not opened.
    if not video.isOpened():
        print("Could not open video")
        sys.exit()

    # Read first frame.
    ok, frame = video.read()
    if not ok:
        print('Cannot read video file')
        sys.exit()

    # Define an initial bounding box
    bbox = (287, 23, 86, 320)

    # Uncomment the line below to select a different bounding box
    bbox = cv2.selectROI(frame, False)

    # Initialize tracker with first frame and bounding box
    #ok = tracker.init(frame, bbox)
    for tracker_type in trackers:
        trackers[tracker_type].init(frame, bbox)

    while True:
        # Read a new frame
        ok, frame = video.read()
        if not ok:
            break

        # Start timer
        timer = cv2.getTickCount()

        # Update tracker
        #ok, bbox = tracker.update(frame)
        for tracker_type in trackers:
            ok, bbox = trackers[tracker_type].update(frame)

            # Calculate Frames per second (FPS)
            #fps = cv2.getTickFrequency() / (cv2.getTickCount() - timer);

            # Draw bounding box
            if ok:
                # Tracking success
                p1 = (int(bbox[0]), int(bbox[1]))
                p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
                cv2.rectangle(frame, p1, p2, (255,0,0), 2, 1)
                cv2.putText(frame, tracker_type, p1, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)
            else :
                # Tracking failure
                cv2.putText(frame, "Tracking failure detected", (100,80), cv2.FONT_HERSHEY_SIMPLEX, 0.75,(0,0,255),2)

        # Display tracker type on frame
        #cv2.putText(frame, tracker_type + " Tracker", (100,20), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (50,170,50),2);

        # Display FPS on frame
        #cv2.putText(frame, "FPS : " + str(int(fps)), (100,50), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (50,170,50), 2);

        # Display result
        cv2.imshow("Tracking", frame)

        # Write output
        out.write(frame)

        # Exit if ESC pressed
        k = cv2.waitKey(1) & 0xff
        if k == 27 : break

video.release()
out.release()
cv2.destroyAllWindows()
