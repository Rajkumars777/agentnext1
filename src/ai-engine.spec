# -*- mode: python ; coding: utf-8 -*-
#
# Project layout assumed:
#
#   C:\Users\rajak\Music\AI-agent---LTID-main\
#   ├── bin\
#   │   └── node.exe
#   ├── .openclaw\
#   ├── frontend\
#   │   ├── out\                  ← Next.js static export  (run: npm run export)
#   │   └── node_modules\
#   │       └── openclaw\
#   └── src\
#       ├── desktop_main.py       ← PyInstaller entry point  (this spec)
#       ├── main.py               ← FastAPI app
#       ├── api\
#       ├── core\
#       │   └── openclaw_process.py
#       ├── capabilities\
#       └── config.json
#
# Build command (run from the src\ directory):
#   cd C:\Users\rajak\Music\AI-agent---LTID-main\src
#   pyinstaller ai-engine.spec --clean
#
# Output:  src\dist\ai-engine.exe

import os

# Project root is one level above src/
PROJECT_ROOT = os.path.dirname(os.path.abspath(SPECPATH))

a = Analysis(
    # Entry point — must match the file that calls main()
    ['desktop_main.py'],

    # Tell PyInstaller to also look in src/ and the project root
    pathex=[
        SPECPATH,           # src/
        PROJECT_ROOT,       # project root
    ],

    binaries=[],

    datas=[
        # ── Python source packages ────────────────────────────────────────
        # All destinations are relative to _MEIPASS.
        # '.' means "land at the root of _MEIPASS" so imports work without a prefix.

        # FastAPI entry point
        ('main.py',                             '.'),

        # Backend packages
        ('api',                                 'api'),
        ('capabilities',                        'capabilities'),
        ('core',                                'core'),

        # Runtime config
        ('config.json',                         '.'),

        # ── Frontend static export ────────────────────────────────────────
        # Next.js output → bundled as 'static/' in _MEIPASS
        # Run `npm run export` (or `next export`) in frontend/ first.
        (os.path.join(PROJECT_ROOT, 'frontend', 'out'),             'static'),

        # ── Node.js binary ────────────────────────────────────────────────
        # Lands at _MEIPASS/bin/node.exe
        # openclaw_process.py looks here via _get_node_executable()
        (os.path.join(PROJECT_ROOT, 'bin', 'node.exe'),             'bin'),

        # ── OpenClaw JS package ───────────────────────────────────────────
        # Lands at _MEIPASS/openclaw/
        # openclaw_process.py _get_openclaw_script() checks this path first
        (os.path.join(PROJECT_ROOT, 'frontend', 'node_modules', 'openclaw'), 'openclaw'),

        # ── OpenClaw config / session data ────────────────────────────────
        # Lands at _MEIPASS/.openclaw/
        # openclaw_process.py _get_openclaw_home() picks this up when frozen
        (os.path.join(PROJECT_ROOT, '.openclaw'),                   '.openclaw'),
    ],

    # uvicorn dynamically imports these — PyInstaller misses them without this list
    hiddenimports=[
        'uvicorn',
        'uvicorn.logging',
        'uvicorn.loops',
        'uvicorn.loops.auto',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.websockets',
        'uvicorn.protocols.websockets.auto',
        'uvicorn.lifespan',
        'uvicorn.lifespan.on',
        'uvicorn.main',
        'fastapi',
        'starlette',
        'anyio',
        'anyio._backends._asyncio',
        'httptools',
        'websockets',
    ],

    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='ai-engine',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,

    # ─────────────────────────────────────────────────────────────────────
    # KEEP console=True while debugging so you can see crash output.
    # Flip to False only for the final production release build.
    # ─────────────────────────────────────────────────────────────────────
    console=True,

    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
