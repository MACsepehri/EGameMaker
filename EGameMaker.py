
### FREE AND OPEN-SOURCE
### EGameMaker
### ---------------------------------------------

import os
import sys
import json
import pickle
import shutil
import tkinter as tk
import tkinter.colorchooser
import tkinter.filedialog
import subprocess as sub
from tkinter import simpledialog
from tkinter import messagebox as tk_alert
from Assets.GUI.Render.RenderGUIComponent import RenderGUIComponent


render_gui = RenderGUIComponent()

### pkl path of the action function of the button currently being configured
_button_action_path = None

### (state, index, entry_string) of the Global.json button entry that is
### currently being edited; None means a new button is being configured
_edit_button_entry = None

### (state, index, entry_string) of the Global.json text entry that is
### currently being edited; None means a new text is being configured
_edit_text_entry = None

### (state, index, entry_string) of the Global.json image entry that is
### currently being edited; None means a new image is being configured
_edit_image_entry = None


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
        self.create_button_configure_action()
        self.create_button_action_action()
        self.create_text_configure_action()
        self.create_image_configure_action()

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
        path = 'Assets/Action/InProject/007.pkl'

        with open(path, 'wb') as file:
            pickle.dump(set_game_configure, file)

        # add pkl object func to remove the currently open project
        path = 'Assets/Action/InProject/0010.pkl'

        with open(path, 'wb') as file:
            pickle.dump(remove_current_project, file)

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

    def create_button_configure_action(self):
        # add pkl object funcs used by the AddButton window buttons
        actions = {
            '40': save_button_configure,
            '41': close_button_configure_window,
            '42': open_button_action_window,
        }

        for action_id, func in actions.items():
            path = f'Assets/Action/AddButton/{action_id}.pkl'

            os.makedirs(os.path.dirname(path), exist_ok=True)

            with open(path, 'wb') as file:
                pickle.dump(func, file)

    def create_button_action_action(self):
        # add pkl object funcs used by the ButtonAction window buttons
        actions = {
            '50': save_button_action,
            '51': close_button_action_window,
        }

        for action_id, func in actions.items():
            path = f'Assets/Action/ButtonAction/{action_id}.pkl'

            os.makedirs(os.path.dirname(path), exist_ok=True)

            with open(path, 'wb') as file:
                pickle.dump(func, file)

    def create_text_configure_action(self):
        # add pkl object funcs used by the AddText window buttons
        actions = {
            '80': save_text_configure,
            '81': close_text_configure_window,
        }

        for action_id, func in actions.items():
            path = f'Assets/Action/AddText/{action_id}.pkl'

            os.makedirs(os.path.dirname(path), exist_ok=True)

            with open(path, 'wb') as file:
                pickle.dump(func, file)

    def create_image_configure_action(self):
        # add pkl object funcs used by the AddImage window buttons
        actions = {
            '110': save_image_configure,
            '111': close_image_configure_window,
        }

        for action_id, func in actions.items():
            path = f'Assets/Action/AddImage/{action_id}.pkl'

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

    def refresh_projects(self):
        ### rebuild the project button list of the main page
        stale_ids = []

        for line in render_gui.content['MainPage']:
            if not line.startswith('BUTTON='):
                continue

            try:
                _, _, button_id, _ = render_gui.parse_button(line)
            except (ValueError, IndexError):
                continue

            if button_id != '03':
                stale_ids.append(button_id)

        for button_id in stale_ids:
            render_gui.removeButtonComponent('MainPage.GUI', button_id)

            pkl_path = f'Assets/Action/MainPage/{button_id}.pkl'

            if os.path.isfile(pkl_path):
                os.remove(pkl_path)

        projects = (
            [
                name for name in os.listdir('Projects')
                if os.path.isdir(os.path.join('Projects', name))
            ]
            if os.path.isdir('Projects')
            else []
        )

        if not projects:
            render_gui.addTextComponent(
                'MainPage.GUI',
                "You don't have any projects...",
                ('0.02', '0.15'),
                '02'
            )
        else:
            self.show_projects(projects)

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
        self.save_pickle_object('009',show_all_dir_and_files)
        self.save_pickle_object('008',get_directory)
        self.save_pickle_object('006',show_all_states)
        self.save_pickle_object('005',add_state)
        self.save_pickle_object('001',add_button)
        self.save_pickle_object('011',edit_button)
        self.save_pickle_object('012',remove_button)
        self.save_pickle_object('013',add_font)
        self.save_pickle_object('014',remove_font)
        self.save_pickle_object('015',add_text)
        self.save_pickle_object('016',edit_text)
        self.save_pickle_object('017',remove_text)
        self.save_pickle_object('018',edit_state)
        self.save_pickle_object('019',remove_state)
        self.save_pickle_object('020',add_image)
        self.save_pickle_object('021',remove_image)
        self.save_pickle_object('022',edit_image)


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

    def save_pickle_object(self, filename, func):
        _path = f"Assets/Action/InProject/{filename}.pkl"

        if not os.path.exists(_path):
            with open(_path,"x"):
                pass

        os.makedirs(os.path.dirname(_path), exist_ok=True)

        if not os.path.isfile(_path) or os.path.getsize(_path) == 0:
            with open(_path, "wb") as file:
                pickle.dump(func, file)


def run_current_project(app):
    project_name = getattr(app, 'current_project', None)

    if not project_name:
        tk_alert.showerror('Error', 'No project is open.')
        return

    run_project(project_name)


