# Super Smash Bros – Single Player
# Dimensiones y constantes del juego original (src/game/settings.py)

# ---- Pantalla ----
SCREEN_WIDTH  = 900   # arena 700 + panel lateral 200
SCREEN_HEIGHT = 700
ARENA_WIDTH   = 700   # zona de juego (igual que el original)
FPS = 60
TITLE = "Super Smash Bros"

# ---- Colores ----
BLACK      = (0,   0,   0)
WHITE      = (255, 255, 255)
RED        = (153, 38,  0)
GREEN      = (40,  77,  0)
ORANGE     = (255, 117, 26)
GRAY       = (191, 191, 191)
DARK_GRAY  = (50,  50,  50)
LIGHT_GRAY = (200, 200, 200)
YELLOW     = (255, 215, 0)
BLUE       = (30,  80,  220)

# ---- Física (del original) ----
GRAVITY = 0.5
FRIC    = -0.12    # fricción horizontal
VEL     = 15       # velocidad de salto (vel.y = -VEL)

# ---- Muertos si caen fuera ----
DEATH_Y = 750

# ---- Plataformas (posiciones originales del SSB) ----
# (x, y, width, height)
PLATFORMS = [
    (0,   670, 700, 30),   # suelo
    (60,  460, 200, 50),   # plataforma inferior izquierda
    (435, 460, 200, 50),   # plataforma inferior derecha
    (250, 260, 200, 50),   # plataforma central superior
]

# ---- Personajes ----
CHARACTERS = ["mario", "luigi", "yoshi", "popo", "nana", "link"]

CHARACTER_LABELS = {
    "mario": "Mario",
    "luigi": "Luigi",
    "yoshi": "Yoshi",
    "popo":  "Popo",
    "nana":  "Nana",
    "link":  "Link",
}

# Stats: (weak_dmg, heavy_dmg, acceleration)
CHARACTER_STATS = {
    "mario": (3,    6,    0.5),
    "luigi": (4,    8,    0.4),
    "yoshi": (5,    10,   0.3),
    "popo":  (5.5,  11,   0.25),
    "nana":  (5.75, 11.5, 0.225),
    "link":  (6,    12,   0.2),
}

# Walk frame counts (de los archivos m1..mN del SSB)
WALK_FRAMES = {
    "mario": 7,
    "luigi": 8,
    "yoshi": 8,
    "popo":  3,
    "nana":  3,
    "link":  10,
}

# ---- Estados de animación ----
STAND        = "stand"
WALK         = "walk"
WEAK_ATTACK  = "weak"
HEAVY_ATTACK = "heavy"
DAMAGED      = "damaged"
DEAD         = "dead"

# ---- Combate ----
ATTACK_DURATION   = 35   # frames que dura la animación de ataque (~0.58s a 60fps)
DAMAGED_DURATION  = 22   # frames de animación de golpe
ATTACK_RANGE      = 55   # pixeles de alcance del golpe

# ---- Victoria ----
ENEMIES_TO_DEFEAT = 10   # cuántos enemigos eliminar

# ---- HUD ----
HUD_MARGIN = 12
HEALTHBAR_W = 180
HEALTHBAR_H = 18

# ---- Panel lateral ----
PANEL_X     = ARENA_WIDTH     # x donde empieza el panel
PANEL_W     = SCREEN_WIDTH - ARENA_WIDTH

# ---- Spawn ----
PLAYER_SPAWN = (350, 300)   # (x, y) spawn del jugador
ENEMY_SPAWNS = [            # posibles spawns de enemigos
    (100, 400),
    (580, 400),
    (300, 200),
    (450, 200),
    (650, 600),
    ( 50, 600),
]

# ---- IA ----
MAX_ENEMIES_ON_SCREEN = 3
ENEMY_SPAWN_INTERVAL  = 360   # frames entre spawns
