"""Carga centralizada de todos los assets del juego SSB."""
import os
import pygame
from src.constants import ARENA_WIDTH, SCREEN_HEIGHT, CHARACTERS, WALK_FRAMES

_BASE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "images")


def _p(*parts):
    return os.path.join(_BASE, *parts)


class Assets:
    _instance = None

    @classmethod
    def get(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        # ---- Fondos ----
        arena_raw = pygame.image.load(_p("backgrounds", "arena.png")).convert()
        self.arena = pygame.transform.scale(arena_raw, (ARENA_WIDTH, SCREEN_HEIGHT))

        intro_raw = pygame.image.load(_p("backgrounds", "intro.png")).convert()
        from src.constants import SCREEN_WIDTH
        self.intro_bg = pygame.transform.scale(intro_raw, (SCREEN_WIDTH, SCREEN_HEIGHT))

        char_raw = pygame.image.load(_p("backgrounds", "startCharacter.png")).convert()
        self.char_bg = pygame.transform.scale(char_raw, (SCREEN_WIDTH, SCREEN_HEIGHT))

        # ---- Plataformas ----
        self.floor    = pygame.image.load(_p("others", "floor.png")).convert_alpha()
        self.platform = pygame.image.load(_p("others", "platform.png")).convert_alpha()

        # ---- Sprite "dead" compartido ----
        self.dead_sprite = pygame.image.load(_p("characters", "dead.png")).convert_alpha()

        # ---- Sprites de personajes ----
        # Estructura: sprites[char_name] = {
        #   "stand_r", "stand_l",
        #   "walk_r": [...], "walk_l": [...],
        #   "weak_r", "weak_l",
        #   "heavy_r", "heavy_l",
        #   "damaged_r", "damaged_l"
        # }
        self.sprites: dict = {}
        for char in CHARACTERS:
            self.sprites[char] = self._load_char(char)

        # ---- Botones de selección de personaje ----
        self.char_buttons: dict = {}
        for char in CHARACTERS:
            a = pygame.image.load(_p("buttons", f"{char}a.png")).convert_alpha()
            b = pygame.image.load(_p("buttons", f"{char}b.png")).convert_alpha()
            self.char_buttons[char] = (a, b)

    def _load_char(self, name: str) -> dict:
        def img(filename):
            return pygame.image.load(_p("characters", name, filename)).convert_alpha()

        stand_r   = img("s1.png")
        weak_r    = img("w1.png")
        heavy_r   = img("h1.png")
        damaged_r = img("d1.png")

        n_walk = WALK_FRAMES[name]
        walk_r = [img(f"m{i}.png") for i in range(1, n_walk + 1)]

        def flip_all(surfaces):
            return [pygame.transform.flip(s, True, False) for s in surfaces]

        return {
            "stand_r":   stand_r,
            "stand_l":   pygame.transform.flip(stand_r, True, False),
            "walk_r":    walk_r,
            "walk_l":    flip_all(walk_r),
            "weak_r":    weak_r,
            "weak_l":    pygame.transform.flip(weak_r, True, False),
            "heavy_r":   heavy_r,
            "heavy_l":   pygame.transform.flip(heavy_r, True, False),
            "damaged_r": damaged_r,
            "damaged_l": pygame.transform.flip(damaged_r, True, False),
        }

    def get_sprite(self, char: str, state: str, direc: str, walk_frame: int = 0) -> pygame.Surface:
        from src.constants import DEAD
        if state == DEAD:
            return self.dead_sprite
        s = self.sprites[char]
        side = "r" if direc == "right" else "l"
        from src.constants import WALK
        if state == WALK:
            frames = s[f"walk_{side}"]
            return frames[walk_frame % len(frames)]
        key = f"{state}_{side}"
        return s.get(key, s["stand_r"])
