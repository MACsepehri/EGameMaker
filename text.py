import pygame


class Text:
    ### pygame text label built from the entries of AddText.GUI
    ### text, state, font and position

    def __init__(
        self,
        text,
        position=(0.5, 0.5),
        font_name='base_font',
        font_size=32,
        text_color=(0, 0, 0),
        state_in='main',
    ):
        self.text = text
        self.state_in = state_in
        self.position = position
        self.font_name = font_name
        self.font_size = font_size
        self.text_color = text_color

        self.font = self._load_font()
        self.rect = None

    def _load_font(self):
        if not self.font_name or self.font_name == 'base_font':
            return pygame.font.Font(None, self.font_size)

        try:
            return pygame.font.Font(self.font_name, self.font_size)
        except (FileNotFoundError, OSError, pygame.error):
            return pygame.font.Font(None, self.font_size)

    def render(self, screen, current_state):
        ### draw the text only when the game's current state matches the
        ### state this text was created for, else pass

        if current_state == self.state_in:
            width, height = screen.get_size()
            surface = self.font.render(self.text, True, self.text_color)
            self.rect = surface.get_rect(
                center=(int(self.position[0] * width), int(self.position[1] * height))
            )
            screen.blit(surface, self.rect)
        else:
            pass


if __name__ == '__main__':
    pygame.init()

    screen = pygame.display.set_mode((500, 500))
    label = Text(
        text='Hello',
        position=(0.5, 0.3),
        font_name='base_font',
        font_size=32,
        text_color=(255, 0, 0),
    )

    current_state = 'main'

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

        screen.fill((0, 0, 0))
        label.render(screen, current_state)
        pygame.display.update()
