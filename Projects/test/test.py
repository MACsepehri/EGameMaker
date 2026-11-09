
 ### MADE BY EGameMaker GAME ENGINE
 ### OPEN-SOURCE ENGINE
 ### https://github.com/MACsepehri/EGameMaker

import pygame,sys
import types
import pickle
import testAssets.Global as Global
from button import Button

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

class Game:
    ### the object passed to the user's action code as self, it carries
    ### the button vars and the Global vars

    def __init__(self, win, buttons):
        self.win = win
        self.Global = Global
        self.buttons = {button.text: button for button in buttons}
        self.current_state = next(iter(Global.states), 'main')

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

def make_game(win):
    ### create one Button for every BUTTON entry in Global.states
    buttons = []

    for state, entries in Global.states.items():
        for entry in entries or []:
            button_entry = entry[0]
            action_path = entry[1] if len(entry) > 1 else None
            button = parse_button_entry(button_entry, state)
            button.action_path = action_path
            buttons.append(button)

    return Game(win, buttons)

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

        for button in game.buttons.values():
            button.handle_events(events, game.current_state)

        win.fill(Global.background)

        for button in game.buttons.values():
            button.render(win, game.current_state)

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

