"""Modo multijugador: host (simulación completa) y cliente (render remoto)."""
import pygame
from src.constants import (
    FPS, SCREEN_WIDTH, SCREEN_HEIGHT, ARENA_WIDTH,
    BLACK, WHITE, GRAY, YELLOW, GRAVITY,
    MP_SPAWNS, PLAYER_COLORS, CHARACTER_LABELS,
)
from src.characters.base import Character
from src.platform_map import create_platform_group
from src.assets import Assets

vec = pygame.math.Vector2

# Colores de nombre sobre personaje
_NAME_COLORS = PLAYER_COLORS


# ──────────────────────────────────────────────────────────────────────────────
# HOST – ejecuta la simulación completa
# ──────────────────────────────────────────────────────────────────────────────

class GameMPHost:
    def __init__(self, screen: pygame.Surface, server):
        self.screen    = screen
        self.server    = server
        self.assets    = Assets.get()
        self.clock     = pygame.time.Clock()
        self.platforms = create_platform_group()

        self._font_name  = pygame.font.SysFont("Arial", 14, bold=True)
        self._font_hud   = pygame.font.SysFont("Arial", 18, bold=True)
        self._font_small = pygame.font.SysFont("Arial", 14)

        # Crear personajes para cada jugador en el lobby
        self.chars: dict[int, Character] = {}
        self.names: dict[int, str]       = {}
        for slot, (name, char) in server.get_players().items():
            spawn = MP_SPAWNS[slot] if slot < len(MP_SPAWNS) else MP_SPAWNS[0]
            self.chars[slot] = Character(char, spawn[0], spawn[1])
            self.names[slot] = name

        self._local_slot  = 0
        self._jump_queued = False
        self._result      = None   # ("end", winner_name, winner_slot) cuando termine

    # ------------------------------------------------------------------

    def run(self):
        while True:
            result = self._frame()
            if result:
                return result

    # ------------------------------------------------------------------

    def _frame(self):
        # ---- Eventos ----
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); raise SystemExit
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    self._jump_queued = True
                elif event.key == pygame.K_F10:
                    pygame.display.toggle_fullscreen()

        # ---- Inputs ----
        keys   = pygame.key.get_pressed()
        inputs = self.server.get_inputs()

        # Slot 0 = host local
        inputs[self._local_slot] = {
            "left":  bool(keys[pygame.K_a]),
            "right": bool(keys[pygame.K_d]),
            "jump":  self._jump_queued,
            "weak":  bool(keys[pygame.K_e]),
            "heavy": bool(keys[pygame.K_q]),
            "block": bool(keys[pygame.K_r]),
        }
        self._jump_queued = False

        # Sincronizar jugadores que se desconectaron
        active = self.server.active_slots()
        for slot in list(self.chars.keys()):
            if slot not in active:
                self.chars[slot].alive  = False
                self.chars[slot].health = 0

        # ---- Actualizar personajes ----
        all_chars = list(self.chars.values())
        for slot, char in self.chars.items():
            inp = inputs.get(slot, {})
            self._update_char(char, inp, all_chars)

        # ---- Broadcast de estado ----
        state = self._build_state()
        self.server.broadcast_state(state)

        # ---- Condición de victoria ----
        alive_slots = [s for s, c in self.chars.items() if c.alive]
        if len(alive_slots) <= 1:
            if alive_slots:
                ws = alive_slots[0]
                winner_name = self.names.get(ws, f"Slot {ws}")
            else:
                ws = -1
                winner_name = "Empate"
            self.server.broadcast_end(winner_name, ws)
            return ("end", winner_name)

        # ---- Dibujar ----
        self._draw(state)
        self.clock.tick(FPS)
        return None

    # ------------------------------------------------------------------

    def _update_char(self, char: Character, inp: dict, all_chars: list):
        char._tick_timers()

        if char.health > 0:
            char.acc = vec(0.0, GRAVITY)

            moving = False
            if inp.get("left"):
                char.acc.x = -char.acce
                char.direc = "left"
                moving = True
            elif inp.get("right"):
                char.acc.x = char.acce
                char.direc = "right"
                moving = True

            if moving:
                char._set_moving()
            else:
                char._set_standing()

            if inp.get("jump"):
                char.jump(self.platforms)

            char.blocking = bool(inp.get("block", False))

            others = [c for c in all_chars if c is not char]
            if inp.get("weak") and not char.blocking:
                char.weak_attack(others)
            elif inp.get("heavy") and not char.blocking:
                char.heavy_attack(others)
        else:
            char.acc = vec(0.0, GRAVITY)

        char._apply_physics(self.platforms)
        char._update_image(self.assets)

    # ------------------------------------------------------------------

    def _build_state(self) -> list:
        state = []
        for slot, char in self.chars.items():
            state.append({
                "slot":   slot,
                "name":   self.names.get(slot, ""),
                "char":   char.name,
                "x":      float(char.pos.x),
                "y":      float(char.pos.y),
                "health": float(char.health),
                "direc":  char.direc,
                "state":  char.state,
                "walk_c": char.walk_c,
                "alive":  char.alive,
            })
        return state

    # ------------------------------------------------------------------

    def _draw(self, state: list):
        ws = pygame.Surface((ARENA_WIDTH, SCREEN_HEIGHT)).convert()
        ws.blit(self.assets.arena, (0, 0))
        self.platforms.draw(ws)

        # Dibujar personajes
        for p in state:
            sprite = self.assets.get_sprite(p["char"], p["state"], p["direc"], p["walk_c"])
            rect   = sprite.get_rect(midbottom=(int(p["x"]), int(p["y"])))
            ws.blit(sprite, rect)
            _draw_name_bar(ws, self._font_name, p, rect)

        self.screen.blit(ws, (0, 0))
        self._draw_hud(state)
        pygame.display.flip()

    def _draw_hud(self, state: list):
        # Panel derecho
        panel = pygame.Rect(ARENA_WIDTH, 0, SCREEN_WIDTH - ARENA_WIDTH, SCREEN_HEIGHT)
        pygame.draw.rect(self.screen, (20, 20, 30), panel)
        pygame.draw.line(self.screen, GRAY, (ARENA_WIDTH, 0), (ARENA_WIDTH, SCREEN_HEIGHT), 2)

        x = ARENA_WIDTH + 10
        y = 20
        t = self._font_hud.render("JUGADORES", True, WHITE)
        self.screen.blit(t, (x, y)); y += 30

        for p in sorted(state, key=lambda p: p["slot"]):
            color = PLAYER_COLORS[p["slot"] % len(PLAYER_COLORS)]
            marker = " ◄" if p["slot"] == self._local_slot else ""
            lbl = self._font_small.render(f"{p['name']}{marker}", True, color)
            self.screen.blit(lbl, (x, y)); y += 18
            _draw_healthbar_panel(self.screen, x, y, p["health"],
                                  SCREEN_WIDTH - ARENA_WIDTH - 20, 10)
            y += 18

        # Controles
        cy = SCREEN_HEIGHT - 120
        pygame.draw.line(self.screen, GRAY,
                         (x, cy), (SCREEN_WIDTH - 10, cy)); cy += 8
        for line in ["A/D  Mover", "W  Saltar", "E  Ataque debil",
                 "Q  Ataque fuerte", "R  Bloquear", "F10  Pantalla completa"]:
            s = self._font_small.render(line, True, GRAY)
            self.screen.blit(s, (x, cy)); cy += 18


