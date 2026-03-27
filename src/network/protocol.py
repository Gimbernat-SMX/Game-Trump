"""Protocolo de mensajes para multijugador en red local."""
import json
import struct
import socket

# Tipos de mensaje cliente → servidor
JOIN      = "join"       # {"type":"join","name":"...","char":"mario"}
CHAR_SEL  = "char"       # {"type":"char","char":"mario"}
INPUT     = "input"      # {"type":"input","left":bool,"right":bool,"jump":bool,"weak":bool,"heavy":bool}

# Tipos de mensaje servidor → cliente
JOIN_OK      = "join_ok"      # {"type":"join_ok","slot":1}
PLAYER_LIST  = "player_list"  # {"type":"player_list","players":[...]}
KICKED       = "kicked"       # {"type":"kicked"}
GAME_START   = "game_start"   # {"type":"game_start","players":[...]}
GAME_STATE   = "game_state"   # {"type":"game_state","players":[...]}
GAME_END     = "game_end"     # {"type":"game_end","winner":"...","winner_slot":0}

DEFAULT_PORT = 5555


def encode(msg: dict) -> bytes:
    data = json.dumps(msg).encode("utf-8")
    return struct.pack(">I", len(data)) + data


def decode_from(sock) -> "dict | None":
    header = _recv_exact(sock, 4)
    if header is None:
        return None
    length = struct.unpack(">I", header)[0]
    if length > 1_000_000:
        return None
    body = _recv_exact(sock, length)
    if body is None:
        return None
    try:
        return json.loads(body.decode("utf-8"))
    except Exception:
        return None


def _recv_exact(sock, n: int) -> "bytes | None":
    buf = b""
    while len(buf) < n:
        try:
            chunk = sock.recv(n - len(buf))
            if not chunk:
                return None
            buf += chunk
        except Exception:
            return None
    return buf


def get_local_ip() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"
