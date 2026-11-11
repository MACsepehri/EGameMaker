
### MADE BY EGameMaker GAME ENGINE
### OPEN-SOURCE ENGINE
### https://github.com/MACsepehri/EGameMaker

import json

def get_json(index, path="testAssets/Global.json"):
    data = json.load(open(path,"r"))
    return data[index]

def set_state(value):
    ### switch the game to another state at runtime, the running game
    ### picks up the new state on the next frame
    global current_state

    if value not in states:
        print('set_state: unknown state "' + str(value) + '", available states: ' + str(list(states)))
        return

    current_state = value

fullscreen = get_json("fullscreen")
base_window_size = get_json("base.window.size")
fps = get_json("fps")
title = get_json("title")
background = get_json("background")
try:
    states = get_json("states")
except KeyError:
    states = {}
current_state = next(iter(states), 'main')
try:
    fonts = get_json("fonts")
except KeyError:
    fonts = {}
try:
    texts = get_json("texts")
except KeyError:
    texts = {}
try:
    images = get_json("images")
except KeyError:
    images = {}
try:
    image_components = get_json("image_components")
except KeyError:
    image_components = {}

 