def remove_current_project(app):
    ### Remove Project button of the InProject page
    project_name = getattr(app, 'current_project', None)

    if not project_name:
        tk_alert.showerror('Error', 'No project is open.')
        return

    if not tk_alert.askyesno(
        'Remove Project',
        f'Remove project "{project_name}"? This cannot be undone.'
    ):
        return

    shutil.rmtree(f'Projects/{project_name}', ignore_errors=True)

    app.current_project = None
    render_gui.close_component_window('GameConfigure')
    app.refresh_projects()
    app.change_page('MainPage', [('01', 30)])


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
        file.write('''
### MADE BY EGameMaker GAME ENGINE
### OPEN-SOURCE ENGINE
### https://github.com/MACsepehri/EGameMaker

import pygame,sys
import types
import pickle
import os
import __PROJECT_NAME__Assets.Global as Global
from button import Button
from text import Text
from image import Image

pygame.init()

def initialization():
    if (Global.fullscreen):
        win = pygame.display.set_mode((0,0),pygame.FULLSCREEN)
    else:
        win = pygame.display.set_mode(Global.base_window_size)
    pygame.display.set_caption(Global.title)
    return win

def split_top_level(text):
    ### split on commas that are not inside [ ]
    parts, depth, current = [], 0, ''

    for char in text:
        if char == '[':
            depth += 1
        elif char == ']':
            depth -= 1

        if char == ',' and depth == 0:
            parts.append(current)
            current = ''
        else:
            current += char

    if current:
        parts.append(current)

    return parts

def parse_button_entry(entry, state_in):
    ### turn a BUTTON(...) entry of Global.json states into a Button
    body = entry[len('BUTTON('):-1]
    values = {}

    for part in split_top_level(body):
        key, _, value = part.partition('=')
        values[key.strip()] = value.strip()

    def items(raw):
        ### values are stored like [a,b,c]; strip one pair of [ ] then
        ### split on the top-level commas
        raw = raw.strip()

        if raw.startswith('[') and raw.endswith(']'):
            raw = raw[1:-1]

        return [item for item in split_top_level(raw) if item != '']

    def pair(key, cast):
        raw = values.get(key, '')
        return [cast(item) for item in items(raw)] if raw else None

    def color(key, default):
        raw = values.get(key, '')
        return tuple(int(item) for item in items(raw)) if raw else default

    return Button(
        text=values.get('text', ''),
        position=pair('pos', float) or (0.5, 0.5),
        size=pair('size', int) or (150, 50),
        state_in=state_in,
        base_color=color('base_color', (200, 200, 200)),
        hover_color=color('hover_color', (255, 255, 0)),
        text_color=color('text_color', (0, 0, 0)),
        font_name=values.get('font_name', 'base_font') or 'base_font',
        font_size=int(values.get('font_size', '14') or 14),
    )

def parse_text_entry(entry, state_in):
    ### turn a TEXT(...) entry of Global.texts into a Text
    body = entry[len('TEXT('):-1]
    values = {}

    for part in split_top_level(body):
        key, _, value = part.partition('=')
        values[key.strip()] = value.strip()

    def items(raw):
        ### values are stored like [a,b,c]; strip one pair of [ ] then
        ### split on the top-level commas
        raw = raw.strip()

        if raw.startswith('[') and raw.endswith(']'):
            raw = raw[1:-1]

        return [item for item in split_top_level(raw) if item != '']

    def pair(key, cast):
        raw = values.get(key, '')
        return [cast(item) for item in items(raw)] if raw else None

    def color(key, default):
        raw = values.get(key, '')
        return tuple(int(item) for item in items(raw)) if raw else default

    return Text(
        text=values.get('text', ''),
        position=pair('pos', float) or (0.5, 0.5),
        font_name=values.get('font_name', 'base_font') or 'base_font',
        font_size=int(values.get('font_size', '32') or 32),
        text_color=color('text_color', (0, 0, 0)),
        state_in=state_in,
    )

def parse_image_entry(entry, state_in):
    ### turn an IMAGE(...) entry of Global.image_components into an Image
    body = entry[len('IMAGE('):-1]
    values = {}

    for part in split_top_level(body):
        key, _, value = part.partition('=')
        values[key.strip()] = value.strip()

    def items(raw):
        ### values are stored like [a,b,c]; strip one pair of [ ] then
        ### split on the top-level commas
        raw = raw.strip()

        if raw.startswith('[') and raw.endswith(']'):
            raw = raw[1:-1]

        return [item for item in split_top_level(raw) if item != '']

    def pair(key, cast):
        raw = values.get(key, '')
        return [cast(item) for item in items(raw)] if raw else None

    return Image(
        image_name=values.get('image', ''),
        position=pair('pos', float) or (0.5, 0.5),
        size=tuple(int(item) for item in items(values.get('size', ''))) or (200, 200),
        border_radius=int(values.get('border_radius', '0') or 0),
        state_in=state_in,
    )

class Game:
    ### the object passed to the user's action code as self, it carries
    ### the button vars and the Global vars

    def __init__(self, win, buttons, texts, images):
        self.win = win
        self.Global = Global
        self.buttons = {button.text: button for button in buttons}
        self.texts = texts
        self.images = images
        self.current_state = getattr(
            Global, 'current_state', next(iter(Global.states), 'main')
        )

def load_action(path):
    ### load a button's pickled action, the pkl stores the action source
    ### text so the function is rebuilt by execing it with Global
    if not path:
        return None

    if path.startswith(f'Projects/__PROJECT_NAME__/'):
        path = path[len(f'Projects/__PROJECT_NAME__/'):]

    try:
        with open(path, 'rb') as file:
            loaded = pickle.load(file)
    except (OSError, EOFError, pickle.UnpicklingError):
        return None

    if isinstance(loaded, str):
        return _rebuild_action_func(loaded)

    return loaded

def _rebuild_action_func(source):
    ### exec the stored action source in a namespace where Global and the
    ### builtins resolve, then return the function the source defines
    namespace = {'Global': Global}
    exec(compile(source, '<button_action>', 'exec'), namespace)

    for name, value in namespace.items():
        if name in ('Global', '__builtins__'):
            continue
        if isinstance(value, types.FunctionType):
            return value

    return None

def fire_action(action, game):
    ### call the action, passing the game object only when the action is
    ### declared to take a positional argument
    code = getattr(action, '__code__', None)
    if code is None or code.co_argcount >= 1:
        action(game)
    else:
        action()

def bind_component_font(component):
    ### resolve a component's font name to a project font file and rebind
    ### its font, names come from the fonts map of Global.json
    if not component.font_name or component.font_name == 'base_font':
        return

    font_path = (getattr(Global, 'fonts', {}) or {}).get(component.font_name)

    if not font_path:
        return

    full_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), font_path)

    try:
        component.font = pygame.font.Font(full_path, component.font_size)
    except (pygame.error, OSError):
        ### fall back to the default font the component already set up
        pass

def bind_image(component):
    ### resolve an image component's registered name to its file and
    ### load it, names come from the images map of Global.json
    if not component.image_name:
        return

    image_path = (getattr(Global, 'images', {}) or {}).get(component.image_name)

    if not image_path:
        return

    full_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), image_path)
    component.set_image(full_path)

def make_game(win):
    ### create one Button, Text and Image for every entry of Global
    buttons = []
    texts = []

    for state, entries in Global.states.items():
        for entry in entries or []:
            button_entry = entry[0]
            action_path = entry[1] if len(entry) > 1 else None
            button = parse_button_entry(button_entry, state)
            button.action_path = action_path
            bind_component_font(button)
            buttons.append(button)

    for state, entries in (getattr(Global, 'texts', {}) or {}).items():
        for text_entry in entries or []:
            text = parse_text_entry(text_entry, state)
            bind_component_font(text)
            texts.append(text)

    images = []

    for state, entries in (getattr(Global, 'image_components', {}) or {}).items():
        for image_entry in entries or []:
            image = parse_image_entry(image_entry, state)
            bind_image(image)
            images.append(image)

    return Game(win, buttons, texts, images)

def app():
    win = initialization()
    clock = pygame.time.Clock()
    game = make_game(win)

    while True:
        events = pygame.event.get()

        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)

        ### Global.current_state is the source of truth, set_state() in
        ### Global switches it and the loop picks it up here
        state = Global.current_state
        game.current_state = state

        for button in game.buttons.values():
            button.handle_events(events, state)

        win.fill(Global.background)

        for image in game.images:
            image.render(win, state)

        for text in game.texts:
            text.render(win, state)

        for button in game.buttons.values():
            button.render(win, state)

        pygame.display.update()

        for button in game.buttons.values():
            if button.clicked:
                action = load_action(button.action_path)

                if action is not None:
                    try:
                        fire_action(action, game)
                    except Exception as error:
                        print(f'action error for "{button.text}": {error}')

        clock.tick(Global.fps)

if __name__ == "__main__":
    app()

'''.replace('__PROJECT_NAME__', projectName))

    with open('button.py', 'r') as buttonFile, open(projectPath+f'/button.py', 'w') as file:
        file.write(buttonFile.read())

    with open('text.py', 'r') as textFile, open(projectPath+f'/text.py', 'w') as file:
        file.write(textFile.read())

    with open('image.py', 'r') as imageFile, open(projectPath+f'/image.py', 'w') as file:
        file.write(imageFile.read())

    with open(projectPath+f'/{projectName}Assets/Global.json', 'w') as globalFile:
            globalFile.write('''
{
    "fullscreen":false,
    "base.window.size":[500,500],
    "fps":60,
    "title":"'''+projectName+'''",
    "background":[255,255,255],

    "fonts": {},

    "images": {},

    "image_components": {},

    "texts": {
        "main": []
    },

    "states": {
        "main": []
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
    states = {{}}
current_state = next(iter(states), 'main')
try:
    fonts = get_json("fonts")
except KeyError:
    fonts = {{}}
try:
    texts = get_json("texts")
except KeyError:
    texts = {{}}
try:
    images = get_json("images")
except KeyError:
    images = {{}}
try:
    image_components = get_json("image_components")
except KeyError:
    image_components = {{}}

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

def add_state(app):
    ### Adding new state in 'Global.json' file for every project

    project_name = getattr(app, 'current_project', None)

    if not project_name:
        tk_alert.showerror('Error', 'No project is open.')
        return

    state_value = simpledialog.askstring(
        'Add new state',
        'Enter state value :',
        parent=app
    )

    if state_value is None:
        return

    state_value = state_value.strip()

    if not state_value:
        tk_alert.showerror('Error', 'State value cannot be empty.')
        return

    try:
        data = load_global_json(project_name)
    except (OSError, json.JSONDecodeError) as error:
        tk_alert.showerror('Error', f'Could not load Global.json:\n{error}')
        return

    states = data.setdefault('states', {})

    if any(name.casefold() == state_value.casefold() for name in states):
        tk_alert.showerror('Error', f'State "{state_value}" is already exist.')
        return

    states[state_value] = []
    write_global_json(project_name, data)
    tk_alert.showinfo('Success', f'State "{state_value}" added.')


def edit_state(app):
    ### Edit State button of the InProject page
    ### lets the user pick an existing state and rename it; the buttons
    ### and texts of the state follow the rename

    _open_state_picker(app, 'Edit State', on_picked=lambda name: _begin_state_rename(app, name))


def _begin_state_rename(app, old_name):
    project_name = app.current_project

    new_name = simpledialog.askstring(
        'Edit State',
        f'Enter the new name for state "{old_name}":',
        parent=app,
        initialvalue=old_name,
    )

    if new_name is None:
        return

    new_name = new_name.strip()

    if not new_name:
        tk_alert.showerror('Error', 'State value cannot be empty.')
        return

    if new_name == old_name:
        return

    try:
        data = load_global_json(project_name)
    except (OSError, json.JSONDecodeError) as error:
        tk_alert.showerror('Error', f'Could not load Global.json:\n{error}')
        return

    states = data.get('states') or {}

    if old_name not in states:
        tk_alert.showerror('Error', f'State "{old_name}" no longer exists in Global.json.')
        return

    if any(name.casefold() == new_name.casefold() for name in states):
        tk_alert.showerror('Error', f'State "{new_name}" already exists in the project.')
        return

    states[new_name] = states.pop(old_name)

    texts = data.get('texts')

    if isinstance(texts, dict) and old_name in texts:
        texts[new_name] = texts.pop(old_name)

    write_global_json(project_name, data)
    tk_alert.showinfo('Success', f'State "{old_name}" renamed to "{new_name}".')


def remove_state(app):
    ### Remove State button of the InProject page
    ### lets the user pick a state, then removes it from Global.json
    ### when it holds no buttons or texts

    _open_state_picker(app, 'Remove State', on_picked=lambda name: _confirm_state_removal(app, name))


def _confirm_state_removal(app, state_name):
    project_name = app.current_project

    try:
        data = load_global_json(project_name)
    except (OSError, json.JSONDecodeError) as error:
        tk_alert.showerror('Error', f'Could not load Global.json:\n{error}')
        return

    button_count = len((data.get('states') or {}).get(state_name) or [])
    text_count = len((data.get('texts') or {}).get(state_name) or [])

    if button_count or text_count:
        tk_alert.showerror(
            'Error',
            f'State "{state_name}" still has {button_count} button(s) and '
            f'{text_count} text(s). Remove them first.'
        )
        return

    if not tk_alert.askyesno(
        'Remove State',
        f'Remove state "{state_name}"?'
    ):
        return

    states = data.get('states') or {}

    if state_name not in states:
        tk_alert.showerror('Error', f'State "{state_name}" no longer exists in Global.json.')
        return

    del states[state_name]
    data['states'] = states

    texts = data.get('texts')

    if isinstance(texts, dict):
        texts.pop(state_name, None)
        data['texts'] = texts

    write_global_json(project_name, data)
    tk_alert.showinfo('Removed', f'State "{state_name}" removed.')


def _open_state_picker(app, title, on_picked):
    ### list the states of the open project and let the user pick one;
    ### on_picked is called with the picked state name

    project_name = getattr(app, 'current_project', None)

    if not project_name:
        tk_alert.showerror('Error', 'No project is open.')
        return

    try:
        data = load_global_json(project_name)
    except (OSError, json.JSONDecodeError) as error:
        tk_alert.showerror('Error', f'Could not load Global.json:\n{error}')
        return

    names = list((data.get('states') or {}).keys())

    if not names:
        tk_alert.showinfo('Info', f'There are no states in "{project_name}" yet.')
        return

    picker = tk.Toplevel(app)
    picker.title(title)
    picker.transient(app)
    picker.resizable(False, False)

    try:
        picker.grab_set()
    except tk.TclError:
        pass

    ### make sure the picker opens on top of the main window with focus
    try:
        picker.update_idletasks()
        picker.lift()
    except tk.TclError:
        pass

    listbox = tk.Listbox(
        picker,
        height=min(12, max(4, len(names))),
        width=32,
        selectborderwidth=2
    )

    for name in names:
        listbox.insert(tk.END, name)

    if len(names) == 1:
        listbox.selection_set(0)

    listbox.pack(padx=10, pady=(10, 4))

    def pick():
        selection = listbox.curselection()

        if not selection:
            tk_alert.showerror('Error', 'Select a state first.')
            return

        picker.destroy()
        on_picked(names[selection[0]])

    select = tk.Button(picker, text='Select', command=pick, width=10)
    select.pack(pady=4)

    cancel = tk.Button(picker, text='Cancel', command=picker.destroy, width=10)
    cancel.pack(pady=(0, 10))


def show_all_states(app):
    ### Show all states from project 'Global.json' file
    global_project_data = load_global_json(app.current_project)
    string_result = ''
    index = 1
    for states in global_project_data['states']:
        string_result += f'{index}. {states}\n'
        index += 1
    
    tk_alert.showinfo('All States',f'All states in global json file :\n\n{string_result}')

def show_all_dir_and_files(app):
    ### Show all directories in project assets
    dirs = os.listdir(f"Projects/{app.current_project}/{app.current_project}Assets")
    string_result = ''
    index = 1
    for states in dirs:
        string_result += f'{index}. {states}\n'
        index += 1
    
    tk_alert.showinfo('All Assets Directories and Files',f'All directories/files in assets :\n\n{string_result}')

def add_font(app):
    ### Add Font button of the InProject page
    ### gives a font file a name, copies it into the project assets and
    ### registers it in Global.json so components can use it by name

    project_name = getattr(app, 'current_project', None)

    if not project_name:
        tk_alert.showerror('Error', 'No project is open.')
        return

    try:
        data = load_global_json(project_name)
    except (OSError, json.JSONDecodeError) as error:
        tk_alert.showerror('Error', f'Could not load Global.json:\n{error}')
        return

    fonts = data.get('fonts') or {}
    font_name = _ask_font_name(app, fonts)

    if font_name is None:
        return

    font_file = tk.filedialog.askopenfilename(
        parent=app,
        title='Select the font file',
        filetypes=[
            ('Font files', '*.ttf;*.otf;*.ttc'),
            ('All files', '*.*'),
        ],
    )

    if not font_file:
        return

    extension = os.path.splitext(font_file)[1]
    folder = f'Projects/{project_name}/{project_name}Assets/Fonts'
    os.makedirs(folder, exist_ok=True)

    shutil.copy2(font_file, os.path.join(folder, font_name + extension))

    fonts[font_name] = f'{project_name}Assets/Fonts/{font_name}{extension}'
    data['fonts'] = fonts
    write_global_json(project_name, data)

    tk_alert.showinfo('Added', f'Font "{font_name}" added to {project_name}.')


def _ask_font_name(app, fonts):
    ### ask for a font name that is not empty, filesystem safe and not
    ### already used in the project; None means the user cancelled

    while True:
        raw = simpledialog.askstring(
            'Add Font',
            'Enter a name for the font:',
            parent=app
        )

        if raw is None:
            return None

        font_name = raw.strip()

        if not font_name:
            tk_alert.showerror('Error', 'Font name cannot be empty.')
            continue

        if any(char in font_name for char in '\\/:*?"<>|'):
            tk_alert.showerror('Error', 'Font name contains invalid characters.')
            continue

        if any(font_name.casefold() == name.casefold() for name in fonts):
            tk_alert.showerror('Error', f'Font "{font_name}" already exists in the project.')
            continue

        return font_name


def remove_font(app):
    ### Remove Font button of the InProject page
    ### lets the user pick a registered font, then removes it from
    ### Global.json and the project fonts folder when no button uses it

    _open_font_picker(app, on_picked=lambda name: _confirm_font_removal(app, name))


def _confirm_font_removal(app, font_name):
    project_name = app.current_project

    try:
        used_by = [
            fields.get('font_name')
            for *_, fields in _collect_button_entries(project_name)
        ]
    except (OSError, json.JSONDecodeError):
        used_by = []

    if font_name in used_by:
        tk_alert.showerror(
            'Error',
            f'Font "{font_name}" is used by a button and cannot be removed.'
        )
        return

    if not tk_alert.askyesno(
        'Remove Font',
        f'Remove font "{font_name}"? This cannot be undone.'
    ):
        return

    try:
        data = load_global_json(project_name)
    except (OSError, json.JSONDecodeError) as error:
        tk_alert.showerror('Error', f'Could not load Global.json:\n{error}')
        return

    fonts = data.get('fonts') or {}

    if font_name not in fonts:
        tk_alert.showerror('Error', f'Font "{font_name}" no longer exists in Global.json.')
        return

    font_path = fonts[font_name]
    del fonts[font_name]
    data['fonts'] = fonts

    write_global_json(project_name, data)

    full_path = os.path.join('Projects', project_name, font_path)

    if os.path.isfile(full_path):
        os.remove(full_path)

    tk_alert.showinfo('Removed', f'Font "{font_name}" removed from {project_name}.')


def _open_font_picker(app, on_picked):
    ### list the fonts of the open project and let the user pick one;
    ### on_picked is called with the picked font name

    project_name = getattr(app, 'current_project', None)

    if not project_name:
        tk_alert.showerror('Error', 'No project is open.')
        return

    try:
        data = load_global_json(project_name)
    except (OSError, json.JSONDecodeError) as error:
        tk_alert.showerror('Error', f'Could not load Global.json:\n{error}')
        return

    names = list((data.get('fonts') or {}).keys())

    if not names:
        tk_alert.showinfo('Info', f'There are no fonts in "{project_name}" yet.')
        return

    picker = tk.Toplevel(app)
    picker.title('Pick Font')
    picker.transient(app)
    picker.resizable(False, False)

    try:
        picker.grab_set()
    except tk.TclError:
        pass

    ### make sure the picker opens on top of the main window with focus
    try:
        picker.update_idletasks()
        picker.lift()
    except tk.TclError:
        pass

    listbox = tk.Listbox(
        picker,
        height=min(12, max(4, len(names))),
        width=40,
        selectborderwidth=2
    )

    for name in names:
        listbox.insert(tk.END, name)

    if len(names) == 1:
        listbox.selection_set(0)

    listbox.pack(padx=10, pady=(10, 4))

    def pick():
        selection = listbox.curselection()

        if not selection:
            tk_alert.showerror('Error', 'Select a font first.')
            return

        picker.destroy()
        on_picked(names[selection[0]])

    select = tk.Button(picker, text='Select', command=pick, width=10)
    select.pack(pady=4)

    cancel = tk.Button(picker, text='Cancel', command=picker.destroy, width=10)
    cancel.pack(pady=(0, 10))


def add_image(app):
    ### Add Image button of the InProject page
    ### gives an image file a name, copies it into the project assets and
    ### registers it in Global.json, then opens the AddImage window so the
    ### image's placement (state, position, size, corner radius) is set

    global _edit_image_entry

    project_name = getattr(app, 'current_project', None)

    if not project_name:
        tk_alert.showerror('Error', 'No project is open.')
        return

    try:
        data = load_global_json(project_name)
    except (OSError, json.JSONDecodeError) as error:
        tk_alert.showerror('Error', f'Could not load Global.json:\n{error}')
        return

    ### placing a new image, drop any edit that was in progress
    _edit_image_entry = None

    images = data.get('images') or {}
    image_name = _ask_image_name(app, images)

    if image_name is None:
        return

    image_file = tk.filedialog.askopenfilename(
        parent=app,
        title='Select the image file',
        filetypes=[
            ('Image files', '*.png;*.jpg;*.jpeg;*.gif;*.bmp;*.webp'),
            ('All files', '*.*'),
        ],
    )

    if not image_file:
        return

    extension = os.path.splitext(image_file)[1]
    folder = f'Projects/{project_name}/{project_name}Assets/Images'
    os.makedirs(folder, exist_ok=True)

    shutil.copy2(image_file, os.path.join(folder, image_name + extension))

    images[image_name] = f'{project_name}Assets/Images/{image_name}{extension}'
    data['images'] = images
    write_global_json(project_name, data)

    ### open the configure window with the new image pre-filled
    _open_image_configure_window(app, f'Add Image : {project_name}', {
        '90': next(iter(data.get('states') or {'main': []}), 'main'),
        '92': image_name,
        '94': '0.5,0.5',
        '96': '200',
        '98': '200',
        '100': '0',
    })


def _ask_image_name(app, images):
    ### ask for an image name that is not empty, filesystem safe and not
    ### already used in the project; None means the user cancelled

    while True:
        raw = simpledialog.askstring(
            'Add Image',
            'Enter a name for the image:',
            parent=app
        )

        if raw is None:
            return None

        image_name = raw.strip()

        if not image_name:
            tk_alert.showerror('Error', 'Image name cannot be empty.')
            continue

        if any(char in image_name for char in '\\/:*?"<>|'):
            tk_alert.showerror('Error', 'Image name contains invalid characters.')
            continue

        if any(image_name.casefold() == name.casefold() for name in images):
            tk_alert.showerror('Error', f'Image "{image_name}" already exists in the project.')
            continue

        return image_name


def edit_image(app):
    ### Edit Image button of the InProject page
    ### lets the user pick a placed image and re-open the AddImage window
    ### with its values so they can be changed

    global _edit_image_entry

    _edit_image_entry = None

    _open_image_picker(app, 'Edit Image', on_picked=lambda picked: _begin_image_edit(app, picked))


def _begin_image_edit(app, picked):
    ### picker callback of edit_image: remember the picked entry and open
    ### the AddImage window pre-filled with the image's values

    global _edit_image_entry

    state, index, entry_string, fields = picked

    _edit_image_entry = (state, index, entry_string)

    size_raw = _strip_brackets(fields.get('size') or '200,200')
    size_parts = size_raw.split(',')
    width_value = size_parts[0] if len(size_parts) > 0 else '200'
    height_value = size_parts[1] if len(size_parts) > 1 else '200'

    _open_image_configure_window(app, f'Edit Image : {app.current_project}', {
        '90': state,
        '92': fields.get('image') or '',
        '94': _strip_brackets(fields.get('pos') or '0.5,0.5'),
        '96': width_value,
        '98': height_value,
        '100': fields.get('border_radius') or '0',
    })


def remove_image(app):
    ### Remove Image button of the InProject page
    ### lets the user pick a placed image, removes its entry from
    ### Global.json and the image file when no other image uses it

    _open_image_picker(app, 'Remove Image', on_picked=lambda picked: _confirm_image_removal(app, picked))


def _confirm_image_removal(app, picked):
    state, index, entry_string, fields = picked
    project_name = app.current_project
    image_name = fields.get('image') or ''

    if not tk_alert.askyesno(
        'Remove Image',
        f'Remove image "{image_name}" from state "{state}"?'
    ):
        return

    try:
        data = load_global_json(project_name)
    except (OSError, json.JSONDecodeError) as error:
        tk_alert.showerror('Error', f'Could not load Global.json:\n{error}')
        return

    entries = (data.get('image_components') or {}).get(state) or []

    if not (index < len(entries) and entries[index] == entry_string):
        tk_alert.showerror(
            'Error',
            'That image no longer exists in Global.json. It may have been changed.'
        )
        return

    del entries[index]

    ### delete the image file when no remaining placed image uses it
    if image_name:
        still_used = any(
            _parse_button_fields(other).get('image') == image_name
            for other_entries in (data.get('image_components') or {}).values()
            for other in (other_entries or [])
            if isinstance(other, str)
        )

        if not still_used:
            images = data.get('images') or {}

            if image_name in images:
                image_path = images[image_name]
                del images[image_name]
                data['images'] = images
                write_global_json(project_name, data)

                full_path = os.path.join('Projects', project_name, image_path)

                if os.path.isfile(full_path):
                    os.remove(full_path)

    write_global_json(project_name, data)
    tk_alert.showinfo('Removed', f'Image "{image_name}" removed from state "{state}".')


def save_image_configure(app):
    ### Save button of the AddImage window
    ### writes the configured image into the chosen state of Global.json,
    ### replacing the picked entry when an image is being edited

    global _edit_image_entry

    project_name = getattr(app, 'current_project', None)

    if not project_name:
        tk_alert.showerror('Error', 'No project is open.')
        return

    try:
        data = load_global_json(project_name)
    except (OSError, json.JSONDecodeError) as error:
        tk_alert.showerror('Error', f'Could not load Global.json:\n{error}')
        return

    state = _read_field('AddImage', '90')

    if state is None:
        tk_alert.showerror('Error', 'Image configure window is not open.')
        return

    if not state:
        tk_alert.showerror('Error', 'State cannot be empty.')
        return

    if state not in data.get('states', {}):
        tk_alert.showerror(
            'Error',
            f'State "{state}" does not exist. Add it first with "Add State".'
        )
        return

    image_name = _read_field('AddImage', '92')

    if not image_name:
        tk_alert.showerror('Error', 'Image name cannot be empty.')
        image_name = None

    if image_name and image_name not in (data.get('images') or {}):
        tk_alert.showerror(
            'Error',
            f'Image "{image_name}" does not exist in {project_name}. Add it first with "Add Image".'
        )
        image_name = None

    position = _read_pair_field(app, '94', 'Position', window='AddImage')
    width = _read_int_field(app, '96', 'Width', window='AddImage')
    height = _read_int_field(app, '98', 'Height', window='AddImage')
    border_radius = _read_int_field(app, '100', 'Border radius', minimum=0, window='AddImage')

    if (
        image_name is None
        or position is None
        or width is None
        or height is None
        or border_radius is None
    ):
        return

    image_entry = 'IMAGE(' + ','.join([
        f'image={image_name}',
        f'pos={_format_values(position)}',
        f'size={_format_values([width, height])}',
        f'border_radius={border_radius}',
    ]) + ')'

    was_editing = _edit_image_entry is not None

    components = data.setdefault('image_components', {})
    target = components.setdefault(state, [])

    if was_editing:
        edit_state, edit_index, old_entry = _edit_image_entry

        if state == edit_state:
            ### keep the image's place in the state's list
            if edit_index < len(target):
                target[edit_index] = image_entry
            else:
                target.append(image_entry)
        else:
            ### the image moved to another state, drop the old entry
            ### and append to the new state
            _remove_image_entry_from_data(data, _edit_image_entry)
            target.append(image_entry)
    else:
        target.append(image_entry)

    write_global_json(project_name, data)
    _edit_image_entry = None

    tk_alert.showinfo(
        'Saved',
        f'Image "{image_name}" updated in state "{state}".'
        if was_editing
        else f'Image "{image_name}" added to state "{state}".',
    )


def close_image_configure_window(app):
    ### Close button of the AddImage window
    render_gui.close_component_window('AddImage')


def _open_image_configure_window(app, title, prefill):
    ### open the AddImage window with the given field values pre-filled

    project_name = getattr(app, 'current_project', None)

    if not project_name:
        tk_alert.showerror('Error', 'No project is open.')
        return

    render_gui.close_component_window('AddImage')

    window = render_gui.open_component_window(
        'AddImage',
        title=title,
        geometry='420x440',
        text_font=[
            ('00', 20),
            ('91', 12),
            ('93', 12),
            ('95', 12),
            ('97', 12),
            ('99', 12),
            ('101', 12),
        ],
    )
    window.transient(app)

    def fill(entry_id, value):
        entry = render_gui.getInput('AddImage', entry_id)
        entry.delete(0, tk.END)
        entry.insert(0, str(value))

    for entry_id, value in prefill.items():
        fill(entry_id, value)


def _collect_image_entries(project_name):
    ### every placed image of the project as
    ### (state, index, entry_string, fields) tuples
    data = load_global_json(project_name)
    images = []

    for state, entries in (data.get('image_components') or {}).items():
        for index, entry in enumerate(entries or []):
            if not isinstance(entry, str) or not entry.startswith('IMAGE('):
                continue

            images.append((
                state,
                index,
                entry,
                _parse_button_fields(entry),
            ))

    return images


def _remove_image_entry_from_data(data, entry_ref):
    ### drop the picked image entry from in-memory Global.json data so the
    ### following append replaces it instead of duplicating it

    state, index, old_entry = entry_ref
    entries = (data.get('image_components') or {}).get(state) or []

    if index < len(entries) and entries[index] == old_entry:
        del entries[index]


def _open_image_picker(app, title, on_picked):
    ### list every placed image of the open project and let the user pick
    ### one; on_picked is called with the picked
    ### (state, index, entry, fields) tuple

    project_name = getattr(app, 'current_project', None)

    if not project_name:
        tk_alert.showerror('Error', 'No project is open.')
        return

    try:
        images = _collect_image_entries(project_name)
    except (OSError, json.JSONDecodeError) as error:
        tk_alert.showerror('Error', f'Could not load Global.json:\n{error}')
        return

    if not images:
        tk_alert.showinfo('Info', f'There are no images in "{project_name}" yet.')
        return

    picker = tk.Toplevel(app)
    picker.title(title)
    picker.transient(app)
    picker.resizable(False, False)

    try:
        picker.grab_set()
    except tk.TclError:
        pass

    ### make sure the picker opens on top of the main window with focus
    try:
        picker.update_idletasks()
        picker.lift()
    except tk.TclError:
        pass

    listbox = tk.Listbox(
        picker,
        height=min(12, max(4, len(images))),
        width=40,
        selectborderwidth=2
    )

    for state, index, _, fields in images:
        listbox.insert(tk.END, f'{state} : {fields.get("image", "")}')

    if len(images) == 1:
        listbox.selection_set(0)

    listbox.pack(padx=10, pady=(10, 4))

    def pick():
        selection = listbox.curselection()

        if not selection:
            tk_alert.showerror('Error', 'Select an image first.')
            return

        picker.destroy()
        on_picked(images[selection[0]])

    select = tk.Button(picker, text='Select', command=pick, width=10)
    select.pack(pady=4)

    cancel = tk.Button(picker, text='Cancel', command=picker.destroy, width=10)
    cancel.pack(pady=(0, 10))


def add_text(app):
    ### Add Text button of the InProject page
    ### opens a window to configure a new text label, then stores it in
    ### the chosen state of the project Global.json

    global _edit_text_entry

    project_name = getattr(app, 'current_project', None)

    if not project_name:
        tk_alert.showerror('Error', 'No project is open.')
        return

    try:
        data = load_global_json(project_name)
    except (OSError, json.JSONDecodeError) as error:
        tk_alert.showerror('Error', f'Could not load Global.json:\n{error}')
        return

    ### configuring a new text, drop any edit that was in progress
    _edit_text_entry = None

    render_gui.close_component_window('AddText')

    window = render_gui.open_component_window(
        'AddText',
        title=f'Add Text : {project_name}',
        geometry='420x420',
        text_font=[
            ('00', 20),
            ('61', 12),
            ('63', 12),
            ('65', 12),
            ('67', 12),
            ('69', 12),
            ('71', 12),
        ],
    )
    window.transient(app)

    def fill(entry_id, value):
        entry = render_gui.getInput('AddText', entry_id)
        entry.delete(0, tk.END)
        entry.insert(0, value)

    fill('60', next(iter(data.get('states') or {'main': []}), 'main'))
    fill('62', 'text')
    fill('64', 'base_font')
    fill('66', '32')
    fill('68', '0,0,0')
    fill('70', '0.5,0.2')


def edit_text(app):
    ### Edit Text button of the InProject page
    ### lets the user pick an existing text and pre-fills the
    ### AddText window with its fields; saving then replaces the entry

    global _edit_text_entry

    _edit_text_entry = None

    _open_text_picker(app, 'Edit Text', on_picked=lambda picked: _begin_text_edit(app, picked))


def _begin_text_edit(app, picked):
    ### picker callback of edit_text: remember the picked entry and open
    ### the AddText window pre-filled with the text's fields

    global _edit_text_entry

    state, index, entry_string, fields = picked

    _edit_text_entry = (state, index, entry_string)

    project_name = app.current_project

    render_gui.close_component_window('AddText')

    window = render_gui.open_component_window(
        'AddText',
        title=f'Edit Text : {project_name}',
        geometry='420x420',
        text_font=[
            ('00', 20),
            ('61', 12),
            ('63', 12),
            ('65', 12),
            ('67', 12),
            ('69', 12),
            ('71', 12),
        ],
    )
    window.transient(app)

    def fill(entry_id, value):
        entry = render_gui.getInput('AddText', entry_id)
        entry.delete(0, tk.END)
        entry.insert(0, value)

    fill('60', state)
    fill('62', fields.get('text') or '')
    fill('64', fields.get('font_name') or 'base_font')
    fill('66', fields.get('font_size') or '32')
    fill('68', _strip_brackets(fields.get('text_color') or '0,0,0'))
    fill('70', _strip_brackets(fields.get('pos') or '0.5,0.2'))


def remove_text(app):
    ### Remove Text button of the InProject page
    ### lets the user pick an existing text, then removes its entry
    ### from Global.json

    _open_text_picker(app, 'Remove Text', on_picked=lambda picked: _confirm_text_removal(app, picked))


def _confirm_text_removal(app, picked):
    state, index, entry_string, fields = picked
    project_name = app.current_project
    text = fields.get('text') or ''

    if not tk_alert.askyesno(
        'Remove Text',
        f'Remove text "{text}" from state "{state}"?'
    ):
        return

    try:
        data = load_global_json(project_name)
    except (OSError, json.JSONDecodeError) as error:
        tk_alert.showerror('Error', f'Could not load Global.json:\n{error}')
        return

    entries = (data.get('texts') or {}).get(state) or []

    if not (index < len(entries) and entries[index] == entry_string):
        tk_alert.showerror(
            'Error',
            'That text no longer exists in Global.json. It may have been changed.'
        )
        return

    del entries[index]
    write_global_json(project_name, data)
    tk_alert.showinfo('Removed', f'Text "{text}" removed from state "{state}".')


def save_text_configure(app):
    ### Save button of the AddText window
    ### writes the configured text into the chosen state of Global.json,
    ### replacing the picked entry when a text is being edited

    global _edit_text_entry

    project_name = getattr(app, 'current_project', None)

    if not project_name:
        tk_alert.showerror('Error', 'No project is open.')
        return

    try:
        data = load_global_json(project_name)
    except (OSError, json.JSONDecodeError) as error:
        tk_alert.showerror('Error', f'Could not load Global.json:\n{error}')
        return

    state = _read_text_field(app, '60')

    if state is None:
        tk_alert.showerror('Error', 'Text configure window is not open.')
        return

    if not state:
        tk_alert.showerror('Error', 'State cannot be empty.')
        return

    if state not in data.get('states', {}):
        tk_alert.showerror(
            'Error',
            f'State "{state}" does not exist. Add it first with "Add State".'
        )
        return

    text = _read_text_field(app, '62')

    if not text:
        tk_alert.showerror('Error', 'Text cannot be empty.')
        return

    font_name = _read_text_field(app, '64')

    if not font_name:
        tk_alert.showerror('Error', 'Font name cannot be empty.')
        font_name = None

    if font_name and font_name != 'base_font' and font_name not in (data.get('fonts') or {}):
        tk_alert.showerror(
            'Error',
            f'Font "{font_name}" does not exist in {project_name}. Add it first with "Add Font".'
        )
        font_name = None

    font_size = _read_int_field(app, '66', 'Font size', window='AddText')
    text_color = _read_rgb_field(app, '68', 'Text color', window='AddText')
    position = _read_pair_field(app, '70', 'Position', window='AddText')

    if (
        font_name is None
        or font_size is None
        or text_color is None
        or position is None
    ):
        return

    text_entry = 'TEXT(' + ','.join([
        f'text={text}',
        f'pos={_format_values(position)}',
        f'font_name={font_name}',
        f'font_size={font_size}',
        f'text_color={_format_values(text_color)}',
    ]) + ')'

    was_editing = _edit_text_entry is not None

    texts = data.setdefault('texts', {})
    target = texts.setdefault(state, [])

    if was_editing:
        edit_state, edit_index, old_entry = _edit_text_entry

        if state == edit_state:
            ### keep the text's place in the state's list
            if edit_index < len(target):
                target[edit_index] = text_entry
            else:
                target.append(text_entry)
        else:
            ### the text moved to another state, drop the old entry
            ### and append to the new state
            _remove_text_entry_from_data(data, _edit_text_entry)
            target.append(text_entry)
    else:
        target.append(text_entry)

    write_global_json(project_name, data)
    _edit_text_entry = None

    tk_alert.showinfo(
        'Saved',
        f'Text "{text}" updated in state "{state}".'
        if was_editing
        else f'Text "{text}" added to state "{state}".',
    )


def close_text_configure_window(app):
    ### Close button of the AddText window
    render_gui.close_component_window('AddText')


def add_button(app):
    ### Add Button button of the InProject page
    ### opens a window to configure a new button, then stores it in the
    ### chosen state of the project Global.json

    global _edit_button_entry, _button_action_path

    project_name = getattr(app, 'current_project', None)

    if not project_name:
        tk_alert.showerror('Error', 'No project is open.')
        return

    try:
        data = load_global_json(project_name)
    except (OSError, json.JSONDecodeError) as error:
        tk_alert.showerror('Error', f'Could not load Global.json:\n{error}')
        return

    ### configuring a new button, drop any edit that was in progress
    _edit_button_entry = None
    _button_action_path = None

    render_gui.close_component_window('AddButton')
    render_gui.close_component_window('ButtonAction')

    window = render_gui.open_component_window(
        'AddButton',
        title=f'Add Button : {project_name}',
        geometry='420x480',
        text_font=[
            ('00', 20),
            ('21', 12),
            ('23', 12),
            ('25', 12),
            ('27', 12),
            ('29', 12),
            ('31', 12),
            ('33', 12),
            ('35', 12),
            ('37', 12),
        ],
    )
    window.transient(app)

    def fill(entry_id, value):
        entry = render_gui.getInput('AddButton', entry_id)
        entry.delete(0, tk.END)
        entry.insert(0, value)

    fill('20', next(iter(data.get('states') or {'main': []}), 'main'))
    fill('24', '255,255,0')
    fill('26', '200,200,200')
    fill('28', '0,0,0')
    fill('30', 'base_font')
    fill('32', '14')
    fill('34', '0.5,0.5')
    fill('36', '150,50')


def edit_button(app):
    ### Edit Button button of the InProject page
    ### lets the user pick an existing button and pre-fills the
    ### AddButton window with its fields; saving then replaces the entry

    global _edit_button_entry

    _edit_button_entry = None

    _open_button_picker(app, 'Edit Button', on_picked=lambda picked: _begin_button_edit(app, picked))


def _begin_button_edit(app, picked):
    ### picker callback of edit_button: remember the picked entry and open
    ### the AddButton window pre-filled with the button's fields

    global _edit_button_entry, _button_action_path

    state, index, entry_string, action_path, fields = picked

    _edit_button_entry = (state, index, entry_string)
    _button_action_path = action_path

    project_name = app.current_project

    render_gui.close_component_window('AddButton')
    render_gui.close_component_window('ButtonAction')

    window = render_gui.open_component_window(
        'AddButton',
        title=f'Edit Button : {project_name}',
        geometry='420x480',
        text_font=[
            ('00', 20),
            ('21', 12),
            ('23', 12),
            ('25', 12),
            ('27', 12),
            ('29', 12),
            ('31', 12),
            ('33', 12),
            ('35', 12),
            ('37', 12),
        ],
    )
    window.transient(app)

    def fill(entry_id, value):
        entry = render_gui.getInput('AddButton', entry_id)
        entry.delete(0, tk.END)
        entry.insert(0, value)

    fill('20', state)
    fill('22', fields.get('text') or '')
    fill('24', _strip_brackets(fields.get('hover_color') or '255,255,0'))
    fill('26', _strip_brackets(fields.get('base_color') or '200,200,200'))
    fill('28', _strip_brackets(fields.get('text_color') or '0,0,0'))
    fill('30', fields.get('font_name') or 'base_font')
    fill('32', fields.get('font_size') or '14')
    fill('34', _strip_brackets(fields.get('pos') or '0.5,0.5'))
    fill('36', _strip_brackets(fields.get('size') or '150,50'))


def remove_button(app):
    ### Remove Button button of the InProject page
    ### lets the user pick an existing button, then removes its entry
    ### from Global.json and its action pkl when no other button uses it

    _open_button_picker(app, 'Remove Button', on_picked=lambda picked: _confirm_button_removal(app, picked))


def _confirm_button_removal(app, picked):
    state, index, entry_string, action_path, fields = picked
    project_name = app.current_project
    button_text = fields.get('text') or ''

    if not tk_alert.askyesno(
        'Remove Button',
        f'Remove button "{button_text}" from state "{state}"?'
    ):
        return

    try:
        data = load_global_json(project_name)
    except (OSError, json.JSONDecodeError) as error:
        tk_alert.showerror('Error', f'Could not load Global.json:\n{error}')
        return

    entries = data.get('states', {}).get(state) or []

    if not (index < len(entries) and entries[index] and entries[index][0] == entry_string):
        tk_alert.showerror(
            'Error',
            'That button no longer exists in Global.json. It may have been changed.'
        )
        return

    del entries[index]

    ### delete the button's action pkl when no other button entry uses it
    if action_path:
        shared = any(
            isinstance(entry, (list, tuple)) and len(entry) > 1 and entry[1] == action_path
            for state_entries in data.get('states', {}).values()
            for entry in (state_entries or [])
        )

        if not shared:
            pkl_path = os.path.join('Projects', project_name, action_path)

            if os.path.isfile(pkl_path):
                os.remove(pkl_path)

    write_global_json(project_name, data)
    tk_alert.showinfo('Removed', f'Button "{button_text}" removed from state "{state}".')


def _remove_button_entry_from_data(data, entry_ref):
    ### drop the picked entry from in-memory Global.json data so the
    ### following append replaces it instead of duplicating it

    state, index, old_entry = entry_ref
    entries = data.get('states', {}).get(state) or []

    if index < len(entries):
        target = entries[index]

        if isinstance(target, (list, tuple)) and target and target[0] == old_entry:
            del entries[index]


def save_button_configure(app):
    ### Save button of the AddButton window
    ### writes the configured button (and its action pkl path) into the
    ### chosen state of Global.json

    global _button_action_path, _edit_button_entry

    project_name = getattr(app, 'current_project', None)

    if not project_name:
        tk_alert.showerror('Error', 'No project is open.')
        return

    try:
        data = load_global_json(project_name)
    except (OSError, json.JSONDecodeError) as error:
        tk_alert.showerror('Error', f'Could not load Global.json:\n{error}')
        return

    state = _read_button_field(app, '20')

    if state is None:
        tk_alert.showerror('Error', 'Button configure window is not open.')
        return

    if not state:
        tk_alert.showerror('Error', 'State cannot be empty.')
        return

    if state not in data.get('states', {}):
        tk_alert.showerror(
            'Error',
            f'State "{state}" does not exist. Add it first with "Add State".'
        )
        return

    text = _read_button_field(app, '22')

    if not text:
        tk_alert.showerror('Error', 'Button text cannot be empty.')
        return

    hover_color = _read_rgb_field(app, '24', 'Hover color')
    base_color = _read_rgb_field(app, '26', 'Base color')
    text_color = _read_rgb_field(app, '28', 'Text color')
    font_name = _read_button_field(app, '30')

    if not font_name:
        tk_alert.showerror('Error', 'Font name cannot be empty.')
        font_name = None

    if font_name and font_name != 'base_font' and font_name not in (data.get('fonts') or {}):
        tk_alert.showerror(
            'Error',
            f'Font "{font_name}" does not exist in {project_name}. Add it first with "Add Font".'
        )
        font_name = None

    font_size = _read_int_field(app, '32', 'Font size')
    position = _read_pair_field(app, '34', 'Position')
    size = _read_pair_field(app, '36', 'Size', integer=True, minimum=1)

    if (
        hover_color is None
        or base_color is None
        or text_color is None
        or font_name is None
        or font_size is None
        or position is None
        or size is None
    ):
        return

    button_entry = 'BUTTON(' + ','.join([
        f'text={text}',
        f'pos={_format_values(position)}',
        f'size={_format_values(size)}',
        f'font_name={font_name}',
        f'font_size={font_size}',
        f'base_color={_format_values(base_color)}',
        f'hover_color={_format_values(hover_color)}',
        f'text_color={_format_values(text_color)}',
    ]) + ')'

    ### if the action window is open its code box decides the button's
    ### action: written code is pickled now, a cleared box removes the
    ### stored action
    try:
        action_code = render_gui.getCodeValue('ButtonAction', '44').strip()
    except (KeyError, RuntimeError):
        action_code = None

    if action_code is not None:
        if action_code:
            if action_code != _load_action_source(app, _button_action_path):
                save_button_action(app)
        else:
            _button_action_path = None

    was_editing = _edit_button_entry is not None

    if was_editing:
        edit_state, edit_index, old_entry = _edit_button_entry

        if state == edit_state:
            ### keep the button's place in the state's list
            entries = data.get('states', {}).get(state) or []
            new_entry = [button_entry, _button_action_path]

            if edit_index < len(entries):
                entries[edit_index] = new_entry
            else:
                entries.append(new_entry)
        else:
            ### the button moved to another state, drop the old entry
            ### and append to the new state
            _remove_button_entry_from_data(data, _edit_button_entry)
            data['states'][state].append([button_entry, _button_action_path])
    else:
        data['states'][state].append([button_entry, _button_action_path])

    write_global_json(project_name, data)
    _button_action_path = None
    _edit_button_entry = None

    tk_alert.showinfo(
        'Saved',
        f'Button "{text}" updated in state "{state}".'
        if was_editing
        else f'Button "{text}" added to state "{state}".',
    )


def close_button_configure_window(app):
    ### Close button of the ButtonConfigure window
    render_gui.close_component_window('AddButton')


def open_button_action_window(app):
    ### Write Action button of the AddButton window
    ### opens a window to write the python action code of the new button

    project_name = getattr(app, 'current_project', None)

    render_gui.close_component_window('ButtonAction')

    title = f'Button Action : {project_name}' if project_name else 'Button Action'

    window = render_gui.open_component_window(
        'ButtonAction',
        title=title,
        geometry='520x460',
        text_font=[
            ('00', 20),
            ('43', 12),
        ],
    )
    window.transient(app)

    ### when editing, load the button's stored action code into the box
    if _edit_button_entry is not None:
        source = _load_action_source(app, _button_action_path)

        if source:
            render_gui.getCode('ButtonAction', '44').insert('1.0', source)


def save_button_action(app):
    ### Save button of the ButtonAction window
    ### validates the written code, pickles the source text (not the
    ### function object, code objects cannot be pickled) and remembers the
    ### pkl path for the button that is being configured

    global _button_action_path

    try:
        code = render_gui.getCodeValue('ButtonAction', '44')
    except (KeyError, RuntimeError):
        tk_alert.showerror('Error', 'Action window is not open.')
        return

    if code.strip():
        ### exec the code to validate it defines a function; what we
        ### actually store is the source text, the game process execs it
        if _compile_button_action_code(code) is None:
            return

        source = code
    else:
        source = ''

    button_text = _read_button_field(app, '22') or ''

    path = _store_button_action_pickle(
        getattr(app, 'current_project', None),
        button_text,
        source,
    )

    if path is None:
        return

    _button_action_path = path
    tk_alert.showinfo('Saved', f'Action saved to {path}.')


def close_button_action_window(app):
    ### Close button of the ButtonAction window
    render_gui.close_component_window('ButtonAction')


def _compile_button_action_code(code):
    ### exec the user code in the app module namespace and return the
    ### function object that the code defines

    tracked = {
        name: id(value)
        for name, value in globals().items()
        if callable(value)
    }

    try:
        exec(compile(code, '<button_action>', 'exec'), globals())
    except Exception as error:
        tk_alert.showerror('Error', f'Invalid action code:\n{error}')
        return None

    for name, value in globals().items():
        if not callable(value) or name.startswith('_'):
            continue

        if tracked.get(name) != id(value):
            return value

    tk_alert.showerror('Error', 'The action code must define a function.')
    return None


def _store_button_action_pickle(project_name, button_text, code):
    ### pickle the action source text into the project action folder, the
    ### file name is the button text, then the next_id and the .pkl
    ### extension. the game process execs the source with its own Global
    ### to rebuild the action function

    folder = f'Projects/{project_name}/{project_name}Assets/Action'

    os.makedirs(folder, exist_ok=True)

    def trailing_id(name):
        digits = ''

        for char in reversed(name[:-4]):
            if char.isdigit():
                digits = char + digits
            else:
                break

        return int(digits) if digits else None

    existing = [
        value
        for value in (
            trailing_id(name)
            for name in os.listdir(folder)
            if name.endswith('.pkl')
        )
        if value is not None
    ]

    next_id = max(existing) + 1 if existing else 1

    with open(f'{folder}/{button_text}{next_id}.pkl', 'wb') as file:
        pickle.dump(code, file)

    return f'{project_name}Assets/Action/{button_text}{next_id}.pkl'


def _format_values(values):
    return '[' + ','.join(str(value) for value in values) + ']'


def _read_button_field(app, entry_id):
    try:
        return render_gui.getInput('AddButton', entry_id).get().strip()
    except (KeyError, RuntimeError):
        return None


def _read_text_field(app, entry_id):
    try:
        return render_gui.getInput('AddText', entry_id).get().strip()
    except (KeyError, RuntimeError):
        return None


def _read_field(window, entry_id):
    try:
        return render_gui.getInput(window, entry_id).get().strip()
    except (KeyError, RuntimeError):
        return None


def _read_int_field(app, entry_id, label, minimum=1, maximum=4096, window='AddButton'):
    raw = _read_field(window, entry_id)

    if raw is None:
        return None

    try:
        value = int(raw)
    except ValueError:
        tk_alert.showerror('Error', f'{label} must be a number.')
        return None

    if value < minimum:
        tk_alert.showerror('Error', f'{label} must be at least {minimum}.')
        return None

    if value > maximum:
        tk_alert.showerror('Error', f'{label} must be at most {maximum}.')
        return None

    return value


def _read_rgb_field(app, entry_id, label, window='AddButton'):
    raw = _read_field(window, entry_id)

    if raw is None:
        return None

    parts = [part.strip() for part in raw.split(',')]

    if len(parts) != 3:
        tk_alert.showerror('Error', f'{label} must be in the form "r,g,b".')
        return None

    try:
        values = [int(part) for part in parts]
    except ValueError:
        tk_alert.showerror('Error', f'{label} values must be whole numbers.')
        return None

    if any(value < 0 or value > 255 for value in values):
        tk_alert.showerror('Error', f'{label} values must be between 0 and 255.')
        return None

    return values


def _read_pair_field(app, entry_id, label, integer=False, minimum=None, window='AddButton'):
    raw = _read_field(window, entry_id)

    if raw is None:
        return None

    parts = [part.strip() for part in raw.split(',')]

    if len(parts) != 2:
        tk_alert.showerror('Error', f'{label} must be in the form "a,b".')
        return None

    values = []

    for part in parts:
        if integer:
            try:
                value = int(part)
            except ValueError:
                tk_alert.showerror('Error', f'{label} values must be whole numbers.')
                return None
        else:
            try:
                float(part)
            except ValueError:
                tk_alert.showerror('Error', f'{label} values must be numbers.')
                return None
            value = part

        if minimum is not None and float(part) < minimum:
            tk_alert.showerror('Error', f'{label} values must be at least {minimum}.')
            return None

        values.append(value)

    return values


def _split_top_level(text):
    ### split on commas that are not inside [ ] (mirror of the game's parser)
    parts, depth, current = [], 0, ''

    for char in text:
        if char == '[':
            depth += 1
        elif char == ']':
            depth -= 1

        if char == ',' and depth == 0:
            parts.append(current)
            current = ''
        else:
            current += char

    if current:
        parts.append(current)

    return parts


def _parse_button_fields(entry_string):
    ### extract the key/value pairs of a component entry string, either
    ### BUTTON(key=value,...), TEXT(key=value,...) or
    ### IMAGE(key=value,...)
    if not isinstance(entry_string, str):
        return {}

    if not entry_string.startswith(('BUTTON(', 'TEXT(', 'IMAGE(')):
        return {}

    body = entry_string[entry_string.index('(') + 1:-1]
    fields = {}

    for part in _split_top_level(body):
        key, _, value = part.partition('=')
        fields[key.strip()] = value.strip()

    return fields


def _collect_button_entries(project_name):
    ### every button entry of the project as
    ### (state, index, entry_string, action_path, fields) tuples
    data = load_global_json(project_name)
    buttons = []

    for state, entries in (data.get('states') or {}).items():
        for index, entry in enumerate(entries or []):
            if not isinstance(entry, (list, tuple)) or not entry:
                continue

            entry_string = entry[0]

            buttons.append((
                state,
                index,
                entry_string,
                entry[1] if len(entry) > 1 else None,
                _parse_button_fields(entry_string),
            ))

    return buttons


def _collect_text_entries(project_name):
    ### every text entry of the project as
    ### (state, index, entry_string, fields) tuples
    data = load_global_json(project_name)
    texts = []

    for state, entries in (data.get('texts') or {}).items():
        for index, entry in enumerate(entries or []):
            if not isinstance(entry, str) or not entry.startswith('TEXT('):
                continue

            texts.append((
                state,
                index,
                entry,
                _parse_button_fields(entry),
            ))

    return texts


def _remove_text_entry_from_data(data, entry_ref):
    ### drop the picked text entry from in-memory Global.json data so the
    ### following append replaces it instead of duplicating it

    state, index, old_entry = entry_ref
    entries = (data.get('texts') or {}).get(state) or []

    if index < len(entries) and entries[index] == old_entry:
        del entries[index]


def _open_button_picker(app, title, on_picked):
    ### list every button of the open project and let the user pick one;
    ### on_picked is called with the picked (state, index, entry, action, fields) tuple
    project_name = getattr(app, 'current_project', None)

    if not project_name:
        tk_alert.showerror('Error', 'No project is open.')
        return

    try:
        buttons = _collect_button_entries(project_name)
    except (OSError, json.JSONDecodeError) as error:
        tk_alert.showerror('Error', f'Could not load Global.json:\n{error}')
        return

    if not buttons:
        tk_alert.showinfo('Info', f'There are no buttons in "{project_name}" yet.')
        return

    picker = tk.Toplevel(app)
    picker.title(title)
    picker.transient(app)
    picker.resizable(False, False)

    try:
        picker.grab_set()
    except tk.TclError:
        pass

    ### make sure the picker opens on top of the main window with focus
    try:
        picker.update_idletasks()
        picker.lift()
    except tk.TclError:
        pass

    listbox = tk.Listbox(
        picker,
        height=min(12, max(4, len(buttons))),
        width=48,
        selectborderwidth=2
    )

    for state, index, _, _, fields in buttons:
        listbox.insert(tk.END, f'{state} : {fields.get("text", "")}')

    if len(buttons) == 1:
        listbox.selection_set(0)

    listbox.pack(padx=10, pady=(10, 4))

    def pick():
        selection = listbox.curselection()

        if not selection:
            tk_alert.showerror('Error', 'Select a button first.')
            return

        picker.destroy()
        on_picked(buttons[selection[0]])

    select = tk.Button(picker, text='Select', command=pick, width=10)
    select.pack(pady=4)

    cancel = tk.Button(picker, text='Cancel', command=picker.destroy, width=10)
    cancel.pack(pady=(0, 10))


def _open_text_picker(app, title, on_picked):
    ### list every text of the open project and let the user pick one;
    ### on_picked is called with the picked (state, index, entry, fields) tuple
    project_name = getattr(app, 'current_project', None)

    if not project_name:
        tk_alert.showerror('Error', 'No project is open.')
        return

    try:
        texts = _collect_text_entries(project_name)
    except (OSError, json.JSONDecodeError) as error:
        tk_alert.showerror('Error', f'Could not load Global.json:\n{error}')
        return

    if not texts:
        tk_alert.showinfo('Info', f'There are no texts in "{project_name}" yet.')
        return

    picker = tk.Toplevel(app)
    picker.title(title)
    picker.transient(app)
    picker.resizable(False, False)

    try:
        picker.grab_set()
    except tk.TclError:
        pass

    ### make sure the picker opens on top of the main window with focus
    try:
        picker.update_idletasks()
        picker.lift()
    except tk.TclError:
        pass

    listbox = tk.Listbox(
        picker,
        height=min(12, max(4, len(texts))),
        width=48,
        selectborderwidth=2
    )

    for state, index, _, fields in texts:
        listbox.insert(tk.END, f'{state} : {fields.get("text", "")}')

    if len(texts) == 1:
        listbox.selection_set(0)

    listbox.pack(padx=10, pady=(10, 4))

    def pick():
        selection = listbox.curselection()

        if not selection:
            tk_alert.showerror('Error', 'Select a text first.')
            return

        picker.destroy()
        on_picked(texts[selection[0]])

    select = tk.Button(picker, text='Select', command=pick, width=10)
    select.pack(pady=4)

    cancel = tk.Button(picker, text='Cancel', command=picker.destroy, width=10)
    cancel.pack(pady=(0, 10))


def _strip_brackets(raw):
    raw = (raw or '').strip()

    if raw.startswith('[') and raw.endswith(']'):
        raw = raw[1:-1].strip()

    return raw


def _load_action_source(app, action_path):
    ### read the pickled action source text of a stored button action so
    ### it can be shown in the ButtonAction window
    if not action_path:
        return None

    project_name = getattr(app, 'current_project', None)

    if not project_name:
        return None

    full_path = os.path.join('Projects', project_name, action_path)

    if not os.path.isfile(full_path):
        return None

    try:
        with open(full_path, 'rb') as file:
            loaded = pickle.load(file)
    except (OSError, EOFError, pickle.UnpicklingError):
        return None

    return loaded if isinstance(loaded, str) else None


def run_project(name):
    ### WARNING DON'T CHANGE THIS FUNCTION!
    sub.Popen([sys.executable, f'{name}.py'], cwd=f'Projects/{name}')

app = EGameMaker()

### using assets
game_name = None
render_gui.init_app(app)

app.run()
