### Headless test of the "Remove Project" flow.
### Monkeypatches mainloop so the module import does not block.

import os
import json
import sys
import tkinter as tk

# Create a throwaway project so the flow has something to act on.
os.makedirs('Projects/demoGame/demoGameAssets', exist_ok=True)
with open('Projects/demoGame/demoGameAssets/Global.json', 'w') as f:
    json.dump({"fullscreen": False, "title": "demoGame"}, f)

tk.Tk.mainloop = lambda self, *a, **k: None

sys.path.insert(0, '.')
import EGameMaker as egm

app = egm.app

# Simulate opening a project
egm.OpenProjectAction('demoGame')(app)
assert app.current_project == 'demoGame', app.current_project
assert app.current_page == 'InProject', app.current_page

# The Remove Project button must exist in the InProject page content
btns = [l for l in egm.render_gui.content['InProject'] if l.startswith('BUTTON=')]
assert any('Remove Project' in l for l in btns), btns

# The 009.pkl action must have been created on startup
assert os.path.isfile('Assets/Action/InProject/009.pkl')

# Load the pickled action exactly like the renderer would and run it.
with open('Assets/Action/InProject/009.pkl', 'rb') as f:
    remove = __import__('pickle').load(f)

egm.tk_alert.askyesno = lambda *a, **k: True
remove(app)

# After removal
assert app.current_project is None, app.current_project
assert app.current_page == 'MainPage', app.current_page
assert not os.path.isdir('Projects/demoGame'), 'project dir still present'

# MainPage should show the "no projects" text again
mp = egm.render_gui.content['MainPage']
assert any("You don't have any projects" in l for l in mp), mp

# Stale project pkl removed
assert not os.path.isfile('Assets/Action/MainPage/demoGame.pkl')

# Keep the .GUI files clean for the next run
egm.render_gui.removeTextComponent('InProject.GUI', '01')

print('ALL CHECKS PASSED')
app.destroy()
