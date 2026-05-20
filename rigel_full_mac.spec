# RIGEL Business — PyInstaller spec — macOS Full (.app → .dmg)
# Run on macOS: pyinstaller rigel_full_mac.spec
# Then wrap with create-dmg (see build_macos.sh)
# Output: dist/RIGEL_Business_Full.app → dist/RIGEL_Business_Full.dmg

block_cipher = None

a = Analysis(
    ['rigel_full_mac.py'],
    pathex=['.'],
    binaries=[],
    datas=[],
    hiddenimports=[
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
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='RIGEL_Business_Full',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=True,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='RIGEL_Business_Full',
)

app = BUNDLE(
    coll,
    name='RIGEL_Business_Full.app',
    icon=None,
    bundle_identifier='co.za.stellalumen.rigel-full',
    version='1.0.0',
    info_plist={
        'CFBundleName':             'RIGEL Business',
        'CFBundleDisplayName':      'RIGEL Business',
        'CFBundleVersion':          '1.0.0',
        'CFBundleShortVersionString':'1.0',
        'CFBundleIdentifier':       'co.za.stellalumen.rigel-full',
        'NSHumanReadableCopyright': '© 2026 Stella Lumen (Pty) Ltd',
        'NSHighResolutionCapable':  True,
        'NSRequiresAquaSystemAppearance': False,
        'LSMinimumSystemVersion':   '12.0',
        'CFBundleDocumentTypes':    [],
    },
)
