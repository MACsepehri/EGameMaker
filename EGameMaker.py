
### FREE AND OPEN-SOURCE
### EGameMaker
### ---------------------------------------------

import os
import sys
import pickle
import tkinter as tk
import subprocess as sub
from tkinter import simpledialog
from tkinter import messagebox as tk_alert
from Assets.GUI.Render.RenderGUIComponent import RenderGUIComponent


render_gui = RenderGUIComponent()


class EGameMaker(tk.Tk):
    ### main class of GUI

    def __init__(self):
        super().__init__()
        self.geometry(f"{self.winfo_screenwidth()}x{self.winfo_screenheight()}")
        self.title('EGameMaker : Game maker engine')
        self.current_page = 'MainPage'
        self.components = []
        self.current_project = None
        self.after(100, self.maximize)
        render_gui.init_app(self)
        render_gui.init_font()
        self.create_new_project()
        self.create_project_action()
        self.create_inproject_action()

        projects = os.listdir('Projects')
        if len(projects) < 1:
            render_gui.addTextComponent('MainPage.GUI', "You don't have any projects...", ('0.02', '0.15'), '02')
        else:
            self.show_projects(projects)

    def maximize(self):
        try:
            self.state('zoomed')
            if self.state() == 'zoomed':
                self.resizable(False, False)
                return
        except tk.TclError:
            pass

        try:
            self.wm_attributes('-zoomed', True)
            if self.state() == 'zoomed':
                self.resizable(False, False)
                return
        except tk.TclError:
            pass

        self.update_idletasks()
        self.geometry(f'{self.winfo_screenwidth()}x{self.winfo_screenheight()}+0+0')
        self.resizable(False, False)

    def create_new_project(self):
        # add pkl object func to create new project
        path = 'Assets/Action/MainPage/03.pkl'

        os.makedirs(os.path.dirname(path), exist_ok=True)

        with open(path, 'wb') as file:
            pickle.dump(create_project, file)

        with open(path, 'rb') as file:
            func = pickle.load(file)

        func(self)

    def create_project_action(self):
        # add pkl object func to create new project
        path = 'Assets/Action/NewProject/03.pkl'

        os.makedirs(os.path.dirname(path), exist_ok=True)

        with open(path, 'wb') as file:
            pickle.dump(save_project_action, file)

    def create_inproject_action(self):
        # add pkl object func to run the currently open project
        path = 'Assets/Action/InProject/03.pkl'

        os.makedirs(os.path.dirname(path), exist_ok=True)

        with open(path, 'wb') as file:
            pickle.dump(run_current_project, file)

    def move_run_button_to_bottom(self):
        # pin the InProject "Run" button near the bottom edge.
        # the .GUI renderer places by rely (0..1 fraction of window height),
        # so "window height - 0.1" == 0.9
        y_rel = 1.0 - 0.1
        render_gui.addButtonComponent(
            'InProject.GUI',
            text='Run',
            pos=('0.02', f'{y_rel:.4f}'),
            id='03',
            action_path='InProject/03.pkl',
        )

    def show_projects(self, projects):
        # user has projects -> remove the "no projects" text and list them
        render_gui.removeTextComponent('MainPage.GUI', '02')

        for index, name in enumerate(projects):
            if not os.path.isdir(os.path.join('Projects', name)):
                continue

            action_path = f'MainPage/{name}.pkl'
            full_path = os.path.join('Assets/Action', action_path)

            os.makedirs(os.path.dirname(full_path), exist_ok=True)

            with open(full_path, 'wb') as file:
                pickle.dump(OpenProjectAction(name), file)

            render_gui.addButtonComponent(
                'MainPage.GUI',
                text=name,
                pos=('0.02', f'{0.35 + index * 0.07:.2f}'),
                id=name,
                action_path=action_path,
            )

    def change_page(self, new_state, text_font=None):
        for component in self.components:
            if component.winfo_exists():
                component.destroy()

        self.components.clear()

        self.current_page = new_state
        render_gui.render(self.current_page, text_font or [])

        self.components = self.winfo_children()

    def run(self):
        self.change_page('MainPage', [('01', 30)])
        self.maximize()
        self.mainloop()


def create_project(app):
    app.change_page('NewProject')


