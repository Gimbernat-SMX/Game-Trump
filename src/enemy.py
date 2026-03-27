"""Enemigo IA: persigue y ataca al jugador en melee."""
import pygame
import random
from src.constants import (
    GRAVITY, ARENA_WIDTH, STAND, WALK, ATTACK_RANGE, CHARACTERS,
)
from src.characters.base import Character

vec = pygame.math.Vector2

_ENEMY_POOL = ["luigi", "yoshi", "popo", "nana", "link", "mario"]
_pool_idx   = 0


def make_enemy(player_char: str, x: int, y: int) -> "Enemy":
    global _pool_idx
    pool = [c for c in _ENEMY_POOL if c != player_char]
    char_name = pool[_pool_idx % len(pool)]
    _pool_idx += 1
    return Enemy(char_name, x, y)


class Enemy(Character):
    def __init__(self, char_name: str, x: int, y: int):
        super().__init__(char_name, x, y)

        self._attack_cd  = random.randint(30, 90)
        self._jump_timer = random.randint(60, 180)

    def update(self, platforms, player, assets):
        self._tick_timers()

        if self.health > 0 and player.alive:
            dx   = player.pos.x - self.pos.x
            dy   = player.pos.y - self.pos.y
            dist = abs(dx)

            self.acc = vec(0.0, GRAVITY)

            # ---- Movimiento ----
            if dist > ATTACK_RANGE * 0.8:
                self.direc = "right" if dx > 0 else "left"
                move_acc   = self.acce if dx > 0 else -self.acce

                # Evitar salir del arena
                if self.pos.x <= 40:
                    move_acc   = abs(self.acce)
                    self.direc = "right"
                elif self.pos.x >= ARENA_WIDTH - 40:
                    move_acc   = -abs(self.acce)
                    self.direc = "left"

                self.acc.x = move_acc
                self._set_moving()
            else:
                self._set_standing()

            # ---- Salto IA ----
            self._jump_timer -= 1
            if self._jump_timer <= 0:
                if dy < -40 or random.random() < 0.3:
                    self.jump(platforms)
                self._jump_timer = random.randint(60, 180)

            # ---- Ataque ----
            self._attack_cd -= 1
            if self._attack_cd <= 0 and dist < ATTACK_RANGE:
                if random.random() < 0.6:
                    self.weak_attack([player])
                else:
                    self.heavy_attack([player])
                self._attack_cd = random.randint(40, 100)
        else:
            self.acc = vec(0.0, GRAVITY)

        self._apply_physics(platforms)
        self._update_image(assets)

    def draw(self, screen: pygame.Surface):
        screen.blit(self.image, self.rect)

        if self.health > 0:
            bw = 40
            bh = 5
            bx = self.rect.centerx - bw // 2
            by = self.rect.top - 10
            pygame.draw.rect(screen, (200, 0,   0),   (bx, by, bw, bh))
            pygame.draw.rect(screen, (0,   200, 0),   (bx, by, int(bw * self.health / 100), bh))
            pygame.draw.rect(screen, (255, 255, 255), (bx, by, bw, bh), 1)
