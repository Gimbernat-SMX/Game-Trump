"""Plataformas del arena SSB (posiciones del original)."""
import pygame
from src.constants import PLATFORMS
from src.assets import Assets


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, is_floor=False):
        super().__init__()
        assets = Assets.get()
        raw = assets.floor if is_floor else assets.platform
        self.image = pygame.transform.scale(raw, (w, h))
        self.rect  = self.image.get_rect(topleft=(x, y))

    def draw(self, screen):
        screen.blit(self.image, self.rect)


def create_platform_group() -> pygame.sprite.Group:
    group = pygame.sprite.Group()
    for i, (x, y, w, h) in enumerate(PLATFORMS):
        group.add(Platform(x, y, w, h, is_floor=(i == 0)))
    return group
