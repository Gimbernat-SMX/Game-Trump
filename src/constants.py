# PumpTrump - Game Constants
# Fiel al original C++/Qt con Box2D

# Screen
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 600
FPS = 60
TITLE = "PumpTrump"

# Colors
WHITE    = (255, 255, 255)
BLACK    = (0,   0,   0)
RED      = (220, 30,  30)
BLUE     = (30,  80,  220)
MAGENTA  = (200, 30,  200)
GRAY     = (130, 130, 130)
DARK_GRAY= (50,  50,  50)
LIGHT_GRAY=(200, 200, 200)
GREEN    = (30,  200, 30)
YELLOW   = (255, 220, 0)
ORANGE   = (255, 140, 0)
BROWN    = (139, 90,  43)
DARK_GREEN=(30,  100, 30)

# Player color options (menu display colors)
PLAYER_COLORS = {
    "black":   (40,  40,  40),
    "blue":    BLUE,
    "red":     RED,
    "magenta": MAGENTA,
}

# Sprite player IDs (matches original naming: idle/10..49, run/10..45)
PLAYER_SPRITE_ID = {
    "black":   1,
    "blue":    2,
    "red":     3,
    "magenta": 4,
}

# Enemy sprite IDs cycling through player sprite sets
ENEMY_SPRITE_IDS = [2, 3, 4, 1]

# ---- Physics (converted from original Box2D values at 1024×600) ----
# Original: scale 10x from Box2D units to pixels
# Player hitbox half-extents: W/350 × H/135  =>  ×10 ×2 = full size
PLAYER_WIDTH  = 58   # pixels  (1024/350 * 10 * 2 ≈ 58)
PLAYER_HEIGHT = 89   # pixels  (600/135  * 10 * 2 ≈ 89)

# Sprite draw size (original: W/96 × H/54 in pixels)
SPRITE_W = 107   # 1024/96 * 10
SPRITE_H = 111   # 600/54  * 10

# Shield draw size and offset (original: W/767 × H/350, offset +W/250 right)
SHIELD_W      = 32   # scaled up a bit for visibility
SHIELD_H      = 40
SHIELD_OFF_X  = 14   # pixels right from player center

# Physics
GRAVITY       = 0.5          # pixels/frame² (approx Box2D 140 @ 60fps)
PLAYER_SPEED  = 17           # pixels/frame  (original: W/44 = 23 → we soften)
JUMP_FORCE    = -13          # pixels/frame  (original: H/12.8 = 46.9 → soften)
BULLET_SPEED  = 17           # pixels/frame  (original: W/17 = 60 → scale to px/frame)

# Ammo
MAX_AMMO          = 3        # original: 3
RELOAD_TIME_TOTAL = 180      # frames for full reload (3 bullets × 60 frames)
BULLET_COOLDOWN   = 20       # frames between shots

# Double jump
MAX_JUMPS = 2

# ---- Platforms (from original Box2D positions × 10, screen 1024×600) ----
# All platform rects: (x, y, width, height) in pixels
# Box2D center position × 10 = pixel center
PLATFORM_THICKNESS = 14   # visual thickness
GROUND_Y = 560            # top of ground

# Computed platform tops (center_y - PLATFORM_THICKNESS//2):
# Signs at cy=474px, Platforms at 355px and 194px
PLATFORMS = [
    # ground
    (0, GROUND_Y, SCREEN_WIDTH, SCREEN_HEIGHT - GROUND_Y),
    # "Make America" sign (cx=160, cy=474, hw=81)
    (79,  474 - PLATFORM_THICKNESS // 2, 162, PLATFORM_THICKNESS),
    # "White House" sign  (cx=399, cy=474, hw=228)
    (171, 474 - PLATFORM_THICKNESS // 2, 456, PLATFORM_THICKNESS),
    # "Great Again" sign  (cx=786, cy=474, hw=81)
    (705, 474 - PLATFORM_THICKNESS // 2, 162, PLATFORM_THICKNESS),
    # Platform bot-left   (cx=275, cy=355, hw=197)
    (78,  355 - PLATFORM_THICKNESS // 2, 394, PLATFORM_THICKNESS),
    # Platform top-right  (cx=551, cy=194, hw=197)
    (354, 194 - PLATFORM_THICKNESS // 2, 394, PLATFORM_THICKNESS),
]

# ---- Player spawn positions (original: W/132, W/10.8, W/32, W/14.6  × 10) ----
# These are Box2D center x → pixel x (center of player)
PLAYER_SPAWN_XS = [77, 948, 320, 701]

# Enemy
ENEMY_SHOOT_COOLDOWN_MIN = 90
ENEMY_SHOOT_COOLDOWN_MAX = 180
ENEMY_SPEED = 2
MAX_ENEMIES_ON_SCREEN = 4   # máximo de enemigos simultáneos

# Victory condition
ENEMIES_TO_DEFEAT = 15

# HUD
HEART_DISPLAY_H = 30   # height to scale heart.png
AMMO_ICON_H     = 22
HUD_MARGIN      = 10
