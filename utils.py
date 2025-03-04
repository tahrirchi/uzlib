import os
from openai import OpenAI
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

MODEL_NAMES = [
    "gemini-2.0-pro-exp-02-05",
    "gemini-2.0-flash-001",
    "gemini-2.0-flash-lite-001",
    "gemini-1.5-pro-002",
    "gemini-1.5-flash-002",

    "gpt-4o-2024-11-20",
    "gpt-4o-mini-2024-07-18",
    
    "claude-3-5-sonnet-20241022",
    "claude-3-5-sonnet-20240620",
    "claude-3-5-haiku-20241022",
    
    "google/gemma-2-9b-it",
    "google/gemma-2-27b-it",
    
    "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
    "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
    "meta-llama/Llama-3.3-70B-Instruct-Turbo",
    
    "Qwen/Qwen2.5-7B-Instruct-Turbo",
    "Qwen/Qwen2.5-72B-Instruct-Turbo",
    
    "deepseek-ai/DeepSeek-V3",
    "deepseek-ai/DeepSeek-R1-Distill-Llama-70B",

    "CohereForAI/c4ai-command-r7b-12-2024"
    "CohereForAI/c4ai-command-r-08-2024",
    "CohereForAI/c4ai-command-r-plus-08-2024",

    "mistralai/Mistral-7B-Instruct-v0.3",
    "mistralai/Mistral-Nemo-Instruct-2407",


]

def get_client(MODEL_NAME):
    if MODEL_NAME not in MODEL_NAMES:
        print(f"{MODEL_NAME} is not supported yet")
        return None
    
    if "gpt" in MODEL_NAME:
        client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    elif "claude" in MODEL_NAME:
        client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    elif "gemini" in MODEL_NAME:
        client = OpenAI(
              api_key = os.environ["GEMINI_API_KEY"],
              base_url = "https://generativelanguage.googleapis.com/v1beta/"  
        )
    
    elif "gemma" in MODEL_NAME or "cohere" in MODEL_NAME.lower() or "mistral" in MODEL_NAME.lower():
        client = OpenAI(
            api_key = os.environ["HUGGINGFACE_API_KEY"],
            base_url="https://api-inference.huggingface.co/v1/"
        )

    else:
        client = OpenAI(
            api_key=os.environ["TOGETHER_API_KEY"],
            base_url="https://api.together.xyz/v1",
        )

    return client