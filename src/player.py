"""
Jugador: envuelve un Character con controles de teclado.
Controles (fieles al SSB original):
  LEFT / RIGHT → moverse
  UP           → saltar
  Z            → ataque débil
  X            → ataque fuerte
"""
import pygame
from src.constants import (
    GRAVITY, ARENA_WIDTH, STAND, WALK, WEAK_ATTACK, HEAVY_ATTACK,
)
from src.characters.base import Character

vec = pygame.math.Vector2


def make_player(char_name: str, x: int, y: int) -> "Player":
    """Factory: crea un Player con el personaje elegido."""
    from src.characters.mario  import Mario
    from src.characters.luigi  import Luigi
    from src.characters.yoshi  import Yoshi
    from src.characters.popo   import Popo
    from src.characters.nana   import Nana
    from src.characters.link   import Link
    classes = {"mario": Mario, "luigi": Luigi, "yoshi": Yoshi,
               "popo": Popo, "nana": Nana, "link": Link}
    cls = classes[char_name]
    return Player(cls, x, y)


class Player(Character):
    """Character con input de teclado."""

    def __init__(self, char_class, x: int, y: int):
        # Heredamos el name de la clase del personaje elegido
        self.__class__ = type(
            char_class.__name__,
            (Player, char_class),
            {"name": char_class.name},
        )
        super().__init__(x, y, is_player=True)
        self.name = char_class.name   # asegurar atributo de instancia

    def update(self, platforms, enemies, assets):
        """Llamar cada frame con el estado de las teclas."""
        keys = pygame.key.get_pressed()

        self._tick_timers()

        if self.health > 0:
            # ---- Movimiento horizontal ----
            self.acc = vec(0, GRAVITY)

            if keys[pygame.K_LEFT] and self.pos.x > 40:
                self.acc.x = -self.acce
                self.direc = "left"
                if self._attack_timer == 0 and self._damaged_timer == 0:
                    self.state  = WALK
                    self.walk_c = (self.walk_c + 1) % self.n_walk

            elif keys[pygame.K_RIGHT] and self.pos.x < ARENA_WIDTH - 40:
                self.acc.x = self.acce
                self.direc = "right"
                if self._attack_timer == 0 and self._damaged_timer == 0:
                    self.state  = WALK
                    self.walk_c = (self.walk_c + 1) % self.n_walk

            else:
                self.walk_c = 0
                if self._attack_timer == 0 and self._damaged_timer == 0:
                    self.state = STAND

            # ---- Salto ----
            if keys[pygame.K_UP]:
                self.jump(platforms)

            # ---- Ataques ----
            if keys[pygame.K_z]:
                self.weak_attack(enemies)
            elif keys[pygame.K_x]:
                self.heavy_attack(enemies)

        else:
            self.acc = vec(0, GRAVITY)

        self._apply_physics(platforms)
        self._update_image(assets)

    def draw(self, screen: pygame.Surface):
        screen.blit(self.image, self.rect)
