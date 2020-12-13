import os
import json

CMD = "youtube-dl --download-archive downloaded.txt -f 18 {item}"

langs = json.load(open("./data.json", "r"))

for _ in langs:
    ids = langs[_]
    for id in ids:
        os.system(CMD.format(item=id))