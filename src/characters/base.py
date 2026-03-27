"""
Clase base para todos los personajes.
Física y animación fiel al original SSB (settings.py + Mario.py).
"""
import pygame
from src.constants import (
    GRAVITY, FRIC, VEL, ARENA_WIDTH, SCREEN_HEIGHT, DEATH_Y,
    STAND, WALK, WEAK_ATTACK, HEAVY_ATTACK, DAMAGED, DEAD,
    ATTACK_DURATION, DAMAGED_DURATION, ATTACK_RANGE, CHARACTER_STATS, WALK_FRAMES,
)

vec = pygame.math.Vector2


class Character(pygame.sprite.Sprite):
    """
    Personaje jugable/IA con física de vectores (igual que el original SSB).

    Subclases solo necesitan definir `name` como atributo de clase.
    Los stats se leen de CHARACTER_STATS.
    """

    name: str = ""   # sobrescribir en subclase

    def __init__(self, x: int, y: int, is_player: bool = True):
        super().__init__()

        self.is_player = is_player

        weak, heavy, acce = CHARACTER_STATS[self.name]
        self.weak  = weak
        self.heavy = heavy
        self.acce  = acce
        self.n_walk = WALK_FRAMES[self.name]

        self.health = 100.0
        self.direc  = "right"
        self.state  = STAND       # estado de animación actual
        self.walk_c = 0           # contador de frame de walk
        self.alive  = True

        # Timers de estados
        self._attack_timer  = 0
        self._damaged_timer = 0

        # Física
        self.pos = vec(x, y)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)

        # Sprite inicial (placeholder; se actualiza en update)
        self.image = pygame.Surface((30, 50), pygame.SRCALPHA)
        self.rect  = self.image.get_rect(midbottom=(x, y))

    # ------------------------------------------------------------------
    # Física – igual que el original SSB
    # ------------------------------------------------------------------

    def _apply_physics(self, platforms):
        """Aplica gravedad, fricción, colisiones con plataformas."""
        self.acc.x += self.vel.x * FRIC
        self.vel   += self.acc
        self.pos   += self.vel + 0.5 * self.acc
        self.rect.midbottom = self.pos

        # Colisión hacia abajo
        if self.vel.y > 0:
            collision = pygame.sprite.spritecollide(self, platforms, False)
            if collision:
                self.pos.y      = collision[0].rect.top + 1
                self.vel.y      = 0
                self.rect.midbottom = self.pos

        # Muerte por caída
        if self.pos.y > DEATH_Y:
            self.health = 0
            self.alive  = False

    # ------------------------------------------------------------------
    # Salto
    # ------------------------------------------------------------------

    def jump(self, platforms):
        """Salta si está sobre una plataforma (igual que el original)."""
        self.rect.x += 1
        collision = pygame.sprite.spritecollide(self, platforms, False)
        self.rect.x -= 1
        if collision:
            self.vel.y = -VEL

    # ------------------------------------------------------------------
    # Ataques
    # ------------------------------------------------------------------

    def weak_attack(self, targets):
        """Ataque débil: daña targets adyacentes. Devuelve lista de tocados."""
        if self.health <= 0 or self._attack_timer > 0:
            return []
        self._attack_timer = ATTACK_DURATION
        self.state = WEAK_ATTACK
        return self._hit_targets(targets, self.weak)

    def heavy_attack(self, targets):
        """Ataque fuerte: más daño."""
        if self.health <= 0 or self._attack_timer > 0:
            return []
        self._attack_timer = ATTACK_DURATION
        self.state = HEAVY_ATTACK
        return self._hit_targets(targets, self.heavy)

    def _hit_targets(self, targets, damage: float):
        hit = []
        for t in targets:
            if t is self:
                continue
            if abs(t.rect.centerx - self.rect.centerx) < ATTACK_RANGE and \
               abs(t.rect.centery - self.rect.centery) < ATTACK_RANGE * 1.5:
                t.receive_damage(damage)
                hit.append(t)
        return hit

    def receive_damage(self, amount: float):
        if self.health <= 0:
            return
        self.health = max(0.0, self.health - amount)
        self._damaged_timer = DAMAGED_DURATION
        if self.health <= 0:
            self.alive  = False
            self.state  = DEAD

    # ------------------------------------------------------------------
    # Actualización de estado / animación
    # ------------------------------------------------------------------

    def _tick_timers(self):
        if self._attack_timer > 0:
            self._attack_timer -= 1
            if self._attack_timer == 0 and self.state in (WEAK_ATTACK, HEAVY_ATTACK):
                self.state = STAND

        if self._damaged_timer > 0:
            self._damaged_timer -= 1
            if self._damaged_timer > 0:
                self.state = DAMAGED
            elif self.state == DAMAGED:
                self.state = STAND

    def _update_image(self, assets):
        char = self.name
        if self.health <= 0:
            self.image = assets.dead_sprite
        else:
            wf = self.walk_c % self.n_walk if self.state == WALK else 0
            self.image = assets.get_sprite(char, self.state, self.direc, wf)
        self.rect = self.image.get_rect(midbottom=self.pos)
