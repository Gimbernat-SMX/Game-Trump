"""Cliente para conectarse al host en multijugador."""
import socket
import threading
from src.network.protocol import (
    encode, decode_from,
    JOIN, CHAR_SEL, INPUT,
    JOIN_OK, PLAYER_LIST, KICKED, GAME_START, GAME_STATE, GAME_END,
    DEFAULT_PORT,
)


class Client:
    def __init__(self):
        self._sock        = None
        self._lock        = threading.Lock()
        self.slot         = -1
        self.connected    = False

        self._player_list  = []
        self._game_started = False
        self._latest_state = None
        self._latest_end   = None
        self._kicked       = False

    # ------------------------------------------------------------------

    def connect(self, host_ip: str, name: str, char: str) -> bool:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5.0)
            sock.connect((host_ip.strip(), DEFAULT_PORT))
            sock.settimeout(None)

            sock.sendall(encode({"type": JOIN, "name": name, "char": char}))

            msg = decode_from(sock)
            if not msg or msg.get("type") != JOIN_OK:
                sock.close()
                return False

            self._sock     = sock
            self.slot      = msg["slot"]
            self.connected = True

            threading.Thread(target=self._recv_loop, daemon=True).start()
            return True
        except Exception:
            return False

    # ------------------------------------------------------------------

    def _recv_loop(self):
        while self.connected:
            msg = decode_from(self._sock)
            if msg is None:
                self.connected = False
                break
            t = msg.get("type")
            with self._lock:
                if t == PLAYER_LIST:
                    self._player_list = msg.get("players", [])
                elif t == GAME_START:
                    self._game_started = True
                    self._player_list  = msg.get("players", [])
                elif t == GAME_STATE:
                    self._latest_state = msg.get("players", [])
                elif t == GAME_END:
                    self._latest_end = msg
                elif t == KICKED:
                    self._kicked   = True
                    self.connected = False

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def send_input(self, left: bool, right: bool, jump: bool,
                   weak: bool, heavy: bool, block: bool = False):
        if not self.connected:
            return
        try:
            self._sock.sendall(encode({
                "type": INPUT,
                "left": left, "right": right, "jump": jump,
                "weak": weak, "heavy": heavy, "block": block,
            }))
        except Exception:
            self.connected = False

    def send_char(self, char: str):
        if not self.connected:
            return
        try:
            self._sock.sendall(encode({"type": CHAR_SEL, "char": char}))
        except Exception:
            pass

    def get_player_list(self) -> list:
        with self._lock:
            return list(self._player_list)

    def pop_latest_state(self) -> "list | None":
        with self._lock:
            s = self._latest_state
            self._latest_state = None
            return s

    def pop_latest_end(self) -> "dict | None":
        with self._lock:
            e = self._latest_end
            self._latest_end = None
            return e

    def is_game_started(self) -> bool:
        with self._lock:
            return self._game_started

    def is_kicked(self) -> bool:
        with self._lock:
            return self._kicked

    def close(self):
        self.connected = False
        try:
            self._sock.close()
        except Exception:
            pass
