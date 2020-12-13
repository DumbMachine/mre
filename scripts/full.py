"""
Independent full thing processor
MUTLI-PERSON processing: https://www.youtube.com/watch?v=BNQcoGKPHsM

"""
import os
import sys
import json
import shutil

from glob import glob
from tqdm import tqdm
from datetime import timedelta
from decord import VideoReader, cpu
from defaults import CURRENT_DOWNLOAD_PATH
from something import scene_to_json
from moviepy.editor import VideoFileClip
from utils import extract_scenes, download_youtube_video, frame_count_to_timestamp

YOUTUBE_URL = sys.argv[1]
CURRENT_DOWNLOAD_PATH = "dataprocessing"
marked_files_path = "markedFiles.json"

if not os.path.exists(CURRENT_DOWNLOAD_PATH):
    os.makedirs(CURRENT_DOWNLOAD_PATH)

try:
    # download the video
    download_youtube_video(YOUTUBE_URL)

    # create segments of the video
    # always only one file  for processing
    vpath = glob(os.path.join(CURRENT_DOWNLOAD_PATH, "*mp4"))[0]
    extract_scenes(vpath)

    # processing the scenes
    scene_files = glob(os.path.join(CURRENT_DOWNLOAD_PATH, "*Scene*.mp4"))
    for path in scene_files:
        scene_to_json(path, outfolder=CURRENT_DOWNLOAD_PATH)

    # parsing the scenes
    processed_files = glob(os.path.join(CURRENT_DOWNLOAD_PATH, "*Scene*.json"))
    for file_path in tqdm(processed_files, disable=False):
        features = json.load(open(file_path, "r"))
        scene_path = os.path.join(
            f"{CURRENT_DOWNLOAD_PATH}",
            os.path.basename(file_path).split(".")[0] + ".mp4",
        )
        # check if the scene in present
        if scene_path in scene_files:
            scene = VideoReader(scene_path, ctx=cpu(0))
            fps = scene.get_avg_fps()
            # extracting all the face utterances from this scene
            # taking empty frames as the breakpoint for smaller scenes
            indices = [
                i
                for i, _ in enumerate(features["features"])
                if _ == {"shape": [], "lips": [], "rects": []}
            ]
            indices = [0] + indices + [len(scene)]
            breakpoints = [
                (indices[i], indices[i + 1]) for i in range(0, len(indices) - 1)
            ]
            breakpoints = [
                _breakpoint
                for _breakpoint in breakpoints
                if _breakpoint[0] + 1 != _breakpoint[1]
                and _breakpoint[0] != _breakpoint[1]
            ]

            for itr, (scene_start, scene_end) in enumerate(breakpoints):
                # validate the scene
                if scene_end - scene_start > 20:
                    # convert this to iterations
                    frames = scene.get_batch(range(scene_start, scene_end)).asnumpy()
                    start_time, end_time = (
                        frame_count_to_timestamp(scene_start, fps),
                        frame_count_to_timestamp(scene_end, fps),
                    )
                    # extract the clip and save it in the final folder
                    if not os.path.exists(CURRENT_DOWNLOAD_PATH):
                        os.makedirs(CURRENT_DOWNLOAD_PATH, exist_ok=True)

                    clip = VideoFileClip(scene_path).subclip(
                        str(start_time), str(end_time)
                    )

                    clip.write_videofile(
                        os.path.join(
                            CURRENT_DOWNLOAD_PATH,
                            f"start_time-{scene_start}-start_end-{scene_end}-"
                            + os.path.basename(scene_path),
                        ),
                        logger=None,
                    )

    # # now move all the files to the proper locations
    processed_mp4s = glob(os.path.join(CURRENT_DOWNLOAD_PATH, "start_time*.mp4"))
    for file in processed_mp4s:
        shutil.move(
            file,
            os.path.join("/home/ratkum/mre/processed_scenes", os.path.basename(file)),
        )
    for file in scene_files:
        shutil.move(
            file,
            os.path.join("/home/ratkum/mre/seen_scenes", os.path.basename(file)),
        )
    for file in processed_files:
        shutil.move(
            file,
            os.path.join("/home/ratkum/mre/processed", os.path.basename(file)),
        )
    shutil.move(
        vpath,
        os.path.join("/home/ratkum/mre/data", os.path.basename(vpath)),
    )

    # make sure the current processing data folder is now empty
    for file in glob(CURRENT_DOWNLOAD_PATH + "/*"):
        shutil.rmtree(CURRENT_DOWNLOAD_PATH)

except Exception as e:
    # Store this sad information in a `json` file
    marked_files = []
    if os.path.isfile(marked_files_path):
        marked_files = json.load(open(marked_files_path, "r"))

    marked_files = marked_files + [YOUTUBE_URL]
    json.dump(marked_files, open(marked_files_path, "w"))
