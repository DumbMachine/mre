"""
Draw the results from .json file and the mp4
"""

import json
import os
import random
from glob import glob
from datetime import timedelta

import cv2
import imageio
from imutils import face_utils, resize

from defaults import PROCESSED_FOLDER, SCENES_FOLDER, CURRENT_DOWNLOAD_PATH

basename = "1-raw-Scene-002"

media_file = os.path.join(SCENES_FOLDER, basename + ".mp4")
json_file = os.path.join(PROCESSED_FOLDER, basename + ".json")


def frame_count_to_timestamp(frame_count, fps):
    """Convert the integer frame count to a timestamp"""
    td = timedelta(seconds=(frame_count / fps))
    return td



def download_youtube_video(url):
    """
    Download the youtube video using youtube-dl
    """
    import subprocess 
    FORMAT = "%(id)s-%(title)s.%(ext)s"
    CMD = f"youtube-dl -o '{CURRENT_DOWNLOAD_PATH}/{FORMAT}' -f 18 '{url}'"
    process_output = subprocess.check_output([CMD], shell=True)
    # check if the download was GOOD
    if not "[download] 100%" in process_output.decode("utf-8"):
        raise FileNotFoundError("The file did not download")

    return url


def extract_scenes(vpath, output_folder="dataprocessing"):
    """
    Download the youtube video using youtube-dl
    """
    import subprocess 
    CMD = f'scenedetect -i "{vpath}" detect-content split-video -o {output_folder}'
    process_output = subprocess.check_output([CMD], shell=True)
    # check if the download was GOOD
    if not "\n" in process_output.decode("utf-8"):
        raise FileNotFoundError("The file did not download")
    return vpath

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


def lip_structure(shape):
    """
    Caculate if the distance between left2mid and right2mid of lips is comparable

    In [28]: dist, dist1
    Out[28]: (5.0, 9.219544457292889)
    In [40]: dist, dist1
    Out[40]: (15.132745950421555, 9.848857801796104)

    """
    import math

    from defaults import MOUTH

    x, y = shape[MOUTH["lip_left"]]
    x1, y1 = shape[MOUTH["lip_mid_top"]]
    x2, y2 = shape[MOUTH["lip_mid_bottom"]]

    l_dist = math.hypot(x2 - x, y2 - y)
    l_dist1 = math.hypot(x1 - x, y1 - y)

    x, y = shape[MOUTH["lip_right"]]
    x1, y1 = shape[MOUTH["lip_mid_top"]]
    x2, y2 = shape[MOUTH["lip_mid_bottom"]]

    r_dist = math.hypot(x2 - x, y2 - y)
    r_dist1 = math.hypot(x1 - x, y1 - y)

    return (l_dist + l_dist1) / (r_dist + r_dist1)

if __name__ == "__main__":
    frame_count = int(cv2.VideoCapture(media_file).get(cv2.CAP_PROP_FRAME_COUNT))
    frame_no = random.randint(0, frame_count)

    viz(frame_no, media_file, json_file)
    print("Check the file at: ./temp.jpg")
