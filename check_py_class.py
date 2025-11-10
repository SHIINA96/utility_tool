import os
import ast
import csv
import re

# ================== 配置区（按需修改） ==================

# 学生作业的根目录：每个学生一个子文件夹
# 例如：r"/Users/barney/Documents/utility_tool/homework_root"
HOMEWORK_ROOT = r"/Users/barney/Documents/utility_tool/test_demo"

# 导出结果的 CSV 文件名
OUTPUT_CSV = "class_usage_result.csv"

# 包含“正确姓名 + 分组编号”的 Excel 文件
EXCEL_NAME_FILE = r"./2025 S2 TA Marking.xlsx"

# 不想统计的固定子目录（非 env 类）
EXCLUDED_DIRS = ("__pycache__", ".git", ".idea", ".vscode", "__MACOSX")

# 是否打印调试信息（比如每个被检查的 .py 文件路径）
DEBUG = False

# ============= 全局变量：姓名 & 分组信息 =============

CORRECT_NAMES = []           # 正式姓名列表（Excel 第二列）
CORRECT_NAMES_SLUG = []      # 对应的 slug（用于匹配）
CORRECT_GROUPS = []          # 对应的分组编号（Excel 第一列，纯数字字符串）


# ================== 工具函数 ==================


def slugify_name(name: str) -> str:
    """
    把姓名转换成便于匹配的形式：
    - 全部转成小写
    - 去掉空格、标点、非字母字符
      例如：'Martin Kalanda-Phiri' -> 'martinkalandaphriri'
    """
    name = name.lower()
    # 只保留 a-z 字母
    return re.sub(r"[^a-z]", "", name)


def load_correct_names_from_excel(path: str):
    """
    从 Excel 中读取“分组编号 + 姓名”列表，初始化：
      CORRECT_NAMES, CORRECT_NAMES_SLUG, CORRECT_GROUPS

    假设格式：
      第一列：组号（数字）
      第二列：学生姓名
    行范围：从第 8 行开始（A8:B102），和你之前说的 B8-B102 对齐

    依赖 pandas + openpyxl:
        pip install pandas openpyxl
    """
    global CORRECT_NAMES, CORRECT_NAMES_SLUG, CORRECT_GROUPS

    if not os.path.exists(path):
        print(f"[提示] 未找到 Excel 文件: {path}，将不做姓名/分组纠正。")
        return

    try:
        import pandas as pd
    except ImportError:
        print("[提示] 未安装 pandas，无法从 Excel 读取姓名/分组。")
        print("      如需开启姓名纠正，请先运行: pip install pandas openpyxl")
        return

    try:
        # 读取第一张表，且不假设有表头
        df = pd.read_excel(path, sheet_name=0, header=None)
        # A8:B102 -> 行索引 7~101，列 0 是组号，列 1 是姓名
        sub = df.iloc[7:102, 0:2]
    except Exception as e:
        print(f"[提示] 读取 Excel 时出错: {e}")
        print("      将不做姓名/分组纠正。")
        return

    CORRECT_NAMES = []
    CORRECT_NAMES_SLUG = []
    CORRECT_GROUPS = []

    for _, row in sub.iterrows():
        group_val = row.iloc[0]
        name_val = row.iloc[1]

        # 处理姓名
        if isinstance(name_val, str):
            name = name_val.strip()
        else:
            continue
        if not name:
            continue

        # 处理组号：转成纯数字字符串
        if pd.isna(group_val):
            group = ""
        elif isinstance(group_val, (int, float)):
            group = str(int(group_val))
        else:
            group = str(group_val).strip()

        CORRECT_NAMES.append(name)
        CORRECT_NAMES_SLUG.append(slugify_name(name))
        CORRECT_GROUPS.append(group)

    print(f"[信息] 从 Excel 读取到 {len(CORRECT_NAMES)} 个学生姓名和分组用于匹配。")


def match_correct_name_and_group(raw_student_name: str):
    """
    根据从文件夹解析出来的 raw_student_name（例如 'alshammarikhlaf'），
    在 Excel 名单中找到最相近的一个，返回：
        (正确姓名, 分组编号字符串)
    如果没法找到合适的匹配，就返回 (raw_student_name, "")。
    """
    if not CORRECT_NAMES:
        return raw_student_name, ""

    from difflib import SequenceMatcher

    raw_slug = slugify_name(raw_student_name)
    if not raw_slug:
        return raw_student_name, ""

    # 1) 先看 slug 是否互相包含
    for name, name_slug, group in zip(CORRECT_NAMES, CORRECT_NAMES_SLUG, CORRECT_GROUPS):
        if not name_slug:
            continue
        if raw_slug in name_slug or name_slug in raw_slug:
            return name, group

    # 2) 用相似度挑一个最接近的
    best_ratio = 0.0
    best_idx = -1
    for i, name_slug in enumerate(CORRECT_NAMES_SLUG):
        if not name_slug:
            continue
        ratio = SequenceMatcher(None, raw_slug, name_slug).ratio()
        if ratio > best_ratio:
            best_ratio = ratio
            best_idx = i

    if best_idx >= 0 and best_ratio >= 0.5:   # 阈值可按效果调
        return CORRECT_NAMES[best_idx], CORRECT_GROUPS[best_idx]

    return raw_student_name, ""


