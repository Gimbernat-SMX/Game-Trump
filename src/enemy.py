import pygame
import random
from src.constants import *
from src.bullet import Bullet


class Enemy:
    """
    Enemigo IA.  Usa los mismos sprites del jugador (otros colores).
    Comportamiento: patrol → chase → shoot.
    """

    _next_id = 0  # cycling sprite selection

    def __init__(self, x: int, y: int):
        Enemy._next_id = (Enemy._next_id + 1) % len(ENEMY_SPRITE_IDS)
        self.sprite_id = ENEMY_SPRITE_IDS[Enemy._next_id]

        self.rect = pygame.Rect(0, 0, PLAYER_WIDTH, PLAYER_HEIGHT)
        self.rect.centerx = x
        self.rect.bottom  = y

        # Physics
        self.vel_y      = 0.0
        self.on_ground  = False
        self.direction  = random.choice([-1, 1])
        self.consec_jumps = 0

        # Lives
        self.lives = 2
        self.alive = True
        self.invincible_timer = 0

        # AI state
        self.patrol_timer   = random.randint(60, 180)
        self.shoot_cooldown = random.randint(ENEMY_SHOOT_COOLDOWN_MIN, ENEMY_SHOOT_COOLDOWN_MAX)
        self.jump_timer     = random.randint(90, 240)

        # Animation
        self._anim_tick  = random.randint(0, 100)
        self._anim_frame = 0
        self._anim_name  = "idle"

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    def update(self, platforms, player_rect: pygame.Rect):
        if not self.alive:
            return

        if self.invincible_timer > 0:
            self.invincible_timer -= 1

        # ---- AI decision ----
        dx = player_rect.centerx - self.rect.centerx
        dy = abs(player_rect.centery - self.rect.centery)
        dist = abs(dx)

        moving = False
        if dist < 420:
            # Chase player
            self.direction = 1 if dx > 0 else -1
            self.rect.x   += ENEMY_SPEED * self.direction
            moving = True
        else:
            # Patrol
            self.patrol_timer -= 1
            if self.patrol_timer <= 0:
                self.direction    *= -1
                self.patrol_timer  = random.randint(60, 180)
            self.rect.x += ENEMY_SPEED * self.direction
            moving = True

        # ---- Random jump ----
        self.jump_timer -= 1
        if self.jump_timer <= 0:
            if self.on_ground and self.consec_jumps < MAX_JUMPS:
                self.vel_y       = JUMP_FORCE * 0.9
                self.on_ground   = False
                self.consec_jumps+= 1
            self.jump_timer = random.randint(90, 240)

        # ---- Gravity ----
        self.vel_y    += GRAVITY
        self.rect.y   += int(self.vel_y)

        # ---- Platform collisions ----
        self.on_ground = False
        for plat in platforms:
            if self.rect.colliderect(plat):
                if self.vel_y >= 0:
                    self.rect.bottom  = plat.top
                    self.vel_y        = 0
                    self.on_ground    = True
                    self.consec_jumps = 0
                elif self.vel_y < 0:
                    self.rect.top = plat.bottom
                    self.vel_y    = 0

        # ---- Screen bounds ----
        if self.rect.left < 0:
            self.rect.left = 0
            self.direction = 1
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
            self.direction  = -1

        # ---- Animation ----
        self._anim_tick += 1
        if moving:
            self._anim_name  = "run"
            self._anim_frame = (self._anim_tick % 60) // 10
        else:
            self._anim_name  = "idle"
            self._anim_frame = (self._anim_tick % 100) // 10

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def try_shoot(self, player_rect: pygame.Rect) -> "Bullet | None":
        self.shoot_cooldown -= 1
        if self.shoot_cooldown > 0:
            return None

        dx   = player_rect.centerx - self.rect.centerx
        dy   = abs(player_rect.centery - self.rect.centery)
        dist = abs(dx)

        if dist < 500 and dy < 160:
            self.shoot_cooldown = random.randint(ENEMY_SHOOT_COOLDOWN_MIN,
                                                 ENEMY_SHOOT_COOLDOWN_MAX)
            direction = 1 if dx > 0 else -1
            bx = self.rect.right if direction == 1 else self.rect.left
            by = self.rect.centery
            return Bullet(bx, by, direction, "enemy")
        return None

    def take_damage(self):
        if self.invincible_timer > 0:
            return
        self.lives        -= 1
        self.invincible_timer = 30
        if self.lives <= 0:
            self.alive = False

    # ------------------------------------------------------------------
    # Draw
    # ------------------------------------------------------------------

    def draw(self, screen: pygame.Surface, assets):
        if not self.alive:
            return
        if self.invincible_timer > 0 and (self.invincible_timer // 3) % 2 == 0:
            return

        flip   = (self.direction == -1)
        sprite = assets.get_sprite(self.sprite_id, self._anim_name, self._anim_frame, flip)

        sx = self.rect.centerx - SPRITE_W // 2
        sy = self.rect.bottom   - SPRITE_H
        screen.blit(sprite, (sx, sy))

        # Health bar above sprite
        bar_w = 40
        bar_h = 5
        bx    = self.rect.centerx - bar_w // 2
        by    = sy - 10
        pygame.draw.rect(screen, RED,   (bx, by, bar_w, bar_h))
        pygame.draw.rect(screen, GREEN, (bx, by, bar_w * self.lives // 2, bar_h))
        pygame.draw.rect(screen, WHITE, (bx, by, bar_w, bar_h), 1)
