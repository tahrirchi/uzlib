# UzLiB - Uzbek Linguistic Benchmark

[![HuggingFace](https://img.shields.io/badge/🤗%20Dataset-UzLiB-yellow)](https://huggingface.co/datasets/murodbek/uzlib)
[![GitHub](https://img.shields.io/badge/GitHub-UzLiB-blue)](https://github.com/shopulatov/uzlib)

UzLiB is a multiple-choice question benchmark for evaluating the linguistic abilities of Large Language Models (LLMs) in the Uzbek language. This benchmark helps measure how well AI models understand correct Uzbek language forms and usage.

## Overview

- **Question Types**: The benchmark includes questions on correct word choice, word meanings, contextual meanings, and fill-in-the-blank exercises
- **Question Format**: All questions are multiple-choice with options A, B, C, and D
- **Data Source**: Questions collected from popular Uzbek language Telegram channels
- **Current Leaders**: Check the [leaderboard](LEADERBOARD.md) for the latest results

## Benchmark Details

UzLiB contains questions sourced from selected Telegram channels that specialize in Uzbek language quizzes:
- [Orif Tolib](https://t.me/oriftolib)
- [Тўғри ёзамиз — мутахассис блоги](https://t.me/xatoliklar)
- [Tahrir.uz📝](https://t.me/tahrir_uz)
- [Tahrirchi | Tilmoch](https://t.me/tahrirchi_uz)

Each question has been manually labeled with the correct answer and categorized by question type.

## Getting Started

### Prerequisites
- Python 3.8+
- OpenAI API key (for testing with compatible models)
- Access to models you want to evaluate

### Installation

1. Clone the repository:
```bash
git clone https://github.com/shopulatov/uzlib.git
cd uzlib/
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.sample .env
# Edit .env with your API keys
```

### Running the Benchmark

To test a specific model:
```bash
python run_uzlib.py --model_name MODEL_NAME
```

Supported models are listed in the `MODEL_NAMES` list in [utils.py](utils.py).

### Using vLLM for Evaluation

For models from `mistralai` and `behbudiy`, we use [vllm](https://vllm.ai)'s OpenAI-Compatible Server:

1. [Install vLLM](https://docs.vllm.ai/en/latest/getting_started/installation/index.html)

2. Start the server for most models:
```bash
vllm serve MODEL_NAME --api-key token-abc123
```

3. For the `behbudiy/Llama-3.1-8B-Instuct-Uz` model, use this special command:
```bash
vllm serve behbudiy/Llama-3.1-8B-Instuct-Uz --api-key token-abc123 --chat-template "{% for message in messages %}{{'<|begin_of_text|>' if loop.first else ''}}<|start_header_id|>{{ message.role }}<|end_header_id|>\n\n{{ message.content }}\n\n<|eot_id|>{% endfor %}{% if add_generation_prompt %}<|start_header_id|>assistant<|end_header_id|>\n\n{% endif %}"
```

### Generating the Leaderboard

After evaluating models, generate an updated leaderboard:
```bash
python generate_leaderboard.py
```

## Extending the Benchmark

You can evaluate new models by adding them to the `MODEL_NAMES` list in `utils.py` and configuring the appropriate client setup.

## Citation
```
@misc{Shopulatov2025UzLiB,
      title={UzLiB: A benchmark for evaluating LLMs on Uzbek linguistics}, 
      author={Abror Shopulatov},
      year={2025}
      url={https://huggingface.co/datasets/murodbek/uzlib},
      note={Accessed: 2025-02-18}, % change this date
      urldate   = {2025-02-18} % change this date
}
```

## Contact

For questions or issues related to the dataset or code, please contact [ml.muhandis@gmail.com](mailto:ml.muhandis@gmail.com).