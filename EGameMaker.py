
### FREE AND OPEN-SOURCE
### EGameMaker
### ---------------------------------------------

import os
import sys
import json
import pickle
import tkinter as tk
import tkinter.colorchooser
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
        self.create_game_configure_action()

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

        # add pkl object func to open the game configure window
        path = 'Assets/Action/InProject/008.pkl'

        with open(path, 'wb') as file:
            pickle.dump(set_game_configure, file)

    def create_game_configure_action(self):
        # add pkl object funcs used by the GameConfigure window buttons
        actions = {
            '10': save_game_configure,
            '13': pick_background_color,
            '14': close_game_configure_window,
        }

        for action_id, func in actions.items():
            path = f'Assets/Action/GameConfigure/{action_id}.pkl'

            os.makedirs(os.path.dirname(path), exist_ok=True)

            with open(path, 'wb') as file:
                pickle.dump(func, file)

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
            if component.winfo_exists() and not isinstance(component, tk.Toplevel):
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

        # let the user configure the freshly created project
        set_game_configure(app)

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

def global_json_path(project_name):
    return f'Projects/{project_name}/{project_name}Assets/Global.json'


def load_global_json(project_name):
    with open(global_json_path(project_name), 'r') as file:
        return json.load(file)


def write_global_json(project_name, data):
    with open(global_json_path(project_name), 'w') as file:
        json.dump(data, file, indent=4)


def rgb_to_hex(rgb):
    try:
        r, g, b = (int(value) for value in list(rgb)[:3])
    except (TypeError, ValueError):
        return '#FFFFFF'

    return (
        f'#{max(0, min(255, r)):02X}'
        f'{max(0, min(255, g)):02X}'
        f'{max(0, min(255, b)):02X}'
    )


def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return [int(hex_color[i:i + 2], 16) for i in (0, 2, 4)]


def _read_number_field(app, entry_id, label):
    try:
        raw = render_gui.getInput('GameConfigure', entry_id).get().strip()
    except (KeyError, RuntimeError):
        return None

    if raw == '':
        tk_alert.showerror('Error', f'{label} cannot be empty.')
        return None

    try:
        value = int(raw)
    except ValueError:
        tk_alert.showerror('Error', f'{label} must be a number.')
        return None

    if value < 1:
        tk_alert.showerror('Error', f'{label} must be at least 1.')
        return None

    if value > 4096:
        tk_alert.showerror('Error', f'{label} must be at most 4096.')
        return None

    return value


def set_game_configure(app):
    project_name = getattr(app, 'current_project', None)

    if not project_name:
        tk_alert.showerror('Error', 'No project is open.')
        return

    try:
        data = load_global_json(project_name)
    except (OSError, json.JSONDecodeError) as error:
        tk_alert.showerror('Error', f'Could not load Global.json:\n{error}')
        return

    render_gui.close_component_window('GameConfigure')

    window = render_gui.open_component_window(
        'GameConfigure',
        title=f'Game Configure : {project_name}',
        geometry='420x380',
        text_font=[('00', 20)],
    )
    window.transient(app)

    size = data.get('base.window.size', [500, 500])

    def fill(entry_id, value):
        entry = render_gui.getInput('GameConfigure', entry_id)
        entry.delete(0, tk.END)
        entry.insert(0, str(value))

    fill('02', data.get('title', project_name))
    fill('04', size[0])
    fill('06', size[1])
    fill('08', data.get('fps', 60))

    render_gui.getCheckbox('GameConfigure', '12').set(
        bool(data.get('fullscreen', False))
    )
    render_gui.getCheckboxWidget('GameConfigure', '12').config(
        command=lambda: save_global_field(app, 'fullscreen')
    )

    app.game_background = rgb_to_hex(data.get('background', [255, 255, 255]))
    render_gui.setText('GameConfigure', '11', app.game_background)

    title_entry = render_gui.getInput('GameConfigure', '02')
    width_entry = render_gui.getInput('GameConfigure', '04')
    height_entry = render_gui.getInput('GameConfigure', '06')
    fps_entry = render_gui.getInput('GameConfigure', '08')

    for entry, field in ((title_entry, 'title'), (fps_entry, 'fps')):
        entry.bind('<FocusOut>', lambda e, f=field: save_global_field(app, f))
        entry.bind('<Return>', lambda e, f=field: save_global_field(app, f))

    for entry, index in ((width_entry, 0), (height_entry, 1)):
        entry.bind('<FocusOut>', lambda e, i=index: save_size_field(app, i))
        entry.bind('<Return>', lambda e, i=index: save_size_field(app, i))


