import pygame


class Image:
    ### pygame image label built from the entries of AddImage.GUI
    ### registered image name, state, position, size and corner radius

    def __init__(
        self,
        image_name,
        position=(0.5, 0.5),
        size=(200, 200),
        border_radius=0,
        state_in='main',
    ):
        self.image_name = image_name
        self.state_in = state_in
        self.position = position
        self.size = size
        self.border_radius = border_radius

        self.image = None
        self.rect = None

    def set_image(self, path):
        ### load the registered image file, scale it and round the
        ### corners; a placeholder keeps the component renderable when
        ### the file cannot be loaded
        width = max(1, int(self.size[0]))
        height = max(1, int(self.size[1]))

        try:
            surface = pygame.image.load(path)
        except (FileNotFoundError, OSError, pygame.error):
            surface = None

        if surface is not None:
            surface = pygame.transform.smoothscale(surface, (width, height))
            surface = surface.convert_alpha()

            if self.border_radius > 0:
                mask = pygame.Surface((width, height), pygame.SRCALPHA)
                mask.fill((0, 0, 0, 0))
                pygame.draw.rect(
                    mask,
                    (255, 255, 255, 255),
                    (0, 0, width, height),
                    border_radius=int(self.border_radius)
                )
                surface.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

            self.image = surface
        else:
            self.image = pygame.Surface((width, height), pygame.SRCALPHA)

    def render(self, screen, current_state):
        ### draw the image only when the game's current state matches the
        ### state this image was created for, else pass

        if current_state != self.state_in or self.image is None:
            return

        width, height = screen.get_size()
        self.rect = self.image.get_rect(
            center=(int(self.position[0] * width), int(self.position[1] * height))
        )
        screen.blit(self.image, self.rect)


if __name__ == '__main__':
    pygame.init()

    screen = pygame.display.set_mode((500, 500))
    label = Image(
        image_name='demo',
        position=(0.5, 0.5),
        size=(120, 120),
        border_radius=16,
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
