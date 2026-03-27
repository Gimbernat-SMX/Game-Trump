"""Menú de selección de personaje y pantallas de modo de juego."""
import pygame
from src.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, CHARACTERS, CHARACTER_LABELS,
    CHARACTER_STATS, WHITE, BLACK, YELLOW, GRAY, LIGHT_GRAY, DARK_GRAY,
)
from src.network.discovery import discover_lobbies


class Menu:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.font_title = pygame.font.SysFont("Arial", 46, bold=True)
        self.font_med   = pygame.font.SysFont("Arial", 28, bold=True)
        self.font_small = pygame.font.SysFont("Arial", 20)
        self.font_stat  = pygame.font.SysFont("Arial", 16)

    # ------------------------------------------------------------------
    # Pantalla de selección de modo
    # ------------------------------------------------------------------

    def mode_screen(self, assets) -> str:
        """Devuelve 'singleplayer', 'host' o 'join'."""
        options = [
            ("Un Jugador",      "singleplayer"),
            ("Crear Partida",   "host"),
            ("Unirse a Partida","join"),
        ]
        selected = 0
        clock    = pygame.time.Clock()
        font_opt = pygame.font.SysFont("Arial", 34, bold=True)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); raise SystemExit
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected = (selected - 1) % len(options)
                    elif event.key == pygame.K_DOWN:
                        selected = (selected + 1) % len(options)
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        return options[selected][1]
                    elif event.key == pygame.K_F10:
                        pygame.display.toggle_fullscreen()

            self.screen.blit(assets.intro_bg, (0, 0))
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 120))
            self.screen.blit(overlay, (0, 0))

            for i, (label, _) in enumerate(options):
                color = YELLOW if i == selected else WHITE
                if i == selected:
                    surf = font_opt.render(f"▶  {label}", True, color)
                else:
                    surf = font_opt.render(f"   {label}", True, color)
                self.screen.blit(surf, (SCREEN_WIDTH // 2 - surf.get_width() // 2,
                                        280 + i * 70))

            hint = self.font_stat.render("↑↓ Navegar   |   Enter confirmar   |   F10 pantalla completa", True, GRAY)
            self.screen.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2,
                                    SCREEN_HEIGHT - 40))

            pygame.display.flip()
            clock.tick(FPS)

    # ------------------------------------------------------------------
    # Pantalla de introducir nombre (host)
    # ------------------------------------------------------------------

    def host_setup_screen(self, assets) -> "tuple[str, str] | None":
        """Devuelve (nombre, personaje) o None si se cancela."""
        while True:
            name = self._name_input_screen(assets, "CREAR PARTIDA", "Tu nombre:")
            if name is None:
                return None

            char = self.character_screen(assets)
            if char is None:
                continue  # volver a introducir nombre

            return name, char

    # ------------------------------------------------------------------
    # Pantalla de unirse a partida
    # ------------------------------------------------------------------

    def join_setup_screen(self, assets) -> "tuple[str, str, str] | None":
        """Devuelve (nombre, ip, personaje) o None si se cancela."""
        while True:
            name = self._name_input_screen(assets, "UNIRSE A PARTIDA", "Tu nombre:")
            if name is None:
                return None

            while True:
                ip = self._lobby_browser_screen(assets)
                if not ip:
                    break  # volver a pantalla de nombre

                char = self.character_screen(assets)
                if char is None:
                    continue  # volver a selección de sala

                return name, ip, char

    def _lobby_browser_screen(self, assets) -> "str | None":
        """Pantalla para descubrir y seleccionar salas LAN disponibles."""
        font_t = pygame.font.SysFont("Arial", 36, bold=True)
        font_p = pygame.font.SysFont("Arial", 24, bold=True)
        font_s = pygame.font.SysFont("Arial", 18)
        clock = pygame.time.Clock()

        lobbies = discover_lobbies()
        selected = 0

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); raise SystemExit
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return None
                    if event.key == pygame.K_UP and lobbies:
                        selected = (selected - 1) % len(lobbies)
                    elif event.key == pygame.K_DOWN and lobbies:
                        selected = (selected + 1) % len(lobbies)
                    elif event.key in (pygame.K_r, pygame.K_F5):
                        lobbies = discover_lobbies()
                        if lobbies:
                            selected = min(selected, len(lobbies) - 1)
                        else:
                            selected = 0
                    elif event.key == pygame.K_m:
                        manual_ip = self._name_input_screen(
                            assets,
                            "UNIRSE A PARTIDA",
                            "IP del anfitrión:",
                            max_len=15,
                            hint="Ejemplo: 192.168.1.10",
                        )
                        if manual_ip:
                            return manual_ip
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        if lobbies:
                            return lobbies[selected]["ip"]

            self.screen.blit(assets.char_bg, (0, 0))
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 165))
            self.screen.blit(overlay, (0, 0))

            self._shadow(font_t, "SALAS EN RED LOCAL", YELLOW, 80)

            if not lobbies:
                msg = font_p.render("No se encontraron partidas.", True, LIGHT_GRAY)
                self.screen.blit(msg, (SCREEN_WIDTH // 2 - msg.get_width() // 2,
                                       SCREEN_HEIGHT // 2 - 40))
                hint = font_s.render("R/F5 buscar otra vez   |   M IP manual   |   ESC volver",
                                     True, GRAY)
                self.screen.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2,
                                        SCREEN_HEIGHT - 80))
            else:
                y = 170
                for i, lobby in enumerate(lobbies):
                    is_sel = (i == selected)
                    rect = pygame.Rect(SCREEN_WIDTH // 2 - 320, y - 6, 640, 48)
                    if is_sel:
                        pygame.draw.rect(self.screen, (60, 60, 80), rect, border_radius=6)
                        pygame.draw.rect(self.screen, YELLOW, rect, 2, border_radius=6)

                    txt = (f"{lobby['host_name']}  |  {lobby['ip']}:{lobby['port']}"
                           f"  |  Jugadores: {lobby['players']}/{lobby['max_players']}")
                    s = font_s.render(txt, True, WHITE if is_sel else LIGHT_GRAY)
                    self.screen.blit(s, (SCREEN_WIDTH // 2 - 300, y + 9))
                    y += 56

                hint = font_s.render("↑↓ seleccionar   |   Enter unir   |   R/F5 refrescar   |   M IP manual   |   ESC volver",
                                     True, GRAY)
                self.screen.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2,
                                        SCREEN_HEIGHT - 80))

            pygame.display.flip()
            clock.tick(FPS)

    # ------------------------------------------------------------------
    # Pantalla de selección de personaje
    # ------------------------------------------------------------------

    def character_screen(self, assets) -> "str | None":
        """Devuelve el personaje elegido o None si se cancela con ESC."""
        selected = 0
        clock    = pygame.time.Clock()

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
                    elif event.key == pygame.K_ESCAPE:
                        return None
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        return CHARACTERS[selected]

            self.screen.blit(assets.char_bg, (0, 0))

            overlay = pygame.Surface((SCREEN_WIDTH, 310), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            self.screen.blit(overlay, (0, SCREEN_HEIGHT - 310))

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

            char = CHARACTERS[selected]
            weak, heavy, acce = CHARACTER_STATS[char]
            stats_y = cy + btn_h + 34
            self._shadow(self.font_med, CHARACTER_LABELS[char], YELLOW, stats_y)
            stats_y += 34
            for label, value in [("Ataque débil", f"{weak}"),
                                  ("Ataque fuerte", f"{heavy}"),
                                  ("Velocidad", f"{acce}")]:
                t = self.font_stat.render(f"{label}: {value}", True, WHITE)
                self.screen.blit(t, (SCREEN_WIDTH // 2 - t.get_width() // 2, stats_y))
                stats_y += 20

            self._shadow(self.font_small,
                         "← / → elegir   |   Enter confirmar   |   ESC volver   |   F10 pantalla completa",
                         LIGHT_GRAY, SCREEN_HEIGHT - 35)

            pygame.display.flip()
            clock.tick(FPS)

    # ------------------------------------------------------------------
    # Pantalla de Game Over / Victoria (single player)
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

            self._shadow(font_big,  title, color,     SCREEN_HEIGHT // 2 - 90)
            self._shadow(font_med,  sub,   WHITE,     SCREEN_HEIGHT // 2 + 10)
            self._shadow(font_s,    "Enter – Volver al menú   |   ESC – Salir",
                         GRAY, SCREEN_HEIGHT - 50)

            pygame.display.flip()
            clock.tick(30)

    # ------------------------------------------------------------------
    # Pantalla de fin de partida multijugador
    # ------------------------------------------------------------------

    def end_screen_mp(self, assets, winner: str) -> str:
        font_big = pygame.font.SysFont("Arial", 60, bold=True)
        font_med = pygame.font.SysFont("Arial", 30)
        font_s   = pygame.font.SysFont("Arial", 22)
        overlay  = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        clock = pygame.time.Clock()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); raise SystemExit
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        return "menu"
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit(); raise SystemExit

            self.screen.blit(assets.arena, (0, 0))
            self.screen.blit(overlay, (0, 0))

            self._shadow(font_big, "¡FIN DE PARTIDA!", YELLOW, SCREEN_HEIGHT // 2 - 100)
            self._shadow(font_med, f"Ganador: {winner}", WHITE, SCREEN_HEIGHT // 2)
            self._shadow(font_s,
                         "Enter – Volver al menú   |   ESC – Salir",
                         GRAY, SCREEN_HEIGHT - 50)

            pygame.display.flip()
            clock.tick(30)

    # ------------------------------------------------------------------
    # Util
    # ------------------------------------------------------------------

    def _name_input_screen(self, assets, title: str, prompt: str,
                            max_len: int = 16, hint: str = "") -> "str | None":
        """Pantalla de entrada de texto. Devuelve texto o None con ESC."""
        font_t = pygame.font.SysFont("Arial", 36, bold=True)
        font_p = pygame.font.SysFont("Arial", 24)
        font_i = pygame.font.SysFont("Arial", 30)
        clock  = pygame.time.Clock()
        text   = ""
        cursor_tick = 0

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); raise SystemExit
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN and text.strip():
                        return text.strip()
                    elif event.key == pygame.K_ESCAPE:
                        return None
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    elif event.unicode and len(text) < max_len:
                        if event.unicode.isprintable():
                            text += event.unicode

            self.screen.blit(assets.char_bg, (0, 0))
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            self.screen.blit(overlay, (0, 0))

            self._shadow(font_t, title, YELLOW, SCREEN_HEIGHT // 2 - 130)

            ps = font_p.render(prompt, True, LIGHT_GRAY)
            self.screen.blit(ps, (SCREEN_WIDTH // 2 - ps.get_width() // 2,
                                  SCREEN_HEIGHT // 2 - 60))

            if hint:
                hs = font_p.render(hint, True, GRAY)
                self.screen.blit(hs, (SCREEN_WIDTH // 2 - hs.get_width() // 2,
                                      SCREEN_HEIGHT // 2 - 30))

            # Caja de texto
            cursor_tick += 1
            cursor = "|" if (cursor_tick // 30) % 2 == 0 else ""
            inp_s = font_i.render(text + cursor, True, WHITE)
            box   = pygame.Rect(SCREEN_WIDTH // 2 - 180, SCREEN_HEIGHT // 2 + 10, 360, 44)
            pygame.draw.rect(self.screen, (40, 40, 60), box, border_radius=6)
            pygame.draw.rect(self.screen, YELLOW, box, 2, border_radius=6)
            self.screen.blit(inp_s, (box.x + 10, box.y + 7))

            enter_s = self.font_stat.render("Enter confirmar   |   ESC volver", True, GRAY)
            self.screen.blit(enter_s, (SCREEN_WIDTH // 2 - enter_s.get_width() // 2,
                                       SCREEN_HEIGHT // 2 + 70))

            pygame.display.flip()
            clock.tick(FPS)

    def _shadow(self, font, text, color, y):
        surf   = font.render(text, True, color)
        shadow = font.render(text, True, BLACK)
        cx     = SCREEN_WIDTH // 2 - surf.get_width() // 2
        self.screen.blit(shadow, (cx + 2, y + 2))
        self.screen.blit(surf,   (cx,     y))
