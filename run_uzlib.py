import os
import re
import json
import time
import pandas as pd
from tqdm import tqdm
from tabulate import tabulate
from datasets import load_dataset
from argparse import ArgumentParser

from utils import get_client

def send_request(prompt, model_name):
    client = get_client(model_name)
    try:
        response = client.chat.completions.create(
            model=model_name,
            # n=1,
            temperature = 1,
            top_p = 0.95,
            max_completion_tokens = 100,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return response.choices[0].message.content
    
    except ValueError as e:
        print(f"Value Error: {str(e)}")
        return None
    
    except Exception as e:
        print(f"Exception: {str(e)}")
        return None
    
def extract_answer(response_text):
    if not isinstance(response_text, str) or not response_text.strip():
        return None
    
    response_text = response_text.replace('**', '')
    
    patterns = [
        r'^\s*([ABCD])\s*$',
        r'javob:\s*([ABCD])\)',
        r'javob\s*([ABCD])\)',
        r'variant:?\s*([ABCD])\)',
        r'([ABCD])\).*to\'g\'ri',
        r'([ABCD])\).',
        r'\s([ABCD])\s.*to\'g\'ri'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, response_text, re.IGNORECASE)
        if match:
            return match.group(1)
    
    return None

def calculate_accuracy(df, drop_none=False):
    if drop_none:
        df = df.dropna(subset=['extracted_answer'], ignore_index=True)

    result = {}
    result['all'] = sum(df['answer']==df['extracted_answer'])/len(df)

    for qtype in ['correct_word', 'meaning', 'meaning_in_context', 'fill_in']:
        df_mini = df[df['type']==qtype]
        if  not df_mini.empty:
            result[qtype] = sum(df_mini['answer']==df_mini['extracted_answer'])/len(df_mini)

    return result

def main(model_name, MAX_RETRIES):
    uzlib = load_dataset('murodbek/uzlib', split='all')
    df = uzlib.to_pandas()

    artifact_name = f"artifacts/{model_name.split('/')[-1]}.jsonl"

    with open(artifact_name, "w") as file:
        for i, row in tqdm(df.iterrows(), total=len(df), desc=model_name):
            num_tries = 0
            extracted_answer = None
            
            prompt = f"{row['question']}\nA) {row['option_a']}\nB) {row['option_b']}\nC) {row['option_c']}\nD) {row['option_d']}\n\nJavob: "
            while num_tries < MAX_RETRIES and extracted_answer == None:
                response_txt = send_request(prompt, model_name)
                extracted_answer = extract_answer(response_txt)

                num_tries += 1

            file.write(json.dumps({'id': row['id'], 'response': response_txt, 'extracted_answer': extracted_answer})+'\n')

    df_result = pd.read_json(artifact_name, lines=True)
    df_all = df.merge(df_result, on=['id'])

    accuracy = calculate_accuracy(df_all)
    accuracy_data = list(accuracy.items())
    print(tabulate(accuracy_data, headers=['Question Type', 'Accuracy'], tablefmt='pretty'))


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--model_name", type=str, required=True)
    parser.add_argument("--max_retries", type=int, default=3)

    args = parser.parse_args()
    main(args.model_name, args.max_retries)