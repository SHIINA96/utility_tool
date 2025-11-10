# Utility Tool 集合

本仓库包含若干实用的 Python 小工具，包含：

- JSON -> CSV 转换工具（`json2csv_simplify_ch.py`）
- 批量解压 ZIP 到同名文件夹（`unzip2folder.py`）
- 学生作业中的 class 使用检测并导出 CSV（`check_py_class.py`）

下面分别说明每个工具的用途、配置和使用方法。

## 1) JSON -> CSV 转换工具 (`json2csv_simplify_ch.py`)

用途：将 JSON 转换为 CSV，并确保包含简体中文时在 Excel 中正确显示。

主要功能：

- 将 JSON（对象或对象数组）转换为 CSV
- 自动在第一列添加序号（从 1 开始）
- 将文本中的换行符替换为空格，避免 Excel 中换行导致格式问题
- 使用 UTF-8 BOM（`utf-8-sig`）编码生成 CSV，兼容 Excel

快速使用：

1. 在脚本目录准备 `input.json`（或修改脚本底部的 `json_file_path`）
2. 运行：
```bash
python json2csv_simplify_ch.py
```
3. 输出文件：`output.csv`

注意：输入 JSON 请使用 UTF-8 编码；脚本使用标准库，无需额外依赖。

示例输入（含换行）已在代码仓库中提供（README 上方示例）。

## 2) 批量解压工具 (`unzip2folder.py`)

用途：遍历指定目录，批量解压所有 `.zip` 文件到与 ZIP 同名的子文件夹中。

关键配置：

- `BASE_DIR`：要扫描并解压的目标目录（脚本顶端配置），例如：
    `BASE_DIR = r"/Users/barney/Documents/utility_tool/test_demo"`

使用方法：

1. 修改脚本中 `BASE_DIR` 为你要解压的目录（或者把脚本移到目标目录并修改为相对路径）
2. 运行脚本：
```bash
python unzip2folder.py
```
3. 脚本会为每个 ZIP 创建一个同名文件夹并将内容解压进去，处理完成后会打印 "全部解压完成。"

注意事项：

- 只处理以 `.zip` 结尾的文件，文件名不区分大小写
- 如果 ZIP 内包含同名文件夹或特殊权限，解压行为遵循 `zipfile` 模块的默认行为

## 3) 学生作业 class 使用检测工具 (`check_py_class.py`)

用途：遍历给定的作业根目录（每个学生一个子文件夹），统计每个学生提交的 `.py` 文件中定义的 class 数量，并导出一个 CSV 报表，方便批量检查作业中是否使用了 class。

主要配置（脚本顶部）：

- `HOMEWORK_ROOT`：作业根目录（每个学生一个子文件夹）
- `OUTPUT_CSV`：导出 CSV 的文件名（默认为 `class_usage_result.csv`）
- `EXCEL_NAME_FILE`：可选，包含“分组编号 + 正式姓名”的 Excel 文件（用于把文件夹名纠正为正式姓名并获取分组）
- `EXCLUDED_DIRS`：在遍历时跳过的子目录名（默认包含 `__pycache__`, `.git`, `.idea`, `.vscode`, `__MACOSX`）
- `DEBUG`：是否打印调试信息

特点与行为：

- 统计每个学生目录下所有 `.py` 文件中的 `class` 定义（基于 `ast` 解析）
- 如果给定 Excel 名单并安装 `pandas`，脚本会尝试把文件夹名中的学生名匹配到正式姓名与分组（需要 `pandas` + `openpyxl`）
- 输出 CSV 使用 `utf-8-sig` 编码，包含字段：
    `folder, student_name_raw, student_name, team_parsed, team_from_excel, used_class, class_count, py_files`

运行方法：

1. 修改 `HOMEWORK_ROOT` 为你要检查的目录（脚本默认在顶部配置）
2. （可选）把 `EXCEL_NAME_FILE` 指向包含学生名单的 Excel 文件，以启用姓名/分组纠正
3. 运行：
```bash
python check_py_class.py
```
4. 运行结束后，会在当前目录生成 `class_usage_result.csv`（或你在配置中设置的 `OUTPUT_CSV` 名称）

依赖（可选）：

- 若需要从 Excel 自动读取并纠正姓名/分组，请安装：
```bash
pip install pandas openpyxl
```

实现细节与注意事项：

- `.py` 文件读取默认使用 UTF-8；遇到 `UnicodeDecodeError` 会回退到 `gbk` 并忽略错误以便尽可能解析学生提交的文件
- 通过 `ast.parse` 构建抽象语法树并统计 `ClassDef` 节点来计算 class 数量
- 当遇到语法错误或不可解析的文件（例如包含空字节）时，脚本会跳过并输出警告

## 通用说明

- 所有工具都尽量使用标准库实现，除非某个功能显式依赖第三方包（例如 `pandas`）
- 在 macOS 上，建议在仓库根目录添加 `.gitignore`（本仓库已包含）以忽略 `.json`、`.csv` 等输出文件
- 若要把某些被 `.gitignore` 忽略的文件加入版本控制，可使用 `git add -f <file>` 强制添加

## 示例：同时运行两个工具

假设你想先解压 `test_demo` 目录下的 ZIP 文件，然后统计解压后的学生目录：

```bash
# 1) 批量解压
python unzip2folder.py

# 2) 指定 HOMEWORK_ROOT 为解压后的目录（修改 check_py_class.py 顶部配置），然后运行
python check_py_class.py
```

---

如果你希望我把这些说明拆成独立的文档（例如 `docs/` 下的详细使用说明），或为每个脚本添加示例输入/输出文件，我可以继续帮你补充并创建示例文件。

已拆分为 `docs/` 和 `examples/`：

- 详细文档位于 `docs/`（`json2csv.md`, `unzip2folder.md`, `check_py_class.md`）。
- 示例文件位于 `examples/`：
    - `examples/json/input.json`：JSON->CSV 工具的示例输入
    - `examples/check/homework_root/...`：`check_py_class.py` 的示例学生提交（含 `student_alice` 和 `student_bob`）
    - `examples/make_demo_zip.py`：一个小脚本，可将 `examples/check/homework_root` 打包成 `examples/check_demo.zip`，以便用 `unzip2folder.py` 测试解压流程。

要运行示例：

1. 生成示例 ZIP（可选）：
```bash
python examples/make_demo_zip.py
```
2. 运行批量解压（确保 `unzip2folder.py` 中的 `BASE_DIR` 指向 `examples/`）：
```bash
python unzip2folder.py
```
3. 使用 JSON->CSV 示例：
```bash
cp examples/json/input.json ./input.json
python json2csv_simplify_ch.py
```
4. 使用 class 检查示例：
```bash
# 修改 check_py_class.py 顶部的 HOMEWORK_ROOT 指向 examples/check/homework_root
python check_py_class.py
```