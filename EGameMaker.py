### FREE AND OPEN-SOURCE
### EGameMaker
### Libraries that used for this project :
###  - tkinter
###  - pygame
### ---------------------------------------------

import os
import tkinter as tk
from Assets.GUI.Render.RenderGUIComponent import RenderGUIComponent





render_gui = RenderGUIComponent()


class EGameMaker(tk.Tk):
    ### main class of GUI

    def __init__(self):
        super().__init__()
        self.geometry(f"{self.winfo_screenwidth()}x{self.winfo_screenheight()}")
        self.title('EGameMaker : Game maker engine')
        self.after(100, self.maximize)
        render_gui.init_app(self)
        render_gui.init_font()

        projects = os.listdir('Projects')
        if len(projects) < 1:
            render_gui.addTextComponent('MainPage.GUI',"You don't have any projects...", ('0.02','0.15'), '02')

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

    def run(self):
        render_gui.render('MainPage',[('01',30)])
        self.maximize()
        self.mainloop()

app = EGameMaker()

### using assets
state = 'MainPage'
render_gui.init_app(app)

app.run()