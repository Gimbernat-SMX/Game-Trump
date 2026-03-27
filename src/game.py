"""Loop principal del juego Super Smash Bros single-player."""
import pygame
import random
from src.constants import (
    FPS, SCREEN_WIDTH, SCREEN_HEIGHT, ARENA_WIDTH,
    BLACK, WHITE, GRAY, YELLOW,
    ENEMY_SPAWNS, MAX_ENEMIES_ON_SCREEN, ENEMY_SPAWN_INTERVAL,
    ENEMIES_TO_DEFEAT, PLAYER_SPAWN, DEFAULT_ZOOM,
)
from src.player import Player
from src.enemy  import make_enemy
from src.hud    import HUD
from src.platform_map import create_platform_group
from src.assets import Assets


class Game:
    def __init__(self, screen: pygame.Surface, char_name: str):
        self.screen    = screen
        self.assets    = Assets.get()
        self.clock     = pygame.time.Clock()
        self.hud       = HUD()
        self.char_name = char_name

        # Plataformas (sprites)
        self.platforms = create_platform_group()

        # Jugador
        self.player = Player(char_name, *PLAYER_SPAWN)

        # Cámara / zoom
        self.zoom = DEFAULT_ZOOM
        # convert() para compatibilidad con el formato del display
        self._world_surf = pygame.Surface((ARENA_WIDTH, SCREEN_HEIGHT)).convert()

        # Enemigos
        self.enemies: list   = []
        self.kills            = 0
        self.spawn_timer      = 90    # primer spawn rápido
        self._spawn_initial()

    # ------------------------------------------------------------------

    def run(self) -> str:
        """Loop principal. Devuelve 'victory' o 'game_over'."""
        while True:
            result = self._frame()
            if result:
                return result

    # ------------------------------------------------------------------

    def _spawn_initial(self):
        self._spawn_enemy()

    def _spawn_enemy(self):
        pos = random.choice(ENEMY_SPAWNS)
        # Asegurar que no spawn encima del jugador
        while abs(pos[0] - self.player.pos.x) < 120:
            pos = random.choice(ENEMY_SPAWNS)
        self.enemies.append(make_enemy(self.char_name, pos[0], pos[1]))

    def _frame(self) -> "str | None":
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); raise SystemExit
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    result = self._pause()
                    if result:
                        return result
                elif event.key == pygame.K_F10:
                    pygame.display.toggle_fullscreen()
                elif event.key == pygame.K_w:
                    self.player.queue_jump()
                elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                    self.zoom = min(3.0, self.zoom + 0.2)
                elif event.key == pygame.K_MINUS:
                    self.zoom = max(1.0, self.zoom - 0.2)

        # ---- Actualizar jugador ----
        self.player.update(self.platforms, self.enemies, self.assets)

        # ---- Actualizar enemigos ----
        for e in self.enemies:
            e.update(self.platforms, self.player, self.assets)

        # ---- Spawn ----
        self.spawn_timer -= 1
        if (self.spawn_timer <= 0
                and len(self.enemies) < MAX_ENEMIES_ON_SCREEN
                and self.kills < ENEMIES_TO_DEFEAT):
            self._spawn_enemy()
            self.spawn_timer = ENEMY_SPAWN_INTERVAL

        # ---- Limpiar muertos ----
        new_enemies = []
        for e in self.enemies:
            if not e.alive:
                self.kills += 1
            else:
                new_enemies.append(e)
        self.enemies = new_enemies

        # ---- Condiciones de fin ----
        if self.kills >= ENEMIES_TO_DEFEAT:
            return "victory"
        if not self.player.alive:
            return "game_over"

        # ---- Dibujar ----
        self._draw()
        self.clock.tick(FPS)
        return None

    def _draw(self):
        # Renderizar mundo a superficie auxiliar
        ws = self._world_surf
        ws.blit(self.assets.arena, (0, 0))
        self.platforms.draw(ws)
        for e in self.enemies:
            e.draw(ws)
        self.player.draw(ws)

        # Zoom: escalar el mundo completo y recortar centrado en el jugador
        zoomed_w = int(ARENA_WIDTH * self.zoom)
        zoomed_h = int(SCREEN_HEIGHT * self.zoom)
        zoomed = pygame.transform.scale(ws, (zoomed_w, zoomed_h))
        view_x = int(self.player.pos.x * self.zoom - ARENA_WIDTH / 2)
        view_y = int(self.player.pos.y * self.zoom - SCREEN_HEIGHT / 2)
        view_x = max(0, min(zoomed_w - ARENA_WIDTH, view_x))
        view_y = max(0, min(zoomed_h - SCREEN_HEIGHT, view_y))
        self.screen.blit(zoomed, (0, 0), pygame.Rect(view_x, view_y, ARENA_WIDTH, SCREEN_HEIGHT))

        # HUD (panel lateral sin zoom)
        self.hud.draw(self.screen, self.player, self.enemies, self.kills)

        pygame.display.flip()

    # ------------------------------------------------------------------
    # Pausa
    # ------------------------------------------------------------------

    def _pause(self) -> "str | None":
        font    = pygame.font.SysFont("Arial", 50, bold=True)
        small   = pygame.font.SysFont("Arial", 26)
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); raise SystemExit
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return None       # continuar
                    if event.key == pygame.K_q:
                        return "game_over"

            self.screen.blit(overlay, (0, 0))
            self._center(font,  "PAUSA",                        YELLOW, SCREEN_HEIGHT // 2 - 50)
            self._center(small, "ESC – Continuar   |   Q – Salir   |   +/- Zoom", WHITE, SCREEN_HEIGHT // 2 + 20)
            pygame.display.flip()
            self.clock.tick(30)

    def _center(self, font, text, color, y):
        surf   = font.render(text, True, color)
        shadow = font.render(text, True, BLACK)
        cx     = ARENA_WIDTH // 2 - surf.get_width() // 2
        self.screen.blit(shadow, (cx + 2, y + 2))
        self.screen.blit(surf,   (cx,     y))
