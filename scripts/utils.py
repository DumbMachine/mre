"""
Draw the results from .json file and the mp4
"""

import os
import cv2
import json
import random
import imageio
from imutils import face_utils, resize

from defaults import SCENES_FOLDER, PROCESSED_FOLDER
from glob import glob

basename = "1-raw-Scene-002"

media_file = os.path.join(SCENES_FOLDER, basename + ".mp4")
json_file = os.path.join(PROCESSED_FOLDER, basename + ".json")


def viz(frame_no, media_file, json_file):
    """Draw face on the image using the information from rect (dlib returned)"""
    file_features = json.load(open(json_file, "r"))
    for itr, image in enumerate(imageio.get_reader(media_file)):
        if frame_no == itr:
            frame = image
            frame_feature = file_features["features"][itr]

    frame = resize(frame, width=500)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    for rect, shape in zip(frame_feature["rects"], frame_feature["shape"]):
        x, y, w, h = rect
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 255, 0), 2)

        for (x, y) in shape:
            cv2.circle(frame, (x, y), 1, (0, 0, 255), -1)

    cv2.imwrite("temp.jpg", frame)


def get_lip_height(lip):
    import math

    sum = 0
    for i in [2, 3, 4]:
        # distance between two near points up and down
        distance = math.sqrt(
            (lip[i][0] - lip[12 - i][0]) ** 2 + (lip[i][1] - lip[12 - i][1]) ** 2
        )
        sum += distance
    return sum / 3


def get_mouth_height(top_lip, bottom_lip):
    import math

    sum = 0
    for i in [8, 9, 10]:
        # distance between two near points up and down
        distance = math.sqrt(
            (top_lip[i][0] - bottom_lip[18 - i][0]) ** 2
            + (top_lip[i][1] - bottom_lip[18 - i][1]) ** 2
        )
        sum += distance
    return sum / 3


def check_mouth_open(top_lip, bottom_lip):
    top_lip_height = get_lip_height(top_lip)
    bottom_lip_height = get_lip_height(bottom_lip)
    mouth_height = get_mouth_height(top_lip, bottom_lip)

    # if mouth is open more than lip height * ratio, return true.
    ratio = 0.5
    if mouth_height > min(top_lip_height, bottom_lip_height) * ratio:
        return True
    else:
        return False


frame_count = int(cv2.VideoCapture(media_file).get(cv2.CAP_PROP_FRAME_COUNT))
frame_no = random.randint(0, frame_count)

viz(frame_no, media_file, json_file)
print("Check the file at: ./temp.jpg")
