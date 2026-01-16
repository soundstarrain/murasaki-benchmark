"""
清理 results/models 目录下的JSONL文件
移除 source_file 和 avg_score 字段
"""
import os
import json

def clean_jsonl_file(file_path):
    """清理单个JSONL文件"""
    # 先读取所有内容
    cleaned_lines = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                # 移除不需要的字段
                data.pop('source_file', None)
                data.pop('avg_score', None)
                cleaned_lines.append(json.dumps(data, ensure_ascii=False))
            except json.JSONDecodeError as e:
                print(f"  警告: 跳过无效JSON行: {e}")
                continue
    
    # 写入清理后的内容
    with open(file_path, 'w', encoding='utf-8') as f:
        for line in cleaned_lines:
            f.write(line + '\n')
    
    return len(cleaned_lines)

def main():
    models_dir = 'results/models'
    
    if not os.path.exists(models_dir):
        print(f"错误: 目录 {models_dir} 不存在")
        return
    
    total_files = 0
    total_records = 0
    
    for model_name in os.listdir(models_dir):
        model_path = os.path.join(models_dir, model_name)
        if not os.path.isdir(model_path):
            continue
        
        for file_name in os.listdir(model_path):
            if not file_name.endswith('.jsonl'):
                continue
            
            file_path = os.path.join(model_path, file_name)
            print(f"处理: {file_path}")
            
            try:
                count = clean_jsonl_file(file_path)
                print(f"  已清理 {count} 条记录")
                total_files += 1
                total_records += count
            except Exception as e:
                print(f"  错误: {e}")
    
    print(f"\n完成! 共处理 {total_files} 个文件, {total_records} 条记录")

if __name__ == '__main__':
    main()
