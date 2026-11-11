
### MADE BY EGameMaker GAME ENGINE
### OPEN-SOURCE ENGINE
### https://github.com/MACsepehri/EGameMaker

import pygame,sys
import types
import pickle
import os
import testAssets.Global as Global
from button import Button
from text import Text
from image import Image

pygame.init()

def initialization():
    if (Global.fullscreen):
        win = pygame.display.set_mode((0,0),pygame.FULLSCREEN)
    else:
        win = pygame.display.set_mode(Global.base_window_size)
    pygame.display.set_caption(Global.title)
    return win

def split_top_level(text):
    ### split on commas that are not inside [ ]
    parts, depth, current = [], 0, ''

    for char in text:
        if char == '[':
            depth += 1
        elif char == ']':
            depth -= 1

        if char == ',' and depth == 0:
            parts.append(current)
            current = ''
        else:
            current += char

    if current:
        parts.append(current)

    return parts

def parse_button_entry(entry, state_in):
    ### turn a BUTTON(...) entry of Global.json states into a Button
    body = entry[len('BUTTON('):-1]
    values = {}

    for part in split_top_level(body):
        key, _, value = part.partition('=')
        values[key.strip()] = value.strip()

    def items(raw):
        ### values are stored like [a,b,c]; strip one pair of [ ] then
        ### split on the top-level commas
        raw = raw.strip()

        if raw.startswith('[') and raw.endswith(']'):
            raw = raw[1:-1]

        return [item for item in split_top_level(raw) if item != '']

    def pair(key, cast):
        raw = values.get(key, '')
        return [cast(item) for item in items(raw)] if raw else None

    def color(key, default):
        raw = values.get(key, '')
        return tuple(int(item) for item in items(raw)) if raw else default

    return Button(
        text=values.get('text', ''),
        position=pair('pos', float) or (0.5, 0.5),
        size=pair('size', int) or (150, 50),
        state_in=state_in,
        base_color=color('base_color', (200, 200, 200)),
        hover_color=color('hover_color', (255, 255, 0)),
        text_color=color('text_color', (0, 0, 0)),
        font_name=values.get('font_name', 'base_font') or 'base_font',
        font_size=int(values.get('font_size', '14') or 14),
    )

def parse_text_entry(entry, state_in):
    ### turn a TEXT(...) entry of Global.texts into a Text
    body = entry[len('TEXT('):-1]
    values = {}

    for part in split_top_level(body):
        key, _, value = part.partition('=')
        values[key.strip()] = value.strip()

    def items(raw):
        ### values are stored like [a,b,c]; strip one pair of [ ] then
        ### split on the top-level commas
        raw = raw.strip()

        if raw.startswith('[') and raw.endswith(']'):
            raw = raw[1:-1]

        return [item for item in split_top_level(raw) if item != '']

    def pair(key, cast):
        raw = values.get(key, '')
        return [cast(item) for item in items(raw)] if raw else None

    def color(key, default):
        raw = values.get(key, '')
        return tuple(int(item) for item in items(raw)) if raw else default

    return Text(
        text=values.get('text', ''),
        position=pair('pos', float) or (0.5, 0.5),
        font_name=values.get('font_name', 'base_font') or 'base_font',
        font_size=int(values.get('font_size', '32') or 32),
        text_color=color('text_color', (0, 0, 0)),
        state_in=state_in,
    )

def parse_image_entry(entry, state_in):
    ### turn an IMAGE(...) entry of Global.image_components into an Image
    body = entry[len('IMAGE('):-1]
    values = {}

    for part in split_top_level(body):
        key, _, value = part.partition('=')
        values[key.strip()] = value.strip()

    def items(raw):
        ### values are stored like [a,b,c]; strip one pair of [ ] then
        ### split on the top-level commas
        raw = raw.strip()

        if raw.startswith('[') and raw.endswith(']'):
            raw = raw[1:-1]

        return [item for item in split_top_level(raw) if item != '']

    def pair(key, cast):
        raw = values.get(key, '')
        return [cast(item) for item in items(raw)] if raw else None

    return Image(
        image_name=values.get('image', ''),
        position=pair('pos', float) or (0.5, 0.5),
        size=tuple(int(item) for item in items(values.get('size', ''))) or (200, 200),
        border_radius=int(values.get('border_radius', '0') or 0),
        state_in=state_in,
    )

