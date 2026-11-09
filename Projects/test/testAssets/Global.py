
### MADE BY EGameMaker GAME ENGINE
### OPEN-SOURCE ENGINE
### https://github.com/MACsepehri/EGameMaker

import json

def get_json(index, path="testAssets/Global.json"):
    data = json.load(open(path,"r"))
    return data[index]

def set_state(value):
    global states
    with open("testAssets/Global.json","r") as r_file:
        data = json,load(r_file)
        data["states"] = value
    with open("testAssets/Global.json","w") as w_file:
        json.dump(data,w_file)
    states = value

fullscreen = get_json("fullscreen")
base_window_size = get_json("base.window.size")
fps = get_json("fps")
title = get_json("title")
background = get_json("background")
states = get_json("states")

