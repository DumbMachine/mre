import sys
from something import scene_to_json
from glob import glob
from defaults import SCENES_FOLDER

files = glob(SCENES_FOLDER+"/*")


for file in sorted(files):
    scene_to_json(file)