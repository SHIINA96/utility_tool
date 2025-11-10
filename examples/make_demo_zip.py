"""小工具：把 `examples/check/homework_root` 打包成一个 zip，方便用于 `unzip2folder.py` 示例。

运行后会在 `examples/` 目录生成 `check_demo.zip`。
"""
import os
import zipfile

ROOT = os.path.join(os.path.dirname(__file__), 'check', 'homework_root')
OUT = os.path.join(os.path.dirname(__file__), 'check_demo.zip')

with zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED) as zf:
    for root, dirs, files in os.walk(ROOT):
        for f in files:
            full = os.path.join(root, f)
            arcname = os.path.relpath(full, os.path.join(ROOT, '..'))
            zf.write(full, arcname)

print(f"已生成示例 ZIP: {OUT}")
