import openai

client = openai.OpenAI(
    api_key="EMPTY",
    base_url="http://localhost:8000/v1"
)

response = client.chat.completions.create(
    model="unsloth/gemma-3-1b-it",
    messages=[
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "Привет, что такое база данных?"}
    ],
    temperature=0.7,
    max_tokens=256
)

print(response.choices[0].message.content)
