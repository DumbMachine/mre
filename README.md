# mre
### How do thing work here?
Download all the data and keep it in the `data` folder.

Once you have all the data, next step is to extract scenes from the those videos
The following script will extract all the scenes from the media in the `data` folder.
```bash
$ bash extract.scenes.sh
```
Now have all the scenes moved to the `scenes` folder
```bash
$ mkdir scenes
$ bash move.scenes.sh
```
Having all the scenes in there, lets now extract all the `face` information from all the frames
```bash
cd scripts
$ bash process.scenes.sh
```