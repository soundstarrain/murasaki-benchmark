
import pandas as pd
import os

def generate_report():
    csv_path = r"e:\project\benchmark\results\models\cleaning_summary.csv"
    if not os.path.exists(csv_path):
        print("Summary CSV not found.")
        return

    df = pd.read_csv(csv_path)
    
    # Pivot to get Short and Long valid counts per model
    # We need to identify Short/Long from 'File' column
    
    models = df['Model'].unique()
    rows = []
    
    for model in models:
        model_df = df[df['Model'] == model]
        
        # Initialize
        short_valid = 0
        short_total = 0
        long_valid = 0
        long_total = 0
        
        for _, row in model_df.iterrows():
            fname = row['File'].lower()
            valid = row['Valid']
            total = row['Total']
            
            if 'short' in fname:
                short_valid = valid
                short_total = total
            elif 'long' in fname:
                long_valid = valid
                long_total = total
            else:
                # Fallback for models with single file or different naming (e.g. TranslateGemma)
                # If total is around 200, it might be combined?
                # Or check raw filenames
                if total == 200:
                    # Likely combined
                    short_valid = valid // 2 # Approximation if exact split unknown, or just report total
                    short_total = total // 2
                    long_valid = valid - short_valid
                    long_total = total - short_total
                else:
                    # Treat as undefined or accumulate
                    short_valid += valid
                    short_total += total
        
        total_valid = short_valid + long_valid
        total_count = short_total + long_total
        valid_rate = (total_valid / total_count * 100) if total_count > 0 else 0
        
        rows.append({
            "Model": model,
            "Short": f"{short_valid}/{short_total}",
            "Long": f"{long_valid}/{long_total}",
            "Valid Rate": f"{valid_rate:.1f}%"
        })
    
    # Sort by Valid Rate (descending)
    res_df = pd.DataFrame(rows)
    # Extract numerical rate for sorting
    res_df['sort_key'] = res_df['Valid Rate'].apply(lambda x: float(x.strip('%')))
    res_df = res_df.sort_values(by='sort_key', ascending=False).drop(columns=['sort_key'])
    
    # Print Markdown Table
    print("\n### Data Quality Report\n")
    print(res_df.to_markdown(index=False))

if __name__ == "__main__":
    generate_report()
