import re
import json
import pandas as pd
from tqdm import tqdm
from tabulate import tabulate
from datasets import load_dataset
from argparse import ArgumentParser

from utils import get_client

def send_request(prompt: str, model_name: str):
    client = get_client(model_name)
    if client is None:
        return None
        
    try:
        response = client.chat.completions.create(
            model=model_name,
            temperature=1,
            top_p=0.95,
            max_completion_tokens=100,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return response.choices[0].message.content
    
    except ValueError as e:
        print(f"Value Error for {model_name}: {str(e)}")
        return None
    
    except Exception as e:
        print(f"Exception for {model_name}: {str(e)}")
        return None
    
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
    # Overall accuracy
    if len(df) > 0:
        result['all'] = sum(df['answer']==df['extracted_answer'])/len(df)
    else:
        result['all'] = 0.0

    # Accuracy by question type
    for qtype in ['correct_word', 'meaning', 'meaning_in_context', 'fill_in']:
        df_mini = df[df['type']==qtype]
        if not df_mini.empty:
            result[qtype] = sum(df_mini['answer']==df_mini['extracted_answer'])/len(df_mini)
        else:
            result[qtype] = 0.0  # Avoid division by zero

    return result

def main(model_name: str, MAX_RETRIES: int) -> None:
    # Load the dataset
    uzlib = load_dataset('tahrirchi/uzlib', split='all')
    df = uzlib.to_pandas()

    artifact_name = f"artifacts/{model_name.split('/')[-1]}.jsonl"

    with open(artifact_name, "w") as file:
        for i, row in tqdm(df.iterrows(), total=len(df), desc=model_name):
            num_tries = 0
            extracted_answer = None
            response_txt = None
            
            # Format the prompt
            prompt = f"{row['question']}\nA) {row['option_a']}\nB) {row['option_b']}\nC) {row['option_c']}\nD) {row['option_d']}\n\nJavob: "
            
            # Try to get a valid answer, with retries
            while num_tries < MAX_RETRIES and extracted_answer is None:
                response_txt = send_request(prompt, model_name)
                if response_txt:
                    extracted_answer = extract_answer(response_txt)
                num_tries += 1

            # Write the result to the output file
            file.write(json.dumps({'id': row['id'], 'response': response_txt, 'extracted_answer': extracted_answer})+'\n')

    # Calculate and display results
    df_result = pd.read_json(artifact_name, lines=True)
    df_all = df.merge(df_result, on=['id'])

    accuracy = calculate_accuracy(df_all)
    accuracy_data = list(accuracy.items())
    
    print(f"\nResults for {model_name}:")
    print(tabulate(accuracy_data, headers=['Question Type', 'Accuracy'], tablefmt='pretty'))


if __name__ == "__main__":
    parser = ArgumentParser(description="Run UzLiB benchmark on a specific model")
    parser.add_argument("--model_name", type=str, required=True, help="Name of the model to benchmark")
    parser.add_argument("--max_retries", type=int, default=3, help="Maximum number of retries for each question")

    args = parser.parse_args()
    main(args.model_name, args.max_retries)