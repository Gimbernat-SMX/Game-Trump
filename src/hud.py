"""HUD del juego SSB: barra de vida del jugador + panel lateral con stats."""
import pygame
from src.constants import (
    BLACK, WHITE, RED, GREEN, ORANGE, GRAY,
    HEALTHBAR_W, HEALTHBAR_H, HUD_MARGIN,
    ARENA_WIDTH, SCREEN_WIDTH, SCREEN_HEIGHT,
    PANEL_X, PANEL_W, CHARACTER_LABELS, ENEMIES_TO_DEFEAT,
)


class HUD:
    def __init__(self):
        self.font_big   = pygame.font.SysFont("Arial", 22, bold=True)
        self.font_med   = pygame.font.SysFont("Arial", 18, bold=True)
        self.font_small = pygame.font.SysFont("Arial", 14)

    def draw(self, screen: pygame.Surface, player, enemies: list, kills: int,
             zoom: float = 1.0, view_x: int = 0, view_y: int = 0):
        self._draw_panel(screen, player, enemies, kills)
        self._draw_player_hud(screen, player, zoom, view_x, view_y)

    # ---- Panel lateral derecho ----

    def _draw_panel(self, screen, player, enemies, kills):
        panel = pygame.Rect(PANEL_X, 0, PANEL_W, SCREEN_HEIGHT)
        pygame.draw.rect(screen, (20, 20, 30), panel)
        pygame.draw.line(screen, GRAY, (PANEL_X, 0), (PANEL_X, SCREEN_HEIGHT), 2)

        x = PANEL_X + 10
        y = 20

        # Título
        t = self.font_big.render("GIMBERNAT", True, WHITE)
        screen.blit(t, (x, y)); y += 28
        t = self.font_big.render("BROS", True, WHITE)
        screen.blit(t, (x, y)); y += 40

        # Jugador
        pygame.draw.line(screen, GRAY, (x, y), (PANEL_X + PANEL_W - 10, y)); y += 8
        name_lbl = CHARACTER_LABELS.get(player.name, player.name)
        t = self.font_med.render(f"TÚ: {name_lbl}", True, (100, 200, 255))
        screen.blit(t, (x, y)); y += 22
        self._draw_healthbar(screen, x, y, player.health); y += 26

        # Kills
        y += 10
        t = self.font_med.render(f"Kills: {kills}/{ENEMIES_TO_DEFEAT}", True, WHITE)
        screen.blit(t, (x, y)); y += 26

        # Enemigos activos
        pygame.draw.line(screen, GRAY, (x, y), (PANEL_X + PANEL_W - 10, y)); y += 8
        t = self.font_small.render("Enemigos activos:", True, GRAY)
        screen.blit(t, (x, y)); y += 18
        for e in enemies:
            name_e = CHARACTER_LABELS.get(e.name, e.name)
            t = self.font_small.render(f"  {name_e}", True, (220, 100, 100))
            screen.blit(t, (x, y)); y += 16
            self._draw_healthbar(screen, x + 4, y, e.health, width=PANEL_W - 24, height=8)
            y += 14

        # Controles
        y = SCREEN_HEIGHT - 110
        pygame.draw.line(screen, GRAY, (x, y), (PANEL_X + PANEL_W - 10, y)); y += 8
        for line in ["A/D Mover", "W Saltar", "E Ataque debil",
                 "Q Ataque fuerte", "R Bloquear", "ESC Pausa"]:
            t = self.font_small.render(line, True, GRAY)
            screen.blit(t, (x, y)); y += 18

    def _draw_healthbar(self, screen, x, y, hp, width=HEALTHBAR_W, height=HEALTHBAR_H):
        hp = max(0.0, min(100.0, hp))
        # Fondo
        pygame.draw.rect(screen, (60, 60, 60), (x, y, width, height))
        # Relleno
        fill_w = int(width * hp / 100)
        if hp > 60:
            color = GREEN
        elif hp > 20:
            color = ORANGE
        else:
            color = RED
        pygame.draw.rect(screen, color, (x, y, fill_w, height))
        # Borde
        pygame.draw.rect(screen, WHITE, (x, y, width, height), 1)
        # Texto
        if height >= 14:
            lbl = self.font_small.render(f"{int(hp)}%", True, WHITE)
            screen.blit(lbl, (x + width + 4, y))

    # ---- Barra de vida encima del jugador (in-arena) ----

    def _draw_player_hud(self, screen, player, zoom: float, view_x: int, view_y: int):
        bw = int(50 * zoom)
        bh = max(4, int(6 * zoom))
        # Convertir coordenadas mundo → pantalla
        sx = int(player.rect.centerx * zoom - view_x) - bw // 2
        sy = int(player.rect.top * zoom - view_y) - int(14 * zoom)
        hp = max(0.0, player.health)
        pygame.draw.rect(screen, (60, 60, 60), (sx, sy, bw, bh))
        color = GREEN if hp > 60 else ORANGE if hp > 20 else RED
        pygame.draw.rect(screen, color, (sx, sy, int(bw * hp / 100), bh))
        pygame.draw.rect(screen, WHITE, (sx, sy, bw, bh), 1)
