# -*- mode: python ; coding: utf-8 -*-
# PyInstaller stub — packaging will be refined in a later phase.
# From repo root: pyinstaller build/e7_gear_gui.spec

block_cipher = None

a = Analysis(
    ['gui/app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('inp/character_data.csv', 'inp'),
        ('inp/gear_tiers.csv', 'inp'),
    ],
    hiddenimports=['gui.bootstrap'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
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
    name='E7GearSelector',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
