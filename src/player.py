"""Jugador controlado por teclado."""
import pygame
from src.constants import GRAVITY, ARENA_WIDTH
from src.characters.base import Character

vec = pygame.math.Vector2


class Player(Character):
    def __init__(self, char_name: str, x: int, y: int):
        super().__init__(char_name, x, y)
        self._jump_queued = False

    def queue_jump(self):
        """Llamar desde el event loop al detectar KEYDOWN K_w."""
        self._jump_queued = True

    def update(self, platforms, enemies, assets):
        keys = pygame.key.get_pressed()

        self._tick_timers()

        if self.health > 0:
            self.acc = vec(0.0, GRAVITY)

            moving = False
            if keys[pygame.K_a] and self.pos.x > 40:
                self.acc.x = -self.acce
                self.direc = "left"
                moving = True
            elif keys[pygame.K_d] and self.pos.x < ARENA_WIDTH - 40:
                self.acc.x = self.acce
                self.direc = "right"
                moving = True

            if moving:
                self._set_moving()
            else:
                self._set_standing()

            if self._jump_queued:
                self._jump_queued = False
                self.jump(platforms)

            if keys[pygame.K_f]:
                self.weak_attack(enemies)
            elif keys[pygame.K_x]:
                self.heavy_attack(enemies)
        else:
            self.acc = vec(0.0, GRAVITY)
            self._jump_queued = False

        self._apply_physics(platforms)
        self._update_image(assets)

    def draw(self, screen: pygame.Surface):
        screen.blit(self.image, self.rect)
