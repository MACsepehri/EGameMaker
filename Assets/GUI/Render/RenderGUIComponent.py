### In this file I made a small rendering engine for rendering
### GUI objects easier


import os
import tkinter as tk
import tkinter.font as tkfont


class RenderGUIComponent:
    def __init__(self, base_dir='./Assets/GUI/', _app=None):
        self.content = {}
        self._app = _app
        self.font = None
        self.fonts = {}
        self.base_dir = base_dir

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

        self.font = tkfont.nametofont('TkDefaultFont', root=self._app)

    def render(self, component_file, text_font):
        self.renderText(component_file, text_font)
        self.renderButton(component_file)

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
                    family=self.font.actual('family') if self.font else 'TkDefaultFont',
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
                print(f'Unable to render GUI component: {error}')

    
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
                content = content.strip()

                if not content.startswith('BUTTON=(') or not content.endswith(')'):
                    raise ValueError('Invalid Button component format.')

                content = content[8:-1]
                text, remaining = content.split(',(', 1)
                position, button_id = remaining.split('),', 1)
                x, y = position.split(',', 1)

                button = tk.Button(
                    self._app,
                    text=text
                )

                button.place(
                    relx=float(x),
                    rely=float(y)
                )

            except (ValueError, IndexError, tk.TclError) as error:
                print(f'Unable to render GUI component: {error}')


    def parse_text(self, content):
        content = content.strip()

        if not content.startswith('TEXT=(') or not content.endswith(')'):
            raise ValueError('Invalid TEXT component format.')

        content = content[6:-1]
        text, remaining = content.split(',(', 1)
        position, text_id = remaining.split('),', 1)
        x, y = position.split(',', 1)

        return text, (x, y), text_id

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


    def addButtonComponent(self, component_file, text='', pos=(0, 0), id=''):
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

        new_component = f'BUTTON=({text},({pos[0]},{pos[1]}),{id})\n'

        updated_lines = []
        replaced = False

        for line in lines:
            if line.startswith('BUTTON=(') and line.rstrip().endswith(')'):
                try:
                    content = line.strip()[8:-1]
                    _, remaining = content.split(',(', 1)
                    _, existing_id = remaining.split('),', 1)

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