def parse_folder_name(folder_name: str):
    """
    解析学生文件夹名，返回：
        (student_name_raw, student_name_correct, team_parsed, team_from_excel)

    - student_name_raw：从文件夹中取第一个下划线前的部分
    - student_name_correct：根据 Excel 名单纠正后的名字
    - team_parsed：从文件夹名中解析出的组别字符串（例如 'Team 26'）
    - team_from_excel：从 Excel 第一列读取到的“纯数字组号”（字符串）
    """
    # 学生名字（原始）：取第一个下划线前面
    parts = folder_name.split("_")
    student_name_raw = parts[0] if parts else folder_name

    # 用 Excel 中的列表纠正姓名 + 分组
    student_name_correct, team_from_excel = match_correct_name_and_group(student_name_raw)

    # 匹配 Team_26 / Team26 / team24 / group16 / Group_11 / Group 24 等（来自文件夹）
    m = re.search(r"(team|group)[ _]?(\d+)", folder_name, re.IGNORECASE)
    if m:
        group_word = m.group(1).capitalize()  # 统一成 Team / Group
        group_num = m.group(2)
        team_parsed = f"{group_word} {group_num}"    # 例如 "Team 26"
    else:
        team_parsed = ""

    return student_name_raw, student_name_correct, team_parsed, team_from_excel


def count_classes_in_file(py_file: str) -> int:
    """统计单个 .py 文件中 class 的数量"""
    try:
        with open(py_file, "r", encoding="utf-8") as f:
            source = f.read()
    except UnicodeDecodeError:
        # 如果有学生用奇怪编码，退而求其次
        with open(py_file, "r", encoding="gbk", errors="ignore") as f:
            source = f.read()

    # 防止 "source code string cannot contain null bytes" 报错
    if "\x00" in source:
        print(f"[警告] 文件包含空字节，跳过：{py_file}")
        return 0

    try:
        tree = ast.parse(source)
    except (SyntaxError, ValueError) as e:
        # SyntaxError: 语法错误
        # ValueError: 比如仍然有奇怪内容（包括 null bytes 等）
        print(f"[警告] 无法解析（{e.__class__.__name__}）：{py_file}")
        return 0

    # 在语法树里统计 ClassDef 节点
    count = sum(isinstance(node, ast.ClassDef) for node in ast.walk(tree))
    return count


def check_student_dir(folder_name: str, student_path: str) -> dict:
    """
    统计某个学生目录里所有 .py 文件中的 class 总数，
    并解析出学生名字（原始 + 纠正后）、组别（文件夹解析 + Excel）。
    """
    (
        student_name_raw,
        student_name_correct,
        team_parsed,
        team_from_excel,
    ) = parse_folder_name(folder_name)

    total_classes = 0
    py_files = 0

    # os.walk 会递归遍历所有子目录
    for root, dirs, files in os.walk(student_path):
        # ====== 排除不想遍历的子目录 ======
        # 1）排除 EXCLUDED_DIRS 里的固定目录
        # 2）排除名字中包含 "env"（不区分大小写）的目录
        dirs[:] = [
            d for d in dirs
            if d not in EXCLUDED_DIRS and "env" not in d.lower()
        ]
        # =================================

        for filename in files:
            if filename.endswith(".py"):
                full_path = os.path.join(root, filename)
                if DEBUG:
                    print(f"[调试] 正在检查: {full_path}")
                py_files += 1
                c = count_classes_in_file(full_path)
                total_classes += c

    used_class = total_classes > 0
    return {
        "folder": folder_name,                 # 原始文件夹名
        "student_name_raw": student_name_raw,  # 文件夹里的名字
        "student_name": student_name_correct,  # 纠正后的正式姓名（来自 Excel）
        "team_parsed": team_parsed,            # 从文件夹名解析出的组别（如 "Team 26"）
        "team_from_excel": team_from_excel,    # 从 Excel 读取的组号（纯数字字符串）
        "used_class": used_class,
        "class_count": total_classes,
        "py_files": py_files,
    }


def main():
    # 先从 Excel 读取“姓名 + 分组”
    load_correct_names_from_excel(EXCEL_NAME_FILE)

    results = []

    # 遍历作业根目录下的每个“学生文件夹”
    for folder_name in sorted(os.listdir(HOMEWORK_ROOT)):
        student_path = os.path.join(HOMEWORK_ROOT, folder_name)
        if not os.path.isdir(student_path):
            # 不是文件夹就跳过（比如杂散的文件）
            continue

        info = check_student_dir(folder_name, student_path)
        results.append(info)

        print(
            f"目录: {info['folder']}\n"
            f"  文件夹姓名: {info['student_name_raw']}\n"
            f"  表格姓名:   {info['student_name']}\n"
            f"  组别(文件夹): {info['team_parsed'] or '未知'}\n"
            f"  组别(Excel):   {info['team_from_excel'] or '未知'}\n"
            f"  是否使用class -> {info['used_class']}\n"
            f"  class数量: {info['class_count']}, "
            f"py文件数: {info['py_files']}\n"
        )

    # 导出 CSV，方便用 Excel 打开
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "folder",            # 原始文件夹名
                "student_name_raw",  # 文件夹里的名字
                "student_name",      # 纠正后的正式姓名（来自 Excel）
                "team_parsed",       # 从文件夹名解析出的组别（Team 26 / Group 11 等）
                "team_from_excel",   # Excel 中的分组编号（仅数字）
                "used_class",
                "class_count",
                "py_files",
            ],
        )
        writer.writeheader()
        writer.writerows(results)

    print(f"\n检测完成，结果已保存到: {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
