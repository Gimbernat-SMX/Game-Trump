"""Servidor del host para multijugador en red local."""
import socket
import threading
import time
from src.network.protocol import (
    encode, decode_from,
    JOIN, CHAR_SEL, INPUT,
    JOIN_OK, PLAYER_LIST, KICKED, GAME_START, GAME_STATE, GAME_END,
    DEFAULT_PORT,
)

MAX_PLAYERS = 4


class _PlayerSlot:
    def __init__(self, slot: int, name: str, char: str, sock=None):
        self.slot  = slot
        self.name  = name
        self.char  = char
        self.sock  = sock
        self.input = {"left": False, "right": False, "jump": False,
                      "weak": False, "heavy": False, "block": False}
        self.active = True


class Server:
    def __init__(self, host_name: str, host_char: str):
        self._lock    = threading.Lock()
        self._players: dict[int, _PlayerSlot] = {}
        self._next_slot = 1
        self._running   = True
        self.game_started = False

        # Slot 0 = host (no socket)
        self._players[0] = _PlayerSlot(0, host_name, host_char)

        self._srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._srv.bind(("0.0.0.0", DEFAULT_PORT))
        self._srv.listen(MAX_PLAYERS - 1)
        self._srv.settimeout(0.2)

        threading.Thread(target=self._accept_loop, daemon=True).start()

    # ------------------------------------------------------------------
    # Bucle de aceptación
    # ------------------------------------------------------------------

    def _accept_loop(self):
        while self._running and not self.game_started:
            try:
                conn, _addr = self._srv.accept()
            except socket.timeout:
                continue
            except Exception:
                break
            with self._lock:
                if len(self._players) >= MAX_PLAYERS:
                    conn.close()
                    continue
                slot = self._next_slot
                self._next_slot += 1
            threading.Thread(target=self._handshake, args=(conn, slot),
                             daemon=True).start()

    def _handshake(self, conn, slot: int):
        msg = decode_from(conn)
        if not msg or msg.get("type") != JOIN:
            conn.close()
            return
        name = str(msg.get("name", f"Player{slot}"))[:16]
        char = str(msg.get("char", "mario"))

        with self._lock:
            p = _PlayerSlot(slot, name, char, conn)
            self._players[slot] = p

        self._send(conn, {"type": JOIN_OK, "slot": slot})
        self._broadcast_player_list()
        threading.Thread(target=self._recv_loop, args=(slot,), daemon=True).start()

    # ------------------------------------------------------------------
    # Bucle de recepción por cliente
    # ------------------------------------------------------------------

    def _recv_loop(self, slot: int):
        with self._lock:
            p = self._players.get(slot)
        if not p:
            return

        while self._running:
            msg = decode_from(p.sock)
            if msg is None:
                self._disconnect(slot)
                return
            t = msg.get("type")
            if t == CHAR_SEL and not self.game_started:
                with self._lock:
                    p.char = str(msg.get("char", p.char))
                self._broadcast_player_list()
            elif t == INPUT:
                with self._lock:
                    inp = p.input
                    inp["left"]  = bool(msg.get("left",  False))
                    inp["right"] = bool(msg.get("right", False))
                    # jump es acumulativo: si llega True, se queda True hasta que el game loop lo consuma
                    if msg.get("jump"):
                        inp["jump"] = True
                    inp["weak"]  = bool(msg.get("weak",  False))
                    inp["heavy"] = bool(msg.get("heavy", False))
                    inp["block"] = bool(msg.get("block", False))

    def _disconnect(self, slot: int):
        with self._lock:
            p = self._players.pop(slot, None)
        if p and p.sock:
            try:
                p.sock.close()
            except Exception:
                pass
        self._broadcast_player_list()

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def kick(self, slot: int):
        if slot == 0:
            return
        with self._lock:
            p = self._players.get(slot)
        if p and p.sock:
            self._send(p.sock, {"type": KICKED})
            time.sleep(0.05)
        self._disconnect(slot)

    def start_game(self):
        self.game_started = True
        data = {"type": GAME_START, "players": self._player_list_data()}
        with self._lock:
            socks = [(s, p.sock) for s, p in self._players.items() if p.sock]
        for _s, sock in socks:
            self._send(sock, data)

    def broadcast_state(self, state: list):
        msg = {"type": GAME_STATE, "players": state}
        with self._lock:
            socks = [p.sock for p in self._players.values() if p.sock]
        for sock in socks:
            self._send(sock, msg)

    def broadcast_end(self, winner_name: str, winner_slot: int):
        msg = {"type": GAME_END, "winner": winner_name, "winner_slot": winner_slot}
        with self._lock:
            socks = [p.sock for p in self._players.values() if p.sock]
        for sock in socks:
            self._send(sock, msg)

    def get_inputs(self) -> "dict[int, dict]":
        """Devuelve inputs de todos los slots y limpia el flag jump."""
        with self._lock:
            result = {}
            for slot, p in self._players.items():
                result[slot] = dict(p.input)
                p.input["jump"] = False  # consumir el evento de salto
        return result

    def get_players(self) -> "dict[int, tuple]":
        """Devuelve {slot: (name, char)} de los jugadores activos."""
        with self._lock:
            return {slot: (p.name, p.char) for slot, p in self._players.items()}

    def get_player_list(self) -> list:
        """Lista de dicts para la UI del lobby."""
        with self._lock:
            return [{"slot": p.slot, "name": p.name, "char": p.char}
                    for p in sorted(self._players.values(), key=lambda x: x.slot)]

    def active_slots(self) -> set:
        with self._lock:
            return set(self._players.keys())

    def close(self):
        self._running = False
        try:
            self._srv.close()
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Helpers internos
    # ------------------------------------------------------------------

    def _broadcast_player_list(self):
        msg = {"type": PLAYER_LIST, "players": self._player_list_data()}
        with self._lock:
            socks = [p.sock for p in self._players.values() if p.sock]
        for sock in socks:
            self._send(sock, msg)

    def _player_list_data(self) -> list:
        with self._lock:
            return [{"slot": p.slot, "name": p.name, "char": p.char}
                    for p in sorted(self._players.values(), key=lambda x: x.slot)]

    def _send(self, sock, msg: dict):
        try:
            sock.sendall(encode(msg))
        except Exception:
            pass