def save_global_field(app, field):
    ### saves a single changed field of Global.json right away

    project_name = getattr(app, 'current_project', None)

    if not project_name:
        return

    try:
        data = load_global_json(project_name)
    except (OSError, json.JSONDecodeError):
        return

    if field == 'fullscreen':
        try:
            data['fullscreen'] = render_gui.getCheckbox('GameConfigure', '12').get()
        except (KeyError, RuntimeError):
            return
    elif field == 'title':
        try:
            value = render_gui.getInput('GameConfigure', '02').get().strip()
        except (KeyError, RuntimeError):
            return

        if not value:
            tk_alert.showerror('Error', 'Title cannot be empty.')
            return

        data['title'] = value
    elif field == 'fps':
        value = _read_number_field(app, '08', 'Fps')

        if value is None:
            return

        data['fps'] = value
    else:
        return

    write_global_json(project_name, data)


def save_size_field(app, index):
    ### saves one side of base.window.size of Global.json right away

    project_name = getattr(app, 'current_project', None)

    if not project_name:
        return

    is_width = index == 0
    value = _read_number_field(
        app,
        '04' if is_width else '06',
        'Width' if is_width else 'Height',
    )

    if value is None:
        return

    try:
        data = load_global_json(project_name)
    except (OSError, json.JSONDecodeError):
        return

    size = list(data.get('base.window.size', [500, 500]))

    while len(size) < 2:
        size.append(500)

    size[index] = value
    data['base.window.size'] = size

    write_global_json(project_name, data)


def save_game_configure(app):
    ### Save button of the GameConfigure window

    project_name = getattr(app, 'current_project', None)

    if not project_name:
        tk_alert.showerror('Error', 'No project is open.')
        return

    try:
        data = load_global_json(project_name)
    except (OSError, json.JSONDecodeError) as error:
        tk_alert.showerror('Error', f'Could not load Global.json:\n{error}')
        return

    try:
        title = render_gui.getInput('GameConfigure', '02').get().strip()
    except (KeyError, RuntimeError):
        tk_alert.showerror('Error', 'Game configure window is not open.')
        return

    if not title:
        tk_alert.showerror('Error', 'Title cannot be empty.')
        return

    width = _read_number_field(app, '04', 'Width')
    height = _read_number_field(app, '06', 'Height')
    fps = _read_number_field(app, '08', 'Fps')

    if width is None or height is None or fps is None:
        return

    try:
        fullscreen = render_gui.getCheckbox('GameConfigure', '12').get()
    except (KeyError, RuntimeError):
        fullscreen = bool(data.get('fullscreen', False))

    data['title'] = title
    data['base.window.size'] = [width, height]
    data['fps'] = fps
    data['fullscreen'] = fullscreen

    background = getattr(app, 'game_background', None)

    if background:
        data['background'] = hex_to_rgb(background)

    write_global_json(project_name, data)
    tk_alert.showinfo(
        'Saved',
        f'Game settings saved to {project_name}Assets/Global.json.'
    )


def close_game_configure_window(app):
    ### Close button of the GameConfigure window
    render_gui.close_component_window('GameConfigure')


def pick_background_color(app):
    ### Pick Color button of the GameConfigure window

    project_name = getattr(app, 'current_project', None)

    if not project_name:
        tk_alert.showerror('Error', 'No project is open.')
        return

    window = render_gui.windows.get('GameConfigure')
    initial = getattr(app, 'game_background', '#FFFFFF')

    result = tk.colorchooser.askcolor(
        color=initial,
        parent=window if window is not None else app,
        title='Pick Background Color'
    )

    if result[0] is None:
        return

    hex_color = result[1]
    rgb = [int(channel) for channel in result[0]]

    app.game_background = hex_color

    try:
        render_gui.setText('GameConfigure', '11', hex_color)
    except (KeyError, RuntimeError):
        pass

    try:
        data = load_global_json(project_name)
    except (OSError, json.JSONDecodeError) as error:
        tk_alert.showerror('Error', f'Could not load Global.json:\n{error}')
        return

    data['background'] = rgb

    write_global_json(project_name, data)
    tk_alert.showinfo(
        'Saved',
        f'Background color saved to {project_name}Assets/Global.json.'
    )

def run_project(name):
    ### WARNING DON'T CHANGE THIS FUNCTION!
    sub.Popen([sys.executable, f'{name}.py'], cwd=f'Projects/{name}')

app = EGameMaker()

### using assets
game_name = None
render_gui.init_app(app)

app.run()
