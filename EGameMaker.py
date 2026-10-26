
### FREE AND OPEN-SOURCE
### EGameMaker
### Libraries that used for this project :
###  - tkinter
###  - pygame
### ---------------------------------------------

import os
import pickle
import tkinter as tk
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

        projects = os.listdir('Projects')
        if len(projects) < 1:
            render_gui.addTextComponent('MainPage.GUI', "You don't have any projects...", ('0.02', '0.15'), '02')

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

        if not os.path.exists(path) or os.path.getsize(path) == 0:
            with open(path, 'wb') as file:
                pickle.dump(create_project, file)

        with open(path, 'rb') as file:
            func = pickle.load(file)

        func(self)

    def change_page(self, new_state, text_font=None):
        for component in self.components:
            if component.winfo_exists():
                component.destroy()

        self.components.clear()

        self.current_page = new_state
        render_gui.render(self.current_page, text_font or [])

        self.components = self.winfo_children()

    def run(self):
        render_gui.render('MainPage', [('01', 30)])
        self.components = self.winfo_children()
        self.maximize()
        self.mainloop()


def create_project(app):
    app.change_page('NewProject')


app = EGameMaker()

### using assets
render_gui.init_app(app)

app.run()
