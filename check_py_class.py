import os
import ast
import csv
import re

# ================== Settings ==================

# Root directory of student homework: one subfolder per student
# e.g.: r"/Users/barney/Documents/utility_tool/homework_root"
HOMEWORK_ROOT = r"/Users/barney/Documents/utility_tool/test_demo"

# Output CSV filename
OUTPUT_CSV = "class_usage_result.csv"

# Excel file that contains "correct name + group number"
EXCEL_NAME_FILE = r"./2025 S2 TA Marking.xlsx"

# Exclude venv and system DB folder from counting
EXCLUDED_DIRS = ("__pycache__", ".git", ".idea", ".vscode", "__MACOSX")

# print checked .py file path
DEBUG = False

# ============= variables: names & group info =============

CORRECT_NAMES = []           # Name list (second column in Excel)
CORRECT_NAMES_SLUG = []      # Corresponding slug (for matching)
CORRECT_GROUPS = []          # group number (first column in Excel, numeric string)）


# ================== Functions ==================


def slugify_name(name: str) -> str:
    """
    parse name to a slug for matching
      eg：'Martin Kalanda-Phiri' -> 'martinkalandaphriri'
    """
    name = name.lower()
    # letters only
    return re.sub(r"[^a-z]", "", name)


def load_correct_names_from_excel(path: str):
    """
    read correct student names and groups from Excel file
      CORRECT_NAMES, CORRECT_NAMES_SLUG, CORRECT_GROUPS

    eg:
      Column A: group number
      Column B: student name
    Row range: A8:B102
    """
    global CORRECT_NAMES, CORRECT_NAMES_SLUG, CORRECT_GROUPS

    if not os.path.exists(path):
        print(f"[info] cannot find Excel file: {path}, skip name and group number correction")
        return

    try:
        import pandas as pd
    except ImportError:
        print("[info] pandas not installed, cannot read name and groun number from Excel")
        print("      please run: pip install pandas openpyxl")
        return

    try:
        # read first sheet in range A8:B102
        df = pd.read_excel(path, sheet_name=0, header=None)
        # A8:B102 -> row indices 7~101, column 0 is group number, column 1 is name
        sub = df.iloc[7:102, 0:2]
    except Exception as e:
        print(f"[info] can't read Excel file: {e}")
        print("      skip name and group number correction")
        return

    CORRECT_NAMES = []
    CORRECT_NAMES_SLUG = []
    CORRECT_GROUPS = []

    for _, row in sub.iterrows():
        group_val = row.iloc[0]
        name_val = row.iloc[1]

        # parse name: must be non-empty string
        if isinstance(name_val, str):
            name = name_val.strip()
        else:
            continue
        if not name:
            continue

        # parse group number: convert to string
        if pd.isna(group_val):
            group = ""
        elif isinstance(group_val, (int, float)):
            group = str(int(group_val))
        else:
            group = str(group_val).strip()

        CORRECT_NAMES.append(name)
        CORRECT_NAMES_SLUG.append(slugify_name(name))
        CORRECT_GROUPS.append(group)

    print(f"[info] read {len(CORRECT_NAMES)} student names and group ID for match")


def match_correct_name_and_group(raw_student_name: str):
    """
    find studnet name from CANVAS folder as raw_student_name,
      eg: 'alshammarikhlaf',
    find a match in excel, if not found, return (raw_student_name, "")
    """
    if not CORRECT_NAMES:
        return raw_student_name, ""

    from difflib import SequenceMatcher

    raw_slug = slugify_name(raw_student_name)
    if not raw_slug:
        return raw_student_name, ""

    # 1) check slug contains or is contained by
    for name, name_slug, group in zip(CORRECT_NAMES, CORRECT_NAMES_SLUG, CORRECT_GROUPS):
        if not name_slug:
            continue
        if raw_slug in name_slug or name_slug in raw_slug:
            return name, group

    # 2) fuzzy match by ratio
    best_ratio = 0.0
    best_idx = -1
    for i, name_slug in enumerate(CORRECT_NAMES_SLUG):
        if not name_slug:
            continue
        ratio = SequenceMatcher(None, raw_slug, name_slug).ratio()
        if ratio > best_ratio:
            best_ratio = ratio
            best_idx = i

    if best_idx >= 0 and best_ratio >= 0.5:   # adjust threshold as needed
        return CORRECT_NAMES[best_idx], CORRECT_GROUPS[best_idx]

    return raw_student_name, ""


