"""
Clase base para todos los personajes.
Recibe char_name como parámetro – sin herencia dinámica.
"""
import pygame
from src.constants import (
    GRAVITY, FRIC, VEL, ARENA_WIDTH, DEATH_Y,
    STAND, WALK, WEAK_ATTACK, HEAVY_ATTACK, DAMAGED, DEAD,
    ATTACK_DURATION, DAMAGED_DURATION, ATTACK_RANGE,
    CHARACTER_STATS, WALK_FRAMES,
)

vec = pygame.math.Vector2

# Cuántos ticks de juego entre cambios de frame de walk (throttle)
# 6 ticks a 60 FPS = ~10 fps de animación
ANIM_SPEED = 6


class Character(pygame.sprite.Sprite):
    def __init__(self, char_name: str, x: int, y: int):
        super().__init__()

        self.name   = char_name
        weak, heavy, acce = CHARACTER_STATS[char_name]
        self.weak   = weak
        self.heavy  = heavy
        self.acce   = acce
        self.n_walk = WALK_FRAMES[char_name]

        self.health = 100.0
        self.direc  = "right"
        self.state  = STAND
        self.alive  = True

        # Frame de walk y throttle
        self.walk_c    = 0   # índice de frame actual (0..n_walk-1)
        self._anim_tick = 0  # contador de ticks desde el último cambio de frame

        # Timers de estados
        self._attack_timer  = 0
        self._damaged_timer = 0

        # Física
        self.pos = vec(float(x), float(y))
        self.vel = vec(0.0, 0.0)
        self.acc = vec(0.0, 0.0)

        # Sprite inicial
        self.image = pygame.Surface((30, 50), pygame.SRCALPHA)
        self.rect  = self.image.get_rect(midbottom=(x, y))

    # ------------------------------------------------------------------
    # Física
    # ------------------------------------------------------------------

    def _apply_physics(self, platforms):
        self.acc.x += self.vel.x * FRIC
        self.vel   += self.acc
        self.pos   += self.vel + 0.5 * self.acc

        # Clamp horizontal dentro del arena
        if self.pos.x < 15:
            self.pos.x = 15
            self.vel.x = 0
        elif self.pos.x > ARENA_WIDTH - 15:
            self.pos.x = ARENA_WIDTH - 15
            self.vel.x = 0

        self.rect.midbottom = self.pos

        # Colisión hacia abajo: elegir la plataforma con top más alto (menor y)
        # que esté realmente bajo los pies del personaje para evitar bugs en esquinas
        if self.vel.y >= 0:
            hits = pygame.sprite.spritecollide(self, platforms, False)
            if hits:
                # Filtrar solo plataformas cuyo top sea >= pos anterior (bajando hacia ellas)
                landing = [p for p in hits if self.rect.bottom >= p.rect.top
                           and self.rect.centerx >= p.rect.left
                           and self.rect.centerx <= p.rect.right]
                if landing:
                    best = min(landing, key=lambda p: p.rect.top)
                    self.pos.y  = best.rect.top + 1
                    self.vel.y  = 0
                    self.rect.midbottom = self.pos

        if self.pos.y > DEATH_Y:
            self.health = 0
            self.alive  = False

    def jump(self, platforms):
        self.rect.x += 1
        collision = pygame.sprite.spritecollide(self, platforms, False)
        self.rect.x -= 1
        if collision:
            self.vel.y = -VEL

    # ------------------------------------------------------------------
    # Ataques
    # ------------------------------------------------------------------

    def weak_attack(self, targets):
        if self.health <= 0 or self._attack_timer > 0:
            return []
        self._attack_timer = ATTACK_DURATION
        self.state = WEAK_ATTACK
        return self._hit_targets(targets, self.weak)

    def heavy_attack(self, targets):
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
            if (abs(t.rect.centerx - self.rect.centerx) < ATTACK_RANGE and
                    abs(t.rect.centery - self.rect.centery) < ATTACK_RANGE * 1.5):
                t.receive_damage(damage)
                hit.append(t)
        return hit

    def receive_damage(self, amount: float):
        if self.health <= 0:
            return
        self.health = max(0.0, self.health - amount)
        self._damaged_timer = DAMAGED_DURATION
        if self.health <= 0:
            self.alive = False
            self.state = DEAD

    # ------------------------------------------------------------------
    # Timers y animación
    # ------------------------------------------------------------------

    def _tick_timers(self):
        """Gestiona los timers de ataque y daño, con prioridad correcta."""
        if self._attack_timer > 0:
            self._attack_timer -= 1
            if self._attack_timer == 0 and self.state in (WEAK_ATTACK, HEAVY_ATTACK):
                self.state = STAND

        # DAMAGED tiene prioridad sobre ataque
        if self._damaged_timer > 0:
            self._damaged_timer -= 1
            self.state = DAMAGED
        elif self.state == DAMAGED:
            self.state = STAND

    def _advance_walk_frame(self):
        """Avanza el frame de walk solo cada ANIM_SPEED ticks (throttle)."""
        self._anim_tick += 1
        if self._anim_tick >= ANIM_SPEED:
            self._anim_tick = 0
            self.walk_c = (self.walk_c + 1) % self.n_walk

    def _set_moving(self):
        """Activa el estado de caminar y avanza el frame si no hay acción activa."""
        if self._attack_timer == 0 and self._damaged_timer == 0:
            self.state = WALK
            self._advance_walk_frame()

    def _set_standing(self):
        """Vuelve a reposo si no hay acción activa."""
        if self._attack_timer == 0 and self._damaged_timer == 0:
            self.state    = STAND
            self.walk_c   = 0
            self._anim_tick = 0

    def _update_image(self, assets):
        if self.health <= 0:
            self.image = assets.dead_sprite
        else:
            wf = self.walk_c if self.state == WALK else 0
            self.image = assets.get_sprite(self.name, self.state, self.direc, wf)
        self.rect = self.image.get_rect(midbottom=self.pos)
