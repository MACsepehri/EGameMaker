### Headless test of the "Add Text", "Edit Text" and "Remove Text" flows,
### and of the font-name validation for text components.
### Monkeypatches mainloop so the module import does not block.

import os
import json
import sys
import shutil
import pickle
import tkinter as tk

# Create a throwaway project with a registered font but no texts yet
# (no "texts" key at all, to cover the setdefault path)
shutil.rmtree('Projects/textGame', ignore_errors=True)
os.makedirs('Projects/textGame/textGameAssets/Fonts', exist_ok=True)
with open('Projects/textGame/textGameAssets/Global.json', 'w') as f:
    json.dump({
        "fullscreen": False,
        "title": "textGame",
        "fonts": {"funky": "textGameAssets/Fonts/funky.ttf"},
        "states": {
            "main": []
        },
    }, f)

with open('Projects/textGame/textGameAssets/Fonts/funky.ttf', 'w') as f:
    f.write('fake ttf bytes')

tk.Tk.mainloop = lambda self, *a, **k: None

sys.path.insert(0, '.')
import EGameMaker as egm

app = egm.app

### the InProject action pkls must be (re)created in this process, pkls
### written by a direct app run reference __main__ and cannot be loaded
### here
for pkl_id in ('015', '016', '017'):
    stale = f'Assets/Action/InProject/{pkl_id}.pkl'
    if os.path.isfile(stale):
        os.remove(stale)

# Simulate opening a project
egm.OpenProjectAction('textGame')(app)
assert app.current_project == 'textGame', app.current_project

with open('Assets/Action/InProject/015.pkl', 'rb') as f:
    add = pickle.load(f)
with open('Assets/Action/InProject/016.pkl', 'rb') as f:
    edit = pickle.load(f)
with open('Assets/Action/InProject/017.pkl', 'rb') as f:
    remove = pickle.load(f)

assert add.__name__ == 'add_text', add
assert edit.__name__ == 'edit_text', edit
assert remove.__name__ == 'remove_text', remove

# Keep the tests out of the dialogs and the interactive picker
egm.tk_alert.showinfo = lambda *a, **k: None
egm.tk_alert.showerror = lambda *a, **k: None
egm.tk_alert.askyesno = lambda *a, **k: True

def fake_picker(app_, title, on_picked):
    current = egm._collect_text_entries(app_.current_project)
    assert current, 'no texts found for the picker'
    on_picked(current[0])

real_picker = egm._open_text_picker
egm._open_text_picker = fake_picker

# # # # Add text flow # # # #

add(app)

def input_value(entry_id):
    return egm.render_gui.getInput('AddText', entry_id).get()

### the AddText window must be pre-filled with the defaults
assert input_value('60') == 'main'
assert input_value('62') == 'text'
assert input_value('64') == 'base_font'
assert input_value('66') == '32'
assert input_value('68') == '0,0,0'
assert input_value('70') == '0.5,0.2'

def set_input(entry_id, value):
    entry = egm.render_gui.getInput('AddText', entry_id)
    entry.delete(0, tk.END)
    entry.insert(0, value)

### an unknown font name must be rejected
set_input('62', 'hello')
set_input('64', 'missing_font')

egm.save_text_configure(app)

data = egm.load_global_json('textGame')
assert not data.get('texts', {}).get('main'), 'a text with an unknown font must be rejected'

### the registered font goes through
set_input('64', 'funky')

egm.save_text_configure(app)

data = egm.load_global_json('textGame')
main = data['texts']['main']
assert len(main) == 1, main
assert main[0].startswith('TEXT(text=hello,'), main[0]
assert 'font_name=funky' in main[0], main[0]
assert 'font_size=32' in main[0], main[0]
assert egm._edit_text_entry is None

# # # # Edit text flow # # # #

edit(app)

state, index, entry_string = egm._edit_text_entry
assert (state, index) == ('main', 0), (state, index)
assert entry_string == main[0], entry_string

### the AddText window must be pre-filled with the text's values
assert input_value('60') == 'main'
assert input_value('62') == 'hello'
assert input_value('64') == 'funky'
assert input_value('66') == '32'
assert input_value('68') == '0,0,0'
assert input_value('70') == '0.5,0.2'

### change the content and position, saving must replace in place
set_input('62', 'welcome')
set_input('70', '0.1,0.9')

egm.save_text_configure(app)

data = egm.load_global_json('textGame')
main = data['texts']['main']
assert len(main) == 1, main
assert main[0].startswith('TEXT(text=welcome,'), main[0]
assert 'pos=[0.1,0.9]' in main[0], main[0]
assert 'font_name=funky' in main[0], main[0]
assert egm._edit_text_entry is None

# # # # Remove text flow # # # #

remove(app)

data = egm.load_global_json('textGame')
assert not data.get('texts', {}).get('main'), data

### the real text picker must build without error and list the texts
add(app)
set_input('62', 'one')
set_input('64', 'base_font')
egm.save_text_configure(app)
set_input('62', 'two')
egm.save_text_configure(app)

real_picker(app, 'Remove Text', on_picked=lambda *picked: None)
pickers = [
    w for w in app.winfo_children()
    if isinstance(w, tk.Toplevel) and w.title() == 'Remove Text'
]
assert pickers, 'text picker window was not created'
picker_listboxes = [
    child for child in pickers[0].winfo_children()
    if isinstance(child, tk.Listbox)
]
assert len(picker_listboxes) == 1, 'text picker has no listbox'
items = picker_listboxes[0].get(0, tk.END)
assert items == ('main : one', 'main : two'), items
for picker in pickers:
    picker.destroy()

# # # # Clean up # # # #

egm.remove_current_project(app)
assert not os.path.isdir('Projects/textGame')
egm.render_gui.removeTextComponent('InProject.GUI', '01')

### let the next app run regenerate the InProject pkls in its own context
for pkl_id in ('015', '016', '017'):
    stale = f'Assets/Action/InProject/{pkl_id}.pkl'
    if os.path.isfile(stale):
        os.remove(stale)

print('ALL CHECKS PASSED')
app.destroy()
