### Headless test of the "Add Font" and "Remove Font" flows, and of the
### font-name validation when adding a button.
### Monkeypatches mainloop so the module import does not block.

import os
import json
import sys
import shutil
import pickle
import tkinter as tk
from tkinter import simpledialog

# Create a throwaway project with a button that wants the custom font
# "funky" so the removal blocking is covered
shutil.rmtree('Projects/fontGame', ignore_errors=True)
os.makedirs('Projects/fontGame/fontGameAssets', exist_ok=True)
with open('Projects/fontGame/fontGameAssets/Global.json', 'w') as f:
    json.dump({
        "fullscreen": False,
        "title": "fontGame",
        "states": {
            "main": [
                [
                    "BUTTON(text=go,pos=[0.5,0.5],size=[150,50],font_name=funky,font_size=14,base_color=[200,200,200],hover_color=[255,255,0],text_color=[0,0,0])",
                    None,
                ]
            ]
        },
    }, f)

# A fake font file for the copy step
fake_font = '/tmp/opencode/fake_font.ttf'
os.makedirs('/tmp/opencode', exist_ok=True)
with open(fake_font, 'w') as f:
    f.write('fake ttf bytes')

tk.Tk.mainloop = lambda self, *a, **k: None

sys.path.insert(0, '.')
import EGameMaker as egm

app = egm.app

### the InProject action pkls must be (re)created in this process, pkls
### written by a direct app run reference __main__ and cannot be loaded
### here
for pkl_id in ('013', '014'):
    stale = f'Assets/Action/InProject/{pkl_id}.pkl'
    if os.path.isfile(stale):
        os.remove(stale)

# Simulate opening a project
egm.OpenProjectAction('fontGame')(app)
assert app.current_project == 'fontGame', app.current_project

with open('Assets/Action/InProject/013.pkl', 'rb') as f:
    add = pickle.load(f)
with open('Assets/Action/InProject/014.pkl', 'rb') as f:
    remove = pickle.load(f)

assert add.__name__ == 'add_font', add
assert remove.__name__ == 'remove_font', remove

# Keep the tests out of the dialogs: scripted answers, no real pickers
egm.tk_alert.showinfo = lambda *a, **k: None
egm.tk_alert.showerror = lambda *a, **k: None
egm.tk_alert.showwarning = lambda *a, **k: None
egm.tk_alert.askyesno = lambda *a, **k: True

askstring_answers = ['funky', 'funky', 'neat']
egm.simpledialog.askstring = lambda *a, **k: (
    askstring_answers.pop(0) if askstring_answers else None
)
egm.tk.filedialog.askopenfilename = lambda *a, **k: fake_font

# # # # Add font flow # # # #

add(app)

data = egm.load_global_json('fontGame')
assert data.get('fonts') == {'funky': 'fontGameAssets/Fonts/funky.ttf'}, data
assert os.path.isfile('Projects/fontGame/fontGameAssets/Fonts/funky.ttf')

### a duplicate name must loop back to the name prompt, the new name
### goes through
add(app)

data = egm.load_global_json('fontGame')
assert data.get('fonts') == {
    'funky': 'fontGameAssets/Fonts/funky.ttf',
    'neat': 'fontGameAssets/Fonts/neat.ttf',
}, data

# # # # Button font-name validation # # # #

egm.add_button(app)

def set_input(entry_id, value):
    entry = egm.render_gui.getInput('AddButton', entry_id)
    entry.delete(0, tk.END)
    entry.insert(0, value)

set_input('20', 'main')
set_input('22', 'go2')
set_input('30', 'missing_font')

egm.save_button_configure(app)

data = egm.load_global_json('fontGame')
assert len(data['states']['main']) == 1, 'a button with an unknown font must be rejected'

set_input('30', 'funky')

egm.save_button_configure(app)

data = egm.load_global_json('fontGame')
assert len(data['states']['main']) == 2, data
assert 'font_name=funky' in data['states']['main'][1][0], data

# # # # Remove font flow # # # #

### "funky" is used by a button, it must not be removable
real_font_picker = egm._open_font_picker
egm._open_font_picker = lambda app_, on_picked: on_picked('funky')

remove(app)

data = egm.load_global_json('fontGame')
assert 'funky' in data.get('fonts', {}), 'a font in use must not be removed'
assert os.path.isfile('Projects/fontGame/fontGameAssets/Fonts/funky.ttf')

### no button uses it anymore, removal goes through and deletes the file
data = egm.load_global_json('fontGame')
data['states']['main'] = []
egm.write_global_json('fontGame', data)

remove(app)

data = egm.load_global_json('fontGame')
assert data.get('fonts') == {'neat': 'fontGameAssets/Fonts/neat.ttf'}, data
assert not os.path.isfile('Projects/fontGame/fontGameAssets/Fonts/funky.ttf')

### the real font picker must build without error and list the fonts
real_font_picker(app, on_picked=lambda *picked: None)
pickers = [
    w for w in app.winfo_children()
    if isinstance(w, tk.Toplevel) and w.title() == 'Pick Font'
]
assert pickers, 'font picker window was not created'
picker_listboxes = [
    child for child in pickers[0].winfo_children()
    if isinstance(child, tk.Listbox)
]
assert len(picker_listboxes) == 1, 'font picker has no listbox'
items = picker_listboxes[0].get(0, tk.END)
assert items == ('neat',), items
for picker in pickers:
    picker.destroy()

# # # # Clean up # # # #

egm.remove_current_project(app)
assert not os.path.isdir('Projects/fontGame')
egm.render_gui.removeTextComponent('InProject.GUI', '01')

### let the next app run regenerate the InProject pkls in its own context
for pkl_id in ('013', '014'):
    stale = f'Assets/Action/InProject/{pkl_id}.pkl'
    if os.path.isfile(stale):
        os.remove(stale)

os.remove(fake_font)

print('ALL CHECKS PASSED')
app.destroy()
