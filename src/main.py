"""Super Smash Bros – Single Player. Punto de entrada: ./run"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame
from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE
from src.assets import Assets
from src.menu  import Menu
from src.game  import Game


def main():
    pygame.init()
    pygame.display.set_caption(TITLE)

    try:
        icon = pygame.image.load(
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                         "assets", "images", "others", "icon.png"))
        pygame.display.set_icon(icon)
    except Exception:
        pass

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    Assets.get()   # pre-carga

    menu = Menu(screen)

    while True:
        assets   = Assets.get()
        char     = menu.character_screen(assets)
        game     = Game(screen, char)
        result   = game.run()           # 'victory' | 'game_over'
        menu.end_screen(assets, result, game.kills)
        # vuelve al menú


if __name__ == "__main__":
    main()
