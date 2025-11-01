# UzLiB - Uzbek Linguistic Benchmark

[![HuggingFace](https://img.shields.io/badge/🤗%20Dataset-UzLiB-yellow)](https://huggingface.co/datasets/tahrirchi/uzlib)
[![GitHub](https://img.shields.io/badge/GitHub-UzLiB-blue)](https://github.com/tahrirchi/uzlib)
[![Blogpost (UZ)](https://img.shields.io/badge/Blog%20Post-Read%20More-lightgrey)](https://tilmoch.ai/uz/uzlib-ozbekcha-lingvistik-benchmark)

UzLiB is the first comprehensive multiple-choice question benchmark designed to evaluate the linguistic abilities of Large Language Models (LLMs) in the Uzbek language. It measures how well AI models understand correct Uzbek language forms, usage, and nuances.

For a detailed background on the motivation and creation process, please refer to our [blog post (in Uzbek)](https://tilmoch.ai/uzlib-ozbek-lingvistik-benchmark).

## Benchmark Details

UzLiB questions were sourced from popular quizzes on the following Telegram channels specializing in Uzbek linguistics:
-   [Orif Tolib](https://t.me/oriftolib)
-   [Тўғри ёзамиз — мутахассис блоги](https://t.me/xatoliklar)
-   [Tahrir.uz📝](https://t.me/tahrir_uz)
-   [Tahrirchi | Tilmoch](https://t.me/tahrirchi_uz)

Each question underwent manual verification and standardization to ensure quality and consistency. The dataset includes conversion to Latin script and shuffling of answer choices.

Original (raw, pre-standardization) and processed versions of the benchmark are available in the [data/](data/) folder.

## Evaluation Approach

The results presented in the [leaderboard](LEADERBOARD.md) were obtained using a consistent prompt template and standard generation parameters (`temperature=1.0`, `top-p=0.95`) across all models, reflecting typical usage scenarios. Evaluation scripts and model outputs are provided for transparency.

## Getting Started

### Prerequisites
-   Python 3.8+
-   API keys for relevant LLM services (if applicable).
-   Access to models you wish to evaluate.

### Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/tahrirchi/uzlib.git
    cd uzlib/
    ```

2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3.  Set up environment variables:
    ```bash
    cp .env.sample .env
    # Edit .env with your API keys and service endpoints
    ```

### Running the Benchmark

To evaluate a specific model:
```bash
python run_uzlib.py --model_name MODEL_NAME
```

Supported models for leaderboard replication are listed in `utils.py`.

### Using vLLM for Local Evaluation

For efficient local evaluation of compatible open-source models (e.g., `Mistral`, `Llama`, `Gemma` families):

1.  [Install vLLM](https://docs.vllm.ai/en/latest/getting_started/installation/index.html).

2.  Start the vLLM OpenAI-Compatible Server:
    ```bash
    vllm serve MODEL_NAME --api-key token-abc123
    ```
    
    For the `behbudiy/Llama-3.1-8B-Instuct-Uz` model, use this special command:
    ```bash
    vllm serve behbudiy/Llama-3.1-8B-Instuct-Uz --api-key token-abc123 --chat-template "{% for message in messages %}{{'<|begin_of_text|>' if loop.first else ''}}<|start_header_id|>{{ message.role }}<|end_header_id|>\n\n{{ message.content }}\n\n<|eot_id|>{% endfor %}{% if add_generation_prompt %}<|start_header_id|>assistant<|end_header_id|>\n\n{% endif %}"
    ```

    For the `behbudiy/Mistral-Nemo-Instruct-Uz` model, use this special command:
    ```bash
    vllm serve behbudiy/Mistral-Nemo-Instruct-Uz --api-key token-abc123  --tokenizer_mode mistral --config_format mistral --load_format mistral
    ```
    
    For the `bxod/Llama-3.2-1B-Instruct-uz` and `bxod/Llama-3.2-3B-Instruct-uz` models, use this special command:
    ```bash
    vllm serve bxod/Llama-3.2-3B-Instruct-uz --api-key token-abc123 --chat-template "{% for message in messages %}{% if message['role'] == 'system' %}<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n{{ message['content'] }}<|eot_id|>{% elif message['role'] == 'user' %}<|start_header_id|>user<|end_header_id|>\n{{ message['content'] }}<|eot_id|>{% elif message['role'] == 'assistant' %}<|start_header_id|>assistant<|end_header_id|>\n{{ message['content'] }}<|eot_id|>{% endif %}{% endfor %}{% if add_generation_prompt %}<|start_header_id|>assistant<|end_header_id|>\n{% endif %}"
    ```

4.  Start evaluating deployed model.

### Generating the Leaderboard

After running evaluations (outputs are stored in `artifacts/`), update the leaderboard:
```bash
python generate_leaderboard.py
```

## Extending the Benchmark

Contributions are welcome! To evaluate new models:
1.  Add the model configuration in `utils.py`.
2.  Implement or adjust the client interaction logic if necessary.
3.  Run the evaluation and consider submitting results via a Pull Request.

## Citation

If you use UzLiB in your work, please cite it as follows:

```bibtex
@misc{Shopulatov2025UzLiB,
      title={{UzLiB: A Benchmark for Evaluating LLMs on Uzbek Linguistics}},
      author={Abror Shopulatov},
      year={2025},
      howpublished={\url{https://huggingface.co/datasets/tahrirchi/uzlib}},
      note={Accessed: YYYY-MM-DD} % Update with access date
}
```
*(Please update the `note` field with the date you accessed the resource.)*

## Contact

For inquiries regarding the benchmark or code, please contact [a.shopulatov@tilmoch.ai](mailto:a.shopulatov@tilmoch.ai).
