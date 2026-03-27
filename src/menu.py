import pygame
from src.constants import *


class Menu:
    """Pantallas de menú: configuración de vidas y selección de personaje."""

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.font_title = pygame.font.SysFont("Arial", 56, bold=True)
        self.font_med   = pygame.font.SysFont("Arial", 32, bold=True)
        self.font_small = pygame.font.SysFont("Arial", 22)

    # ------------------------------------------------------------------
    # Pantalla 1: elegir vidas
    # ------------------------------------------------------------------

    def lives_screen(self, assets) -> int:
        lives = 3
        clock = pygame.time.Clock()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP   and lives < 9:
                        lives += 1
                    elif event.key == pygame.K_DOWN and lives > 1:
                        lives -= 1
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        return lives

            # Background
            self.screen.blit(assets.background, (0, 0))
            # Dark overlay
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            self.screen.blit(overlay, (0, 0))

            self._text_shadow(self.font_title, "PumpTrump",
                              YELLOW, SCREEN_HEIGHT // 6)
            self._text_shadow(self.font_med, "¿Cuántas vidas quieres?",
                              WHITE, SCREEN_HEIGHT // 6 + 70)

            # Heart icons
            heart = assets.heart
            hw    = heart.get_width()
            total_w = lives * (hw + 4) - 4
            hx    = SCREEN_WIDTH // 2 - total_w // 2
            hy    = SCREEN_HEIGHT // 2 - HEART_DISPLAY_H // 2
            for i in range(lives):
                self.screen.blit(heart, (hx + i * (hw + 4), hy))

            self._text_shadow(self.font_med, f"Vidas: {lives}",
                              WHITE, SCREEN_HEIGHT // 2 + HEART_DISPLAY_H + 16)
            self._text_shadow(self.font_small,
                              "↑ / ↓  para cambiar   |   Enter para confirmar",
                              LIGHT_GRAY, SCREEN_HEIGHT - 55)

            pygame.display.flip()
            clock.tick(FPS)

    # ------------------------------------------------------------------
    # Pantalla 2: selección de personaje
    # ------------------------------------------------------------------

    def character_screen(self, assets) -> str:
        options = list(PLAYER_COLORS.keys())
        labels  = {
            "black":   "Negro",
            "blue":    "Azul",
            "red":     "Rojo",
            "magenta": "Magenta",
        }
        selected = 0
        clock    = pygame.time.Clock()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        selected = (selected - 1) % len(options)
                    elif event.key == pygame.K_RIGHT:
                        selected = (selected + 1) % len(options)
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        return options[selected]

            # Background
            self.screen.blit(assets.background, (0, 0))
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            self.screen.blit(overlay, (0, 0))

            self._text_shadow(self.font_title, "Elige tu personaje",
                              YELLOW, SCREEN_HEIGHT // 7)

            # Character previews using sprite id=1,2,3,4
            n     = len(options)
            box_w = SPRITE_W + 16
            gap   = 32
            total = n * box_w + (n - 1) * gap
            sx0   = SCREEN_WIDTH // 2 - total // 2
            cy    = SCREEN_HEIGHT // 2 - SPRITE_H // 2 + 10

            for i, key in enumerate(options):
                pid  = PLAYER_SPRITE_ID[key]
                surf = assets.get_sprite(pid, "idle", 0, False)
                x    = sx0 + i * (box_w + gap)

                if i == selected:
                    pygame.draw.rect(self.screen, YELLOW,
                                     (x - 6, cy - 6, SPRITE_W + 12, SPRITE_H + 12), 3,
                                     border_radius=8)

                self.screen.blit(surf, (x, cy))

                # Color name label
                lbl = self.font_small.render(labels[key], True, PLAYER_COLORS[key])
                lx  = x + SPRITE_W // 2 - lbl.get_width() // 2
                self.screen.blit(lbl, (lx, cy + SPRITE_H + 8))

            self._text_shadow(
                self.font_small,
                "← / →  para elegir   |   Enter para confirmar",
                LIGHT_GRAY, SCREEN_HEIGHT - 55,
            )

            pygame.display.flip()
            clock.tick(FPS)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _text_shadow(self, font, text, color, y, shadow_color=(0, 0, 0)):
        surf   = font.render(text, True, color)
        shadow = font.render(text, True, shadow_color)
        cx     = SCREEN_WIDTH // 2 - surf.get_width() // 2
        self.screen.blit(shadow, (cx + 2, y + 2))
        self.screen.blit(surf,   (cx,     y))
