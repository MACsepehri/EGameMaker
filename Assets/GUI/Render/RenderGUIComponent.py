### In this file I made a small rendering engine for rendering
### GUI objects easier



import os
import tkinter as tk
import tkinter.font as tkfont
import pickle
from tkinter import simpledialog


class RenderGUIComponent:
    def __init__(self, base_dir='./Assets/GUI/', _app=None):
        self.content = {}
        self._app = _app
        self.font = None
        self.fonts = {}
        self.buttons = {}
        self.entries = {}
        self.base_dir = base_dir
        self.action_base_dir = 'Assets/Action'

        self.load_components()

    def load_components(self):
        if not os.path.isdir(self.base_dir):
            raise FileNotFoundError(
                f'GUI directory not found: {self.base_dir}'
            )

        for filename in os.listdir(self.base_dir):
            if filename.endswith('.GUI'):
                path = os.path.join(self.base_dir, filename)

                with open(path, 'r', encoding='utf-8') as file:
                    self.content[filename[:-4]] = file.readlines()

    def init_app(self, app):
        self._app = app
        self.init_font()

    def init_font(self):
        if self._app is None:
            raise RuntimeError('Initialize the application first.')

        self.font = tkfont.nametofont(
            'TkDefaultFont',
            root=self._app
        )

    def render(self, component_file, text_font=None):
        self.renderText(component_file, text_font)
        self.renderButton(component_file)
        self.renderInput(component_file)

    def renderText(self, component_file='', font=None):
        if self._app is None:
            raise RuntimeError('Application has not been initialized.')

        if component_file not in self.content:
            raise FileNotFoundError(
                f'GUI component file not found: {component_file}.GUI'
            )

        if font is None:
            font = []

        font_sizes = {
            str(item[0]): int(item[1])
            for item in font
        }

        for content in self.content[component_file]:
            if not content.startswith('TEXT='):
                continue

            try:
                text, pos, text_id = self.parse_text(content)

                font_size = font_sizes.get(text_id, 14)

                component_font = tkfont.Font(
                    root=self._app,
                    family=(
                        self.font.actual('family')
                        if self.font
                        else 'TkDefaultFont'
                    ),
                    size=font_size
                )

                label = tk.Label(
                    self._app,
                    text=text,
                    font=component_font
                )

                label.place(
                    relx=float(pos[0]),
                    rely=float(pos[1])
                )

                self.fonts[text_id] = component_font

            except (ValueError, IndexError, tk.TclError) as error:
                # print(f'Unable to render GUI component: {error}')
                print(f'Unable to render GUI component: {error} | Content: {content!r}')

    def renderButton(self, component_file):
        if self._app is None:
            raise RuntimeError('Application has not been initialized.')

        if component_file not in self.content:
            raise FileNotFoundError(
                f'GUI component file not found: {component_file}.GUI'
            )

        for content in self.content[component_file]:
            if not content.startswith('BUTTON='):
                continue

            try:
                text, pos, button_id, action_path = self.parse_button(content)

                button = tk.Button(
                    self._app,
                    text=text,
                    command=lambda path=action_path: self.execute_action(path)
                )

                button.place(
                    relx=float(pos[0]),
                    rely=float(pos[1])
                )

                self.buttons[button_id] = button

            except (ValueError, IndexError, tk.TclError) as error:
                # print(f'Unable to render GUI component: {error}')
                print(f'Unable to render GUI component: {error} | Content: {content!r}')

    def renderInput(self, component_file):
        if self._app is None:
            raise RuntimeError('Application has not been initialized.')

        if component_file not in self.content:
            raise FileNotFoundError(
                f'GUI component file not found: {component_file}.GUI'
            )

        self.entries.clear()

        for content in self.content[component_file]:
            if not content.startswith('INPUT='):
                continue

            try:
                pos, input_id = self.parse_input(content)

                entry = tk.Entry(self._app)

                entry.place(
                    relx=float(pos[0]),
                    rely=float(pos[1])
                )

                self.entries[input_id] = entry

            except (ValueError, IndexError, tk.TclError) as error:
                print(f'Unable to render GUI component: {error} | Content: {content!r}')

    def getInputValue(self, input_id):
        entry = self.entries.get(str(input_id))

        if entry is None:
            raise KeyError(f'Input component not found: {input_id}')

        if not entry.winfo_exists():
            raise RuntimeError(f'Input component has been destroyed: {input_id}')

        return entry.get()

    def execute_action(self, action_path):
        base_path = os.path.abspath(self.action_base_dir)
        full_path = os.path.abspath(
            os.path.join(base_path, action_path)
        )

        if os.path.commonpath([base_path, full_path]) != base_path:
            raise ValueError('Invalid action path.')

        if not os.path.isfile(full_path):
            raise FileNotFoundError(
                f'Action file not found: {full_path}'
            )

        with open(full_path, 'rb') as file:
            action = pickle.load(file)

        if not callable(action):
            raise TypeError('The loaded action is not callable.')

        action(self._app)

    def parse_text(self, content):
        content = content.strip()

        if not content.startswith('TEXT=(') or not content.endswith(')'):
            raise ValueError('Invalid TEXT component format.')

        content = content[len('TEXT=('):-1]
        text, remaining = content.split(',(', 1)
        position, text_id = remaining.split('),', 1)
        x, y = position.split(',', 1)

        return text, (x, y), text_id


    def parse_button(self, content):
        content = content.strip()

        if not content.startswith('BUTTON=(') or not content.endswith(')'):
            raise ValueError(f'Invalid BUTTON component format: {content!r}')

        content = content[8:-1]
        text, remaining = content.split(',(', 1)
        position, remaining = remaining.split('),', 1)
        x, y = position.split(',', 1)

        parts = remaining.split(',', 1)

        if len(parts) != 2:
            raise ValueError(
                f'BUTTON requires an ID and action path: {content!r}'
            )

        button_id, action_path = parts

        return text, (x, y), button_id, action_path

    def parse_input(self, content):
        content = content.strip()

        if not content.startswith('INPUT=(') or not content.endswith(')'):
            raise ValueError(f'Invalid INPUT component format: {content!r}')

        content = content[len('INPUT=('):-1]
        position, input_id = content.rsplit(',', 1)

        if not (position.startswith('(') and position.endswith(')')):
            raise ValueError(f'Invalid INPUT position format: {position!r}')

        x, y = position[1:-1].split(',', 1)

        return (x, y), input_id


    def addTextComponent(self, component_file, text='', pos=(0, 0), id=''):
        filename = (
            component_file
            if component_file.endswith('.GUI')
            else component_file + '.GUI'
        )

        path = os.path.join(self.base_dir, filename)

        if not os.path.isfile(path):
            raise FileNotFoundError(f'GUI file not found: {path}')

        with open(path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        new_component = f'TEXT=({text},({pos[0]},{pos[1]}),{id})\n'

        updated_lines = []
        replaced = False

        for line in lines:
            if line.startswith('TEXT='):
                try:
                    _, _, existing_id = self.parse_text(line)

                    if existing_id == str(id):
                        if not replaced:
                            updated_lines.append(new_component)
                            replaced = True
                        continue

                except (ValueError, IndexError):
                    pass

            updated_lines.append(line)

        if not replaced:
            if updated_lines and not updated_lines[-1].endswith('\n'):
                updated_lines[-1] += '\n'

            updated_lines.append(new_component)

        with open(path, 'w', encoding='utf-8') as file:
            file.writelines(updated_lines)

        self.content[filename[:-4]] = updated_lines

    def removeTextComponent(self, component_file, id=''):
        filename = (
            component_file
            if component_file.endswith('.GUI')
            else component_file + '.GUI'
        )

        path = os.path.join(self.base_dir, filename)

        if not os.path.isfile(path):
            raise FileNotFoundError(f'GUI file not found: {path}')

        with open(path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        updated_lines = []

        for line in lines:
            if line.startswith('TEXT='):
                try:
                    _, _, existing_id = self.parse_text(line)

                    if existing_id == str(id):
                        continue

                except (ValueError, IndexError):
                    pass

            updated_lines.append(line)

        with open(path, 'w', encoding='utf-8') as file:
            file.writelines(updated_lines)

        self.content[filename[:-4]] = updated_lines

    def addButtonComponent(
        self,
        component_file,
        text='',
        pos=(0, 0),
        id='',
        action_path=''
    ):
        filename = (
            component_file
            if component_file.endswith('.GUI')
            else component_file + '.GUI'
        )

        path = os.path.join(self.base_dir, filename)

        if not os.path.isfile(path):
            raise FileNotFoundError(f'GUI file not found: {path}')

        new_component = (
            f'BUTTON=({text},({pos[0]},{pos[1]}),{id},{action_path})\n'
        )

        with open(path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        updated_lines = []
        replaced = False

        for line in lines:
            if line.startswith('BUTTON='):
                try:
                    _, _, existing_id, _ = self.parse_button(line)

                    if existing_id == str(id):
                        if not replaced:
                            updated_lines.append(new_component)
                            replaced = True
                        continue

                except (ValueError, IndexError):
                    pass

            updated_lines.append(line)

        if not replaced:
            if updated_lines and not updated_lines[-1].endswith('\n'):
                updated_lines[-1] += '\n'

            updated_lines.append(new_component)

        with open(path, 'w', encoding='utf-8') as file:
            file.writelines(updated_lines)

        self.content[filename[:-4]] = updated_lines

    def addInputComponent(
        self,
        component_file,
        pos=(0, 0),
        id=''
    ):
        filename = (
            component_file
            if component_file.endswith('.GUI')
            else component_file + '.GUI'
        )

        path = os.path.join(self.base_dir, filename)

        if not os.path.isfile(path):
            raise FileNotFoundError(f'GUI file not found: {path}')

        new_component = (
            f'INPUT=(({pos[0]},{pos[1]}),{id})\n'
        )

        with open(path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        updated_lines = []
        replaced = False

        for line in lines:
            if line.startswith('INPUT='):
                try:
                    _, existing_id = self.parse_input(line)

                    if existing_id == str(id):
                        if not replaced:
                            updated_lines.append(new_component)
                            replaced = True
                        continue

                except (ValueError, IndexError):
                    pass

            updated_lines.append(line)

        if not replaced:
            if updated_lines and not updated_lines[-1].endswith('\n'):
                updated_lines[-1] += '\n'

            updated_lines.append(new_component)

        with open(path, 'w', encoding='utf-8') as file:
            file.writelines(updated_lines)

        self.content[filename[:-4]] = updated_lines

    def getInput(
        self,
        component_file,
        input_id
    ):
        if component_file not in self.content:
            raise FileNotFoundError(
                f'GUI component file not found: {component_file}.GUI'
            )

        entry = self.entries.get(str(input_id))

        if entry is None:
            raise KeyError(f'Input component not found: {input_id}')

        if not entry.winfo_exists():
            raise RuntimeError(f'Input component has been destroyed: {input_id}')

        return entry