
### MADE BY EGameMaker GAME ENGINE
### OPEN-SOURCE ENGINE
### https://github.com/MACsepehri/EGameMaker

import json

with open("testAssets/Global.json","r") as file:
    content = json.load(file)

FULLSCREEN = content["fullscreen"]
BASE_WINDOW_SIZE = (content["base.window.size"][0],content["base.window.size"][1])
FPS = content["fps"]
BACKGROUND_COLOR = (content["background"][0],content["background"][1],content["background"][2])
WINDOW_TITLE = content["title"]