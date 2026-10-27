
### FREE AND OPEN-SOURCE
### EGameMaker
### Libraries that used for this project :
###  - tkinter
###  - pygame
### ---------------------------------------------

import os
import pickle
import tkinter as tk
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
        self.after(100, self.maximize)
        render_gui.init_app(self)
        render_gui.init_font()
        self.create_new_project()
        self.create_project_action()

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
        self.project_name = project_name

    def __call__(self, app):
        app.change_page('InProject', [('01', 30)])


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
        app.change_page('InProject', [('01', 30)])

def save_project(inp):
    ### IMPORTANT : DON'T CHANGE THIS FUNCTION!
    ###  - IN THIS FUNCTION BASE OF GAME WILL CREATE

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


    ### Creating project structure
    os.mkdir(projectPath)
    os.mkdir(projectPath+f'/{projectName}Assets')
    

    ### Saving basics
    with open(projectPath+f'/{projectName}.py', 'w') as file:
        file.write('print("hello world")')


app = EGameMaker()

### using assets
render_gui.init_app(app)

app.run()
