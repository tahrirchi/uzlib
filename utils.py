import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# List of supported model names
MODEL_NAMES = [
    "gemini-2.0-pro-exp-02-05",
    "gemini-2.0-flash-001",
    "gemini-2.0-flash-lite-001",
    "gemini-1.5-pro-002",
    "gemini-1.5-flash-002",

    "gpt-4o-2024-11-20",
    "gpt-4o-mini-2024-07-18",
    
    "claude-3-7-sonnet-20250219",
    "claude-3-5-sonnet-20241022",
    "claude-3-5-sonnet-20240620",
    "claude-3-5-haiku-20241022",
    
    "google/gemma-2-27b-it",
    "google/gemma-2-9b-it",
    
    "meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo",
    "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
    "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
    "meta-llama/Llama-3.3-70B-Instruct-Turbo",
    
    "Qwen/Qwen2.5-72B-Instruct-Turbo",
    "Qwen/Qwen2.5-7B-Instruct-Turbo",
    
    "deepseek-ai/DeepSeek-V3",

    "microsoft/phi-4",

    "CohereForAI/c4ai-command-r-plus-08-2024",
    "CohereForAI/c4ai-command-r-08-2024",
    "CohereForAI/c4ai-command-r7b-12-2024",

    "mistralai/Mistral-Nemo-Instruct-2407",
    "mistralai/Mistral-7B-Instruct-v0.3",

    "behbudiy/Mistral-7B-Instruct-Uz",
    "behbudiy/Mistral-Nemo-Instruct-Uz",
    "behbudiy/Llama-3.1-8B-Instuct-Uz",
]

def get_client(MODEL_NAME):
    """
    Get the appropriate OpenAI client for a given model.
    
    Args:
        MODEL_NAME (str): The name of the model to use.
        
    Returns:
        OpenAI: An initialized OpenAI client or None if model is not supported.
        
    Raises:
        KeyError: If required environment variables are missing.
    """
    if MODEL_NAME not in MODEL_NAMES:
        print(f"{MODEL_NAME} is not supported yet")
        return None
    
    try:
        if "gpt" in MODEL_NAME:
            client = OpenAI(
                api_key=os.environ["OPENAI_API_KEY"]
            )

        elif "claude" in MODEL_NAME:
            client = OpenAI(
                api_key=os.environ["ANTHROPIC_API_KEY"],
                base_url="https://api.anthropic.com/v1/"  
            )

        elif "gemini" in MODEL_NAME:
            client = OpenAI(
                api_key=os.environ["GEMINI_API_KEY"],
                base_url="https://generativelanguage.googleapis.com/v1beta/"  
            )
        
        elif "gemma" in MODEL_NAME or "cohere" in MODEL_NAME.lower():
            client = OpenAI(
                api_key=os.environ["HUGGINGFACE_API_KEY"],
                base_url="https://api-inference.huggingface.co/v1/"
            )
        
        elif "phi" in MODEL_NAME:
            client = OpenAI(
                api_key=os.environ["NEBIUS_API_KEY"],
                base_url="https://api.studio.nebius.ai/v1/"
            )

        elif "mistral" in MODEL_NAME or "behbudiy" in MODEL_NAME:
            # Note: This uses hardcoded values which might need configuration
            client = OpenAI(
                api_key="token-abc123",
                base_url="http://localhost:8000/v1",
            )

        else:   
            client = OpenAI(
                api_key=os.environ["TOGETHER_API_KEY"],
                base_url="https://api.together.xyz/v1",
            )

        return client
        
    except KeyError as e:
        print(f"Error: {str(e)}")
        return None