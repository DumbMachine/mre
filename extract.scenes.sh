cd scenes
for f in ../data/*.mp4; do
    scenedetect -i "$f" detect-content split-video
done