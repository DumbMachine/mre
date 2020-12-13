"""
Extract all small utterances from the processed videos

"""
import os
import cv2
import json
import shutil

# import moviepy
# import imageio

from glob import glob
from tqdm import tqdm
from datetime import timedelta
from decord import VideoReader, cpu
from moviepy.editor import VideoFileClip
from defaults import FSCENES_FOLDER, DATA_FILE_PATH, SCENES_FOLDER, PROCESSED_FOLDER

marked_files_path = "/home/ratkum/mre/pre-markedFiles.json"
scene_files = [
    os.path.join("/home/ratkum/mre/scenes", os.path.basename(path).replace(".json", ""))
    for path in glob(f"{SCENES_FOLDER}/*")
]
processed_files = [path for path in glob(f"{PROCESSED_FOLDER}/*")]


def frame_count_to_timestamp(frame_count, fps):
    """Convert the integer frame count to a timestamp"""
    td = timedelta(seconds=(frame_count / fps))
    return td


def get_lanuage_ids(fpath):
    """Read the data file and generate dict of language keys and the corresponding youtube ids"""
    pass


for file_path in tqdm(processed_files, disable=False):
    try:
        features = json.load(open(file_path, "r"))
        scene_path = os.path.join(
            "/home/ratkum/mre/scenes",
            os.path.basename(file_path).split(".")[0] + ".mp4",
        )
        # check if the scene in present
        if scene_path in scene_files and not os.path.isfile(
            os.path.join("/home/ratkum/mre/seen_scenes", os.path.basename(scene_path))
        ):
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
                if scene_end - scene_start > fps:
                    # convert this to iterations
                    frames = scene.get_batch(range(scene_start, scene_end)).asnumpy()
                    start_time, end_time = (
                        frame_count_to_timestamp(scene_start, fps),
                        frame_count_to_timestamp(scene_end, fps),
                    )
                    # extract the clip and save it in the final folder
                    if not os.path.exists(FSCENES_FOLDER):
                        os.makedirs(FSCENES_FOLDER, exist_ok=True)

                    clip = VideoFileClip(scene_path).subclip(
                        str(start_time), str(end_time)
                    )

                    clip.write_videofile(
                        os.path.join(
                            FSCENES_FOLDER,
                            f"start_time-{scene_start}-start_end-{scene_end}-"
                            + os.path.basename(scene_path),
                        )
                    )

                shutil.move(
                    scene_path,
                    os.path.join(
                        "/home/ratkum/mre/seen_scenes", os.path.basename(scene_path)
                    ),
                )
    except Exception as e:
        # Store this sad information in a `json` file
        marked_files = []
        if os.path.isfile(marked_files_path):
            marked_files = json.load(open(marked_files_path, "r"))

        marked_files = marked_files + [file_path]
        json.dump(marked_files, open(marked_files_path, "w"))


def write_video(outpath, video_itr, fps, verbose, **kwargs):
    """
    Read frames in iterations
    """
    print(verbose)
    # writer = imageio.get_writer(outpath, fps=fps, ffmpeg_log_level="error", **kwargs)
    return outpath


def draw_on_image(frame, frame_feature):
    frame = resize(frame, width=500)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    for rect, shape in zip(frame_feature["rects"], frame_feature["shape"]):
        x, y, w, h = rect
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 255, 0), 2)

        for (x, y) in shape:
            cv2.circle(frame, (x, y), 1, (0, 0, 255), -1)


def get_fps(vpath):
    """
    Get the fps from the video file using cv2
    """
    invideo = cv2.VideoCapture(vpath)
    fps = invideo.get(cv2.CAP_PROP_FPS)
    return fps


def frames_to_timecode(total_frames, frame_rate, drop=False):
    """
    Method that converts frames to SMPTE timecode.

    :param total_frames: Number of frames
    :param frame_rate: frames per second
    :param drop: true if time code should drop frames, false if not
    :returns: SMPTE timecode as string, e.g. '01:02:12:32' or '01:02:12;32'
    """
    if drop and frame_rate not in [29.97, 59.94]:
        raise NotImplementedError(
            "Time code calculation logic only supports drop frame "
            "calculations for 29.97 and 59.94 fps."
        )
    fps_int = int(round(frame_rate))

    if drop:
        FRAMES_IN_ONE_MINUTE = 1800 - 2

        FRAMES_IN_TEN_MINUTES = (FRAMES_IN_ONE_MINUTE * 10) - 2

        ten_minute_chunks = total_frames / FRAMES_IN_TEN_MINUTES
        one_minute_chunks = total_frames % FRAMES_IN_TEN_MINUTES

        ten_minute_part = 18 * ten_minute_chunks
        one_minute_part = 2 * ((one_minute_chunks - 2) / FRAMES_IN_ONE_MINUTE)

        if one_minute_part < 0:
            one_minute_part = 0

        # add extra frames
        total_frames += ten_minute_part + one_minute_part

        # for 60 fps drop frame calculations, we add twice the number of frames
        if fps_int == 60:
            total_frames = total_frames * 2

        # time codes are on the form 12:12:12;12
        smpte_token = ";"

    else:
        # time codes are on the form 12:12:12:12
        smpte_token = ":"

    # now split our frames into time code
    hours = int(total_frames / (3600 * fps_int))
    minutes = int(total_frames / (60 * fps_int) % 60)
    seconds = int(total_frames / fps_int % 60)
    frames = int(total_frames % fps_int)

    return "%02d:%02d:%02d%s%02d" % (hours, minutes, seconds, smpte_token, frames)
