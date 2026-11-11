### Headless test of the "Add Image", "Edit Image" and "Remove Image"
### flows. Monkeypatches mainloop so the module import does not block.

import os
import json
import sys
import shutil
import struct
import zlib
import pickle
import tkinter as tk

# Create a throwaway project without any image keys yet
shutil.rmtree('Projects/imgGame', ignore_errors=True)
os.makedirs('Projects/imgGame/imgGameAssets', exist_ok=True)
with open('Projects/imgGame/imgGameAssets/Global.json', 'w') as f:
    json.dump({
        "fullscreen": False,
        "title": "imgGame",
        "states": {
            "main": []
        },
    }, f)

### a real minimal 4x4 RGBA png so the copy step has a valid file
def make_png(path, width=4, height=4):
    def chunk(chunk_type, payload):
        block = struct.pack('>I', len(payload)) + chunk_type + payload
        return block + struct.pack('>I', zlib.crc32(chunk_type + payload) & 0xFFFFFFFF)

    ihdr = struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0)
    raw = b''.join(b'\x00' + b'\xff\x00\x00\xff' * width for _ in range(height))
    png = b'\x89PNG\r\n\x1a\n'
    png += chunk(b'IHDR', ihdr)
    png += chunk(b'IDAT', zlib.compress(raw))
    png += chunk(b'IEND', b'')
    with open(path, 'wb') as f:
        f.write(png)

fake_image = '/tmp/opencode/logo.png'
os.makedirs('/tmp/opencode', exist_ok=True)
make_png(fake_image)

tk.Tk.mainloop = lambda self, *a, **k: None

sys.path.insert(0, '.')
import EGameMaker as egm

app = egm.app

### the InProject action pkls must be (re)created in this process, pkls
### written by a direct app run reference __main__ and cannot be loaded
### here
for pkl_id in ('020', '021', '022'):
    stale = f'Assets/Action/InProject/{pkl_id}.pkl'
    if os.path.isfile(stale):
        os.remove(stale)

# Simulate opening a project
egm.OpenProjectAction('imgGame')(app)
assert app.current_project == 'imgGame', app.current_project

with open('Assets/Action/InProject/020.pkl', 'rb') as f:
    add = pickle.load(f)
with open('Assets/Action/InProject/021.pkl', 'rb') as f:
    remove = pickle.load(f)
with open('Assets/Action/InProject/022.pkl', 'rb') as f:
    edit = pickle.load(f)
with open('Assets/Action/AddImage/110.pkl', 'rb') as f:
    save = pickle.load(f)

assert add.__name__ == 'add_image', add
assert remove.__name__ == 'remove_image', remove
assert edit.__name__ == 'edit_image', edit
assert save.__name__ == 'save_image_configure', save

# Scripted dialogs, no real pickers
egm.tk_alert.showinfo = lambda *a, **k: None
egm.tk_alert.showerror = lambda *a, **k: None
egm.tk_alert.askyesno = lambda *a, **k: True

askstring_answers = ['logo', 'logo2']
egm.simpledialog.askstring = lambda *a, **k: (
    askstring_answers.pop(0) if askstring_answers else None
)
egm.tk.filedialog.askopenfilename = lambda *a, **k: fake_image

def fake_picker(app_, title, on_picked):
    current = egm._collect_image_entries(app_.current_project)
    assert current, 'no placed images found for the picker'
    on_picked(current[0])

real_picker = egm._open_image_picker
egm._open_image_picker = fake_picker

def set_input(entry_id, value):
    entry = egm.render_gui.getInput('AddImage', entry_id)
    entry.delete(0, tk.END)
    entry.insert(0, value)

def input_value(entry_id):
    return egm.render_gui.getInput('AddImage', entry_id).get()

# # # # Add image flow # # # #

### add registers the asset and opens the configure window pre-filled
add(app)

