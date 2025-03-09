import os
import pandas as pd
from datasets import load_dataset
from tabulate import tabulate

from run_uzlib import extract_answer, calculate_accuracy

human_baseline = {
    'model_name': 'Human voters＊',
    'all': 0.5894,
    'correct_word': 0.6054,
    'meaning': 0.5247,
    'meaning_in_context': 0.5254,
    'fill_in': 0.5094
}

random_baseline = {
    'model_name': 'Random Baseline',
    'all': 0.25,
    'correct_word': 0.25,
    'meaning': 0.25,
    'meaning_in_context': 0.25,
    'fill_in': 0.25
}

def generate_leaderboard():
    if not os.path.exists('artifacts/'):
        print("Error: 'artifacts' directory not found.")
        return None
        
    available_models = [file for file in sorted(os.listdir('artifacts/')) 
                        if file.endswith(".jsonl")]
        
    print(f"Found {len(available_models)} model results.")
    
    uzlib = load_dataset('murodbek/uzlib', split='all')
    df_original = uzlib.to_pandas()
    expected_rows = len(df_original)
    print(f"Loaded dataset with {expected_rows} questions.")
    
    accuracy_info = []
    skipped_models = []

    for model_name in available_models:
        try:
            df = pd.read_json(f"artifacts/{model_name}", lines=True)
            
            if len(df) != expected_rows:
                print(f"Skipping {model_name}: Expected {expected_rows} rows, found {len(df)}")
                skipped_models.append(model_name)
                continue
            
            df['extracted_answer'] = df['response'].apply(extract_answer)
            
            df_result = df_original.merge(df, on=['id'])
            
            accuracy = calculate_accuracy(df_result)
            model_display_name = model_name[:-6]  # Remove .jsonl extension
            accuracy['model_name'] = model_display_name
            
            accuracy_info.append(accuracy)
            
        except Exception as e:
            print(f"Error processing {model_name}: {str(e)}")
            skipped_models.append(model_name)
    
    if not accuracy_info:
        print("No valid model results found.")
        return None
    
    df = pd.DataFrame(accuracy_info)
    columns = ['model_name', 'all', 'correct_word', 'meaning', 'meaning_in_context', 'fill_in']
    df = df[columns]

    df = pd.concat([df, pd.DataFrame([human_baseline, random_baseline])], ignore_index=True)

    df = df.sort_values(by='all', ascending=False).reset_index(drop=True)
    
    for col in df.columns:
        if col != 'model_name':
            df[col] = df[col].apply(lambda x: f"{x:.4f}")
    
    # Save the leaderboard
    # df.to_csv("uzlib_leaderboard.csv", index=False)

    with open("LEADERBOARD.md", "w") as f:
        f.write("# UzLiB Leaderboard\n\n")
        f.write(tabulate(df.values.tolist(), headers=df.columns, tablefmt="pipe"))
        f.write("\n\n* Human voters score is not the average of humans doing all the questions but the average of average accurate answers for each question. Also, note that random baseline for humans is 0.4229 due to variable number of options (2-3) in the original questions.")
    print("Leaderboard saved to LEADERBOARD.md")
    
    # Print the leaderboard
    print("\n=== UzLiB Leaderboard ===\n")
    print(tabulate(df.values.tolist(), headers=df.columns, tablefmt="grid"))
    
    return df

if __name__ == "__main__":
    generate_leaderboard()