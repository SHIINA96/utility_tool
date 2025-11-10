# unzip2folder.py — 详细说明

目的

批量解压目标目录中所有 `.zip` 文件，每个 ZIP 解压到与 ZIP 同名的子文件夹中。适合把一堆作业 ZIP、数据集压缩包等快速拆开为文件夹。

关键配置

- `BASE_DIR`：脚本顶部的路径变量。将其设置为要扫描并解压的目录，例如：

```python
BASE_DIR = r"/Users/barney/Documents/utility_tool/test_demo"
```

使用方法

```bash
python unzip2folder.py
```

脚本会对 `BASE_DIR` 下的每个以 `.zip` 结尾的文件创建一个同名文件夹并解压进去，完成后打印 "全部解压完成。"。

示例

1. 把 `examples/check_demo.zip` 放到 `BASE_DIR` 指定目录。
2. 运行脚本：`python unzip2folder.py`。
3. 会生成一个与 `check_demo.zip` 同名的文件夹并把内容解压到该文件夹。

注意事项

- 只处理 `.zip`（不处理 `.tar`、`.gz` 等），文件名大小写不敏感。
- 解压操作遵循 Python 标准库 `zipfile` 的行为：覆盖、权限等以 `zipfile` 的默认逻辑为准。
- 如果 ZIP 非常大，请确保磁盘空间足够。

小技巧

- 若想先预览将解压哪些文件，可先在终端用 `zipinfo <zipfile>` 或写一个小脚本读取 `ZipFile.namelist()`。
- 如需对 `.zip` 以外的格式支持，可扩展脚本并引入 `shutil.unpack_archive` 或第三方包。