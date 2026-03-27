import pygame
from src.constants import *


class HUD:
    """
    Heads-Up Display:
      - Corazones (sprites originales)
      - Barra de munición con iconos
      - Contador de kills / objetivo
      - Indicador de recarga
    """

    def __init__(self):
        self.font       = pygame.font.SysFont("Arial", 20, bold=True)
        self.font_small = pygame.font.SysFont("Arial", 16)

    def draw(self, screen: pygame.Surface, player, kills: int, target: int, assets):
        self._draw_hearts(screen, player.lives, player.max_lives, assets)
        self._draw_ammo(screen, player, assets)
        self._draw_kills(screen, kills, target)
        if player.shielding:
            self._draw_shield_status(screen, assets)

    # ---- Hearts ----

    def _draw_hearts(self, screen, lives, max_lives, assets):
        heart = assets.heart
        hw    = heart.get_width()
        x = HUD_MARGIN
        y = HUD_MARGIN
        for i in range(max_lives):
            if i < lives:
                screen.blit(heart, (x + i * (hw + 4), y))
            else:
                # Gray-out lost hearts
                gray = pygame.Surface(heart.get_size(), pygame.SRCALPHA)
                gray.fill((0, 0, 0, 0))
                gray.blit(heart, (0, 0))
                gray.fill((80, 80, 80, 160), special_flags=pygame.BLEND_RGBA_MULT)
                screen.blit(gray, (x + i * (hw + 4), y))

    # ---- Ammo ----

    def _draw_ammo(self, screen, player, assets):
        x = HUD_MARGIN
        y = HUD_MARGIN + HEART_DISPLAY_H + 8

        if player.reloading:
            # Progress bar for reload
            total_w = MAX_AMMO * (AMMO_ICON_H + 4)
            progress = 1.0 - player.reload_frames / RELOAD_TIME_TOTAL
            pygame.draw.rect(screen, DARK_GRAY, (x, y, total_w, AMMO_ICON_H))
            pygame.draw.rect(screen, ORANGE,    (x, y, int(total_w * progress), AMMO_ICON_H))
            pygame.draw.rect(screen, WHITE,     (x, y, total_w, AMMO_ICON_H), 1)
            lbl = self.font_small.render("Recargando...", True, WHITE)
            screen.blit(lbl, (x + total_w + 6, y + 2))
        else:
            icon = assets.bullet_icon
            iw   = icon.get_width()
            for i in range(MAX_AMMO):
                ix = x + i * (iw + 4)
                if i < player.ammo:
                    screen.blit(icon, (ix, y))
                else:
                    # dim
                    dim = pygame.Surface(icon.get_size(), pygame.SRCALPHA)
                    dim.fill((0, 0, 0, 0))
                    dim.blit(icon, (0, 0))
                    dim.fill((30, 30, 30, 180), special_flags=pygame.BLEND_RGBA_MULT)
                    screen.blit(dim, (ix, y))

    # ---- Shield status indicator ----

    def _draw_shield_status(self, screen, assets):
        si   = assets.shield_icon
        sw   = si.get_width() // 2
        sh   = si.get_height() // 2
        icon = pygame.transform.scale(si, (sw, sh))
        x    = SCREEN_WIDTH // 2 - sw // 2
        y    = HUD_MARGIN
        screen.blit(icon, (x, y))
        lbl = self.font.render("ESCUDO ACTIVO", True, (100, 180, 255))
        screen.blit(lbl, (x + sw + 6, y + sh // 2 - 10))

    # ---- Kill counter ----

    def _draw_kills(self, screen, kills, target):
        text  = self.font.render(f"Eliminados: {kills} / {target}", True, WHITE)
        shadow = self.font.render(f"Eliminados: {kills} / {target}", True, BLACK)
        tx = SCREEN_WIDTH - text.get_width() - HUD_MARGIN
        ty = HUD_MARGIN
        screen.blit(shadow, (tx + 1, ty + 1))
        screen.blit(text,   (tx,     ty))
