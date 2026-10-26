### In this file I made a small rendering engine for rendering
### GUI objects easier

import tkinter as tk
import tkinter.font as tkfont
import os

class RenderGUIComponent:
    ### The class for rendering .GUI files 

    def __init__(self, base_dir='./Assets/GUI/', _app=None):
        self.content = {}
        self._app = _app
        self.font = tkfont.nametofont('TkDefaultFont')
        listdir = os.listdir(base_dir)
        for file_ in listdir:
            if file_.endswith('.GUI'):
                self.content[file_.replace('.GUI','')] = open(base_dir+file_,'r').readlines()

    def renderText(self, component_file='', font=[('text_id',12)]):
        for content in self.content[component_file]:
            if content.startswith('TEXT'):
                sp = content.split('=')[1].replace('(','').replace(')','').split(',')
                text,pos,text_id = str(sp[0]),(sp[1],sp[2]),sp[3]
                font_size = 14
                for l in font:
                    if str(l[0]) == str(text_id):
                        font_size = int(l[1])

                tk.Label(self._app, text=text, font=('TkDefaultFont',font_size)).place(relx=pos[0],rely=pos[1])