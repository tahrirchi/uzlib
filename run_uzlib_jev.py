import json
import pandas as pd
from tqdm import tqdm
from tabulate import tabulate
from datasets import load_dataset
from argparse import ArgumentParser
from dotenv import load_dotenv
import concurrent.futures

from typesafe_sdk import Choice, RetryPolicy, TypeSafeClient, TypeSafeAPIError

from run_uzlib import calculate_accuracy

load_dotenv()

ANSWER_QUESTION_ID = "answer"


def process_row(client: TypeSafeClient, row, model_name: str):
    criteria = {
        "A": row["option_a"],
        "B": row["option_b"],
        "C": row["option_c"],
        "D": row["option_d"],
    }

    placeholder = {
        'id': row['id'],
        'response': None,
        'extracted_answer': None,
        'confidence': None,
        'probabilities': None,
        'model': None,
    }

    try:
        result = client.system_one(
            state=row["question"],
            questions={
                ANSWER_QUESTION_ID: Choice(
                    instructions=(
                        "This is a multiple-choice question about the Uzbek "
                        "language. The state contains the question. Which of "
                        "the options is the correct answer?"
                    ),
                    criteria=criteria,
                ),
            },
        )
    except TypeSafeAPIError as e:
        print(f"TypeSafeAPIError for {row['id']}: {e.status} {e.request_id}")
        return placeholder

    answer = result.choices[ANSWER_QUESTION_ID]
    raw = result.raw_http_response.json() if result.raw_http_response else {}

    return {
        'id': row['id'],
        'response': answer.choice,
        'extracted_answer': answer.choice,
        'confidence': answer.confidence,
        'probabilities': dict(answer.probabilities),
        'model': raw.get('model', model_name),
    }


def main(model_name: str, max_retries: int, num_workers: int):
    uzlib = load_dataset('tahrirchi/uzlib', split='all')
    df = uzlib.to_pandas()

    artifact_name = f"artifacts/{model_name.split('/')[-1]}.jsonl"

    with open(artifact_name, 'w') as fout, \
         TypeSafeClient(model=model_name, retry=RetryPolicy(max_retries=max_retries)) as client, \
         concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:

        futures = {
            executor.submit(process_row, client, row, model_name): row['id']
            for _, row in df.iterrows()
        }

        for f in tqdm(
            concurrent.futures.as_completed(futures),
            total=len(futures),
            desc=f"Running {model_name}"
        ):
            try:
                res = f.result()
            except Exception as e:
                # In case of unexpected error, write a placeholder
                print(f"Exception for {futures[f]}: {str(e)}")
                rid = futures[f]
                res = {
                    'id': rid,
                    'response': None,
                    'extracted_answer': None,
                    'confidence': None,
                    'probabilities': None,
                    'model': None,
                }
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
    parser = ArgumentParser(description="Run UzLiB benchmark on Jev (TypeSafe System One)")
    parser.add_argument("--model_name", type=str, default="jev-latest",
                        help="Jev model: jev-latest, jev-preview, or a pinned version like jev-1.13.0")
    parser.add_argument("--max_retries", type=int, default=3,
                        help="Maximum number of API retries per question (SDK RetryPolicy)")
    parser.add_argument("--num_workers", type=int, default=4, help="Number of parallel workers")

    args = parser.parse_args()
    main(args.model_name, args.max_retries, args.num_workers)
