import os
import json

from glob import glob
from tqdm import tqdm
from defaults import CHECKED_FOLDER, PROCESSED_FOLDER


"""
X -> Having multiple peeps
"""

# The conditions each `GOOD` sample must have
NOS_FACES = 1
FACE2FRAME = 0.80
MIN_FRAMES = 100

def check_scene_json(filename):
    """
    Check if the `json` information created for the scene is valid for us
    """
    scene_info = json.load(open(filename, "r"))
    

    if scene_info["face2frame"] >= FACE2FRAME and len(scene_info["features"]) <= MIN_FRAMES:
        basename = os.path.basename(filename).split(".")[0]
        os.rename(filename, os.path.join(CHECKED_FOLDER, basename))



if __name__ == "__main__":
    files = glob(PROCESSED_FOLDER+"/*")

    for filename in tqdm(files):
        check_scene_json(filename)