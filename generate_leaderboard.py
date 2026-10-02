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

def norm_key(name: str):
    """Normalize a model name for matching display rows to artifacts.

    Leaderboard display names use spaces and mixed case ('GPT 5.2'),
    while artifact files use hyphens and lowercase ('gpt-5.2').
    """
    import re
    return re.sub(r'[\s_\-]+', '', name).lower()


def parse_leaderboard(path="LEADERBOARD.md"):
    """Read the existing leaderboard rows.

    Returns (header_lines, rows, baselines, footer_lines) where each row
    is a dict with keys: raw_cells (list of 7 strings), key (normalized
    model key). Baselines (Human/Random) are returned separately so they
    stay pinned after the ranked models. Returns Nones if the file is
    missing or unparseable.
    """
    import re
    try:
        with open(path, encoding="utf-8") as f:
            lines = f.read().splitlines()
    except FileNotFoundError:
        return None, None, None, None

    header_lines, rows, baselines, footer_lines = [], [], [], []
    in_table = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("|") and "**Model Name**" in stripped:
            in_table = True
            header_lines.append(line)
            continue
        if in_table and stripped.startswith("|") and "---" in stripped:
            header_lines.append(line)
            continue
        if in_table and stripped.startswith("|"):
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            if len(cells) != 7:
                footer_lines.append(line)
                continue
            # Baseline rows: keep verbatim, pinned after ranked models.
            label = cells[0]
            plain = re.sub(r'[\*_]', '', label)
            if "Human voters" in plain or "Random Baseline" in plain:
                baselines.append(line)
                continue
            # Model key: link text if present, else the raw label.
            m = re.search(r'\[([^\]]+)\]', label)
            key = norm_key(m.group(1) if m else re.sub(r'[\*_]', '', label))
            rows.append({"raw_cells": cells, "key": key, "raw": line})
            continue
        if in_table:
            footer_lines.append(line)
        else:
            header_lines.append(line)

    if not rows:
        return None, None, None, None
    return header_lines, rows, baselines, footer_lines


def format_row(cells):
    return "| " + " | ".join(cells) + " |"


def generate_leaderboard():
    if not os.path.exists('artifacts/'):
        print("Error: 'artifacts' directory not found.")
        return None
        
    available_models = [file for file in sorted(os.listdir('artifacts/')) 
                        if file.endswith(".jsonl")]
        
    print(f"Found {len(available_models)} model results.")
    
    uzlib = load_dataset('tahrirchi/uzlib', split='all')
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

    # New scores keyed by normalized artifact name.
    scores = {}
    for _, r in df.iterrows():
        scores[norm_key(r['model_name'])] = {
            'all': f"{r['all']:.4f}",
            'correct_word': f"{r['correct_word']:.4f}",
            'meaning': f"{r['meaning']:.4f}",
            'meaning_in_context': f"{r['meaning_in_context']:.4f}",
            'fill_in': f"{r['fill_in']:.4f}",
            'raw_name': r['model_name'],
        }

    # Merge with the existing leaderboard: refresh score cells in place,
    # keep display name / organization / link cells untouched, never drop
    # rows, and append truly new models as minimal rows.
    header_lines, existing, baselines, footer_lines = parse_leaderboard()
    if header_lines is None:
        # No parseable leaderboard: fall back to the old full rewrite.
        df = pd.concat([df, pd.DataFrame([human_baseline, random_baseline])], ignore_index=True)
        df = df.sort_values(by='all', ascending=False).reset_index(drop=True)
        for col in df.columns:
            if col != 'model_name':
                df[col] = df[col].apply(lambda x: f"{x:.4f}")
        with open("LEADERBOARD.md", "w") as f:
            f.write("# UzLiB Leaderboard\n\n")
            f.write(tabulate(df.values.tolist(), headers=df.columns, tablefmt="pipe"))
            f.write("\n\n* ＊ Human voters score is not the average of humans doing all the questions but the average of accuracy score for each question. Also, note that random baseline for humans is 0.4229 due to variable number of options (2-3) in the original questions.")
        print("\n=== UzLiB Leaderboard ===\n")
        print(tabulate(df.values.tolist(), headers=df.columns, tablefmt="grid"))
        return df

    seen = set()
    for row in existing:
        sc = scores.get(row['key'])
        if sc is None:
            print(f"Keeping {row['raw_cells'][0]} (no fresh artifact, scores untouched)")
            continue
        cells = row['raw_cells']
        cells[2] = sc['all']
        cells[3] = sc['correct_word']
        cells[4] = sc['meaning']
        cells[5] = sc['meaning_in_context']
        cells[6] = sc['fill_in']
        seen.add(row['key'])

    fresh = [(k, v) for k, v in scores.items() if k not in seen]
    for key, sc in fresh:
        print(f"Adding new row for {sc['raw_name']}")
        existing.append({
            "raw_cells": [sc['raw_name'], '-', sc['all'], sc['correct_word'],
                          sc['meaning'], sc['meaning_in_context'], sc['fill_in']],
            "key": key,
            "raw": None,
        })

    def sort_score(row):
        try:
            return float(row['raw_cells'][2].replace('*', ''))
        except ValueError:
            return -1.0

    existing.sort(key=sort_score, reverse=True)

    with open("LEADERBOARD.md", "w", encoding="utf-8") as f:
        f.write("\n".join(header_lines) + "\n")
        for row in existing:
            f.write(format_row(row['raw_cells']) + "\n")
        for line in baselines:
            f.write(line + "\n")
        if footer_lines:
            f.write("\n".join(footer_lines) + ("\n" if not footer_lines[-1].endswith("\n") else ""))

    # Print the leaderboard
    print("\n=== UzLiB Leaderboard ===\n")
    print(tabulate([r['raw_cells'] for r in existing],
                   headers=['Model Name', 'Organization', 'All', 'Correct word',
                            'Meaning', 'Meaning in context', 'Fill in'],
                   tablefmt="grid"))

    return df

if __name__ == "__main__":
    generate_leaderboard()