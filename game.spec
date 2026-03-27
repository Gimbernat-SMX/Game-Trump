# -*- mode: python ; coding: utf-8 -*-
import sys

block_cipher = None
APP_NAME     = "GimbernatBros"

# Windows usa one-file (todo en un único .exe, sin carpeta _internal)
# Mac/Linux usan one-dir (necesario para .app y .deb)
ONEFILE = sys.platform == "win32"

a = Analysis(
    ["launcher.py"],
    pathex=["."],
    binaries=[],
    datas=[
        ("assets", "assets"),
    ],
    hiddenimports=[
        "pygame",
        "pygame._sdl2",
        "pygame._sdl2.video",
        "pygame.font",
        "pygame.mixer",
        "src",
        "src.constants",
        "src.assets",
        "src.menu",
        "src.game",
        "src.game_mp",
        "src.lobby",
        "src.player",
        "src.enemy",
        "src.hud",
        "src.platform_map",
        "src.characters",
        "src.characters.base",
        "src.characters.mario",
        "src.characters.luigi",
        "src.characters.yoshi",
        "src.characters.popo",
        "src.characters.nana",
        "src.characters.link",
        "src.network",
        "src.network.protocol",
        "src.network.server",
        "src.network.client",
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

if ONEFILE:
    # ── Windows: un único .exe autocontenido ──────────────────────────
    exe = EXE(
        pyz,
        a.scripts,
        a.binaries,
        a.zipfiles,
        a.datas,
        [],
        name=APP_NAME + ".exe",
        debug=False,
        strip=False,
        upx=False,
        console=False,
        bootloader_ignore_signals=False,
        disable_windowed_traceback=False,
        argv_emulation=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
    )
else:
    # ── Mac / Linux: carpeta con el ejecutable y sus dependencias ─────
    exe = EXE(
        pyz,
        a.scripts,
        [],
        exclude_binaries=True,
        name=APP_NAME,
        debug=False,
        strip=False,
        upx=False,
        console=False,
        bootloader_ignore_signals=False,
        disable_windowed_traceback=False,
        argv_emulation=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
    )

    coll = COLLECT(
        exe,
        a.binaries,
        a.zipfiles,
        a.datas,
        strip=False,
        upx=False,
        name=APP_NAME,
    )

    # macOS: empaquetar en .app
    if sys.platform == "darwin":
        app = BUNDLE(
            coll,
            name=APP_NAME + ".app",
            bundle_identifier="com.gimbernat.gimbernatbros",
        )
