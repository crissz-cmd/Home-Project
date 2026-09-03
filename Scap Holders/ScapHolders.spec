# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules, collect_dynamic_libs
hiddenimports = ["MetaTrader5","pandas","numpy","dotenv","bot","config","mt5_connector","indicators","strategy","risk_manager","license_public_key"]
hiddenimports += collect_submodules("MetaTrader5")
binaries = collect_dynamic_libs("MetaTrader5")
a = Analysis(["product_launcher.py"], pathex=["."], binaries=binaries, datas=[], hiddenimports=hiddenimports, hookspath=[], hooksconfig={}, runtime_hooks=[], excludes=[], noarchive=False)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, a.binaries, a.datas, [], name="ScapHolders", debug=False, bootloader_ignore_signals=False, strip=False, upx=True, console=False, disable_windowed_traceback=False)
