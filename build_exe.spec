# -*- mode: python ; coding: utf-8 -*-

import os
from pathlib import Path

# Pfade definieren
project_root = Path.cwd()
src_path = project_root / "src"

# Alle Python-Dateien sammeln
def collect_python_files(directory):
    """Sammelt alle Python-Dateien in einem Verzeichnis"""
    files = []
    for root, dirs, filenames in os.walk(directory):
        for filename in filenames:
            if filename.endswith('.py'):
                file_path = os.path.join(root, filename)
                # Relativer Pfad für das Zielsystem
                rel_path = os.path.relpath(file_path, project_root)
                files.append((file_path, os.path.dirname(rel_path)))
    return files

# Daten sammeln
datas = []

# Source-Code Dateien hinzufügen
datas.extend(collect_python_files(src_path))

# Storage-Verzeichnis für JSON-Dateien
storage_files = []
storage_path = project_root / "storage"
if storage_path.exists():
    for file in storage_path.glob("*.json"):
        storage_files.append((str(file), "storage"))

datas.extend(storage_files)

# Hidden imports für spezielle Module
hiddenimports = [
    'customtkinter',
    'tkinter',
    'tkinter.ttk',
    'tkinter.messagebox',
    'tkinter.filedialog',
    'tkinter.simpledialog',
    'reportlab',
    'PIL',
    'PIL.Image',
    'PIL.ImageTk',
    'tkcalendar',
    'qrcode',
    'json',
    'datetime',
    'pathlib',
    'decimal',
    'typing',
    'dataclasses',
    'enum',
    'urllib',
    'urllib.request',
    'threading',
    'webbrowser'
]

# PyInstaller Analysis
a = Analysis(
    ['main.py'],
    pathex=[str(project_root)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'test',
        'tests',
        'unittest',
        'pytest',
        'IPython',
        'jupyter',
        'notebook'
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# PYZ (Python ZIP archive)
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# EXE-Datei erstellen
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Rechnungs-Tool',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Keine Konsole anzeigen
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Hier könnte ein Icon-Pfad stehen
    version_info=None
)
