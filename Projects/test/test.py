
### MADE BY EGameMaker GAME ENGINE
### OPEN-SOURCE ENGINE
### https://github.com/MACsepehri/EGameMaker

import pygame,sys
import testAssets.Global as Global

pygame.init()

def initialization():
    if (Global.FULLSCREEN):
        win = pygame.display.set_mode((0,0),pygame.FULLSCREEN)
    else:
        win = pygame.display.set_mode(Global.BASE_WINDOW_SIZE)
    pygame.display.set_caption(Global.WINDOW_TITLE)
    return win

def app():
    win = initialization()
    clock = pygame.time.Clock()

    globalConfigure = Global.GlobalConfigure()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)

        win.fill(Global.BACKGROUND_COLOR)
        pygame.display.update()
        clock.tick(Global.FPS)

if __name__ == "__main__":
    app()