# ──────────────────────────────────────────────────────────────────────────────
# CLIENTE – renderiza el estado recibido del host
# ──────────────────────────────────────────────────────────────────────────────

class GameMPClient:
    def __init__(self, screen: pygame.Surface, client):
        self.screen    = screen
        self.client    = client
        self.assets    = Assets.get()
        self.clock     = pygame.time.Clock()
        self.platforms = create_platform_group()

        self._font_name  = pygame.font.SysFont("Arial", 14, bold=True)
        self._font_hud   = pygame.font.SysFont("Arial", 18, bold=True)
        self._font_small = pygame.font.SysFont("Arial", 14)

        self._jump_queued = False
        self._last_state  = []

    # ------------------------------------------------------------------

    def run(self):
        while True:
            result = self._frame()
            if result:
                return result

    # ------------------------------------------------------------------

    def _frame(self):
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); raise SystemExit
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    self._jump_queued = True
                elif event.key == pygame.K_F10:
                    pygame.display.toggle_fullscreen()

        # ---- Enviar input ----
        self.client.send_input(
            left  = bool(keys[pygame.K_a]),
            right = bool(keys[pygame.K_d]),
            jump  = self._jump_queued,
            weak  = bool(keys[pygame.K_e]),
            heavy = bool(keys[pygame.K_q]),
            block = bool(keys[pygame.K_r]),
        )
        self._jump_queued = False

        # ---- Verificar fin de partida ----
        if not self.client.connected:
            return "disconnect"
        end = self.client.pop_latest_end()
        if end:
            return ("end", end.get("winner", "?"))

        # ---- Actualizar estado ----
        new_state = self.client.pop_latest_state()
        if new_state is not None:
            self._last_state = new_state

        # ---- Dibujar ----
        self._draw(self._last_state)
        self.clock.tick(FPS)
        return None

    # ------------------------------------------------------------------

    def _draw(self, state: list):
        ws = pygame.Surface((ARENA_WIDTH, SCREEN_HEIGHT)).convert()
        ws.blit(self.assets.arena, (0, 0))
        self.platforms.draw(ws)

        for p in state:
            sprite = self.assets.get_sprite(p["char"], p["state"], p["direc"], p["walk_c"])
            rect   = sprite.get_rect(midbottom=(int(p["x"]), int(p["y"])))
            ws.blit(sprite, rect)
            _draw_name_bar(ws, self._font_name, p, rect)

        self.screen.blit(ws, (0, 0))
        self._draw_hud(state)
        pygame.display.flip()

    def _draw_hud(self, state: list):
        panel = pygame.Rect(ARENA_WIDTH, 0, SCREEN_WIDTH - ARENA_WIDTH, SCREEN_HEIGHT)
        pygame.draw.rect(self.screen, (20, 20, 30), panel)
        pygame.draw.line(self.screen, GRAY, (ARENA_WIDTH, 0), (ARENA_WIDTH, SCREEN_HEIGHT), 2)

        x = ARENA_WIDTH + 10
        y = 20
        t = self._font_hud.render("JUGADORES", True, WHITE)
        self.screen.blit(t, (x, y)); y += 30

        for p in sorted(state, key=lambda p: p["slot"]):
            color  = PLAYER_COLORS[p["slot"] % len(PLAYER_COLORS)]
            marker = " ◄" if p["slot"] == self.client.slot else ""
            lbl = self._font_small.render(f"{p['name']}{marker}", True, color)
            self.screen.blit(lbl, (x, y)); y += 18
            _draw_healthbar_panel(self.screen, x, y, p["health"],
                                  SCREEN_WIDTH - ARENA_WIDTH - 20, 10)
            y += 18

        cy = SCREEN_HEIGHT - 120
        pygame.draw.line(self.screen, GRAY,
                         (x, cy), (SCREEN_WIDTH - 10, cy)); cy += 8
        for line in ["A/D  Mover", "W  Saltar", "E  Ataque debil",
                 "Q  Ataque fuerte", "R  Bloquear", "F10  Pantalla completa"]:
            s = self._font_small.render(line, True, GRAY)
            self.screen.blit(s, (x, cy)); cy += 18


