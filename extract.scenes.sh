for f in data/*-raw.mp4; do
    scenedetect -i "$f" detect-content split-video
done