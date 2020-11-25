import os
import cv2
import sys
import dlib
import json
import imutils
import imageio
import numpy as np

from defaults import DETECTOR_LOC, PROCESSED_FOLDER
from tqdm import tqdm
from glob import glob
from imutils import face_utils


# file = "/home/dumbmachine/experiment/mre/scenes/1-raw-Scene-001.mp4"
file = sys.argv[1]
basename = os.path.basename(file).split(".")[0]

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(DETECTOR_LOC)
frame_count = int(cv2.VideoCapture(file).get(cv2.CAP_PROP_FRAME_COUNT))

file_features = []

with tqdm(total=frame_count) as progress:
    progress.set_description(basename)
    for frame in imageio.get_reader(file):
        frame_feature = {}
        frame = imutils.resize(frame, width=500)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        rects = detector(gray, 1)

        frame_feature["shape"] = []
        frame_feature["rects"] = [face_utils.rect_to_bb(rect) for rect in rects]

        for (i, rect) in enumerate(rects):
            shape = predictor(gray, rect)
            shape = face_utils.shape_to_np(shape)

            (x, y, w, h) = face_utils.rect_to_bb(rect)
            face_crop = frame[y : y + h, x : x + w]
            # faces.append(face_crop)

            frame_feature["shape"].append(shape.tolist())

        file_features.append(frame_feature)

        progress.update(1)

# getting some stats about the face scans
_no_faces_detected = [1 for _ in file_features if len(_["rects"]) != 0]
no_faces_detected = sum(_no_faces_detected) / len(file_features)

save_features = {
    # ratio of # of frames with detection and total frames
    "face2frame": no_faces_detected,
    "features": file_features,
}

json.dump(save_features, open(os.path.join(PROCESSED_FOLDER, f"{basename}.json"), "w"))
