import json
import csv
import codecs

def clean_text(text):
    """清理文本，将换行符替换为空格"""
    if isinstance(text, str):
        return ' '.join(text.splitlines())
    return text

def json_to_csv(json_file_path, csv_file_path):
    try:
        # 读取JSON文件
        with open(json_file_path, 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
        
        # 确保数据是列表形式
        if not isinstance(data, list):
            data = [data]
        
        if not data:
            print("JSON文件为空")
            return
        
        # 获取所有字段名，添加序号列
        fields = set()
        for item in data:
            fields.update(item.keys())
        fields = list(fields)
        fields.insert(0, '序号')  # 在最前面添加序号列
        
        # 创建CSV文件，使用UTF-8-BOM编码
        with codecs.open(csv_file_path, 'w', encoding='utf-8-sig') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fields)
            
            # 写入表头
            writer.writeheader()
            
            # 写入数据
            for index, item in enumerate(data, 1):
                # 清理所有文本字段中的换行符
                cleaned_item = {k: clean_text(v) for k, v in item.items()}
                # 添加序号
                cleaned_item['序号'] = index
                writer.writerow(cleaned_item)
                
        print(f"转换成功！CSV文件已保存至: {csv_file_path}")
        
    except Exception as e:
        print(f"转换过程中出错: {str(e)}")

if __name__ == "__main__":
    # 示例使用
    json_file_path = "input.json"  # 输入的JSON文件路径
    csv_file_path = "output.csv"   # 输出的CSV文件路径
    
    json_to_csv(json_file_path, csv_file_path)
