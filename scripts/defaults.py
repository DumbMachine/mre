# all the main folders
DATA_FOLDER = "../data"
SCENES_FOLDER = "../scenes"
PROCESSED_FOLDER = "../processed"

# place for some files
DETECTOR_LOC = "../shape_predictor_68_face_landmarks.dat"

DLIB_DESCRIPTORS = {
    "all": [0, 68],
    "jaw": [0, 17],
    "right eyebrow": [17, 22],
    "left eyebrow": [22, 27],
    "nose": [27, 35],
    "right eye": [36, 42],
    "left eye": [42, 48],
    "mouth": [48, 68],
}

MOUTH = {"lip_left": 49, "lip_right": 55, "lip_mid_top": 63, "lip_mid_bottom": 67}
