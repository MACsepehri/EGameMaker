### FREE AND OPEN-SOURCE
### EGameMaker
### Libraries that used for this project :
###  - tkinter
###  - pygame
### ---------------------------------------------

import tkinter as tk
from Assets.GUI.Render.RenderGUIComponent import RenderGUIComponent





class EGameMaker(tk.Tk):
    ### main class of GUI

    def __init__(self):
        super().__init__()
        self.geometry(f"{self.winfo_screenwidth()}x{self.winfo_screenheight()}")
        self.after(100, self.maximize)

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
        self.geometry(
            f'{self.winfo_screenwidth()}x{self.winfo_screenheight()}+0+0'
        )
        self.resizable(False, False)

    def run(self):
        self.maximize()
        self.mainloop()

app = EGameMaker()

### using assets
render_gui = RenderGUIComponent(_app=app)
render_gui.renderText('MainPage',[('01',30)])

app.run()