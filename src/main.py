"""Super Smash Bros – Single/Multi Player. Punto de entrada: ./run"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame
from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE
from src.assets import Assets
from src.menu   import Menu
from src.game   import Game
from src.game_mp import GameMPHost, GameMPClient
from src.lobby   import run_host_lobby, run_client_lobby
from src.network.server   import Server
from src.network.client   import Client


def main():
    pygame.init()
    pygame.display.set_caption(TITLE)

    try:
        _root = sys._MEIPASS if getattr(sys, "frozen", False) else \
                os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        icon = pygame.image.load(
            os.path.join(_root, "assets", "images", "others", "icon.png"))
        pygame.display.set_icon(icon)
    except Exception:
        pass

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    assets = Assets.get()
    menu   = Menu(screen)

    while True:
        mode = menu.mode_screen(assets)

        # ── Un jugador ──────────────────────────────────────────────────
        if mode == "singleplayer":
            char   = menu.character_screen(assets)
            game   = Game(screen, char)
            result = game.run()
            menu.end_screen(assets, result, game.kills)

        # ── Crear partida ───────────────────────────────────────────────
        elif mode == "host":
            name, char = menu.host_setup_screen(assets)
            server = Server(name, char)
            lobby_result = run_host_lobby(screen, assets, server)

            if lobby_result == "start":
                game   = GameMPHost(screen, server)
                result = game.run()
                winner = result[1] if isinstance(result, tuple) else "?"
                menu.end_screen_mp(assets, winner)

            server.close()

        # ── Unirse a partida ────────────────────────────────────────────
        elif mode == "join":
            name, ip, char = menu.join_setup_screen(assets)
            client = Client()

            if not client.connect(ip, name, char):
                _show_error(screen, assets, menu,
                            f"No se pudo conectar a {ip}:5555")
                continue

            lobby_result = run_client_lobby(screen, assets, client)

            if lobby_result == "start":
                game   = GameMPClient(screen, client)
                result = game.run()
                winner = result[1] if isinstance(result, tuple) else "?"
                menu.end_screen_mp(assets, winner)
            elif lobby_result == "kicked":
                _show_error(screen, assets, menu, "El anfitrión te ha expulsado.")

            client.close()


def _show_error(screen, assets, menu, message: str):
    font_big = pygame.font.SysFont("Arial", 34, bold=True)
    font_s   = pygame.font.SysFont("Arial", 20)
    overlay  = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); raise SystemExit
            if event.type == pygame.KEYDOWN:
                return  # cualquier tecla cierra el mensaje

        screen.blit(assets.arena, (0, 0))
        screen.blit(overlay, (0, 0))

        err  = font_big.render(message, True, (255, 80, 80))
        hint = font_s.render("Pulsa cualquier tecla para continuar", True, (180, 180, 180))
        screen.blit(err,  (SCREEN_WIDTH // 2 - err.get_width() // 2,
                           SCREEN_HEIGHT // 2 - 30))
        screen.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2,
                           SCREEN_HEIGHT // 2 + 20))
        pygame.display.flip()
        clock.tick(30)


if __name__ == "__main__":
    main()
