"""Descubrimiento de salas LAN por broadcast UDP."""
import json
import socket
import threading
import time

from src.network.protocol import DEFAULT_PORT, DISCOVERY_PORT

_DISCOVER_REQ = "discover_lobbies"
_DISCOVER_RES = "lobby_info"
_GAME_ID = "game_trump"


class LobbyDiscoveryResponder:
    """Responde a broadcasts LAN con información de la sala del host."""

    def __init__(self, info_provider):
        self._info_provider = info_provider
        self._running = True
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.bind(("", DISCOVERY_PORT))
        self._sock.settimeout(0.2)
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def _loop(self):
        while self._running:
            try:
                data, addr = self._sock.recvfrom(2048)
            except socket.timeout:
                continue
            except Exception:
                break

            try:
                msg = json.loads(data.decode("utf-8"))
            except Exception:
                continue

            if msg.get("type") != _DISCOVER_REQ or msg.get("game") != _GAME_ID:
                continue

            try:
                info = self._info_provider()
            except Exception:
                info = None

            if not info:
                continue

            payload = {
                "type": _DISCOVER_RES,
                "game": _GAME_ID,
                "port": DEFAULT_PORT,
                **info,
            }

            try:
                self._sock.sendto(json.dumps(payload).encode("utf-8"), addr)
            except Exception:
                continue

    def close(self):
        self._running = False
        try:
            self._sock.close()
        except Exception:
            pass


def discover_lobbies(timeout: float = 0.8, retries: int = 2) -> list:
    """Busca salas LAN disponibles y devuelve una lista de lobbies únicos por IP."""
    found = {}
    req = json.dumps({"type": _DISCOVER_REQ, "game": _GAME_ID}).encode("utf-8")

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("", 0))

    try:
        for _ in range(max(1, retries)):
            try:
                sock.sendto(req, ("255.255.255.255", DISCOVERY_PORT))
            except Exception:
                continue

            end_at = time.time() + max(0.1, timeout)
            while time.time() < end_at:
                remaining = end_at - time.time()
                sock.settimeout(max(0.05, remaining))
                try:
                    data, addr = sock.recvfrom(4096)
                except socket.timeout:
                    break
                except Exception:
                    break

                try:
                    msg = json.loads(data.decode("utf-8"))
                except Exception:
                    continue

                if msg.get("type") != _DISCOVER_RES or msg.get("game") != _GAME_ID:
                    continue
                if msg.get("game_started"):
                    continue

                ip = addr[0]
                found[ip] = {
                    "ip": ip,
                    "port": int(msg.get("port", DEFAULT_PORT)),
                    "host_name": str(msg.get("host_name", "Host"))[:16],
                    "players": int(msg.get("players", 1)),
                    "max_players": int(msg.get("max_players", 4)),
                }
    finally:
        sock.close()

    return sorted(found.values(), key=lambda x: (x["host_name"].lower(), x["ip"]))
