import pygame
from src.constants import BULLET_SPEED, SCREEN_WIDTH


class Bullet:
    """Projectile that travels horizontally. Uses shotBullet.png sprite."""

    def __init__(self, x, y, direction: int, owner: str):
        """
        direction: 1 = right, -1 = left
        owner: 'player' | 'enemy'
        """
        self.direction = direction
        self.owner = owner
        self.alive = True
        w, h = 32, 12
        self.rect = pygame.Rect(x - w // 2, y - h // 2, w, h)

    def update(self):
        self.rect.x += BULLET_SPEED * self.direction
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.alive = False

    def draw(self, screen, assets):
        sprite = assets.shot_bullet_r if self.direction == 1 else assets.shot_bullet_l
        screen.blit(sprite, self.rect.topleft)
