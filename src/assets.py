"""
Centralized asset loader – loads and caches all sprites once.
All paths are relative to the project root (where main.py lives).
"""
import os
import pygame
from src.constants import SPRITE_W, SPRITE_H, HEART_DISPLAY_H, SHIELD_W, SHIELD_H, AMMO_ICON_H

_BASE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "sprites")


def _path(*parts):
    return os.path.join(_BASE, *parts)


class Assets:
    _instance = None

    @classmethod
    def get(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        # --- Background ---
        bg_raw = pygame.image.load(_path("stuff", "whitehouse.png")).convert()
        from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT
        self.background = pygame.transform.scale(bg_raw, (SCREEN_WIDTH, SCREEN_HEIGHT))

        # --- HUD icons ---
        heart_raw  = pygame.image.load(_path("stuff", "heart.png")).convert_alpha()
        shield_raw = pygame.image.load(_path("stuff", "shield.png")).convert_alpha()
        bullet_raw = pygame.image.load(_path("stuff", "bullet.png")).convert_alpha()

        # Scale keeping aspect ratio
        hw = int(heart_raw.get_width() * HEART_DISPLAY_H / heart_raw.get_height())
        self.heart = pygame.transform.scale(heart_raw, (hw, HEART_DISPLAY_H))

        sw_scaled = int(shield_raw.get_width() * SHIELD_H / shield_raw.get_height())
        self.shield_icon = pygame.transform.scale(shield_raw, (sw_scaled, SHIELD_H))

        bw = int(bullet_raw.get_width() * AMMO_ICON_H / bullet_raw.get_height())
        self.bullet_icon = pygame.transform.scale(bullet_raw, (bw, AMMO_ICON_H))

        # --- Shot bullet sprite ---
        shot_raw = pygame.image.load(_path("stuff", "shotBullet.png")).convert_alpha()
        self.shot_bullet_r = pygame.transform.scale(shot_raw, (32, 12))   # right
        self.shot_bullet_l = pygame.transform.flip(self.shot_bullet_r, True, False)  # left

        # --- Player / Enemy sprites: idle (10 frames) and run (6 frames) ---
        # Key: (player_id, "idle"|"run", frame_index)
        self._sprites: dict = {}
        for pid in range(1, 5):
            for frame in range(10):
                self._load_sprite(pid, "idle", frame)
            for frame in range(6):
                self._load_sprite(pid, "run", frame)

    def _load_sprite(self, player_id: int, anim: str, frame: int):
        filename = f"{player_id * 10 + frame}.png"
        raw = pygame.image.load(_path(anim, filename)).convert_alpha()
        surf = pygame.transform.scale(raw, (SPRITE_W, SPRITE_H))
        self._sprites[(player_id, anim, frame)] = surf

    def get_sprite(self, player_id: int, anim: str, frame: int, flip: bool) -> pygame.Surface:
        surf = self._sprites.get((player_id, anim, frame))
        if surf is None:
            return pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)
        if flip:
            return pygame.transform.flip(surf, True, False)
        return surf
