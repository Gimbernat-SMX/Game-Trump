import pygame
from src.constants import PLATFORMS, DARK_GREEN, GREEN, BROWN


def get_platform_rects():
    """Return list of pygame.Rect for all platforms (ground + floating)."""
    return [pygame.Rect(*p) for p in PLATFORMS]


def draw_platforms(screen: pygame.Surface, platform_rects):
    """Render platforms (ground is solid, others are wood planks)."""
    for i, r in enumerate(platform_rects):
        if i == 0:
            # Ground – already covered by whitehouse background mostly,
            # draw a subtle solid strip
            pygame.draw.rect(screen, DARK_GREEN, r)
            pygame.draw.rect(screen, GREEN, (r.x, r.y, r.width, 5))
        else:
            # Floating platform (sign / plank style)
            pygame.draw.rect(screen, BROWN, r)
            pygame.draw.rect(screen, (160, 110, 55), (r.x, r.y, r.width, 4))
            pygame.draw.rect(screen, (100, 60, 20), r, 1)
