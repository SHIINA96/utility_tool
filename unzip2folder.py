import os
import zipfile

# 要批量解压的目录，改成你自己的路径
BASE_DIR = r"/Users/barney/Documents/utility_tool/test_demo"   # 比如：r"C:\Users\你\Desktop\作业"

def batch_unzip(base_dir):
    for name in os.listdir(base_dir):
        file_path = os.path.join(base_dir, name)

        # 只处理 zip 文件
        if os.path.isfile(file_path) and name.lower().endswith(".zip"):
            folder_name = os.path.splitext(name)[0]  # 去掉 .zip
            extract_dir = os.path.join(base_dir, folder_name)

            # 创建同名文件夹
            os.makedirs(extract_dir, exist_ok=True)

            print(f"正在解压: {name} -> {extract_dir}")
            with zipfile.ZipFile(file_path, "r") as zf:
                zf.extractall(extract_dir)

    print("全部解压完成。")

if __name__ == "__main__":
    batch_unzip(BASE_DIR)