class OpenProjectAction:
    def __init__(self, project_name):
        global game_name

        self.project_name = project_name
        self.create_directory()


    def __call__(self, app):
        app.current_project = self.project_name
        game_name = app.current_project
        render_gui.addTextComponent(
            'InProject.GUI',
            text=self.project_name,
            pos=('0.02', '0.08'),
            id='01',
        )
        app.move_run_button_to_bottom()
        app.change_page('InProject', [('01', 30)])

    def create_directory(self):
        path = "Assets/Action/InProject/007.pkl"

        os.makedirs(os.path.dirname(path), exist_ok=True)

        if not os.path.isfile(path) or os.path.getsize(path) == 0:
            with open(path, "wb") as file:
                pickle.dump(get_directory, file)
            


def run_current_project(app):
    project_name = getattr(app, 'current_project', None)

    if not project_name:
        tk_alert.showerror('Error', 'No project is open.')
        return

    run_project(project_name)


def save_project_action(app):
    entry = render_gui.getInput('NewProject', '02')
    name = entry.get()
    already_existed = (
        bool(name.strip()) and os.path.isdir(os.path.join('Projects', name))
    )

    save_project(entry)

    if (
        name.strip()
        and not already_existed
        and os.path.isdir(os.path.join('Projects', name))
    ):
        render_gui.addTextComponent(
            'InProject.GUI',
            text=name.strip(),
            pos=('0.02', '0.08'),
            id='01',
        )
        app.current_project = name.strip()
        app.move_run_button_to_bottom()
        app.change_page('InProject', [('01', 30)])

def save_project(inp):
    ### IMPORTANT : DON'T CHANGE THIS FUNCTION!
    ###  - IN THIS FUNCTION BASE OF GAME WILL CREATE

    global game_name

    projectName = inp.get()
    if projectName.strip() == '':
        tk_alert.showerror('Error','Invalid project name.')
        return
    else:
        for listdir in os.listdir('Projects'):
            if listdir.lower().strip() == projectName.lower().strip():
                tk_alert.showerror('Error','This project is already exist.')
                return
    
    projectPath = f'Projects/{projectName}'

    game_name = projectName

    ### Creating project structure
    os.mkdir(projectPath)
    os.mkdir(projectPath+f'/{projectName}Assets')
    os.mkdir(projectPath+f'/{projectName}Assets/Images')
    

    ### Saving basics
    with open(projectPath+f'/{projectName}.py', 'w') as file:
        file.write(f'''
### MADE BY EGameMaker GAME ENGINE
### OPEN-SOURCE ENGINE
### https://github.com/MACsepehri/EGameMaker

import pygame,sys
import {projectName}Assets.Global as Global

pygame.init()

def initialization():
    if (Global.fullscreen):
        win = pygame.display.set_mode((0,0),pygame.FULLSCREEN)
    else:
        win = pygame.display.set_mode(Global.base_window_size)
    pygame.display.set_caption(Global.title)
    return win

def app():
    win = initialization()
    clock = pygame.time.Clock()

    

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)

        win.fill(Global.background)
        pygame.display.update()
        clock.tick(Global.fps)

if __name__ == "__main__":
    app()

''')

    with open(projectPath+f'/{projectName}Assets/Global.json', 'w') as globalFile:
            globalFile.write('''
{
    "fullscreen":false,
    "base.window.size":[500,500],
    "fps":60,
    "title":"'''+projectName+'''",
    "background":[255,255,255],

    "states": {
        "main": {}
    }
}''')

    with open(projectPath+f'/{projectName}Assets/Global.py', 'w') as globalFile:
        globalFile.write(f'''
### MADE BY EGameMaker GAME ENGINE
### OPEN-SOURCE ENGINE
### https://github.com/MACsepehri/EGameMaker

import json

def get_json(index, path="{projectName}Assets/Global.json"):
    data = json.load(open(path,"r"))
    return data[index]

fullscreen = get_json("fullscreen")
base_window_size = get_json("base.window.size")
fps = get_json("fps")
title = get_json("title")
background = get_json("background")
states = get_json("states")

''')

def get_directory(app):
    path = simpledialog.askstring("Create directory", "Enter directory path :", parent=app)

    if not path:
        return

    target = f'Projects/{app.current_project}/{app.current_project}Assets/{path}'

    try:
        os.mkdir(target)
    except FileExistsError:
        tk_alert.showerror('Error', f'{path} already exists in {app.current_project}Assets folder')
    except OSError as error:
        tk_alert.showerror('Error', f'Could not create {path}:\n{error}')
    else:
        tk_alert.showinfo('Success', f'Successfully created {path} directory in {app.current_project}Assets folder')

def run_project(name):
    ### WARNING DON'T CHANGE THIS FUNCTION!
    sub.Popen([sys.executable, f'{name}.py'], cwd=f'Projects/{name}')

app = EGameMaker()

### using assets
game_name = None
render_gui.init_app(app)

app.run()