class Game:
    ### the object passed to the user's action code as self, it carries
    ### the button vars and the Global vars

    def __init__(self, win, buttons, texts, images):
        self.win = win
        self.Global = Global
        self.buttons = {button.text: button for button in buttons}
        self.texts = texts
        self.images = images
        self.current_state = getattr(
            Global, 'current_state', next(iter(Global.states), 'main')
        )

def load_action(path):
    ### load a button's pickled action, the pkl stores the action source
    ### text so the function is rebuilt by execing it with Global
    if not path:
        return None

    if path.startswith(f'Projects/test/'):
        path = path[len(f'Projects/test/'):]

    try:
        with open(path, 'rb') as file:
            loaded = pickle.load(file)
    except (OSError, EOFError, pickle.UnpicklingError):
        return None

    if isinstance(loaded, str):
        return _rebuild_action_func(loaded)

    return loaded

def _rebuild_action_func(source):
    ### exec the stored action source in a namespace where Global and the
    ### builtins resolve, then return the function the source defines
    namespace = {'Global': Global}
    exec(compile(source, '<button_action>', 'exec'), namespace)

    for name, value in namespace.items():
        if name in ('Global', '__builtins__'):
            continue
        if isinstance(value, types.FunctionType):
            return value

    return None

def fire_action(action, game):
    ### call the action, passing the game object only when the action is
    ### declared to take a positional argument
    code = getattr(action, '__code__', None)
    if code is None or code.co_argcount >= 1:
        action(game)
    else:
        action()

def bind_component_font(component):
    ### resolve a component's font name to a project font file and rebind
    ### its font, names come from the fonts map of Global.json
    if not component.font_name or component.font_name == 'base_font':
        return

    font_path = (getattr(Global, 'fonts', {}) or {}).get(component.font_name)

    if not font_path:
        return

    full_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), font_path)

    try:
        component.font = pygame.font.Font(full_path, component.font_size)
    except (pygame.error, OSError):
        ### fall back to the default font the component already set up
        pass

def bind_image(component):
    ### resolve an image component's registered name to its file and
    ### load it, names come from the images map of Global.json
    if not component.image_name:
        return

    image_path = (getattr(Global, 'images', {}) or {}).get(component.image_name)

    if not image_path:
        return

    full_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), image_path)
    component.set_image(full_path)

def make_game(win):
    ### create one Button, Text and Image for every entry of Global
    buttons = []
    texts = []

    for state, entries in Global.states.items():
        for entry in entries or []:
            button_entry = entry[0]
            action_path = entry[1] if len(entry) > 1 else None
            button = parse_button_entry(button_entry, state)
            button.action_path = action_path
            bind_component_font(button)
            buttons.append(button)

    for state, entries in (getattr(Global, 'texts', {}) or {}).items():
        for text_entry in entries or []:
            text = parse_text_entry(text_entry, state)
            bind_component_font(text)
            texts.append(text)

    images = []

    for state, entries in (getattr(Global, 'image_components', {}) or {}).items():
        for image_entry in entries or []:
            image = parse_image_entry(image_entry, state)
            bind_image(image)
            images.append(image)

    return Game(win, buttons, texts, images)

def app():
    win = initialization()
    clock = pygame.time.Clock()
    game = make_game(win)

    while True:
        events = pygame.event.get()

        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)

        ### Global.current_state is the source of truth, set_state() in
        ### Global switches it and the loop picks it up here
        state = Global.current_state
        game.current_state = state

        for button in game.buttons.values():
            button.handle_events(events, state)

        win.fill(Global.background)

        for image in game.images:
            image.render(win, state)

        for text in game.texts:
            text.render(win, state)

        for button in game.buttons.values():
            button.render(win, state)

        pygame.display.update()

        for button in game.buttons.values():
            if button.clicked:
                action = load_action(button.action_path)

                if action is not None:
                    try:
                        fire_action(action, game)
                    except Exception as error:
                        print(f'action error for "{button.text}": {error}')

        clock.tick(Global.fps)

if __name__ == "__main__":
    app()

