# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('smart_reports', 'smart_reports'),
    ],
    hiddenimports=[
        'tkinter',
        'ttkbootstrap',
        'pyodbc',
        'pandas',
        'numpy',
        'PIL',
        'PIL._tkinter_finder',
        'matplotlib',
        'matplotlib.backends.backend_tkagg',
        'openpyxl',
        'reportlab',
        'smart_reports',
        'smart_reports.config',
        'smart_reports.database',
        'smart_reports.ui',
        'smart_reports.services',
    ],
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
    name='SmartReports_InstitutoHP',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No mostrar consola
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Puedes agregar un icono .ico aquí si tienes uno
)
