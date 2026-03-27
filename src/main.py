"""
PumpTrump – Single-player Python adaptation.
Punto de entrada: ejecutar con ./run desde la raíz del proyecto.
"""
import os
import sys

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame
from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE
from src.assets import Assets
from src.menu import Menu
from src.game import Game


def main():
    pygame.init()
    pygame.display.set_caption(TITLE)

    # Try to set window icon
    try:
        icon_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "assets", "sprites", "stuff", "icon.ico",
        )
        if os.path.exists(icon_path):
            icon = pygame.image.load(icon_path)
            pygame.display.set_icon(icon)
    except Exception:
        pass

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    # Pre-load all assets (required before Menu/Game use sprites)
    Assets.get()

    menu = Menu(screen)

    # Main application loop (allows restart after game ends)
    while True:
        assets    = Assets.get()
        lives     = menu.lives_screen(assets)
        color_key = menu.character_screen(assets)

        game   = Game(screen, color_key, lives)
        result = game.run()   # 'victory' | 'game_over'

        # result loops back to menu (or SystemExit raised inside)


if __name__ == "__main__":
    main()
