"""Menú de selección de personaje usando los assets originales del SSB."""
import pygame
from src.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, CHARACTERS, CHARACTER_LABELS,
    CHARACTER_STATS, WHITE, BLACK, YELLOW, GRAY, LIGHT_GRAY,
)


class Menu:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.font_title = pygame.font.SysFont("Arial", 46, bold=True)
        self.font_med   = pygame.font.SysFont("Arial", 28, bold=True)
        self.font_small = pygame.font.SysFont("Arial", 20)
        self.font_stat  = pygame.font.SysFont("Arial", 16)

    # ------------------------------------------------------------------
    # Pantalla de selección de personaje
    # ------------------------------------------------------------------

    def character_screen(self, assets) -> str:
        """Devuelve el nombre del personaje elegido."""
        selected = 0
        clock    = pygame.time.Clock()

        # Escalar botones de personaje a tamaño cómodo
        btn_w, btn_h = 110, 110
        scaled_btns = {}
        for char, (a, b) in assets.char_buttons.items():
            scaled_btns[char] = (
                pygame.transform.scale(a, (btn_w, btn_h)),
                pygame.transform.scale(b, (btn_w, btn_h)),
            )

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); raise SystemExit
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        selected = (selected - 1) % len(CHARACTERS)
                    elif event.key == pygame.K_RIGHT:
                        selected = (selected + 1) % len(CHARACTERS)
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        return CHARACTERS[selected]

            self.screen.blit(assets.char_bg, (0, 0))

            # Overlay semitransparente en la mitad inferior (botones + stats)
            overlay = pygame.Surface((SCREEN_WIDTH, 310), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            self.screen.blit(overlay, (0, SCREEN_HEIGHT - 310))

            # Botones de personaje en una fila
            gap   = 20
            total = len(CHARACTERS) * (btn_w + gap) - gap
            sx0   = SCREEN_WIDTH // 2 - total // 2
            cy    = SCREEN_HEIGHT // 2 + 30

            for i, char in enumerate(CHARACTERS):
                x    = sx0 + i * (btn_w + gap)
                a, b = scaled_btns[char]

                if i == selected:
                    pygame.draw.rect(self.screen, YELLOW,
                                     (x - 5, cy - 5, btn_w + 10, btn_h + 10), 3,
                                     border_radius=6)
                    self.screen.blit(b, (x, cy))
                else:
                    self.screen.blit(a, (x, cy))

                lbl = self.font_small.render(CHARACTER_LABELS[char], True, WHITE)
                lx  = x + btn_w // 2 - lbl.get_width() // 2
                self.screen.blit(lbl, (lx, cy + btn_h + 4))

            # Stats del personaje seleccionado
            char = CHARACTERS[selected]
            weak, heavy, acce = CHARACTER_STATS[char]
            stats_y = cy + btn_h + 34
            self._shadow(self.font_med, CHARACTER_LABELS[char], YELLOW, stats_y)
            stats_y += 34
            for label, value in [("Ataque débil", f"{weak}"), ("Ataque fuerte", f"{heavy}"), ("Velocidad", f"{acce}")]:
                t = self.font_stat.render(f"{label}: {value}", True, WHITE)
                self.screen.blit(t, (SCREEN_WIDTH // 2 - t.get_width() // 2, stats_y))
                stats_y += 20

            self._shadow(self.font_small,
                         "← / →  elegir   |   Enter confirmar",
                         LIGHT_GRAY, SCREEN_HEIGHT - 35)

            pygame.display.flip()
            clock.tick(FPS)

    # ------------------------------------------------------------------
    # Pantalla de Game Over / Victoria
    # ------------------------------------------------------------------

    def end_screen(self, assets, result: str, kills: int) -> str:
        if result == "victory":
            title = "¡VICTORIA!"
            color = YELLOW
            sub   = f"¡Derrotaste a {kills} enemigos!"
        else:
            title = "GAME OVER"
            color = (220, 30, 30)
            sub   = "Tu personaje ha sido eliminado."

        font_big  = pygame.font.SysFont("Arial", 70, bold=True)
        font_med  = pygame.font.SysFont("Arial", 30)
        font_s    = pygame.font.SysFont("Arial", 22)
        overlay   = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        clock = pygame.time.Clock()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); raise SystemExit
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        return "restart"
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit(); raise SystemExit

            self.screen.blit(assets.arena, (0, 0))
            self.screen.blit(overlay, (0, 0))

            self._shadow(font_big,  title,                    color,      SCREEN_HEIGHT // 2 - 90)
            self._shadow(font_med,  sub,                      WHITE,      SCREEN_HEIGHT // 2 + 10)
            self._shadow(font_s, "Enter – Volver al menú   |   ESC – Salir",
                         GRAY, SCREEN_HEIGHT - 50)

            pygame.display.flip()
            clock.tick(30)

    # ------------------------------------------------------------------
    # Util
    # ------------------------------------------------------------------

    def _shadow(self, font, text, color, y):
        surf   = font.render(text, True, color)
        shadow = font.render(text, True, BLACK)
        cx     = SCREEN_WIDTH // 2 - surf.get_width() // 2
        self.screen.blit(shadow, (cx + 2, y + 2))
        self.screen.blit(surf,   (cx,     y))
