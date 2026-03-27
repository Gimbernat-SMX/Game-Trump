import pygame
from src.constants import *
from src.bullet import Bullet


class Player:
    """
    Personaje del jugador con sprites originales.

    Controles (fieles al original):
      LEFT / RIGHT  → moverse
      X             → saltar (doble salto)
      Z             → disparar
      UP            → recargar
      DOWN          → activar/desactivar escudo (toggle)
    """

    def __init__(self, x: int, y: int, color_key: str, lives: int):
        self.color_key  = color_key
        self.sprite_id  = PLAYER_SPRITE_ID[color_key]
        self.lives      = lives
        self.max_lives  = lives

        # Collision rect (hitbox matches original Box2D body)
        self.rect = pygame.Rect(0, 0, PLAYER_WIDTH, PLAYER_HEIGHT)
        self.rect.centerx = x
        self.rect.bottom  = y

        # Physics
        self.vel_y      = 0.0
        self.on_ground  = False
        self.consec_jumps = 0       # double-jump counter (max MAX_JUMPS)
        self.direction  = 1         # 1=right, -1=left

        # Ammo
        self.ammo          = MAX_AMMO
        self.reloading     = False
        self.reload_frames = 0      # frames left until fully reloaded
        self.shoot_cd      = 0

        # Shield (toggle on DOWN press – same as original)
        self.shielding     = False
        self._shield_prev  = False  # for edge detection on key

        # State
        self.alive            = True
        self.invincible_timer = 0   # brief invincibility after hit

        # Animation
        self._anim_tick  = 0
        self._anim_frame = 0
        self._anim_name  = "idle"

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    def update(self, keys: pygame.key.ScancodeWrapper, platforms):
        if not self.alive:
            return

        # ---- Timers ----
        if self.shoot_cd > 0:
            self.shoot_cd -= 1
        if self.invincible_timer > 0:
            self.invincible_timer -= 1

        # ---- Reload (original: async thread that adds 1 bullet/sec) ----
        if self.reloading:
            self.reload_frames -= 1
            if self.reload_frames <= 0:
                self.ammo = MAX_AMMO
                self.reloading = False

        # ---- Shield toggle (DOWN key edge detection) ----
        down_now = keys[pygame.K_DOWN]
        if down_now and not self._shield_prev:
            self.shielding = not self.shielding
        self._shield_prev = down_now

        # ---- Movement (blocked while shielding) ----
        moving = False
        if not self.shielding:
            if keys[pygame.K_LEFT]:
                self.rect.x -= PLAYER_SPEED
                self.direction = -1
                moving = True
            if keys[pygame.K_RIGHT]:
                self.rect.x += PLAYER_SPEED
                self.direction = 1
                moving = True

        # ---- Gravity ----
        self.vel_y += GRAVITY
        self.rect.y += int(self.vel_y)

        # ---- Platform collisions ----
        self.on_ground = False
        for plat in platforms:
            if self.rect.colliderect(plat):
                if self.vel_y >= 0:
                    self.rect.bottom = plat.top
                    self.vel_y        = 0
                    self.on_ground    = True
                    self.consec_jumps = 0
                elif self.vel_y < 0:
                    self.rect.top = plat.bottom
                    self.vel_y    = 0

        # ---- Screen bounds ----
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH

        # ---- Animation ----
        self._update_anim(moving)

    def _update_anim(self, moving: bool):
        self._anim_tick += 1
        if moving and not self.shielding:
            self._anim_name = "run"
            # 6 frames, change every 10 game ticks (original: tick%60/10)
            self._anim_frame = (self._anim_tick % 60) // 10
        else:
            self._anim_name = "idle"
            # 10 frames, change every 10 game ticks (original: tick%100/10)
            self._anim_frame = (self._anim_tick % 100) // 10

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def try_jump(self, key_x_pressed: bool):
        """Call with True only on the frame X key is first pressed."""
        if not self.alive or self.shielding:
            return
        if key_x_pressed and self.consec_jumps < MAX_JUMPS:
            self.vel_y = JUMP_FORCE
            self.on_ground = False
            self.consec_jumps += 1

    def release_jump(self):
        """When X is released, reduce upward velocity (variable jump height)."""
        if self.vel_y < 0:
            self.vel_y /= 1.5   # original: vel.y /= 1.5f on key release

    def try_shoot(self) -> "Bullet | None":
        """Returns a Bullet if firing is possible, else None."""
        if not self.alive or self.shielding:
            return None
        if self.reloading or self.ammo <= 0 or self.shoot_cd > 0:
            return None
        self.ammo    -= 1
        self.shoot_cd = BULLET_COOLDOWN
        bx = self.rect.right if self.direction == 1 else self.rect.left
        by = self.rect.centery
        return Bullet(bx, by, self.direction, "player")

    def try_reload(self):
        """Start reload if not already reloading and ammo is missing."""
        if self.reloading or self.ammo >= MAX_AMMO or self.shielding:
            return
        self.reloading     = True
        self.reload_frames = RELOAD_TIME_TOTAL

    def take_damage(self):
        if self.shielding or self.invincible_timer > 0:
            return
        self.lives        -= 1
        self.invincible_timer = 60   # 1 s
        if self.lives <= 0:
            self.alive = False

    # ------------------------------------------------------------------
    # Draw
    # ------------------------------------------------------------------

    def draw(self, screen: pygame.Surface, assets):
        if not self.alive:
            return
        # Blink when invincible
        if self.invincible_timer > 0 and (self.invincible_timer // 4) % 2 == 0:
            return

        flip = (self.direction == -1)
        sprite = assets.get_sprite(self.sprite_id, self._anim_name, self._anim_frame, flip)

        # Center sprite over hitbox (sprite is larger than hitbox)
        sx = self.rect.centerx - SPRITE_W // 2
        sy = self.rect.bottom   - SPRITE_H
        screen.blit(sprite, (sx, sy))

        # Shield icon – draw to side of player when shielding
        if self.shielding:
            si = assets.shield_icon
            ix = self.rect.centerx + SHIELD_OFF_X * self.direction - si.get_width() // 2
            iy = self.rect.top - si.get_height() // 2
            screen.blit(si, (ix, iy))
