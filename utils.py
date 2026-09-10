import os
import re
import langid
from openai import OpenAI
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

MODEL_NAMES = [
    "claude-sonnet-5",
    "claude-opus-4-6",
    "claude-sonnet-4-6",
    "claude-opus-4-5-20251101",
    "claude-sonnet-4.5",
    "claude-opus-4-20250514",
    "claude-sonnet-4-20250514",
    "claude-3-7-sonnet-20250219",
    "claude-3-5-sonnet-20241022",
    "claude-3-5-sonnet-20240620",
    "claude-3-5-haiku-20241022",
    
    "gemini-3.5-flash",
    "gemini-3.1-pro-preview",
    "gemini-3-pro-preview",
    "gemini-3-flash-preview",
    "gemini-2.5-pro",
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-2.0-flash-001",
    "gemini-2.0-flash-lite-001",
    
    "gpt-5.2",
    "gpt-5",
    "gpt-5-mini",
    "gpt-5-nano",
    "gpt-4o-2024-11-20",
    "gpt-4o-mini-2024-07-18",

    "x-ai/grok-4.3",
    "grok-3",

    "deepseek/deepseek-v4.1-flash",
    "deepseek/deepseek-v4-pro",
    "deepseek/deepseek-v4-flash",
    "deepseek-ai/DeepSeek-V3-0324",
    
    "meta-llama/Llama-4-Maverick-17B-128E-Instruct",
    "meta-llama/Llama-4-Scout-17B-16E-Instruct",
    "meta-llama/Llama-3.3-70B-Instruct",
    "meta-llama/Meta-Llama-3.1-8B-Instruct",
    "meta-llama/Llama-3.2-3B-Instruct",
    "meta-llama/Llama-3.2-1B-Instruct",
    
    "Qwen/Qwen3.5-397B-A17B",
    "Qwen/Qwen3.5-122B-A10B",
    "Qwen/Qwen3.5-35B-A3B",
    "Qwen/Qwen3.5-27B",
    "Qwen/Qwen3.5-9B",
    "Qwen/Qwen3.5-4B",
    "Qwen/Qwen3.5-2B",
    "Qwen/Qwen3.5-0.8B",
    "qwen/qwen3.8-27b",

    "Qwen/Qwen3-235B-A22B-07-25",
    "Qwen/Qwen3-235B-A22B",
    "Qwen/Qwen3-32B",
    "Qwen/Qwen3-30B-A3B",
    "Qwen/Qwen3-14B",
    "Qwen/Qwen3-8B",
    "Qwen/Qwen3-4B",

    "moonshotai/kimi-k2",

    "z-ai/glm-5.2",
    "z-ai/glm-4.6",

    "xiaomi/mimo-v2-flash:free",

    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b",

    "command-a-03-2025",
    
    "google/gemma-4-31B-it",
    "google/gemma-4-26B-A4B-it",
    "google/gemma-4-E4B-it",
    "google/gemma-4-E2B-it",

    "gemma-3-27b-it",
    "gemma-3-12b-it",
    "gemma-3n-e4b-it",

    "mistralai/Mistral-Nemo-Instruct-2407",
    "mistralai/Mistral-7B-Instruct-v0.3",

    "behbudiy/Mistral-7B-Instruct-Uz",
    "behbudiy/Mistral-Nemo-Instruct-Uz",
    "behbudiy/Llama-3.1-8B-Instuct-Uz",

    "bxod/Llama-3.2-3B-Instruct-uz",
    "bxod/Llama-3.2-1B-Instruct-uz",

    "microsoft/phi-4",

    "NeuronUz/NeuronAI-Uzbek",

    "muse-spark-1.3-contributor",
   
    "inclusionai/ling-3.0-flash",

    "inception/mercury-2.5",
]

def get_client(model_name: str):
    if model_name not in MODEL_NAMES:
        print(f"{model_name} is not supported yet")
        return None
    
    try:
        if "gpt" in model_name:
            client = OpenAI(
                api_key=os.environ["OPENAI_API_KEY"]
            )

        elif "claude" in model_name:
            client = OpenAI(
                api_key=os.environ["ANTHROPIC_API_KEY"],
                base_url="https://api.anthropic.com/v1/"  
            )

        elif "gemini" in model_name:
            client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

        elif "mistral" in model_name or "behbudiy" in model_name or "Qwen3-4B" in model_name \
            or "llama-3.2" in model_name.lower() or "bxod" in model_name or "NeuronAI" in model_name:
            # Note: This uses hardcoded values which might need configuration
            client = OpenAI(
                api_key="token-abc123",
                base_url="http://localhost:8000/v1",
            )
                
        elif "v4.1-flash" in model_name:
            client = OpenAI(
                api_key=os.environ["DEEPSEEK_API_KEY"],
                base_url="https://api.deepseek.com",
            )
        
        else:
            client = OpenAI(
                api_key=os.environ["OPENROUTER_API_KEY"],
                base_url="https://openrouter.ai/api/v1",
            )

        return client
        
    except KeyError as e:
        print(f"Error: {str(e)}")
        return None

def preprocess_text_bxod(text):
    lang, confidence = langid.classify(text)
    return re.sub(r"[''‚‛ʻʼʽʾʿˈˊˋˌˍ'\']", "APST", text) if lang != "en" else text

def postprocess_text_bxod(text):
    return text.replace("APST", "'").strip()

