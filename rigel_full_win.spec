# RIGEL Business — PyInstaller spec — Windows Full (.exe)
# Run: pyinstaller rigel_full_win.spec
# Output: dist/RIGEL_Business_Full.exe

block_cipher = None
import os
import sys
base_dir = os.getcwd()
sys.path.insert(0, base_dir)

a = Analysis(
    ['rigel_full_win.py'],
    pathex=[base_dir],
    binaries=[],
    datas=[],
    hiddenimports=[
        'accounting',
        'rigel_core',
        'assets_b64',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'PyQt6.sip',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'numpy', 'pandas'],
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
    name='RIGEL_Business_Full',
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
    icon=None,
    version_file=None,
)
