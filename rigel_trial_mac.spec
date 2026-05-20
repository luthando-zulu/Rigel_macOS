# RIGEL Business — PyInstaller spec — macOS Trial (.app → .dmg)
# Run on macOS: pyinstaller rigel_trial_mac.spec
# Then wrap with create-dmg (see build_macos.sh)
# Output: dist/RIGEL_Business_Trial.app → dist/RIGEL_Business_Trial.dmg

block_cipher = None

a = Analysis(
    ['rigel_trial_mac.py'],
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
    name='RIGEL_Business_Trial',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,           # Do NOT use UPX on macOS — breaks codesign
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=True, # Required for macOS open-with support
    target_arch=None,    # None = native arch; use 'universal2' for fat binary
    codesign_identity=None,
    entitlements_file=None,
    icon=None,           # Set to 'rigel.icns' if you have one
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='RIGEL_Business_Trial',
)

app = BUNDLE(
    coll,
    name='RIGEL_Business_Trial.app',
    icon=None,           # Set to 'rigel.icns'
    bundle_identifier='co.za.stellalumen.rigel-trial',
    version='1.0.0',
    info_plist={
        'CFBundleName':             'RIGEL Business Trial',
        'CFBundleDisplayName':      'RIGEL Business (Trial)',
        'CFBundleVersion':          '1.0.0',
        'CFBundleShortVersionString':'1.0',
        'CFBundleIdentifier':       'co.za.stellalumen.rigel-trial',
        'NSHumanReadableCopyright': '© 2026 Stella Lumen (Pty) Ltd',
        'NSHighResolutionCapable':  True,
        'NSRequiresAquaSystemAppearance': False,  # Supports dark mode
        'LSMinimumSystemVersion':   '12.0',
        'CFBundleDocumentTypes':    [],
    },
)
