# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['sqlite3','chromadb.telemetry.product.posthog','chromadb.telemetry.posthog', 'chromadb.api.segment', 'chromadb.db.impl', 
    'chromadb.db.impl.sqlite', 'chromadb.migrations', 'chromadb.migrations.embeddings_queue', 
    'chromadb.segment.impl.manager', 'chromadb.segment.impl.manager.local', 'chromadb.segment.impl.metadata',
    'chromadb.segment.impl.metadata.sqlite', 'chromadb.segment.impl.vector', 'chromadb.segment.impl.vector.batch', 
    'chromadb.segment.impl.vector.brute_force_index', 'chromadb.segment.impl.vector.hnsw_params', 'chromadb.segment.impl.vector.local_hnsw', 
    'chromadb.segment.impl.vector.local_persistent_hnsw','chromadb.migrations.sysdb','chromadb.migrations.metadb','chromadb'],
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
    [],
    exclude_binaries=True,
    name='Visual_Prompt_Engineering',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='main',
)
