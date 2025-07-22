import re
import json
import pandas as pd
from tqdm import tqdm
from tabulate import tabulate
from datasets import load_dataset
from argparse import ArgumentParser
import concurrent.futures

from utils import send_request

def extract_answer(response_text: str):
    if not isinstance(response_text, str) or not response_text.strip():
        return None
    
    # Remove markdown formatting that might interfere with regex
    response_text = response_text.replace('**', '')
    
    # Patterns to match different answer formats
    patterns = [
        r'^\s*([ABCD])\s*$',                  # Just A, B, C, or D
        r'javob:\s*([ABCD])\)',               # javob: A)
        r'javob\s*([ABCD])\)',                # javob A)
        r'variant:?\s*([ABCD])\)',            # variant: A)
        r'([ABCD])\).*to\'g\'ri',             # A) ... to'g'ri
        r'([ABCD])\).',                       # A).
        r'\s([ABCD])\s.*to\'g\'ri',           # A ... to'g'ri
    ]
    
    for pattern in patterns:
        match = re.search(pattern, response_text, re.IGNORECASE)
        if match:
            return match.group(1).upper()  # Ensure uppercase for consistency
    
    # If no patterns match, try to find any standalone A, B, C, or D
    standalone = re.search(r'\b([ABCD])\b', response_text)
    if standalone:
        return standalone.group(1).upper()
    
    return None

def calculate_accuracy(df: pd.DataFrame, drop_none: bool = False):
    if drop_none:
        df = df.dropna(subset=['extracted_answer'], ignore_index=True)

    result = {}
    n = len(df)
    result['all'] = (df['answer'] == df['extracted_answer']).sum() / n if n else 0.0

    for qtype in ['correct_word', 'meaning', 'meaning_in_context', 'fill_in']:
        dfm = df[df['type'] == qtype]
        m = len(dfm)
        result[qtype] = (dfm['answer'] == dfm['extracted_answer']).sum() / m if m else 0.0

    return result

def process_row(row, model_name: str, max_retries: int):
    prompt = f"{row['question']}\nA) {row['option_a']}\nB) {row['option_b']}\nC) {row['option_c']}\nD) {row['option_d']}\n\nJavob: "
    
    tries = 0
    response_txt = None
    extracted = None
    while tries < max_retries and extracted is None:
        response_txt = send_request(prompt, model_name)
        if response_txt:
            extracted = extract_answer(response_txt)
        tries += 1

    return {
        'id': row['id'],
        'response': response_txt,
        'extracted_answer': extracted
    }

def main(model_name: str, max_retries: int, num_workers: int):
    uzlib = load_dataset('tahrirchi/uzlib', split='all')
    df = uzlib.to_pandas()

    artifact_name = f"artifacts/{model_name.split('/')[-1]}.jsonl"

    # Open file once for writing; main thread will append as futures complete.
    with open(artifact_name, 'w') as fout, \
         concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:

        futures = {
            executor.submit(process_row, row, model_name, max_retries): row['id']
            for _, row in df.iterrows()
        }

        # As each future completes, write its result
        for f in tqdm(
            concurrent.futures.as_completed(futures),
            total=len(futures),
            desc=f"Running {model_name}"
        ):
            try:
                res = f.result()
            except Exception as e:
                # In case of unexpected error, write a placeholder
                rid = futures[f]
                res = {'id': rid, 'response': None, 'extracted_answer': None}
            fout.write(json.dumps(res) + '\n')

    # Load results and compute accuracy
    df_res = pd.read_json(artifact_name, lines=True)
    df_all = df.merge(df_res, on='id')
    accuracy = calculate_accuracy(df_all)
    accuracy_data = list(accuracy.items())

    print(f"\nResults for {model_name}:")
    print(tabulate(accuracy_data, headers=['Question Type', 'Accuracy'],
                   tablefmt='pretty'))

if __name__ == "__main__":
    parser = ArgumentParser(description="Run UzLiB benchmark on a specific model")
    parser.add_argument("--model_name", type=str, required=True, help="Name of the model to benchmark")
    parser.add_argument("--max_retries", type=int, default=3, help="Maximum number of retries for each question")
    parser.add_argument("--num_workers", type=int, default=4, help="Number of parallel workers")

    args = parser.parse_args()
    main(args.model_name, args.max_retries, args.num_workers)