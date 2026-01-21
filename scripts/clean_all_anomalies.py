
import json
import os
import glob
import shutil
import re
import pandas as pd

def restore_backups(base_dir):
    print(f"Checking for backups to restore in {base_dir}...")
    restored_count = 0
    
    # Recursively find all .bak files
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith(".bak"):
                bak_path = os.path.join(root, file)
                original_path = bak_path[:-4] # Remove .bak
                
                # Restore: overwrite original with backup
                shutil.copy2(bak_path, original_path)
                # Remove backup after restore (optional, but cleaner for a fresh start)
                os.remove(bak_path)
                restored_count += 1
                
    print(f"Restored {restored_count} files from backups.\n")

def clean_anomalies(base_dir):
    # 1. Restore state first
    restore_backups(base_dir)

    print(f"Starting Cleaning Process in {base_dir}...\n")
    
    model_dirs = [d for d in glob.glob(os.path.join(base_dir, "*")) if os.path.isdir(d)]
    
    stats = []
    
    # 2. Analyze and Process
    for model_dir in model_dirs:
        model_name = os.path.basename(model_dir)
        jsonl_files = glob.glob(os.path.join(model_dir, "*.jsonl"))
        
        for filepath in jsonl_files:
            filename = os.path.basename(filepath)
            
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            cleaned_lines = []
            removed_empty = 0
            removed_short = 0
            removed_long = 0
            removed_kana = 0
            removed_invalid = 0
            
            total_items = 0
            
            for line in lines:
                params_line = line.strip()
                if not params_line:
                    continue
                
                total_items += 1
                keep = True
                
                try:
                    item = json.loads(params_line)
                    
                    # Pre-processing: Remove all spaces
                    if 'src' in item:
                        item['src'] = item['src'].replace(" ", "")
                    if 'ref' in item:
                        item['ref'] = item['ref'].replace(" ", "")
                    if 'model_output' in item:
                        item['model_output'] = item['model_output'].replace(" ", "")

                    src = item.get('src', '')
                    model_output = item.get('model_output', '')
                    
                    # Check 1: Empty output
                    if not model_output:
                        removed_empty += 1
                        keep = False
                    
                    # Check 2: Kana Count > 20
                    if keep:
                        kana_count = len(re.findall(r'[\u3040-\u309F\u30A0-\u30FF]', model_output))
                        if kana_count > 20:
                            removed_kana += 1
                            keep = False
                            
                    # Check 3/4: Length Ratio
                    if keep:
                        src_len = len(src)
                        out_len = len(model_output)
                        
                        if src_len == 0:
                            removed_empty += 1 # Treat empty source as empty/invalid
                            keep = False
                        else:
                            ratio = out_len / src_len
                            if ratio < 0.1:
                                removed_short += 1
                                keep = False
                            elif ratio > 4.0:
                                removed_long += 1
                                keep = False
                    
                    if keep:
                        cleaned_lines.append(item)
                        
                except json.JSONDecodeError:
                    removed_invalid += 1
                    continue
            
            
            removed_total = removed_empty + removed_short + removed_long + removed_kana + removed_invalid
            valid_count = total_items - removed_total
            
            # Save Stats
            if removed_total >= 0: # Always add to stats to show valid count even if 0 removed
                stats.append({
                    "Model": model_name,
                    "File": filename,
                    "Total": total_items,
                    "Valid": valid_count,
                    "Removed": removed_total,
                    "Empty": removed_empty,
                    "Short(<0.1)": removed_short,
                    "Long(>4.0)": removed_long,
                    "Kana(>20)": removed_kana
                })
                
                # 3. Save Cleaned File
                backup_path = filepath + ".bak"
                shutil.copy2(filepath, backup_path)
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    for item in cleaned_lines:
                        f.write(json.dumps(item, ensure_ascii=False) + "\n")

    # 4. Print Summary Table
    print("\n" + "="*80)
    print("DATA CLEANING SUMMARY REPORT")
    print("="*80)
    
    if len(stats) == 0:
        print("No files processed.")
    else:
        df_stats = pd.DataFrame(stats)
        # Arrange columns
        cols = ["Model", "File", "Total", "Valid", "Removed", "Empty", "Short(<0.1)", "Long(>4.0)", "Kana(>20)"]
        print(df_stats[cols].to_string(index=False))
        
        # Save summary to file
        df_stats.to_csv(os.path.join(base_dir, "cleaning_summary.csv"), index=False)
        print(f"\nSummary saved to {os.path.join(base_dir, 'cleaning_summary.csv')}")

if __name__ == "__main__":
    clean_anomalies(r"e:\project\benchmark\results\models")
