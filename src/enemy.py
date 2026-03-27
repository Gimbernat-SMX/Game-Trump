"""
Enemigo IA: usa la base Character con lógica de persecución y ataque melee.
"""
import pygame
import random
from src.constants import (
    GRAVITY, ARENA_WIDTH, CHARACTERS, STAND, WALK, DEAD,
    ATTACK_RANGE,
)
from src.characters.base import Character

vec = pygame.math.Vector2

# Ciclar personajes enemigos (excluir al jugador se hace en game.py)
_ENEMY_CHARS = ["luigi", "yoshi", "popo", "nana", "link", "mario"]
_char_idx = 0


def _next_char(exclude: str) -> str:
    global _char_idx
    chars = [c for c in _ENEMY_CHARS if c != exclude]
    c = chars[_char_idx % len(chars)]
    _char_idx += 1
    return c


def make_enemy(player_char: str, x: int, y: int) -> "Enemy":
    from src.characters.mario  import Mario
    from src.characters.luigi  import Luigi
    from src.characters.yoshi  import Yoshi
    from src.characters.popo   import Popo
    from src.characters.nana   import Nana
    from src.characters.link   import Link
    classes = {"mario": Mario, "luigi": Luigi, "yoshi": Yoshi,
               "popo": Popo, "nana": Nana, "link": Link}
    char_name = _next_char(player_char)
    return Enemy(classes[char_name], x, y)


class Enemy(Character):
    """Character con IA simple: perseguir → atacar."""

    def __init__(self, char_class, x: int, y: int):
        self.__class__ = type(
            char_class.__name__ + "Enemy",
            (Enemy, char_class),
            {"name": char_class.name},
        )
        super().__init__(x, y, is_player=False)
        self.name = char_class.name

        # IA
        self._attack_cd  = random.randint(30, 90)
        self._jump_timer = random.randint(60, 180)

    def update(self, platforms, player, assets):
        self._tick_timers()

        if self.health > 0 and player.alive:
            dx = player.pos.x - self.pos.x
            dy = player.pos.y - self.pos.y
            dist = abs(dx)

            self.acc = vec(0, GRAVITY)

            # ---- Movimiento: perseguir al jugador ----
            if dist > ATTACK_RANGE * 0.8:
                self.direc = "right" if dx > 0 else "left"
                self.acc.x = self.acce if dx > 0 else -self.acce
                if self.pos.x <= 40:
                    self.acc.x = abs(self.acce)
                    self.direc = "right"
                elif self.pos.x >= ARENA_WIDTH - 40:
                    self.acc.x = -abs(self.acce)
                    self.direc = "left"
                if self._attack_timer == 0 and self._damaged_timer == 0:
                    self.state  = WALK
                    self.walk_c = (self.walk_c + 1) % self.n_walk
            else:
                if self._attack_timer == 0 and self._damaged_timer == 0:
                    self.state = STAND

            # ---- Salto IA ----
            self._jump_timer -= 1
            if self._jump_timer <= 0:
                if dy < -40:   # jugador está más arriba
                    self.jump(platforms)
                elif random.random() < 0.3:
                    self.jump(platforms)
                self._jump_timer = random.randint(60, 180)

            # ---- Ataque si está cerca ----
            self._attack_cd -= 1
            if self._attack_cd <= 0 and dist < ATTACK_RANGE:
                if random.random() < 0.6:
                    self.weak_attack([player])
                else:
                    self.heavy_attack([player])
                self._attack_cd = random.randint(40, 100)
        else:
            self.acc = vec(0, GRAVITY)

        self._apply_physics(platforms)
        self._update_image(assets)

    def draw(self, screen: pygame.Surface):
        screen.blit(self.image, self.rect)

        # Barra de vida sobre el personaje
        if self.health > 0:
            bw = 40
            bh = 5
            bx = self.rect.centerx - bw // 2
            by = self.rect.top - 10
            pygame.draw.rect(screen, (200, 0, 0),   (bx, by, bw, bh))
            pygame.draw.rect(screen, (0, 200, 0),   (bx, by, int(bw * self.health / 100), bh))
            pygame.draw.rect(screen, (255, 255, 255),(bx, by, bw, bh), 1)
