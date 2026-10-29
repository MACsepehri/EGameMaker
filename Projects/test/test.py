
### MADE BY EGameMaker GAME ENGINE
### OPEN-SOURCE ENGINE
### https://github.com/MACsepehri/EGameMaker

import pygame,sys
import testAssets.Global as Global

pygame.init()

def initialization():
    if (Global.fullscreen):
        win = pygame.display.set_mode((0,0),pygame.FULLSCREEN)
    else:
        win = pygame.display.set_mode(Global.base_window_size)
    pygame.display.set_caption(Global.title)
    return win

def app():
    win = initialization()
    clock = pygame.time.Clock()

    

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)

        win.fill(Global.background)
        pygame.display.update()
        clock.tick(Global.fps)

if __name__ == "__main__":
    app()

