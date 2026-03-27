# -*- mode: python ; coding: utf-8 -*-
import sys
import os

block_cipher = None

APP_NAME = "GimbernatBros"

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

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name=APP_NAME,
    debug=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,        # sin ventana de consola
    bootloader_ignore_signals=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# En macOS, generar también el .app
if sys.platform == "darwin":
    app = BUNDLE(
        exe,
        name=APP_NAME + ".app",
        bundle_identifier="com.gimbernat.gimbernatbros",
    )
