import pygame


class Button:
    ### pygame button built from the entries of AddButton.GUI
    ### text, state, colors, font, position and size

    def __init__(
        self,
        text,
        position=(0.5, 0.5),
        size=(150, 50),
        state_in='main',
        base_color=(200, 200, 200),
        hover_color=(255, 255, 0),
        text_color=(0, 0, 0),
        font_name='base_font',
        font_size=14,
    ):
        self.text = text
        self.state_in = state_in
        self.position = position
        self.size = size
        self.base_color = base_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.font_name = font_name
        self.font_size = font_size

        self.enable_to_click = True
        self.clicked = False
        self.hovered = False

        self.rect = pygame.Rect(0, 0, self.size[0], self.size[1])
        self.font = self._load_font()

    def _load_font(self):
        if not self.font_name or self.font_name == 'base_font':
            return pygame.font.Font(None, self.font_size)

        try:
            return pygame.font.Font(self.font_name, self.font_size)
        except (FileNotFoundError, OSError, pygame.error):
            return pygame.font.Font(None, self.font_size)

    def set_enabled(self, enabled):
        self.enable_to_click = enabled

    def handle_events(self, events, current_state):
        ### process the frame's event list, set clicked when the button
        ### is pressed while enabled and inside its state

        if current_state != self.state_in:
            return

        self.clicked = False

        for event in events:
            if event.type == pygame.MOUSEMOTION:
                self.hovered = self.rect.collidepoint(event.pos)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.enable_to_click and self.rect.collidepoint(event.pos):
                    self.clicked = True

    def render(self, screen, current_state):
        ### draw the button only when the game's current state matches
        ### the state this button was created for, else pass

        if current_state == self.state_in:
            width, height = screen.get_size()
            self.rect.x = int(self.position[0] * width)
            self.rect.y = int(self.position[1] * height)
            self.rect.w, self.rect.h = self.size

            color = self.hover_color if self.hovered else self.base_color
            pygame.draw.rect(screen, color, self.rect)

            label = self.font.render(self.text, True, self.text_color)
            screen.blit(label, label.get_rect(center=self.rect.center))
        else:
            pass


if __name__ == '__main__':
    pygame.init()

    screen = pygame.display.set_mode((500, 500))
    button = Button(
        text='Start',
        position=(0.5, 0.5),
        size=(150, 50),
        state_in='main',
        base_color=(200, 200, 200),
        hover_color=(255, 255, 0),
        text_color=(0, 0, 0),
        font_name='base_font',
        font_size=14,
    )

    current_state = 'main'

    while True:
        events = pygame.event.get()

        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

        button.handle_events(events, current_state)
        screen.fill((0, 0, 0))
        button.render(screen, current_state)
        pygame.display.update()

        if button.clicked:
            print(f'"{button.text}" clicked, current state: {current_state}')
