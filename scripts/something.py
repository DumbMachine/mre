import os
import cv2
import dlib
import json
import imutils
import imageio
import face_recognition

from glob import glob
from tqdm import tqdm
from decord import cpu
from decord import VideoReader
from imutils import face_utils

from utils import lip_structure
from defaults import DETECTOR_LOC, PROCESSED_FOLDER


BATCH = 50

def scene_to_json(file):
    """
    Process scenes and extract all the usefull information from it

    """
    basename = os.path.basename(file).split(".")[0]

    # skip if the file already exists
    if os.path.exists(os.path.join(PROCESSED_FOLDER, f"{basename}.json")):
        print(f"Skipping file {basename} as it already exists")
        return


    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor(DETECTOR_LOC)

    vr = VideoReader(file, ctx=cpu(0))

    file_features = []

    if len(vr) < BATCH:
        frames = vr.get_batch(range(len(vr))).asnumpy()
        face_features = batch_frame_to_json_lips(frames, detector, predictor)
        file_features.extend(face_features)
    else:
        start = 0 
        for end in tqdm(range(BATCH, len(vr), BATCH)):
            frames = vr.get_batch(range(start, end)).asnumpy()
            start = end

            face_features = batch_frame_to_json_lips(frames, detector, predictor)
            file_features.extend(face_features)

        if end < len(vr):
            # processing the last batch of frames
            frames = vr.get_batch(range(end, len(vr))).asnumpy()
            face_features = batch_frame_to_json_lips(frames, detector, predictor)
            file_features.extend(face_features)

    ### getting some stats about the face scans
    ## check for only faces (face_rec)
    # _no_faces_detected = [1 for _ in file_features if len(_) != 0]
    # no_faces_detected = sum(_no_faces_detected) / len(file_features)

    ## check for faces and lips (dlib)
    _no_faces_detected = [1 for _ in file_features if len(_["rects"]) != 0]
    no_faces_detected = sum(_no_faces_detected) / len(file_features)

    save_features = {
        # ratio of # of frames with detection and total frames
        "face2frame": no_faces_detected,
        "features": file_features,
    }

    json.dump(save_features, open(os.path.join(PROCESSED_FOLDER, f"{basename}.json"), "w"))

def batch_frame_to_json(frames, detector, predictor):
    """
    Random
    """
    batch_of_face_locations = face_recognition.batch_face_locations([frame for frame in frames], number_of_times_to_upsample=0)

    return batch_of_face_locations

def batch_frame_to_json_lips(frames, detector, predictor):
    """
    Random
    """
    file_features = []

    for frame in tqdm(frames):
        frame_feature = {}
        frame = imutils.resize(frame, width=500)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        rects = detector(gray, 1)

        frame_feature["shape"] = []
        frame_feature["lips"] = []
        frame_feature["rects"] = [face_utils.rect_to_bb(rect) for rect in rects]

        for (i, rect) in enumerate(rects):
            shape = predictor(gray, rect)
            shape = face_utils.shape_to_np(shape)

            (x, y, w, h) = face_utils.rect_to_bb(rect)
            # face_crop = frame[y : y + h, x : x + w]
            # faces.append(face_crop)

            shape = shape.tolist()
            frame_feature["shape"].append(shape)
            frame_feature["lips"].append(lip_structure(shape))

        file_features.append(frame_feature)

    return file_features


if __name__ == "__main__":
    import sys

    file = "/home/dumbmachine/experiments/mre/scenes/FIRST ARABIC VLOG _ اول ڤلوق بالعربي-X0LfSVTHKYE-Scene-003.mp4"
    scene_to_json(file)