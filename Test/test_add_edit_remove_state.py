### Headless test of the "Add State", "Edit State" and "Remove State"
### flows. Monkeypatches mainloop so the module import does not block.

import os
import json
import sys
import shutil
import pickle
import tkinter as tk
from tkinter import simpledialog

# Create a throwaway project: one empty state plus a text inside it
shutil.rmtree('Projects/stateGame', ignore_errors=True)
os.makedirs('Projects/stateGame/stateGameAssets', exist_ok=True)
with open('Projects/stateGame/stateGameAssets/Global.json', 'w') as f:
    json.dump({
        "fullscreen": False,
        "title": "stateGame",
        "fonts": {},
        "texts": {
            "main": [
                "TEXT(text=hello,pos=[0.5,0.2],font_name=base_font,font_size=32,text_color=[0,0,0])"
            ]
        },
        "states": {
            "main": []
        },
    }, f)

tk.Tk.mainloop = lambda self, *a, **k: None

sys.path.insert(0, '.')
import EGameMaker as egm

app = egm.app

### the new InProject action pkls must be (re)created in this process
for pkl_id in ('018', '019'):
    stale = f'Assets/Action/InProject/{pkl_id}.pkl'
    if os.path.isfile(stale):
        os.remove(stale)

# Simulate opening a project
egm.OpenProjectAction('stateGame')(app)
assert app.current_project == 'stateGame', app.current_project

with open('Assets/Action/InProject/018.pkl', 'rb') as f:
    edit = pickle.load(f)
with open('Assets/Action/InProject/019.pkl', 'rb') as f:
    remove = pickle.load(f)

assert edit.__name__ == 'edit_state', edit
assert remove.__name__ == 'remove_state', remove

# Scripted dialog answers, no real pickers
egm.tk_alert.showinfo = lambda *a, **k: None
egm.tk_alert.showerror = lambda *a, **k: None
egm.tk_alert.askyesno = lambda *a, **k: True

askstring_answers = [
    None,       ### add: user cancels -> nothing happens
    '   ',      ### add: blank name -> rejected
    'level1',   ### add: valid
    'LEVEL1',   ### add: case-insensitive duplicate -> rejected
    'main2',    ### edit: rename main -> main2
    'main2',    ### edit: same name -> no-op
    'main2',    ### edit: level1 -> main2 already exists -> rejected
]
egm.simpledialog.askstring = lambda *a, **k: (
    askstring_answers.pop(0) if askstring_answers else None
)

pick_order = iter(['main', 'level1', 'level1', 'main2', 'empty'])
real_picker = egm._open_state_picker

def fake_state_picker(app_, title, on_picked):
    on_picked(next(pick_order))

egm._open_state_picker = fake_state_picker

def data():
    return egm.load_global_json('stateGame')

# # # # Add state flow # # # #

egm.add_state(app)
egm.add_state(app)
egm.add_state(app)
egm.add_state(app)

assert data()['states'] == {'main': [], 'level1': []}, data()['states']

# # # # Edit state flow # # # #

edit(app)

assert data()['states'] == {'level1': [], 'main2': []}, data()['states']
assert 'main2' in data()['texts'] and 'main' not in data()['texts'], data()['texts']
assert data()['texts']['main2'][0].startswith('TEXT(text=hello,'), data()['texts']

### renaming level1 onto the existing main2 must be rejected
edit(app)

assert data()['states'] == {'level1': [], 'main2': []}, data()['states']

# # # # Remove state flow # # # #

### a state with a button must not be removable
current = data()
current['states']['level1'].append([
    "BUTTON(text=go,pos=[0.5,0.5],size=[150,50],font_name=base_font,font_size=14,base_color=[200,200,200],hover_color=[255,255,0],text_color=[0,0,0])",
    None,
])
egm.write_global_json('stateGame', current)

remove(app)

assert 'level1' in data()['states'], 'a state with a button must not be removed'

### a state with a text must not be removable either
remove(app)

assert 'main2' in data()['states'], 'a state with a text must not be removed'

### an empty state goes through
current = data()
current['states']['empty'] = []
egm.write_global_json('stateGame', current)

remove(app)

assert 'empty' not in data()['states'], data()['states']
### level1 kept its button (removal was blocked), main2 kept its text
assert len(data()['states']['level1']) == 1, data()['states']
assert data()['states']['main2'] == [], data()['states']

### the real state picker must build without error and list the states
real_picker(app, 'Edit State', on_picked=lambda *picked: None)
pickers = [
    w for w in app.winfo_children()
    if isinstance(w, tk.Toplevel) and w.title() == 'Edit State'
]
assert pickers, 'state picker window was not created'
picker_listboxes = [
    child for child in pickers[0].winfo_children()
    if isinstance(child, tk.Listbox)
]
assert len(picker_listboxes) == 1, 'state picker has no listbox'
items = picker_listboxes[0].get(0, tk.END)
assert set(items) == {'level1', 'main2'}, items
for picker in pickers:
    picker.destroy()

# # # # Clean up # # # #

egm.remove_current_project(app)
assert not os.path.isdir('Projects/stateGame')
egm.render_gui.removeTextComponent('InProject.GUI', '01')

### let the next app run regenerate the InProject pkls in its own context
for pkl_id in ('018', '019'):
    stale = f'Assets/Action/InProject/{pkl_id}.pkl'
    if os.path.isfile(stale):
        os.remove(stale)

print('ALL CHECKS PASSED')
app.destroy()