def parse_folder_name(folder_name: str):
    """
    parse folder name, and return:
        (student_name_raw, student_name_correct, team_parsed, team_from_excel)

    - student_name_raw: the part before first underscore
    - student_name_correct:  correct name from Excel
    - team_parsed: try to read group number from folder name
    - team_from_excel: group number from Excel
    """
    # student name is the part before first underscore
    parts = folder_name.split("_")
    student_name_raw = parts[0] if parts else folder_name

    # use Excel data to correct name + group
    student_name_correct, team_from_excel = match_correct_name_and_group(student_name_raw)

    # match Team_26 / Team26 / team24 / group16 / Group_11 / Group 24 etc
    m = re.search(r"(team|group)[ _]?(\d+)", folder_name, re.IGNORECASE)
    if m:
        group_word = m.group(1).capitalize()  # unify to Team / Group
        group_num = m.group(2)
        team_parsed = f"{group_word} {group_num}"
    else:
        team_parsed = ""

    return student_name_raw, student_name_correct, team_parsed, team_from_excel


def count_classes_in_file(py_file: str) -> int:
    # count class definitions in a .py file
    try:
        with open(py_file, "r", encoding="utf-8") as f:
            source = f.read()
    except UnicodeDecodeError:
        # deal with gbk (Chinese) encoding files
        with open(py_file, "r", encoding="gbk", errors="ignore") as f:
            source = f.read()

    # skip empty files
    if "\x00" in source:
        print(f"[warning] empty file, skip:{py_file}")
        return 0

    try:
        tree = ast.parse(source)
    except (SyntaxError, ValueError) as e:
        print(f"[warning] unable to parse({e.__class__.__name__}):{py_file}")
        return 0

    # count class definitions
    count = sum(isinstance(node, ast.ClassDef) for node in ast.walk(tree))
    return count


def check_student_dir(folder_name: str, student_path: str) -> dict:
    """
    conut how many classes in all .py files under student_path
    parse student name
    """
    (
        student_name_raw,
        student_name_correct,
        team_parsed,
        team_from_excel,
    ) = parse_folder_name(folder_name)

    total_classes = 0
    py_files = 0

    # os.walk iterate all files under student_path
    for root, dirs, files in os.walk(student_path):
        dirs[:] = [
            d for d in dirs
            if d not in EXCLUDED_DIRS and "env" not in d.lower()
        ]

        for filename in files:
            if filename.endswith(".py"):
                full_path = os.path.join(root, filename)
                if DEBUG:
                    print(f"[debug] checking: {full_path}")
                py_files += 1
                c = count_classes_in_file(full_path)
                total_classes += c

    used_class = total_classes > 0
    return {
        "folder": folder_name,                 # Original folder name
        "student_name_raw": student_name_raw,  # Name from folder
        "student_name": student_name_correct,  # Corrected official name (from Excel)
        "team_parsed": team_parsed,            # Group parsed from folder name (e.g. "Team 26")
        "team_from_excel": team_from_excel,    # Group number read from Excel (numeric string)
        "used_class": used_class,
        "class_count": total_classes,
        "py_files": py_files,
    }


def main():
    # Read "name + group" from Excel
    load_correct_names_from_excel(EXCEL_NAME_FILE)

    results = []

    # Iterate "student folder" under the homework root
    for folder_name in sorted(os.listdir(HOMEWORK_ROOT)):
        student_path = os.path.join(HOMEWORK_ROOT, folder_name)
        if not os.path.isdir(student_path):
            # Skip if it is not a folder
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

    # Export CSV 
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "folder",            # Original folder name
                "student_name_raw",  # Name from folder
                "student_name",      # Corrected official name (from Excel)
                "team_parsed",       # Group parsed from folder name (Team 26 / Group 11 etc.)
                "team_from_excel",   # Group number in Excel (digits only)
                "used_class",
                "class_count",
                "py_files",
            ],
        )
        writer.writeheader()
        writer.writerows(results)

    print(f"\ncounting complete, results saved into: {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
