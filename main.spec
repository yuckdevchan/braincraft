# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('assets/treasure.json', 'assets/treasure.json'), ('assets/fonts\\pixel.ttf', 'assets/fonts\\pixel.ttf'), ('assets/meta\\block\\block_allium.json', 'assets/meta\\block\\block_allium.json'), ('assets/meta\\block\\block_andesite.json', 'assets/meta\\block\\block_andesite.json'), ('assets/meta\\block\\block_bedrock.json', 'assets/meta\\block\\block_bedrock.json'), ('assets/meta\\block\\block_coal_ore.json', 'assets/meta\\block\\block_coal_ore.json'), ('assets/meta\\block\\block_copper_ore.json', 'assets/meta\\block\\block_copper_ore.json'), ('assets/meta\\block\\block_cornflower.json', 'assets/meta\\block\\block_cornflower.json'), ('assets/meta\\block\\block_dandelion.json', 'assets/meta\\block\\block_dandelion.json'), ('assets/meta\\block\\block_diamond_ore.json', 'assets/meta\\block\\block_diamond_ore.json'), ('assets/meta\\block\\block_dirt_block.json', 'assets/meta\\block\\block_dirt_block.json'), ('assets/meta\\block\\block_emerald_ore.json', 'assets/meta\\block\\block_emerald_ore.json'), ('assets/meta\\block\\block_gold_ore.json', 'assets/meta\\block\\block_gold_ore.json'), ('assets/meta\\block\\block_grass_block.json', 'assets/meta\\block\\block_grass_block.json'), ('assets/meta\\block\\block_iron_ore.json', 'assets/meta\\block\\block_iron_ore.json'), ('assets/meta\\block\\block_lapis_ore.json', 'assets/meta\\block\\block_lapis_ore.json'), ('assets/meta\\block\\block_nether_portal.json', 'assets/meta\\block\\block_nether_portal.json'), ('assets/meta\\block\\block_oak_leaves.json', 'assets/meta\\block\\block_oak_leaves.json'), ('assets/meta\\block\\block_oak_log.json', 'assets/meta\\block\\block_oak_log.json'), ('assets/meta\\block\\block_obsidian.json', 'assets/meta\\block\\block_obsidian.json'), ('assets/meta\\block\\block_poppy.json', 'assets/meta\\block\\block_poppy.json'), ('assets/meta\\block\\block_stone.json', 'assets/meta\\block\\block_stone.json'), ('assets/meta\\structures\\oak_tree.json', 'assets/meta\\structures\\oak_tree.json'), ('assets/textures\\icon.ico', 'assets/textures\\icon.ico'), ('assets/textures\\block\\allium.png', 'assets/textures\\block\\allium.png'), ('assets/textures\\block\\andesite.png', 'assets/textures\\block\\andesite.png'), ('assets/textures\\block\\bedrock.png', 'assets/textures\\block\\bedrock.png'), ('assets/textures\\block\\coal_ore.png', 'assets/textures\\block\\coal_ore.png'), ('assets/textures\\block\\copper_ore.png', 'assets/textures\\block\\copper_ore.png'), ('assets/textures\\block\\cornflower.png', 'assets/textures\\block\\cornflower.png'), ('assets/textures\\block\\dandelion.png', 'assets/textures\\block\\dandelion.png'), ('assets/textures\\block\\diamond_ore.png', 'assets/textures\\block\\diamond_ore.png'), ('assets/textures\\block\\dirt.png', 'assets/textures\\block\\dirt.png'), ('assets/textures\\block\\emerald_ore.png', 'assets/textures\\block\\emerald_ore.png'), ('assets/textures\\block\\gold_ore.png', 'assets/textures\\block\\gold_ore.png'), ('assets/textures\\block\\grass.png', 'assets/textures\\block\\grass.png'), ('assets/textures\\block\\grass_side.png', 'assets/textures\\block\\grass_side.png'), ('assets/textures\\block\\iron_ore.png', 'assets/textures\\block\\iron_ore.png'), ('assets/textures\\block\\lapis_ore.png', 'assets/textures\\block\\lapis_ore.png'), ('assets/textures\\block\\nether_portal.png', 'assets/textures\\block\\nether_portal.png'), ('assets/textures\\block\\oak_leaves.png', 'assets/textures\\block\\oak_leaves.png'), ('assets/textures\\block\\oak_log.png', 'assets/textures\\block\\oak_log.png'), ('assets/textures\\block\\oak_log_top.png', 'assets/textures\\block\\oak_log_top.png'), ('assets/textures\\block\\obsidian.png', 'assets/textures\\block\\obsidian.png'), ('assets/textures\\block\\poppy.png', 'assets/textures\\block\\poppy.png'), ('assets/textures\\block\\stone.png', 'assets/textures\\block\\stone.png'), ('assets/textures\\environment\\clouds.png', 'assets/textures\\environment\\clouds.png'), ('assets/textures\\misc\\crosshair.png', 'assets/textures\\misc\\crosshair.png')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='main',
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
    icon=['assets\\textures\\icon.ico'],
)