def send_request(prompt: str, model_name: str):
    client = get_client(model_name)
    if client is None:
        return None
        
    try:
        if 'bxod' in model_name:
            processed_prompt = preprocess_text_bxod(prompt)
        
            response = client.chat.completions.create(
                model=model_name,
                temperature=1,
                top_p=0.95,
                max_completion_tokens=256,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant"},
                    {"role": "user", "content": processed_prompt}
                ]
            )
            
            result = response.choices[0].message.content
            return postprocess_text_bxod(result)
        
        elif 'qwen3' in model_name.lower():
            if "qwen3.5" in model_name.lower() or "qwen3.8" in model_name.lower():
                extra_body = {"reasoning": {"enabled": False}}
            else:
                extra_body = {"chat_template_kwargs": {"enable_thinking": False}}

            response = client.chat.completions.create(
                model=model_name,
                temperature=1,
                top_p=0.95,
                max_completion_tokens=256,
                messages=[{"role": "user", "content": prompt}],
                extra_body=extra_body,
                # reasoning_effort="none",
            )

            return response.choices[0].message.content
        
        elif 'neuronai' in model_name.lower() or 'neuronuz' in model_name.lower():
            # NeuronUz/NeuronAI-Uzbek model via vLLM
            # Uses Qwen3 base, so disable thinking and use system prompt
            response = client.chat.completions.create(
                model=model_name,
                temperature=1,
                top_p=0.95,
                max_completion_tokens=256,
                messages=[
                    {"role": "system", "content": "Siz o'zbek tili bo'yicha mutaxassis yordamchisiz. Savollarga aniq va qisqa javob bering."},
                    {"role": "user", "content": prompt}
                ],
                extra_body={
                    "chat_template_kwargs": {"enable_thinking": False},
                },
            )
            
            result = response.choices[0].message.content
            # Strip any <think>...</think> tags if present
            if result:
                import re
                result = re.sub(r'<think>.*?</think>', '', result, flags=re.DOTALL | re.IGNORECASE)
                result = re.sub(r'<think>.*', '', result, flags=re.DOTALL | re.IGNORECASE)
                result = result.strip()
            return result
        
        elif 'gemini' in model_name.lower():
            if "3" in model_name.lower():
                thinking_config = types.ThinkingConfig(
                    thinkingLevel = "MINIMAL",
                    # include_thoughts=True
                )

            else:
                thinking_config = types.ThinkingConfig(
                    include_thoughts=True if "2.5-pro" in model_name else None,
                    thinking_budget=128 if "2.5-pro" in model_name else 0
                )

            generate_content_config = types.GenerateContentConfig(
                temperature=1.0,
                top_p=0.95,
                max_output_tokens=512,
                thinking_config = thinking_config,
                response_mime_type="text/plain",
            )

            all_result = ""
            for chunk in client.models.generate_content_stream(
                model = model_name,
                contents = [types.Content(role="user", parts=[types.Part.from_text(text=prompt)])],
                config = generate_content_config,
            ):
                if chunk.text:
                    all_result += chunk.text
            
            return all_result
        
        elif 'gpt-oss' in model_name.lower():
            response = client.chat.completions.create(
                model=model_name,
                temperature=1,
                top_p=0.95,
                max_completion_tokens=1024,
                messages=[{"role": "user", "content": prompt}],
                reasoning_effort="low",
            )

            return response.choices[0].message.content
        
        elif 'gpt-5' in model_name.lower():
            response = client.chat.completions.create(
                model=model_name,
                temperature=1,
                # top_p=0.95,
                max_completion_tokens=256,
                messages=[{"role": "user", "content": [{"type": "text", "text": prompt}]}],
                response_format={"type": "text"},
                verbosity="low",
                reasoning_effort="none" if "5.2" in model_name else "minimal",
                store=False
            )

            return response.choices[0].message.content
        
        elif "glm" in model_name or "mimo" in model_name or "grok" in model_name:
            response = client.chat.completions.create(
                model=model_name,
                temperature=1,
                top_p=0.95,
                max_completion_tokens=256,
                messages=[{"role": "user", "content": prompt}],
                extra_body={"reasoning": {"enabled": False}}
            )

            return response.choices[0].message.content

        elif "muse-spark" in model_name:
            # Mouse Spark 1.3 via OpenCode Go (https://opencode.ai/zen/go/v1).
            # Chat Completions is not served for this model; use the
            # OpenAI Responses API with an x-opencode-session header.
            # The model emits long chain-of-thought traces before answering,
            # so max_output_tokens must be generous (256 truncates every
            # response). Sampling params follow the benchmark standard.
            import uuid as _uuid
            session_id = os.environ.get("OPENCODE_GO_SESSION_ID") or (
                "sess_" + _uuid.uuid4().hex[:24]
            )
            spark_client = OpenAI(
                api_key=os.environ["OPENCODE_GO_API_KEY"],
                base_url=os.environ.get(
                    "OPENCODE_GO_BASE_URL", "https://opencode.ai/zen/go/v1"
                ),
                default_headers={"x-opencode-session": session_id},
            )
            response = spark_client.responses.create(
                model=model_name,
                input=prompt,
                temperature=1,
                top_p=0.95,
                max_output_tokens=4096,
            )

            return response.output_text

        elif "ling-3.0-flash" in model_name or "mercury" in model_name:
            # These models emit long reasoning traces before answering, so
            # max_tokens must be generous (256 truncates most responses).
            response = client.chat.completions.create(
                model=model_name,
                temperature=1,
                top_p=0.95,
                max_tokens=2048,
                messages=[{"role": "user", "content": prompt}],
            )

            return response.choices[0].message.content

        else:
            response = client.chat.completions.create(
                model=model_name,
                temperature=1,
                top_p=0.95,
                max_completion_tokens=256,
                messages=[{"role": "user", "content": prompt}]
            )

            return response.choices[0].message.content
    
    except ValueError as e:
        print(f"Value Error for {model_name}: {str(e)}")
        return None
    
    except Exception as e:
        print(f"Exception for {model_name}: {str(e)}")
        return None
