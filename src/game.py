import pygame
import random
from src.constants import *
from src.player import Player
from src.enemy import Enemy
from src.hud import HUD
from src.platform_map import get_platform_rects, draw_platforms
from src.assets import Assets


class Game:
    """
    Loop principal del juego.

    Estados:
      playing  → victoria / derrota
    """

    # Interval de spawn de enemigos (frames)
    SPAWN_INTERVAL = 300   # 5 segundos a 60 FPS

    def __init__(self, screen: pygame.Surface, color_key: str, lives: int):
        self.screen   = screen
        self.assets   = Assets.get()
        self.clock    = pygame.time.Clock()
        self.hud      = HUD()
        self.font_big = pygame.font.SysFont("Arial", 60, bold=True)
        self.font_med = pygame.font.SysFont("Arial", 32, bold=True)
        self.font_key = pygame.font.SysFont("Arial", 20)

        # Platforms
        self.platforms = get_platform_rects()

        # Player – spawns at original position (left side)
        spawn_x = PLAYER_SPAWN_XS[0]
        self.player = Player(spawn_x, GROUND_Y, color_key, lives)

        # Bullets list
        self.bullets: list = []

        # Enemies
        self.enemies: list  = []
        self.kills           = 0
        self.spawn_timer     = 60            # first spawn quick
        self._initial_spawn()

        # Input edge detection
        self._prev_keys = pygame.key.get_pressed()

    # ------------------------------------------------------------------
    # Public run
    # ------------------------------------------------------------------

    def run(self) -> str:
        """
        Game loop.  Returns:
          'victory'   – player reached ENEMIES_TO_DEFEAT
          'game_over' – player lost all lives
          'quit'      – window closed
        """
        while True:
            result = self._loop_frame()
            if result:
                return result

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _initial_spawn(self):
        """Spawn a couple of enemies on opposite side at start."""
        for _ in range(2):
            self._spawn_enemy()

    def _spawn_enemy(self):
        # Spawn on the opposite side from the player, or random platform
        plat = random.choice(self.platforms[1:])   # not ground (index 0 is ground)
        x    = random.randint(plat.left + 10, plat.right - 10)
        y    = plat.top
        # Ensure enemy spawns away from the player
        if abs(x - self.player.rect.centerx) < 150:
            x = SCREEN_WIDTH - x
            x = max(30, min(SCREEN_WIDTH - 30, x))
        self.enemies.append(Enemy(x, y))

    def _loop_frame(self) -> "str | None":
        dt_events = pygame.event.get()
        for event in dt_events:
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return self._pause()

        keys      = pygame.key.get_pressed()
        prev_keys = self._prev_keys

        # ---- Player input ----
        # Jump on X press (edge)
        if keys[pygame.K_x] and not prev_keys[pygame.K_x]:
            self.player.try_jump(True)
        # Variable jump on X release
        if not keys[pygame.K_x] and prev_keys[pygame.K_x]:
            self.player.release_jump()
        # Shoot on Z press
        if keys[pygame.K_z] and not prev_keys[pygame.K_z]:
            b = self.player.try_shoot()
            if b:
                self.bullets.append(b)
        # Reload on UP press
        if keys[pygame.K_UP] and not prev_keys[pygame.K_UP]:
            self.player.try_reload()

        self.player.update(keys, self.platforms)
        self._prev_keys = keys

        # ---- Enemies ----
        self.spawn_timer -= 1
        if self.spawn_timer <= 0 and self.kills < ENEMIES_TO_DEFEAT:
            self._spawn_enemy()
            self.spawn_timer = self.SPAWN_INTERVAL

        for enemy in self.enemies:
            enemy.update(self.platforms, self.player.rect)
            b = enemy.try_shoot(self.player.rect)
            if b:
                self.bullets.append(b)

        # ---- Bullets ----
        for bullet in self.bullets:
            bullet.update()

        # ---- Collisions ----
        self._handle_collisions()

        # ---- Remove dead objects ----
        self.bullets = [b for b in self.bullets if b.alive]
        for e in self.enemies:
            if not e.alive:
                self.kills += 1
        self.enemies = [e for e in self.enemies if e.alive]

        # ---- Victory / Defeat check ----
        if self.kills >= ENEMIES_TO_DEFEAT:
            return self._end_screen("victory")
        if not self.player.alive:
            return self._end_screen("game_over")

        # ---- Draw ----
        self._draw()

        self.clock.tick(FPS)
        return None

    def _handle_collisions(self):
        for bullet in self.bullets:
            if not bullet.alive:
                continue
            if bullet.owner == "enemy" and self.player.alive:
                if bullet.rect.colliderect(self.player.rect):
                    self.player.take_damage()
                    bullet.alive = False
            elif bullet.owner == "player":
                for enemy in self.enemies:
                    if enemy.alive and bullet.rect.colliderect(enemy.rect):
                        enemy.take_damage()
                        bullet.alive = False
                        break

    def _draw(self):
        # Background (whitehouse)
        self.screen.blit(self.assets.background, (0, 0))

        # Platforms on top of background
        draw_platforms(self.screen, self.platforms)

        # Enemies
        for enemy in self.enemies:
            enemy.draw(self.screen, self.assets)

        # Bullets
        for bullet in self.bullets:
            bullet.draw(self.screen, self.assets)

        # Player
        self.player.draw(self.screen, self.assets)

        # HUD (always on top)
        self.hud.draw(self.screen, self.player, self.kills, ENEMIES_TO_DEFEAT, self.assets)

        # Controls reminder (small, bottom-right)
        self._draw_controls()

        pygame.display.flip()

    def _draw_controls(self):
        lines = [
            "← → Mover   X Saltar   Z Disparar",
            "↑ Recargar   ↓ Escudo   ESC Pausa",
        ]
        y = SCREEN_HEIGHT - len(lines) * 22 - 6
        for line in lines:
            surf   = self.font_key.render(line, True, (200, 200, 200))
            shadow = self.font_key.render(line, True, (0, 0, 0))
            self.screen.blit(shadow, (SCREEN_WIDTH - surf.get_width() - 9, y + 1))
            self.screen.blit(surf,   (SCREEN_WIDTH - surf.get_width() - 10, y))
            y += 22

    # ------------------------------------------------------------------
    # Pause screen
    # ------------------------------------------------------------------

    def _pause(self) -> "str | None":
        font  = pygame.font.SysFont("Arial", 48, bold=True)
        small = pygame.font.SysFont("Arial", 26)
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return None          # resume
                    if event.key == pygame.K_q:
                        return "game_over"   # quit to end

            self.screen.blit(overlay, (0, 0))
            self._centered(font,  "PAUSA", YELLOW, SCREEN_HEIGHT // 2 - 60)
            self._centered(small, "ESC – Continuar   |   Q – Salir", WHITE, SCREEN_HEIGHT // 2 + 10)
            pygame.display.flip()
            self.clock.tick(30)

    # ------------------------------------------------------------------
    # End screen (victory / game over)
    # ------------------------------------------------------------------

    def _end_screen(self, result: str) -> str:
        if result == "victory":
            title = "¡Victoria!"
            color = YELLOW
            sub   = f"¡Derrotaste a {ENEMIES_TO_DEFEAT} enemigos!"
        else:
            title = "GAME OVER"
            color = RED
            sub   = "Has perdido todas tus vidas."

        font_big  = pygame.font.SysFont("Arial", 72, bold=True)
        font_med  = pygame.font.SysFont("Arial", 30)
        font_small= pygame.font.SysFont("Arial", 22)
        overlay   = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        return result
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        raise SystemExit

            self.screen.blit(self.assets.background, (0, 0))
            self.screen.blit(overlay, (0, 0))

            self._centered(font_big,   title, color,     SCREEN_HEIGHT // 2 - 80)
            self._centered(font_med,   sub,   WHITE,     SCREEN_HEIGHT // 2 + 10)
            self._centered(font_small, f"Enemigos eliminados: {self.kills}",
                           LIGHT_GRAY, SCREEN_HEIGHT // 2 + 55)
            self._centered(font_small, "Enter – Menú principal   |   ESC – Salir",
                           LIGHT_GRAY, SCREEN_HEIGHT - 50)

            pygame.display.flip()
            self.clock.tick(30)

    # ------------------------------------------------------------------
    # Util
    # ------------------------------------------------------------------

    def _centered(self, font, text, color, y):
        surf   = font.render(text, True, color)
        shadow = font.render(text, True, BLACK)
        cx     = SCREEN_WIDTH // 2 - surf.get_width() // 2
        self.screen.blit(shadow, (cx + 2, y + 2))
        self.screen.blit(surf,   (cx,     y))
