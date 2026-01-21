
import pandas as pd
import os

def generate_leaderboards():
    csv_path = r"e:\project\benchmark\results\final_comet_scores.csv"
    if not os.path.exists(csv_path):
        print("Scores CSV not found.")
        return

    df = pd.read_csv(csv_path)

    # Long Leaderboard
    df_long = df.sort_values(by='Long_comet', ascending=False).reset_index(drop=True)
    df_long['Rank'] = df_long.index + 1
    
    # Short Leaderboard
    df_short = df.sort_values(by='Short_comet', ascending=False).reset_index(drop=True)
    df_short['Rank'] = df_short.index + 1

    def format_rank(rank):
        if rank == 1: return "🥇"
        if rank == 2: return "🥈"
        if rank == 3: return "🥉"
        return str(rank)

    print("\n### Long Text Leaderboard\n")
    print("| Rank | Model | Long Score |")
    print("|:----:|:------|:----------:|")
    for _, row in df_long.iterrows():
        rank_icon = format_rank(row['Rank'])
        model_name = f"**{row['model_name']}**" if row['Rank'] <= 3 else row['model_name']
        long_score = f"**{row['Long_comet']:.4f}**" if row['Rank'] <= 3 else f"{row['Long_comet']:.4f}"
        print(f"| {rank_icon} | {model_name} | {long_score} |")

    print("\n### Short Text Leaderboard\n")
    print("| Rank | Model | Short Score |")
    print("|:----:|:------|:-----------:|")
    for _, row in df_short.iterrows():
        rank_icon = format_rank(row['Rank'])
        model_name = f"**{row['model_name']}**" if row['Rank'] <= 3 else row['model_name']
        short_score = f"**{row['Short_comet']:.4f}**" if row['Rank'] <= 3 else f"{row['Short_comet']:.4f}"
        print(f"| {rank_icon} | {model_name} | {short_score} |")

if __name__ == "__main__":
    generate_leaderboards()
