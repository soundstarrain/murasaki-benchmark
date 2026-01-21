import json
import os
import glob
import re

def detect_anomalies(base_dir):
    print(f"Scanning for anomalies in {base_dir}...")
    print("Criteria: Empty | Length Ratio < 0.1 or > 4.0 | Safety Refusal | Kana > 20 | (Spaces removed for checks)\n")
    
    # regex for japanese hiragana/katakana
    kana_pattern = re.compile(r'[\u3040-\u309F\u30A0-\u30FF]')
    
    # Find all model directories
    model_dirs = [d for d in glob.glob(os.path.join(base_dir, "*")) if os.path.isdir(d)]
    
    total_issues = 0
    issues_by_model = {}

    print(f"{'Model':<30} | {'File':<20} | {'Line':<5} | {'Issue':<20} | {'Details'}")
    print("-" * 100)

    for model_dir in model_dirs:
        model_name = os.path.basename(model_dir)
        jsonl_files = glob.glob(os.path.join(model_dir, "*.jsonl"))
        
        for filepath in jsonl_files:
            filename = os.path.basename(filepath)
            # Skip backup files if any
            if filename.endswith(".bak"):
                continue

            with open(filepath, 'r', encoding='utf-8') as f:
                line_num = 0
                for line in f:
                    line_num += 1
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        item = json.loads(line)
                        src = item.get('src', '')
                        model_output = item.get('model_output', '')
                        
                        # Pre-processing: Remove all spaces for accurate checking
                        src_clean = src.replace(" ", "")
                        out_clean = model_output.replace(" ", "")

                        # Check 1: Empty output (after stripping spaces)
                        if not out_clean:
                            print(f"{model_name[:30]:<30} | {filename[:20]:<20} | {line_num:<5} | {'Empty Output':<20} | Src len: {len(src_clean)}")
                            total_issues += 1
                            issues_by_model[model_name] = issues_by_model.get(model_name, 0) + 1
                            continue
                        
                        # Check 2: Excessive Japanese Kana (> 20 chars) - Likely failed translation
                        kana_count = len(kana_pattern.findall(out_clean))
                        if kana_count > 20:
                            print(f"{model_name[:30]:<30} | {filename[:20]:<20} | {line_num:<5} | {'Excessive Kana':<20} | Count: {kana_count}")
                            total_issues += 1
                            issues_by_model[model_name] = issues_by_model.get(model_name, 0) + 1
                            continue

                        src_len = len(src_clean)
                        out_len = len(out_clean)

                        if src_len == 0:
                            print(f"{model_name[:30]:<30} | {filename[:20]:<20} | {line_num:<5} | {'Empty Source':<20} | -")
                            total_issues += 1
                            issues_by_model[model_name] = issues_by_model.get(model_name, 0) + 1
                            continue
                        
                        ratio = out_len / src_len
                        
                        # Check 3: Too short (Ratio < 0.1)
                        if ratio < 0.1:
                            print(f"{model_name[:30]:<30} | {filename[:20]:<20} | {line_num:<5} | {'Too Short':<20} | Ratio: {ratio:.2f}, Out: {model_output[:20]}...")
                            total_issues += 1
                            issues_by_model[model_name] = issues_by_model.get(model_name, 0) + 1
                            continue
                        
                        # Check 4: Too long (Ratio > 4.0)
                        if ratio > 4.0:
                             print(f"{model_name[:30]:<30} | {filename[:20]:<20} | {line_num:<5} | {'Too Long':<20} | Ratio: {ratio:.2f}")
                             total_issues += 1
                             issues_by_model[model_name] = issues_by_model.get(model_name, 0) + 1
                             continue

                    except json.JSONDecodeError:
                        print(f"{model_name[:30]:<30} | {filename[:20]:<20} | {line_num:<5} | {'Invalid JSON':<20} | -")
                        continue
    
    print("-" * 100)
    print(f"\nScan Complete. Total Issues Found: {total_issues}")
    if total_issues > 0:
        print("\nIssues by Model:")
        for model, count in sorted(issues_by_model.items(), key=lambda x: x[1], reverse=True):
            print(f"  - {model}: {count} issues")
    else:
        print("No anomalies found based on current criteria.")

if __name__ == "__main__":
    detect_anomalies(r"e:\project\benchmark\results\models")
