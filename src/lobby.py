"""Pantallas de lobby para el modo multijugador."""
import pygame
from src.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS,
    BLACK, WHITE, YELLOW, GRAY, LIGHT_GRAY, DARK_GRAY,
    CHARACTERS, CHARACTER_LABELS, PLAYER_COLORS,
)
from src.network.protocol import get_local_ip

_SLOT_NAMES = {0: "Anfitrión", 1: "Jugador 2", 2: "Jugador 3", 3: "Jugador 4"}


def run_host_lobby(screen: pygame.Surface, assets, server) -> str:
    """
    Pantalla de lobby para el HOST.
    Devuelve "start" o "quit".
    """
    font_title = pygame.font.SysFont("Arial", 38, bold=True)
    font_med   = pygame.font.SysFont("Arial", 24, bold=True)
    font_small = pygame.font.SysFont("Arial", 18)
    clock      = pygame.time.Clock()

    local_ip    = get_local_ip()
    selected    = 0   # índice del jugador seleccionado en la lista (para kick)

    while True:
        players = server.get_player_list()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); raise SystemExit

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "quit"

                elif event.key == pygame.K_UP:
                    selected = max(0, selected - 1)

                elif event.key == pygame.K_DOWN:
                    selected = min(len(players) - 1, selected + 1)

                elif event.key == pygame.K_k:
                    # Kick el jugador seleccionado (no se puede expulsar al host)
                    if 0 <= selected < len(players):
                        slot = players[selected]["slot"]
                        if slot != 0:
                            server.kick(slot)
                            selected = max(0, selected - 1)

                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    if len(players) >= 1:
                        server.start_game()
                        return "start"

        # ---- Dibujar ----
        screen.blit(assets.char_bg, (0, 0))
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        screen.blit(overlay, (0, 0))

        # Título
        _shadow(screen, font_title, "SALA DE JUEGO", YELLOW, 40)

        # IP local
        ip_surf = font_small.render(f"Tu IP: {local_ip}  –  Puerto: 5555", True, LIGHT_GRAY)
        screen.blit(ip_surf, (SCREEN_WIDTH // 2 - ip_surf.get_width() // 2, 100))

        # Lista de jugadores
        list_y = 150
        for i, p in enumerate(players):
            color   = PLAYER_COLORS[p["slot"] % len(PLAYER_COLORS)]
            is_sel  = (i == selected)
            bg_rect = pygame.Rect(SCREEN_WIDTH // 2 - 280, list_y - 4, 560, 36)
            if is_sel:
                pygame.draw.rect(screen, (60, 60, 80), bg_rect, border_radius=4)
                pygame.draw.rect(screen, YELLOW, bg_rect, 2, border_radius=4)

            slot_lbl = _SLOT_NAMES.get(p["slot"], f"Slot {p['slot']}")
            char_lbl = CHARACTER_LABELS.get(p["char"], p["char"])
            text = f"{slot_lbl}: {p['name']}  [{char_lbl}]"
            surf = font_med.render(text, True, color)
            screen.blit(surf, (SCREEN_WIDTH // 2 - 260, list_y))

            # Etiqueta kick (solo para no-host)
            if p["slot"] != 0 and is_sel:
                kick_s = font_small.render("[K] Expulsar", True, (255, 80, 80))
                screen.blit(kick_s, (SCREEN_WIDTH // 2 + 200, list_y + 4))

            list_y += 50

        # Espacio vacío
        for i in range(len(players), 4):
            empty = font_small.render(f"Esperando jugador {i + 1}...", True, DARK_GRAY)
            screen.blit(empty, (SCREEN_WIDTH // 2 - empty.get_width() // 2, list_y + 4))
            list_y += 50

        # Instrucciones
        instructions = [
            "↑↓  Seleccionar jugador",
            "K   Expulsar jugador seleccionado",
            "ENTER   Iniciar partida",
            "ESC   Cancelar",
        ]
        iy = SCREEN_HEIGHT - 110
        for line in instructions:
            s = font_small.render(line, True, GRAY)
            screen.blit(s, (SCREEN_WIDTH // 2 - s.get_width() // 2, iy))
            iy += 22

        pygame.display.flip()
        clock.tick(FPS)


def run_client_lobby(screen: pygame.Surface, assets, client) -> str:
    """
    Pantalla de lobby para el CLIENTE.
    Devuelve "start", "quit" o "kicked".
    """
    font_title = pygame.font.SysFont("Arial", 38, bold=True)
    font_med   = pygame.font.SysFont("Arial", 24, bold=True)
    font_small = pygame.font.SysFont("Arial", 18)
    clock      = pygame.time.Clock()

    selected_char_idx = 0

    while True:
        if client.is_kicked():
            return "kicked"
        if not client.connected:
            return "quit"
        if client.is_game_started():
            return "start"

        players = client.get_player_list()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); raise SystemExit

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "quit"

                elif event.key == pygame.K_LEFT:
                    selected_char_idx = (selected_char_idx - 1) % len(CHARACTERS)
                    client.send_char(CHARACTERS[selected_char_idx])

                elif event.key == pygame.K_RIGHT:
                    selected_char_idx = (selected_char_idx + 1) % len(CHARACTERS)
                    client.send_char(CHARACTERS[selected_char_idx])

        # ---- Dibujar ----
        screen.blit(assets.char_bg, (0, 0))
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        screen.blit(overlay, (0, 0))

        _shadow(screen, font_title, "SALA DE JUEGO", YELLOW, 40)

        wait_s = font_small.render("Esperando que el anfitrión inicie la partida...", True, LIGHT_GRAY)
        screen.blit(wait_s, (SCREEN_WIDTH // 2 - wait_s.get_width() // 2, 100))

        # Lista de jugadores
        list_y = 150
        for p in players:
            color    = PLAYER_COLORS[p["slot"] % len(PLAYER_COLORS)]
            slot_lbl = _SLOT_NAMES.get(p["slot"], f"Slot {p['slot']}")
            char_lbl = CHARACTER_LABELS.get(p["char"], p["char"])
            marker   = " ◄" if p["slot"] == client.slot else ""
            text = f"{slot_lbl}: {p['name']}  [{char_lbl}]{marker}"
            surf = font_med.render(text, True, color)
            screen.blit(surf, (SCREEN_WIDTH // 2 - surf.get_width() // 2, list_y))
            list_y += 50

        # Cambio de personaje
        char_name = CHARACTERS[selected_char_idx]
        char_lbl  = CHARACTER_LABELS.get(char_name, char_name)
        cs = font_small.render(f"Tu personaje: {char_lbl}  (← / → para cambiar)", True, WHITE)
        screen.blit(cs, (SCREEN_WIDTH // 2 - cs.get_width() // 2, SCREEN_HEIGHT - 80))

        esc_s = font_small.render("ESC – Desconectarse", True, GRAY)
        screen.blit(esc_s, (SCREEN_WIDTH // 2 - esc_s.get_width() // 2, SCREEN_HEIGHT - 50))

        pygame.display.flip()
        clock.tick(FPS)


# ---- Util ----

def _shadow(screen, font, text, color, y):
    surf   = font.render(text, True, color)
    shadow = font.render(text, True, BLACK)
    cx = SCREEN_WIDTH // 2 - surf.get_width() // 2
    screen.blit(shadow, (cx + 2, y + 2))
    screen.blit(surf,   (cx,     y))
