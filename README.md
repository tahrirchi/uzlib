# UzLiB - Uzbek Linguistic Benchmark

The Uzbek Linguistic Benchmark (UzLiB) is a benchmark with multiple-choice questions for evaluating linguistic abilities of Large Language Models (LLMs) in Uzbek language.

The source for all questions is collected from selected 4 Telegram channels quizzes: [Orif Tolib](https://t.me/oriftolib), [Тўғри ёзамиз — мутахассис блоги](https://t.me/xatoliklar), [Tahrir.uz📝](https://t.me/tahrir_uz), and [Tahrirchi | Tilmoch](https://t.me/tahrirchi_uz). Then, each question is manually labeled to record correct answer as Telegram does not provide the correct answers for quizzes. After that, each question went through categorization, transliteration and deduplication processes.

This repository contains OpenAI API evaluation code, responses from each evaluated model and the benchmark is available in HuggingFace for download [here](https://huggingface.co/datasets/murodbek/uzlib). Raw version lives on [this Google Sheets](https://docs.google.com/spreadsheets/d/1lVJVlNxj37p-3pcCc-rxpD73z_xLPxgKse-ugqC2XRc/edit?usp=sharing).

# Reproduction

First clone this repository and install the requirements:

```bash
git clone git@github.com:shopulatov/uzlib.git
cd uzlib/
pip install -r requirements.txt
```

Then set-up `.env` file with proper API keys.

```bash
mv .env.sample .env
```

In order to test specific model, you can run:

```bash
python run_uzblib.py --model_name MODEL_NAME
```

Currently, list of testable models are restricted by `MODEL_NAMES` list in [utils.py](https://github.com/shopulatov/uzlib/blob/main/utils.py). However, the script is meant to be hackable. Feel free to include new models and change model providers. 

Some models (those from `mistralai` and `behbudiy`) are tested using [vllm](https://vllm.ai)'s OpenAI-Compatible Server with Nvidia A100 GPU instance. [Here](https://docs.vllm.ai/en/latest/getting_started/installation/index.html) is the instructions for setting up the vllm.

Once you set-up you can run the server using:

```bash
vllm serve MODEL_NAME --api-key token-abc123
```

except `behbudiy/Llama-3.1-8B-Instuct-Uz` model, in which you should change default chat template:

```bash
vllm serve behbudiy/Llama-3.1-8B-Instuct-Uz --api-key token-abc123 --chat-template "{% for message in messages %}{{'<|begin_of_text|>' if loop.first else ''}}<|start_header_id|>{{ message.role }}<|end_header_id|>\n\n{{ message.content }}\n\n<|eot_id|>{% endfor %}{% if add_generation_prompt %}<|start_header_id|>assistant<|end_header_id|>\n\n{% endif %}"
```

# Citation
```
@misc{Shopulatov2025UzLiB,
      title={UzLiB: A benchmark for evaluating Uzbek linguistics}, 
      author={Abror Shopulatov},
      year={2025}
      url={https://huggingface.co/datasets/murodbek/uzlib},
      note={Accessed: 2025-02-18}, % change this date
      urldate   = {2025-02-18} % change this date
}
```

# Contact
For any questions or issues related to the dataset or code, please contact [ml.muhandis@gmail.com](mailto:ml.muhandis@gmail.com).