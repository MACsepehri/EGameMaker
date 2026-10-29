
### MADE BY EGameMaker GAME ENGINE
### OPEN-SOURCE ENGINE
### https://github.com/MACsepehri/EGameMaker

import json

def get_json(index, path="testAssets/Global.json"):
    data = json.load(open(path,"r"))
    return data[index]

fullscreen = get_json("fullscreen")
base_window_size = get_json("base.window.size")
fps = get_json("fps")
title = get_json("title")
background = get_json("background")
states = get_json("states")

