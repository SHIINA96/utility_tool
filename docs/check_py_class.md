# check_py_class.py — 详细说明

目的

遍历一个作业根目录（每个学生一个子文件夹），统计每个学生提交的 `.py` 文件中定义的 `class` 的数量，并输出一个易于在 Excel 中查看的 CSV 报表。

主要配置（脚本顶部）

- `HOMEWORK_ROOT`：作业根目录（每个学生一个子文件夹）
- `OUTPUT_CSV`：导出 CSV 的文件名（默认 `class_usage_result.csv`）
- `EXCEL_NAME_FILE`：可选，指向包含“分组编号 + 正式姓名”的 Excel 文件，用于把文件夹名纠正为正式姓名并获取分组（需 `pandas` + `openpyxl`）
- `EXCLUDED_DIRS`：遍历时跳过的目录，例如 `__pycache__`、`.git` 等
- `DEBUG`：是否打印调试信息

输出 CSV 字段

`folder, student_name_raw, student_name, team_parsed, team_from_excel, used_class, class_count, py_files`

实现细节

- 使用 `ast.parse` 对 `.py` 源码构建抽象语法树，并统计 `ClassDef` 节点数来计算 class 数量。
- 默认用 `utf-8` 打开文件；若遇到 `UnicodeDecodeError` 会回退到 `gbk` 并忽略错误，尽量兼容学生提交的各种编码。
- 遇到语法错误或包含空字节（null bytes）的文件，脚本会跳过并发出警告。

可选的 Excel 名单匹配

- 若提供 `EXCEL_NAME_FILE` 且安装了 `pandas` + `openpyxl`，脚本会读取 Excel 的指定区域（示例脚本读取 A8:B102）并生成姓名 slug 用于匹配文件夹名，进而把 `student_name_raw` 映射为正式姓名并填入 `student_name`，同时填充 `team_from_excel`。

运行方法

1. 修改 `HOMEWORK_ROOT` 为你的作业目录
2. （可选）指定 `EXCEL_NAME_FILE` 路径并安装依赖：

```bash
pip install pandas openpyxl
```

3. 运行：

```bash
python check_py_class.py
```

4. 查看生成的 CSV（默认 `class_usage_result.csv`）。

示例输入（在 `examples/check/homework_root/`）

- `student_alice` 含一个或多个 `.py` 文件，其中包含 `class` 定义。
- `student_bob` 含 `.py` 文件但没有 `class`。

脚本会为每个学生输出统计信息，包括总的 `.py` 文件数与 class 数量。

扩展建议

- 若希望按每个文件列出 class 名称或数量，可在 `count_classes_in_file` 中扩展，返回每个文件的详细清单并把它们写入 CSV。