assert input_value('90') == 'main'
assert input_value('92') == 'logo'
assert input_value('94') == '0.5,0.5'
assert input_value('96') == '200'
assert input_value('98') == '200'
assert input_value('100') == '0'

data = egm.load_global_json('imgGame')
assert data.get('images') == {'logo': 'imgGameAssets/Images/logo.png'}, data
assert os.path.isfile('Projects/imgGame/imgGameAssets/Images/logo.png')

### set the placement values and save
set_input('94', '0.1,0.2')
set_input('96', '120')
set_input('98', '80')
set_input('100', '12')

save(app)

data = egm.load_global_json('imgGame')
entry = data['image_components']['main'][0]
assert entry == (
    'IMAGE(image=logo,pos=[0.1,0.2],size=[120,80],border_radius=12)'
), entry

### a placement with an unknown image name must be rejected
add(app)
assert input_value('92') == 'logo2'
set_input('92', 'missing_image')

save(app)

data = egm.load_global_json('imgGame')
assert len(data['image_components']['main']) == 1, data['image_components']

set_input('92', 'logo2')
save(app)

data = egm.load_global_json('imgGame')
assert len(data['image_components']['main']) == 2, data['image_components']

# # # # Edit image flow # # # #

edit(app)

assert egm._edit_image_entry == (
    'main', 0,
    'IMAGE(image=logo,pos=[0.1,0.2],size=[120,80],border_radius=12)',
), egm._edit_image_entry

### the window must be pre-filled with the placed image's values
assert input_value('90') == 'main'
assert input_value('92') == 'logo'
assert input_value('94') == '0.1,0.2'
assert input_value('96') == '120'
assert input_value('98') == '80'
assert input_value('100') == '12'

### change width and radius, saving must replace the entry in place
set_input('96', '300')
set_input('100', '0')

save(app)

data = egm.load_global_json('imgGame')
main = data['image_components']['main']
assert len(main) == 2, main
assert main[0] == 'IMAGE(image=logo,pos=[0.1,0.2],size=[300,80],border_radius=0)', main[0]
assert main[1].startswith('IMAGE(image=logo2,'), main[1]
assert egm._edit_image_entry is None

# # # # Remove image flow # # # #

### removing the logo placement must also drop its now-unused asset file
remove(app)

data = egm.load_global_json('imgGame')
main = data['image_components']['main']
assert len(main) == 1 and main[0].startswith('IMAGE(image=logo2,'), main
assert 'logo' not in (data.get('images') or {}), data.get('images')
assert not os.path.isfile('Projects/imgGame/imgGameAssets/Images/logo.png')
assert os.path.isfile('Projects/imgGame/imgGameAssets/Images/logo2.png')

### the real picker must build without error and list the placed images
egm._open_image_picker = real_picker
real_picker(app, 'Remove Image', on_picked=lambda *picked: None)
pickers = [
    w for w in app.winfo_children()
    if isinstance(w, tk.Toplevel) and w.title() == 'Remove Image'
]
assert pickers, 'image picker window was not created'
picker_listboxes = [
    child for child in pickers[0].winfo_children()
    if isinstance(child, tk.Listbox)
]
assert len(picker_listboxes) == 1, 'image picker has no listbox'
items = picker_listboxes[0].get(0, tk.END)
assert items == ('main : logo2',), items
for picker in pickers:
    picker.destroy()

egm._open_image_picker = fake_picker

# # # # Clean up # # # #

egm.remove_current_project(app)
assert not os.path.isdir('Projects/imgGame')
egm.render_gui.removeTextComponent('InProject.GUI', '01')

### let the next app run regenerate the InProject pkls in its own context
for pkl_id in ('020', '021', '022'):
    stale = f'Assets/Action/InProject/{pkl_id}.pkl'
    if os.path.isfile(stale):
        os.remove(stale)

if os.path.isfile(fake_image):
    os.remove(fake_image)

print('ALL CHECKS PASSED')
app.destroy()
