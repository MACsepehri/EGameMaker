### Headless test of the "Edit Button" and "Remove Button" flows.
### Monkeypatches mainloop so the module import does not block.

import os
import json
import sys
import shutil
import pickle
import tkinter as tk

# Create a throwaway project with two buttons: one with an action pkl,
# one without, so both branches of the flows are covered.
shutil.rmtree('Projects/demoGame', ignore_errors=True)
os.makedirs('Projects/demoGame/demoGameAssets/Action', exist_ok=True)
with open('Projects/demoGame/demoGameAssets/Global.json', 'w') as f:
    json.dump({
        "fullscreen": False,
        "title": "demoGame",
        "states": {
            "main": [
                [
                    "BUTTON(text=start,pos=[0.5,0.5],size=[150,50],font_name=base_font,font_size=14,base_color=[200,200,200],hover_color=[255,255,0],text_color=[0,0,0])",
                    "demoGameAssets/Action/start1.pkl",
                ],
                [
                    "BUTTON(text=quit,pos=[0.2,0.8],size=[100,40],font_name=base_font,font_size=12,base_color=[150,150,150],hover_color=[255,0,0],text_color=[255,255,255])",
                    None,
                ],
            ]
        },
    }, f)

with open('Projects/demoGame/demoGameAssets/Action/start1.pkl', 'wb') as f:
    pickle.dump('def start(self):\n    print("start")\n', f)

tk.Tk.mainloop = lambda self, *a, **k: None

sys.path.insert(0, '.')
import EGameMaker as egm

app = egm.app

### the InProject action pkls must be (re)created in this process, pkls
### written by a direct app run reference __main__ and cannot be loaded
### here
for pkl_id in ('011', '012'):
    stale = f'Assets/Action/InProject/{pkl_id}.pkl'
    if os.path.isfile(stale):
        os.remove(stale)

# Simulate opening a project
egm.OpenProjectAction('demoGame')(app)
assert app.current_project == 'demoGame', app.current_project
assert app.current_page == 'InProject', app.current_page

assert os.path.isfile('Assets/Action/InProject/011.pkl')
assert os.path.isfile('Assets/Action/InProject/012.pkl')

# Load the pickled actions exactly like the renderer would and run them.
with open('Assets/Action/InProject/011.pkl', 'rb') as f:
    edit = pickle.load(f)
with open('Assets/Action/InProject/012.pkl', 'rb') as f:
    remove = pickle.load(f)

assert edit.__name__ == 'edit_button', edit
assert remove.__name__ == 'remove_button', remove

# Keep the tests out of the dialogs and the interactive picker: pick the
# first button of the project as it is in Global.json at call time.
egm.tk_alert.showinfo = lambda *a, **k: None
egm.tk_alert.showerror = lambda *a, **k: None
egm.tk_alert.askyesno = lambda *a, **k: True

def fake_picker(app_, title, on_picked):
    current = egm._collect_button_entries(app_.current_project)
    assert current, 'no buttons found for the picker'
    on_picked(current[0])

real_picker = egm._open_button_picker
egm._open_button_picker = fake_picker

# # # # Edit flow # # # #

### the real picker must build without error, list both buttons and hand
### the picked one to its callback
picked = []

real_picker(app, 'Edit Button', on_picked=picked.append)
pickers = [
    w for w in app.winfo_children()
    if isinstance(w, tk.Toplevel) and w.title() == 'Edit Button'
]
assert pickers, 'picker window was not created'
picker_listboxes = [
    child for child in pickers[0].winfo_children()
    if isinstance(child, tk.Listbox)
]
assert len(picker_listboxes) == 1, 'picker has no listbox'
assert len(picker_listboxes[0].get(0, tk.END)) == 2, 'picker should list both buttons'

### select the second button and press the Select button
picker_listboxes[0].selection_clear(0, tk.END)
picker_listboxes[0].selection_set(1)
select_button = next(
    child for child in pickers[0].winfo_children()
    if isinstance(child, tk.Button) and child['text'] == 'Select'
)
select_button.invoke()

assert len(picked) == 1, picked
picked_state, picked_index, picked_entry, picked_action, picked_fields = picked[0]
assert picked_index == 1 and picked_fields['text'] == 'quit', picked[0]
assert picked_action is None, picked[0]

edit(app)

assert egm._edit_button_entry is not None
state, index, entry_string = egm._edit_button_entry
assert state == 'main' and index == 0
fields = egm._parse_button_fields(entry_string)
assert fields['text'] == 'start', fields
assert egm._button_action_path == 'demoGameAssets/Action/start1.pkl'

def input_value(entry_id):
    return egm.render_gui.getInput('AddButton', entry_id).get()

### the AddButton window must be pre-filled with the button's values
assert input_value('20') == 'main'
assert input_value('22') == 'start'
assert input_value('24') == '255,255,0'
assert input_value('26') == '200,200,200'
assert input_value('28') == '0,0,0'
assert input_value('30') == 'base_font'
assert input_value('32') == '14'
assert input_value('34') == '0.5,0.5'
assert input_value('36') == '150,50'

### change the text and size, saving must replace the entry in place
egm.render_gui.getInput('AddButton', '22').delete(0, tk.END)
egm.render_gui.getInput('AddButton', '22').insert(0, 'begin')
egm.render_gui.getInput('AddButton', '36').delete(0, tk.END)
egm.render_gui.getInput('AddButton', '36').insert(0, '200,60')

egm.save_button_configure(app)

data = egm.load_global_json('demoGame')
main = data['states']['main']
assert len(main) == 2, main
assert main[0][0].startswith('BUTTON(text=begin'), main[0]
assert 'size=[200,60]' in main[0][0], main[0]
assert main[0][1] == 'demoGameAssets/Action/start1.pkl', main[0]
assert main[1][0].startswith('BUTTON(text=quit'), main[1]
assert not any('text=start' in entry[0] for entry in main), main
assert egm._edit_button_entry is None
assert egm._button_action_path is None

# # # # Remove flow # # # #

### removing the first (edited) button must drop its entry and its pkl,
### and keep the other button untouched
remove(app)

data = egm.load_global_json('demoGame')
main = data['states']['main']
assert len(main) == 1, main
assert main[0][0].startswith('BUTTON(text=quit'), main
assert not os.path.isfile('Projects/demoGame/demoGameAssets/Action/start1.pkl')

# # # # Clean up # # # #

egm.remove_current_project(app)
assert not os.path.isdir('Projects/demoGame')
egm.render_gui.removeTextComponent('InProject.GUI', '01')

### let the next app run regenerate the InProject pkls in its own context
for pkl_id in ('011', '012'):
    stale = f'Assets/Action/InProject/{pkl_id}.pkl'
    if os.path.isfile(stale):
        os.remove(stale)

print('ALL CHECKS PASSED')
app.destroy()