# ──────────────────────────────────────────────────────────────────────────────
# Helpers de dibujo compartidos
# ──────────────────────────────────────────────────────────────────────────────

def _draw_name_bar(surf: pygame.Surface, font, p: dict, char_rect: pygame.Rect):
    color = PLAYER_COLORS[p["slot"] % len(PLAYER_COLORS)]
    # Barra de vida
    bw, bh = 50, 5
    bx = char_rect.centerx - bw // 2
    by = char_rect.top - 18
    hp = max(0.0, min(100.0, p["health"]))
    pygame.draw.rect(surf, (60, 60, 60), (bx, by, bw, bh))
    bar_color = (40, 200, 40) if hp > 60 else (255, 140, 0) if hp > 20 else (200, 30, 30)
    pygame.draw.rect(surf, bar_color, (bx, by, int(bw * hp / 100), bh))
    pygame.draw.rect(surf, (200, 200, 200), (bx, by, bw, bh), 1)
    # Nombre
    lbl = font.render(p["name"], True, color)
    surf.blit(lbl, (char_rect.centerx - lbl.get_width() // 2, by - 14))


def _draw_healthbar_panel(surf, x, y, hp, width, height):
    hp = max(0.0, min(100.0, hp))
    pygame.draw.rect(surf, (60, 60, 60), (x, y, width, height))
    color = (40, 200, 40) if hp > 60 else (255, 140, 0) if hp > 20 else (200, 30, 30)
    pygame.draw.rect(surf, color, (x, y, int(width * hp / 100), height))
    pygame.draw.rect(surf, (200, 200, 200), (x, y, width, height), 1)
